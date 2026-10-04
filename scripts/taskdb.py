"""Loads the registries and every task page into one in-memory view.

Both the build hook (scripts/hooks.py) and the page generator
(scripts/gen_pages.py) read through here, so "what counts as a valid task" is
defined exactly once. scripts/validate.py checks the same view in CI.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import runsdb
import statedb
from taskio import read_page

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA = ROOT / "data"

STATUSES = ["keep", "drop", "needs-review", "pending"]
DIFFICULTIES = ["easy", "medium", "hard", "extreme", "unrated"]

# The display tags' groups (state/display_tags.yml), in display order: a tagged task carries at least one from each.
TAG_GROUPS = ("capability", "domain")

STATUS_HELP = {
    "keep": "Reviewed and staying in the suite.",
    "drop": "Reviewed and excluded. `status_reason` must say why.",
    "needs-review": "Someone looked and hit a question that blocks the call.",
    "pending": "Nobody has triaged this yet.",
}


@dataclass
class Task:
    task_id: str
    benchmark: str
    title: str
    path: Path
    src_uri: str
    meta: dict
    state: dict = field(default_factory=dict)
    body: str = ""

    @property
    def upstream(self) -> dict:
        return self.meta.get("upstream") or {}

    @property
    def status(self) -> str:
        return self.state.get("status") or "pending"

    @property
    def difficulty(self) -> str:
        return self.state.get("difficulty") or "unrated"

    @property
    def excluded(self) -> str:
        """Why the task is not part of the final benchmark (`excluded:` in state/tasks/<benchmark>.yml), "" if it is.

        The benchmark owner's call, apart from the review `status` (a benchmark that uses `drop` keeps it as it is):
        an excluded task keeps its page, its demo and its agent runs, every list shows it greyed and last, and the
        benchmark's own numbers leave it out."""
        value = self.state.get("excluded")
        if value is True:
            return "no reason given"
        return value.strip() if isinstance(value, str) else ""

    @property
    def capabilities(self) -> list[str]:
        """Tier-2 label ids assigned to this task."""
        return list(self.state.get("labels") or [])

    @property
    def tier1(self) -> list[str]:
        """Tier-1 capabilities implied by the tier-2 labels."""
        index = capability_index()
        out = []
        for lid in self.capabilities:
            parent = index.get(lid, {}).get("group_id")
            if parent and parent not in out:
                out.append(parent)
        return out

    @property
    def display_tags(self) -> list[str]:
        """Display tag ids (`display_tags:`), in vocabulary order: Capability tags before Task Domain ones."""
        return ordered_tags(self.state.get("display_tags") or [])

    @property
    def tag_groups(self) -> list[tuple[dict, list[str]]]:
        """(group, this task's display tags in it) for every group of state/display_tags.yml, in its order."""
        index = tag_index()
        return [(group, [tid for tid in self.display_tags if index.get(tid, {}).get("group_id") == group["id"]])
                for group in tag_vocabulary().get("capabilities", [])]

    @property
    def missing_tag_groups(self) -> list[str]:
        """Names of the groups (Capability, Task Domain) this task has no display tag from."""
        return [group["name"] for group, tags in self.tag_groups if group["id"] in TAG_GROUPS and not tags]

    @property
    def tagged(self) -> bool:
        """At least one display tag from each group."""
        return bool(self.display_tags) and not self.missing_tag_groups

    @property
    def skills(self) -> list[str]:
        return list(self.state.get("skills") or [])

    @property
    def note(self) -> str:
        return (self.state.get("note") or "").strip()

    @property
    def rooms(self) -> list[str]:
        return list(self.upstream.get("rooms") or [])

    @property
    def scene(self) -> str:
        return self.upstream.get("scene_model") or "unknown"

    @property
    def duration(self) -> int:
        """Length of the video we actually have, falling back to upstream's.

        Upstream publishes the teleoperation episode length. For the Vimeo
        cohort the posted video is noticeably shorter than that, so labelling a
        row with the upstream number contradicts the player next to it.
        """
        local = demo_manifest(self.benchmark).get(self.task_id, {}).get("seconds")
        return int(local or self.upstream.get("demo_duration_s") or 0)

    @property
    def has_demo(self) -> bool:
        return self.task_id in local_demos(self.benchmark)

    @property
    def scene_image(self) -> str:
        """Scene preview shipped by the benchmark, if any (a filename in its assets)."""
        return self.upstream.get("scene_image") or ""

    @property
    def instruction(self) -> str:
        return (self.upstream.get("instruction") or "").strip()

    @property
    def owner(self) -> str:
        return (self.state.get("owner") or "").strip()

    @property
    def runs(self) -> list[tuple["runsdb.BenchRun", dict]]:
        """This task in every run of its benchmark (state/runs/<benchmark>.yml), the default run first.

        Each item is (the benchmark's run, the task's view in it). The view's `in` says whether the task is in
        that run; if it is, `modes` maps each mode to its latest record from scripts/import_runs.py (or
        {"state": "queued"} before the collector has seen it; "notrun" once the run is closed). If not, `reason`
        says why and `removed` whether that was a decision (`removed:`) or the task is merely not built for it
        (`others`). Empty when the benchmark takes part in no run.
        """
        return [(br, br.view(self.task_id)) for br in runsdb.runs_of(self.benchmark)]

    def run_view(self, run: str | None = None) -> dict | None:
        """The task's view in one run (default: its benchmark's default run), or None without that run."""
        for br, view in self.runs:
            if run is None or br.run == run:
                return view
        return None

    def gaps(self) -> list[str]:
        """Open work on this page, in the order we want it filled in."""
        out = []
        if not self.instruction:
            out.append("instruction missing upstream")
        if not self.tagged:
            out.append("untagged")
        if self.difficulty == "unrated":
            out.append("unrated difficulty")
        if self.status == "pending":
            out.append("untriaged")
        if not self.owner:
            out.append("unowned")
        return out


@dataclass
class Benchmark:
    id: str
    meta: dict
    tasks: list[Task] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.meta.get("name", self.id)

    @property
    def simulator(self) -> str:
        return self.meta.get("simulator", "unknown")

    @property
    def skill_vocabulary(self) -> list[str]:
        return list(self.meta.get("skill_vocabulary") or [])

    @property
    def included(self) -> list[Task]:
        """The benchmark's own tasks: every task but the excluded ones (Task.excluded)."""
        return [t for t in self.tasks if not t.excluded]

    @property
    def excluded(self) -> list[Task]:
        """Tasks the owner left out of the final benchmark: kept on the site, greyed, last, counted apart."""
        return [t for t in self.tasks if t.excluded]


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


@functools.lru_cache(maxsize=1)
def taxonomy() -> dict:
    return statedb.load_taxonomy()


@functools.lru_cache(maxsize=1)
def capability_index() -> dict[str, dict]:
    """label id -> {name, description, group_id, group_name, from_skills, anchor}."""
    return _index(taxonomy(), anchor_for)


@functools.lru_cache(maxsize=1)
def tag_vocabulary() -> dict:
    """The display tags (state/display_tags.yml): the two groups the site shows, Capability then Task Domain."""
    return statedb.load_display_tags()


@functools.lru_cache(maxsize=1)
def tag_index() -> dict[str, dict]:
    """display tag id -> {name, description, group_id, group_name, from_skills, anchor}, in vocabulary order."""
    return _index(tag_vocabulary(), tag_anchor)


def _index(doc: dict, anchor) -> dict[str, dict]:
    out = {}
    for cap in doc.get("capabilities", []):
        for sub in cap.get("subcapabilities") or []:
            out[sub["id"]] = {
                **sub,
                "group_id": cap["id"],
                "group_name": cap["name"],
                "anchor": anchor(sub["id"]),
            }
    return out


@functools.lru_cache(maxsize=1)
def skill_to_tags() -> dict[str, list[str]]:
    """BEHAVIOR skill primitive -> the display tags that roll it up.

    Lets the editor pre-suggest tags from a task's annotated skills instead
    of making someone read the whole vocabulary every time.
    """
    out: dict[str, list[str]] = {}
    for tid, tag in tag_index().items():
        for skill in tag.get("from_skills") or []:
            out.setdefault(skill, []).append(tid)
    return out


def ordered_tags(tag_ids: list[str]) -> list[str]:
    """Display tag ids in vocabulary order (group, then tag); ids it does not know keep their order, last."""
    rank = {tid: i for i, tid in enumerate(tag_index())}
    return sorted(tag_ids, key=lambda tid: rank.get(tid, len(rank)))


def anchor_for(capability_id: str) -> str:
    """Heading ids avoid dots so they stay usable as CSS/JS selectors."""
    return "cap-" + capability_id.replace(".", "-")


def tag_anchor(tag_id: str) -> str:
    """A display tag's heading id on the Label taxonomy page, apart from the labels' `cap-` ones."""
    return "tag-" + tag_id.replace(".", "-")


@functools.lru_cache(maxsize=1)
def benchmarks() -> dict[str, Benchmark]:
    out: dict[str, Benchmark] = {}
    for path in sorted((DATA / "benchmarks").glob("*.yml")):
        bench = Benchmark(id=path.stem, meta=_load_yaml(path))
        task_dir = DOCS / "benchmarks" / bench.id / "tasks"
        records = statedb.load_tasks(bench.id)
        for task_path in sorted(task_dir.glob("*.md")):
            if task_path.stem == "index":
                continue
            meta, body = read_page(task_path)
            task_id = meta.get("task_id", task_path.stem)
            bench.tasks.append(
                Task(
                    task_id=task_id,
                    benchmark=meta.get("benchmark", bench.id),
                    title=meta.get("title", task_path.stem),
                    path=task_path,
                    src_uri=task_path.relative_to(DOCS).as_posix(),
                    meta=meta,
                    state=dict(records.get(task_id) or {}),
                    body=body,
                )
            )
        out[bench.id] = bench
    return out


# Media lives under one folder per benchmark — docs/assets/<benchmark>/ — so
# adding a suite never means dropping files into a shared bucket, and two
# benchmarks are free to use the same task id.
def asset_dir(benchmark: str) -> str:
    return f"assets/{benchmark}/"


def demo_dir(benchmark: str) -> str:
    return f"assets/{benchmark}/demos/"


def scene_dir(benchmark: str) -> str:
    return f"assets/{benchmark}/scenes/"


@functools.lru_cache(maxsize=None)
def demo_manifest(benchmark: str) -> dict[str, dict]:
    """task_id -> {seconds, bytes, width, height, poster} for one benchmark.

    Written by scripts/fetch_demos.py, one manifest per benchmark so two
    suites never write to the same file. A contributor may have none, some or
    all of the demos; the task list degrades to a placeholder for the rest.
    """
    path = DOCS / demo_dir(benchmark) / "manifest.json"
    if not path.is_file():
        return {}
    import json
    try:
        data = json.loads(path.read_text())
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


@functools.lru_cache(maxsize=None)
def local_demos(benchmark: str) -> frozenset[str]:
    return frozenset(demo_manifest(benchmark))


def reset_caches() -> None:
    """Drop every memoised view.

    The caches make a single build fast, but `mkdocs serve` rebuilds inside
    one long-lived process: without this, a rebuild triggered by an edit to
    state/ re-emits the previous values and the page never changes. Called at
    the start of each build from scripts/hooks.py.
    """
    for fn in (taxonomy, capability_index, tag_vocabulary, tag_index, skill_to_tags,
               demo_manifest, local_demos, benchmarks):
        fn.cache_clear()
    runsdb.reset_caches()


def fmt_duration(seconds: int) -> str:
    if not seconds:
        return "—"
    return f"{seconds // 60}m {seconds % 60:02d}s"


def humanize(token: str) -> str:
    return token.replace("_", " ").replace("-", " ").strip().title()

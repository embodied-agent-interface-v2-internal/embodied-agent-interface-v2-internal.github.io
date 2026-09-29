"""The run registry: which agent runs exist, which benchmarks take part in them, and what was collected.

A *run* is one agent configuration, harness + model + settings, registered once as `data/agents/<run>.yml`.
A benchmark takes part in runs through a file of its own, `state/runs/<benchmark>.yml`, owned by whoever owns the
benchmark: its default run and, per run, the Harbor batches, the tasks in scope, why the others are out and what is
arranged for single trials. `scripts/import_runs.py` writes what it collects to `data/runs/<benchmark>/<run>.json`,
one file per benchmark and run, so one owner's import never rewrites another's. `data/prices.yml` holds the list
prices behind the cost estimate.

Read-only, and shared by the importer, the page generator, the build hook and the validator, so all four agree on
what a run is. See docs/contributing/registering-runs.md for the file formats.
"""

from __future__ import annotations

import functools
import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

import sitemode

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / "data" / "agents"          # one file per run definition
PRICES = ROOT / "data" / "prices.yml"
PLANS = ROOT / "state" / "runs"            # one file per benchmark
OUT = ROOT / "data" / "runs"               # <benchmark>/<run>.json, written by scripts/import_runs.py (local only)
PUBLISHED = ROOT / "data" / "published_runs"   # the committed, filtered snapshot the public site shows (publish_runs.py)
LOCAL = ".local.yml"                       # a registry file only this machine has (gitignored): a run kept out of git

DEFAULT_MODES = ["unlimited", "limited"]
DEFAULT_TASK_DIR = "{benchmark}-{task_dashed}-i00"
BILLING = {
    "subscription": "a subscription login: no per-token bill",
    "openrouter": "billed per request by OpenRouter (the charge it reports in every response)",
    "api": "billed by the provider's API; we hold no per-trial bill, so only the estimate is shown",
    "none": "no model bill",
}


# Files that could not be read, as (path, error). One owner's broken file must not stop the importer or the build
# for everyone else: it is skipped, and scripts/validate.py reports it.
ERRORS: list[tuple[str, str]] = []


def _yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else None
    except (OSError, yaml.YAMLError) as exc:
        ERRORS.append((str(path.relative_to(ROOT)), str(exc).replace("\n", " ")[:300]))
        return {}
    if data is not None and not isinstance(data, dict):
        ERRORS.append((str(path.relative_to(ROOT)), "not a mapping"))
    return data if isinstance(data, dict) else {}


def _run_id(path: Path) -> str:
    return path.name[: -len(LOCAL)] if path.name.endswith(LOCAL) else path.stem


@functools.lru_cache(maxsize=1)
def agents() -> dict[str, dict]:
    """run id -> its definition (data/agents/<run>.yml, or <run>.local.yml for one kept out of git), with `id` filled
    in from the file name."""
    return {_run_id(p): {**_yaml(p), "id": _run_id(p)} for p in sorted(AGENTS.glob("*.yml"))}


# A run id: <harness>-<model>-<effort>[-<tag>], fields of [a-z0-9_]+ (docs/contributing/registering-runs.md).
RUN_ID = re.compile(r"^[a-z0-9_]+-[a-z0-9_]+-[a-z0-9_]+(?:-[a-z0-9_]+)?$")


def id_of(agent: dict) -> str | None:
    """The run id an agent definition spells: `harness_id`, the model's `id` in data/prices.yml (via `price`; or
    `model_id` for a model without a price there), the reasoning effort in `settings`, and the optional `tag`. None
    when a part is missing."""
    model = (prices().get(str(agent.get("price") or "")) or {}).get("id") or agent.get("model_id")
    effort = (agent.get("settings") or {}).get("reasoning_effort")
    parts = [agent.get("harness_id"), model, effort] + ([agent["tag"]] if agent.get("tag") else [])
    return "-".join(str(p) for p in parts) if all(parts) else None


@functools.lru_cache(maxsize=1)
def aliases() -> dict[str, str]:
    """former run id -> run id (`formerly:` in data/agents/<run>.yml): a renamed run's old links keep working (a
    redirect page at each of its former log pages, ?run=<former id> on a Runs page)."""
    return {str(old): rid for rid, a in agents().items() for old in (a.get("formerly") or [])}


@functools.lru_cache(maxsize=1)
def prices() -> dict[str, dict]:
    """price key -> {input, cached_input, output, ...}: USD per 1M tokens, list prices (data/prices.yml)."""
    return {k: v for k, v in _yaml(PRICES).items() if isinstance(v, dict)}


@functools.lru_cache(maxsize=1)
def plans() -> dict[str, dict]:
    """benchmark id -> its runs file (state/runs/<benchmark>.yml), with the runs of state/runs/<benchmark>.local.yml
    added: runs this machine keeps out of git (gitignored), after the committed ones."""
    out = {p.stem: _yaml(p) for p in sorted(PLANS.glob("*.yml")) if not p.name.endswith(LOCAL)}
    for p in sorted(PLANS.glob("*" + LOCAL)):
        local = _yaml(p)
        plan = out.setdefault(_run_id(p), {})
        if isinstance(local.get("runs"), dict):
            plan["runs"] = {**(plan.get("runs") or {}), **{k: v for k, v in local["runs"].items() if k not in (plan.get("runs") or {})}}
    return out


@dataclass(frozen=True, eq=False)
class BenchRun:
    """One benchmark's part in one run: its spec from state/runs/<benchmark>.yml and the run's definition."""

    benchmark: str
    run: str
    spec: dict
    agent: dict
    default: bool

    # ---------------------------------------------------------------- what the run is (data/agents/<run>.yml)

    @property
    def label(self) -> str:
        return str(self.agent.get("label") or self.run)

    @property
    def short(self) -> str:
        return str(self.agent.get("short") or self.label)

    @property
    def modes(self) -> list[str]:
        return list(self.spec.get("modes") or self.agent.get("modes") or DEFAULT_MODES)

    @property
    def billing(self) -> str:
        return str(self.agent.get("billing") or "api")

    @property
    def price(self) -> dict | None:
        return prices().get(str(self.agent.get("price") or ""))

    # --------------------------------------------------------- this benchmark's part (state/runs/<benchmark>.yml)

    @property
    def batches(self) -> list[str]:
        """The Harbor batches in order: `batch`, then `rerun_batches`. For a task and mode the last one with the job wins."""
        return [x for x in [self.spec.get("batch"), *(self.spec.get("rerun_batches") or [])] if x]

    @property
    def rerun_all(self) -> bool:
        """The last rerun batch reruns every task and mode; a job it has not started yet is queued, not the old result."""
        return bool(self.spec.get("rerun_all")) and len(self.batches) > 1

    @property
    def tasks(self) -> list[str]:
        return list(self.spec.get("tasks") or [])

    # The notes below name our machines at times ("rerun on the laptop"): the public site hides them
    # (sitemode.scrub_hosts); a local build shows them as written.

    @property
    def removed(self) -> dict[str, str]:
        return {t: sitemode.scrub_hosts(str(why)) for t, why in (self.spec.get("removed") or {}).items()}

    @property
    def others(self) -> str:
        return sitemode.scrub_hosts(str(self.spec.get("others") or ""))

    @property
    def followups(self) -> list[dict]:
        return [{**f, "note": sitemode.scrub_hosts(str(f.get("note") or ""))} if f.get("note") else f
                for f in (self.spec.get("followups") or []) if isinstance(f, dict)]

    @property
    def not_counted(self) -> dict[tuple[str, str, str], str]:
        """(task, mode, trial) -> why: a trial that ran but whose result does not count (`not_counted:` in
        state/runs/<b>.yml), e.g. one that could not be won on its host. It reads "not counted", keeps its page, and
        counts in no statistic, like a trial we stopped; a later trial of the same task and mode counts again."""
        return {(f.get("task"), f.get("mode"), f.get("trial")): sitemode.scrub_hosts(str(f.get("note")))
                for f in (self.spec.get("not_counted") or []) if isinstance(f, dict) and f.get("note")}

    @property
    def notes(self) -> dict[tuple[str, str, str], str]:
        """(task, mode, trial) -> a note on that trial (`notes:` in state/runs/<b>.yml), which is graded as it is:
        nothing is arranged for it, unlike a follow-up. It shows while that trial is the task's record."""
        return {(f.get("task"), f.get("mode"), f.get("trial")): sitemode.scrub_hosts(str(f.get("note")))
                for f in (self.spec.get("notes") or []) if isinstance(f, dict) and f.get("note")}

    @property
    def closed(self) -> str:
        """Why the run is over (empty while it is still going). A closed run's never-started jobs read "not run"."""
        return sitemode.scrub_hosts(str(self.spec.get("closed") or ""))

    @property
    def stopped(self) -> dict[tuple[str, str], str]:
        """(task, mode) -> why: trials we stopped ourselves before they finished (`stopped:` in state/runs/<b>.yml),
        or kept from starting. They read "stopped by us", keep their pages, and count in no statistic."""
        return {(f.get("task"), f.get("mode")): sitemode.scrub_hosts(str(f.get("note") or "stopped by us"))
                for f in (self.spec.get("stopped") or []) if isinstance(f, dict)}

    @property
    def hidden(self) -> bool:
        """`hidden: true`: the owner keeps the run in the registry but out of sight. The site shows it nowhere (run
        picker, overview, task list, task pages, log pages) and scripts/import_runs.py stops collecting it; its entry,
        its data/agents/ file and whatever was collected of it stay."""
        return self.spec.get("hidden") is True

    @property
    def progress_key(self) -> str:
        """Where the grader keeps the partial credit: a reward.json key, or `q_score` (BEHAVIOR's challenge score)."""
        return str(self.spec.get("progress") or (plans().get(self.benchmark) or {}).get("progress") or "final_reward")

    @property
    def metrics(self) -> list[dict]:
        """The continuous grader outputs this benchmark shows beside success (`metrics:` in state/runs/<benchmark>.yml):
        [{key, label, format, unit, better, summary, help}], in the file's order; [] when it declares none."""
        raw = self.spec.get("metrics") or (plans().get(self.benchmark) or {}).get("metrics") or []
        out = []
        for m in raw if isinstance(raw, list) else []:
            if isinstance(m, dict) and m.get("key"):
                out.append({"key": str(m["key"]), "label": str(m.get("label") or m["key"]),
                            "format": str(m.get("format") or ".2f"), "unit": str(m.get("unit") or ""),
                            "better": "lower" if m.get("better") == "lower" else "higher",
                            "summary": "median" if m.get("summary") == "median" else "mean",
                            "help": str(m.get("help") or "")})
        return out

    @property
    def per_family(self) -> dict | None:
        """A grader output whose meaning depends on the task's family (`per_family: {key, label}` in
        state/runs/<benchmark>.yml; RoboPaint's final_reward): the Runs page shows success and its plain mean per family
        and mode, naming each family's metric by its tasks' upstream `continuous_score`, and the home table's aggregate
        is its plain mean, "mean <label>". None when the benchmark declares none."""
        raw = self.spec.get("per_family") or (plans().get(self.benchmark) or {}).get("per_family")
        if not isinstance(raw, dict) or not raw.get("key"):
            return None
        return {"key": str(raw["key"]), "label": str(raw.get("label") or raw["key"])}

    def task_dir(self, task: str) -> str:
        """The harness's task directory for a task id: Harbor names a job <batch>-<mode>-<task dir>."""
        tpl = str(self.spec.get("task_dir") or (plans().get(self.benchmark) or {}).get("task_dir") or DEFAULT_TASK_DIR)
        return tpl.format(benchmark=self.benchmark, task=task, task_dashed=task.replace("_", "-"))

    # ----------------------------------------------------------------------------- what was collected about it

    @property
    def out_path(self) -> Path:
        return OUT / self.benchmark / f"{self.run}.json"

    @property
    def data(self) -> dict:
        return collected(self.benchmark, self.run)

    def view(self, task: str) -> dict:
        """This task in this run: {"in": True, "modes": {mode: record}} or {"in": False, "removed", "reason"}.

        A record is the importer's (scripts/import_runs.py record()), or {"state": "queued"} before it has seen the
        job; in a closed run a job that never started is {"state": "notrun"}; where this machine has collected
        nothing for the run at all (a colleague's run, a build without data), every record is {"state": "nodata"}."""
        if task in self.tasks:
            if not self.data:
                return {"in": True, "modes": {m: {"state": "nodata"} for m in self.modes}}
            got = (self.data.get("tasks") or {}).get(task) or {}
            stopped, notes, void = self.stopped, self.notes, self.not_counted
            rerun_for = {(f.get("task"), f.get("mode"), f.get("trial")): f.get("note") for f in self.followups if f.get("note")}
            modes = {}
            for m in self.modes:
                rec = got.get(m) or {"state": "queued"}
                if self.closed and rec.get("state", "queued") == "queued":
                    rec = {**rec, "state": "notrun"}
                if (task, m) in stopped:     # the importer's state stays in data/runs/ (and status.json) as it was
                    rec = {**rec, "state": "stopped", "stopped": stopped[(task, m)], "state_was": rec.get("state")}
                elif rec.get("trial") and (task, m, rec["trial"]) in void:     # likewise
                    rec = {**rec, "state": "uncounted", "uncounted": void[(task, m, rec["trial"])],
                           "state_was": rec.get("state")}
                if rec.get("trial") and (task, m, rec["trial"]) in notes:     # likewise only here, never collected
                    rec = {**rec, "note": notes[(task, m, rec["trial"])]}
                sup = rec.get("supersedes")
                if isinstance(sup, dict) and (task, m, sup.get("trial")) in rerun_for:   # why a rerun replaced it
                    rec = {**rec, "supersedes": {**sup, "followup": rerun_for[(task, m, sup.get("trial"))]}}
                modes[m] = rec
            return {"in": True, "modes": modes}
        why = self.removed.get(task)
        return {"in": False, "removed": bool(why), "reason": why or self.others or "not in this run"}


@functools.lru_cache(maxsize=None)
def collected(benchmark: str, run: str) -> dict:
    """data/runs/<benchmark>/<run>.json, or {} where this machine has collected nothing for it.

    The public build (scripts/sitemode.py) reads the committed snapshot instead, data/published_runs/<benchmark>/
    <run>.json (scripts/publish_runs.py): never the local data, even on a machine that has it."""
    path = (PUBLISHED if sitemode.PUBLIC else OUT) / benchmark / f"{run}.json"
    try:
        data = json.loads(path.read_text()) if path.is_file() else {}
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def runs_of(benchmark: str, hidden: bool = False) -> list[BenchRun]:
    """The benchmark's runs, its default run first, then in file order; a run marked `hidden: true` only with
    `hidden=True` (BenchRun.hidden)."""
    plan = plans().get(benchmark) or {}
    specs = plan.get("runs") or {}
    if not isinstance(specs, dict):
        return []
    default = plan.get("default") or next(iter(specs), None)
    order = sorted(specs, key=lambda r: r != default)
    runs = [BenchRun(benchmark, r, specs[r] or {}, agents().get(r) or {"id": r}, r == default) for r in order]
    return [br for br in runs if hidden or not br.hidden]


def default_run(benchmark: str) -> BenchRun | None:
    return next(iter(runs_of(benchmark)), None)


def get(benchmark: str, run: str) -> BenchRun | None:
    """One run of a benchmark by id, hidden or not."""
    return next((br for br in runs_of(benchmark, hidden=True) if br.run == run), None)


def all_runs(hidden: bool = False) -> list[BenchRun]:
    return [br for bid in plans() for br in runs_of(bid, hidden)]


def estimate_usd(tokens: dict | None, price: dict | None) -> float | None:
    """List-price estimate of one trial's model use, in USD: (input - cached) x input + cached x cached_input +
    output x output, per 1M tokens (output includes the reasoning tokens). None when either side is unknown."""
    if not tokens or not price or tokens.get("input") is None:
        return None
    try:
        tin, cached, out = float(tokens.get("input") or 0), float(tokens.get("cached") or 0), float(tokens.get("output") or 0)
        return ((tin - cached) * float(price["input"]) + cached * float(price.get("cached_input", price["input"]))
                + out * float(price["output"])) / 1e6
    except (KeyError, TypeError, ValueError):
        return None


def reset_caches() -> None:
    """Drop every memoised view (`mkdocs serve` rebuilds in one long-lived process; see taskdb.reset_caches)."""
    for fn in (agents, aliases, prices, plans, collected):
        fn.cache_clear()
    ERRORS.clear()

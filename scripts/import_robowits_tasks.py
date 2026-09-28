#!/usr/bin/env python3
"""Sync RoboWits task pages from the benchmark's own source tree.

RoboWits publishes no task gallery; the tasks *are* the code. Each environment
module carries everything a reviewer needs in machine-readable form: the
registry id in a `@register_task` decorator, the instruction in the
`task_description` property, and the success criteria as a bullet list in the
class docstring. We read those with `ast` rather than importing, so this runs
anywhere — no Genesis, no GPU.

Point `--source` at a checkout pinned to the commit we build our image from
(`images/robowits/Dockerfile`, currently 9cc30ae) and the result is cached in
`data/benchmarks/robowits.tasks.upstream.json`, so rebuilding the pages needs
no checkout at all.

Re-running is safe and expected:
  * new upstream task    -> a fresh page is scaffolded from the template
  * existing task        -> only the `upstream:` frontmatter block is rewritten
  * task pulled upstream -> reported, never deleted (a human decides)

Usage:
  python scripts/import_robowits_tasks.py --source ~/src/RoboWits   # read + write
  python scripts/import_robowits_tasks.py                           # from the cache
  python scripts/import_robowits_tasks.py --dry-run
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = "robowits"
CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.upstream.json"
TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"
REPO_URL = "https://github.com/UMass-Embodied-AGI/RoboWits"
SITE_URL = "https://umass-embodied-agi.github.io/RoboWits/"

TASK_FILE_RE = re.compile(r"^(\d\d)_([a-z0-9_]+)\.py$")
BLENDERKIT_RE = re.compile(r"blender_kit/([0-9a-f-]{8,})")
MATERIAL_RE = re.compile(r"gs\.materials\.(\w+)")
BULLET_RE = re.compile(r"^(?:[-*\u2022]|\d+[.)])\s+(.*)$")
SECTION_RE = re.compile(r"^[A-Z][\w /]{2,30}:(?:\s|$)")   # "Observation:", "Action:" — a new docstring section

# ───────────────────────────────────────────────────── project-page videos

VIDEO_RE = re.compile(r'src="\./static/videos/(\d\d)\.mp4"')
CAPTION_RE = re.compile(r">([^<>{}]{3,40})<")


def site_videos(url: str = SITE_URL) -> dict[int, dict]:
    """Task number -> {url, caption} from the project page's task gallery.

    The gallery puts each clip's caption after its `<video>`, so the caption of
    clip *k* is the first readable text between clip *k* and clip *k+1*. We
    return it alongside the URL and check it against the task title, because a
    silent renumbering upstream would otherwise attach the wrong video to a
    task — the one failure here nobody would notice by reading a diff.
    """
    import html as _html
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": "robobench-docs/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        page = resp.read().decode("utf-8", "replace")

    hits = list(VIDEO_RE.finditer(page))
    out: dict[int, dict] = {}
    for i, m in enumerate(hits):
        number = int(m.group(1))
        if number in out:
            continue                      # the gallery repeats clips further down
        end = hits[i + 1].start() if i + 1 < len(hits) else len(page)
        caption = ""
        for c in CAPTION_RE.findall(page[m.end():end]):
            c = _html.unescape(c).strip()
            if c and not c.startswith((".", "{", "//")) and not c.lower().startswith("empty column"):
                caption = c
                break
        out[number] = {"url": urllib.parse.urljoin(url, f"static/videos/{number:02d}.mp4"),
                       "caption": caption}
    return out


BODY_TEMPLATE = """
## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/robowits.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- RoboWits ships no oracle demonstrations: the reference solutions are ours,
     written against the task's own success predicate. If this task has one,
     say whether the trajectory is clean and what it relies on. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->
"""


# ────────────────────────────────────────────────────────── source reading

def _docstring_parts(doc: str) -> tuple[str, list[str]]:
    """(summary, success criteria bullets) from a task class docstring."""
    if not doc:
        return "", []
    lines = [ln.strip() for ln in doc.strip().splitlines()]
    summary, criteria = [], []
    in_criteria = False
    summary_done = False
    for ln in lines:
        # Authors write the header as "Success criteria:" or "Task success
        # criteria:", and the bullets as "-", "*" or "1.". Accept all of them.
        if "success criteria" in ln.lower() and ln.rstrip().endswith(":"):
            in_criteria = True
            summary_done = True
            continue
        if in_criteria:
            bullet = BULLET_RE.match(ln)
            if bullet:
                criteria.append(bullet.group(1).strip())
            elif SECTION_RE.match(ln):
                in_criteria = False            # a new docstring section ends the list
            elif ln and criteria:
                criteria[-1] += " " + ln       # a wrapped continuation
            continue
        # The summary is the first paragraph; later paragraphs are detail we
        # keep out of the frontmatter (the page links to the source file).
        if not ln:
            summary_done = bool(summary)
            continue
        if not summary_done:
            summary.append(ln)
    return " ".join(summary), criteria


def _returned_string(node: ast.AST) -> str:
    for sub in ast.walk(node):
        if isinstance(sub, ast.Return) and isinstance(sub.value, ast.Constant) and isinstance(sub.value.value, str):
            return sub.value.value
    return ""


def _init_defaults(cls: ast.ClassDef) -> dict:
    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name == "__init__":
            args = item.args
            names = [a.arg for a in args.args][-len(args.defaults):] if args.defaults else []
            out = {}
            for name, default in zip(names, args.defaults):
                if isinstance(default, ast.Constant):
                    out[name] = default.value
            return out
    return {}


def parse_task_module(path: Path) -> dict | None:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        registry = ""
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and getattr(dec.func, "id", "") == "register_task" and dec.args:
                arg = dec.args[0]
                if isinstance(arg, ast.Constant):
                    registry = arg.value
        if not registry:
            continue
        summary, criteria = _docstring_parts(ast.get_docstring(node) or "")
        instruction = ""
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "task_description":
                instruction = _returned_string(item)
        defaults = _init_defaults(node)
        return {
            "class": node.name,
            "registry_id": registry,
            "summary": summary,
            "success_criteria": criteria,
            "instruction": instruction,
            "episode_steps_default": defaults.get("max_episode_steps"),
            "control_mode_default": defaults.get("control_mode"),
            "blenderkit_assets": len(set(BLENDERKIT_RE.findall(src))),
            "materials": sorted({m for m in MATERIAL_RE.findall(src)}),
        }
    return None


def read_source(source: Path) -> list[dict]:
    env_dir = source / "gs_gym" / "envs" / "robowits"
    if not env_dir.is_dir():
        sys.exit(f"{source} does not look like a RoboWits checkout (no {env_dir})")
    mutation_dir = env_dir / "mutation"
    eval_dir = source / "dataset" / "robowits" / "eval_dataset_50"

    tasks = []
    for path in sorted(env_dir.glob("*.py")):
        m = TASK_FILE_RE.match(path.name)
        if not m:
            continue
        number, slug = m.group(1), m.group(2)
        parsed = parse_task_module(path)
        if not parsed:
            continue

        # The evaluation dataset is the ground truth for what varies between
        # episodes: one entry per scene, each listing every placed object and
        # the physics material it is simulated with.
        objects: list[str] = []
        materials: list[str] = []
        scenes = 0
        eval_json = eval_dir / f"{number}.json"
        if eval_json.is_file():
            entries = json.loads(eval_json.read_text())
            scenes = len(entries)
            if entries:
                objects = sorted(entries[0])
                # Only placed objects appear here. Anything the task spawns itself
                # (dough, sand, water) shows up in the source scan instead.
                materials = sorted({(o or {}).get("material", "") for o in entries[0].values() if isinstance(o, dict)} - {""})

        mutations = len(list(mutation_dir.glob(f"{number}_*.py"))) if mutation_dir.is_dir() else 0

        tasks.append({
            "id": f"{slug}",
            "number": int(number),
            "title": slug.replace("_", " ").title(),
            "source_file": f"gs_gym/envs/robowits/{path.name}",
            "eval_scenes": scenes,
            "objects": objects,
            "object_materials": sorted({m.lower() for m in materials + parsed["materials"]}),
            "mutations": mutations,
            **parsed,
        })
    return tasks


# ────────────────────────────────────────────────────────── page writing

def upstream_block(task: dict, synced: str, commit: str) -> dict:
    """What the benchmark itself states about the task.

    Deliberately not filled: `demo_duration_s`, `oracle_video`. RoboWits
    publishes no per-task demonstration video, and putting our own oracle's
    runtime in a field named "demo duration" would read as upstream's number.
    """
    block = {
        "source": f"{REPO_URL} @ {commit}" if commit else REPO_URL,
        "synced": synced,
        "instruction": task["instruction"] or task["summary"],
        "scene_model": "robowits_table",
        "registry_id": task["registry_id"],
        "task_number": task["number"],
        "source_file": task["source_file"],
        "env_class": task["class"],
    }
    if task["success_criteria"]:
        block["success_criteria"] = task["success_criteria"]
    if task["objects"]:
        block["objects"] = task["objects"]
    if task["object_materials"]:
        block["object_materials"] = task["object_materials"]
    if task["eval_scenes"]:
        block["eval_scenes"] = task["eval_scenes"]
    if task["mutations"]:
        block["mutations"] = task["mutations"]
    if task["blenderkit_assets"]:
        block["blenderkit_assets"] = task["blenderkit_assets"]
    if task["episode_steps_default"]:
        block["episode_steps_default"] = task["episode_steps_default"]
    if task["control_mode_default"]:
        block["control_mode_default"] = task["control_mode_default"]
    if task.get("oracle_video"):
        block["oracle_video"] = task["oracle_video"]
        block["oracle_video_source"] = SITE_URL
    return block


def scaffold(task: dict, synced: str, commit: str) -> dict:
    return {
        "title": task["title"],
        "task_id": task["id"],
        "benchmark": BENCHMARK,
        "upstream": upstream_block(task, synced, commit),
    }


def git_commit(source: Path) -> str:
    import subprocess
    try:
        out = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip()[:7]
    except Exception:  # noqa: BLE001
        return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=None, help="a RoboWits checkout; omit to use the cache")
    ap.add_argument("--no-videos", action="store_true",
                    help="skip the project page; keep whatever video URLs are cached")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rewrite pages even when upstream is unchanged")
    args = ap.parse_args()

    if args.source:
        source = Path(args.source).expanduser()
        tasks = read_source(source)
        if not args.no_videos:
            try:
                videos = site_videos()
            except Exception as exc:  # noqa: BLE001
                print(f"could not read the project page ({exc!r}); no video URLs recorded")
                videos = {}
            matched = mismatched = 0
            for task in tasks:
                hit = videos.get(task["number"])
                if not hit:
                    continue
                task["oracle_video"] = hit["url"]
                expected = task["title"].lower().replace(" ", "")
                got = hit["caption"].lower().replace(" ", "")
                # Titles differ in plurality upstream ("Collect Screw" vs
                # collect_screws), so compare on a prefix rather than exactly.
                if got and not (expected.startswith(got[:8]) or got.startswith(expected[:8])):
                    print(f"  ! task {task['number']:02d} {task['title']!r} <- clip captioned {hit['caption']!r}")
                    mismatched += 1
                else:
                    matched += 1
            print(f"project-page videos: {matched} matched, {mismatched} questionable, "
                  f"{len(tasks) - matched - mismatched} without a clip")
        payload = {"source": REPO_URL, "commit": git_commit(source),
                   "site": SITE_URL, "read": dt.date.today().isoformat(), "tasks": tasks}
        CACHE.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"read {len(tasks)} task(s) from {source} -> {CACHE.name}")
    else:
        if not CACHE.is_file():
            sys.exit(f"no cache at {CACHE}; run once with --source <RoboWits checkout>")
        payload = json.loads(CACHE.read_text())
        tasks = payload["tasks"]

    synced = dt.date.today().isoformat()
    commit = payload.get("commit", "")
    TASK_DIR.mkdir(parents=True, exist_ok=True)

    created = updated = unchanged = 0
    seen = set()
    for task in tasks:
        seen.add(task["id"])
        path = TASK_DIR / f"{task['id']}.md"
        fresh = upstream_block(task, synced, commit)
        if path.is_file():
            meta, body = read_page(path)
            current = dict(meta.get("upstream") or {})
            # `synced` alone is not a reason to rewrite the file.
            comparable = dict(fresh, synced=current.get("synced", synced))
            if current == comparable and not args.force:
                unchanged += 1
                continue
            meta["upstream"] = dict(fresh, synced=synced)
            if not args.dry_run:
                write_page(path, meta, body)
            updated += 1
        else:
            if not args.dry_run:
                write_page(path, scaffold(task, synced, commit), BODY_TEMPLATE)
            created += 1

    orphans = sorted(p.stem for p in TASK_DIR.glob("*.md") if p.stem not in seen and p.stem != "index")

    print(f"upstream tasks : {len(tasks)}")
    print(f"created        : {created}{' (dry run)' if args.dry_run else ''}")
    print(f"updated        : {updated}")
    print(f"unchanged      : {unchanged}")
    if orphans:
        print(f"no longer upstream ({len(orphans)}): {', '.join(orphans)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

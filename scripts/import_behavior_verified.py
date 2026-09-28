#!/usr/bin/env python3
"""Mirror first-hand facts from the licensed BEHAVIOR-1K stack into task pages.

The gallery importer (scripts/import_behavior_tasks.py) mirrors the public demo
gallery. This one mirrors the *distribution we actually run*: the BDDL activity
definitions that define success, and the 2026 challenge task-instance bundle.
Both are licensed downloads, so the extraction happens where they live and the
result is cached in the repository — nobody needs the 33 GB dataset to rebuild
the site.

Why it is worth having: the gallery publishes no instruction for the 50 carried
-over tasks, and its episode durations are wrong for the Vimeo cohort (see
HANDOFF.md). The BDDL goal is the definition the evaluator scores against, and
`task.jsonl` carries the real per-task demonstration statistics.

Two modes:

  --extract     read the BDDL definitions and the dataset, write the cache.
                Run it where those exist — inside the simulator image:

                  docker run --rm -e OMNIGIBSON_NO_OMNIVERSE=1 \
                    -v $PWD/scripts:/s:ro -v $RCB_BEHAVIOR_DATA:/data:ro \
                    -v $PWD/data/benchmarks:/out \
                    ghcr.io/jameskrw/rcb-behavior:0.1.1 \
                    python /s/import_behavior_verified.py --extract \
                      --data-root /data --out /out/behavior-1k.tasks.verified.json

  (default)     write the cached facts into the `verified:` block of every task
                page. Idempotent: re-running with an unchanged cache writes
                nothing. Never touches `upstream:`, the prose, or state/.

The `verified:` block is a third frontmatter zone, owned by this script, kept
separate from `upstream:` so that a gallery re-sync (which replaces `upstream:`
wholesale) cannot drop it.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = "behavior-1k"
CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.verified.json"
TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"

# BDDL heads that structure the goal rather than assert a state.
LOGICAL = {"and", "or", "not", "imply", "forall", "exists",
           "forn", "forpairs", "fornpairs"}
QUANTIFIERS = {"forall", "exists", "forn", "forpairs", "fornpairs"}
CATEGORY_RE = re.compile(r"[a-zA-Z_]+\.n\.\d+")


# ───────────────────────────────────────────────────────────── BDDL parsing

def sexp(text: str):
    """Parse one BDDL file into nested lists. Comments start with `;`."""
    text = re.sub(r";[^\n]*", " ", text)
    tokens = text.replace("(", " ( ").replace(")", " ) ").split()
    stack: list[list] = [[]]
    for tok in tokens:
        if tok == "(":
            stack.append([])
        elif tok == ")":
            done = stack.pop()
            if not stack:
                raise ValueError("unbalanced )")
            stack[-1].append(done)
        else:
            stack[-1].append(tok)
    if len(stack) != 1:
        raise ValueError("unbalanced (")
    return stack[0][0]


def section(tree, name: str):
    for node in tree:
        if isinstance(node, list) and node and node[0] == name:
            return node
    return None


def walk_goal(node, predicates: set, quantifiers: set, categories: set, counts: set) -> None:
    """Collect goal predicates, quantifiers, categories and `forn` counts.

    Two kinds of list are structure, not assertion, and must not be mistaken
    for predicates: a quantifier's parameter list `(?x - category)`, whose head
    is a variable, and `forn`'s count `(2)`, whose head is a number.
    """
    if isinstance(node, str):
        m = CATEGORY_RE.search(node)
        if m:
            categories.add(m.group(0))
        return
    if not node:
        return
    head = node[0] if isinstance(node[0], str) else None
    if head in QUANTIFIERS:
        quantifiers.add(head)
    elif head and head.isdigit():
        counts.add(int(head))
    elif head and not head.startswith("?") and head not in LOGICAL:
        predicates.add(head)
    for child in node:
        walk_goal(child, predicates, quantifiers, categories, counts)


def goal_facts(bddl_text: str) -> dict:
    tree = sexp(bddl_text)
    goal = section(tree, ":goal")
    objects = section(tree, ":objects")

    predicates: set[str] = set()
    quantifiers: set[str] = set()
    categories: set[str] = set()
    counts: set[int] = set()
    clauses = 0
    if goal:
        body = goal[1] if len(goal) > 1 else []
        walk_goal(body, predicates, quantifiers, categories, counts)
        clauses = (len(body) - 1) if (isinstance(body, list) and body and body[0] == "and") else 1

    # `(:objects inst_1 inst_2 - category ...)` — count instances per category.
    obj_categories: dict[str, int] = {}
    if objects:
        pending = 0
        for tok in objects[1:]:
            if not isinstance(tok, str):
                continue
            if tok == "-":
                continue
            if CATEGORY_RE.fullmatch(tok):
                obj_categories[tok] = obj_categories.get(tok, 0) + pending
                pending = 0
            else:
                pending += 1

    return {
        "goal_predicates": sorted(predicates),
        "goal_quantifiers": sorted(quantifiers),
        "goal_counts": sorted(counts),
        "goal_clauses": clauses,
        "goal_categories": sorted(categories),
        "objects": sum(obj_categories.values()),
        "object_categories": len(obj_categories),
    }


# ───────────────────────────────────────────────────────────── extraction

def find_bddl_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    try:
        import bddl  # type: ignore
    except ImportError:
        sys.exit("bddl is not importable here; pass --bddl-root, or run inside the simulator image")
    return Path(bddl.__file__).parent / "activity_definitions"


def read_rooms(data_root: Path) -> dict[str, list[str]]:
    """Official per-task room list (metadata/B100_task_misc.csv)."""
    path = data_root / "2026-challenge-task-instances" / "metadata" / "B100_task_misc.csv"
    if not path.is_file():
        return {}
    out: dict[str, list[str]] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            task = (row.get("Task") or "").strip()
            # The column lists the rooms the evaluator loads (partial scene load),
            # which is a superset of the rooms the activity happens in.
            raw = (row.get("Rooms to inlcude") or row.get("Rooms to include") or "").strip()
            if task:
                out[task] = [r.strip() for r in raw.splitlines() if r.strip()]
    return out


def read_demo_stats(data_root: Path) -> dict[str, dict]:
    """Per-task demonstration statistics (metadata/task.jsonl)."""
    path = data_root / "2026-challenge-task-instances" / "metadata" / "task.jsonl"
    if not path.is_file():
        return {}
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        steps = float(rec["length"]) if rec.get("length") else None
        out[rec["task_name"]] = {
            "demo_episodes": rec.get("num_episodes"),
            "demo_mean_steps": round(steps, 1) if steps else None,
            # The robot is controlled at 30 Hz, so the recorded episode length in
            # steps is seconds x 30 — confirmed against the gallery's published
            # durations (picking_up_trash 5267.8 -> 175.6 s, published 176 s).
            "demo_mean_s": round(steps / 30.0) if steps else None,
            "demo_distance_m": round(float(rec["distance_traveled"]), 2) if rec.get("distance_traveled") else None,
            "demo_eef_m": [
                round(float(rec.get("left_eef_displacement") or 0), 2),
                round(float(rec.get("right_eef_displacement") or 0), 2),
            ],
        }
    return out


def read_scenes(data_root: Path) -> dict[str, str]:
    """Task -> scene model (metadata/available_tasks.yaml)."""
    path = data_root / "2026-challenge-task-instances" / "metadata" / "available_tasks.yaml"
    if not path.is_file():
        return {}
    import yaml
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out = {}
    for task, entries in data.items():
        if isinstance(entries, dict) and entries:
            first = entries[sorted(entries)[0]]
            if isinstance(first, dict) and first.get("scene_model"):
                out[task] = first["scene_model"]
    return out


def read_instances(data_root: Path) -> dict[str, list[int]]:
    """Task -> the public-test instance ids that ship as scene-state JSON."""
    root = data_root / "2026-challenge-task-instances" / "scene_test" / "public"
    out: dict[str, list[int]] = {}
    for d in root.glob("*/json/*_instances"):
        m = re.match(r"^(.+?)_task_(.+)_instances$", d.name)
        if not m:
            continue
        task = m.group(2)
        ids = set()
        for f in d.glob("*.json"):
            n = re.search(rf"_task_{re.escape(task)}_\d+_(\d+)_", f.name)
            if n:
                ids.add(int(n.group(1)))
        if ids:
            out[task] = sorted(ids)
    return out


def extract(data_root: Path, bddl_root: Path) -> dict:
    scenes = read_scenes(data_root)
    stats = read_demo_stats(data_root)
    rooms = read_rooms(data_root)
    instances = read_instances(data_root)

    tasks = sorted(set(scenes) | set(stats) | set(instances))
    if not tasks:
        sys.exit(f"no tasks found under {data_root}")

    out: dict[str, dict] = {}
    missing_bddl = []
    for task in tasks:
        rec: dict = {}
        problem = bddl_root / task / "problem0.bddl"
        if problem.is_file():
            rec.update(goal_facts(problem.read_text(encoding="utf-8")))
        else:
            missing_bddl.append(task)
        if task in scenes:
            rec["scene_model"] = scenes[task]
        if task in rooms:
            rec["rooms_loaded"] = rooms[task]
        rec.update(stats.get(task, {}))
        ids = instances.get(task) or []
        if ids:
            rec["test_instances"] = len(ids)
            rec["test_instance_ids"] = [ids[0], ids[-1]]
        out[task] = {k: v for k, v in rec.items() if v not in (None, [], "")}

    print(f"extracted {len(out)} task(s) from {bddl_root} + {data_root}")
    if missing_bddl:
        print(f"no BDDL definition for {len(missing_bddl)}: {', '.join(missing_bddl[:5])}…")
    return out


# ───────────────────────────────────────────────────────────── page writing

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--extract", action="store_true", help="read the licensed stack and refresh the cache")
    ap.add_argument("--data-root", default="/data", help="directory holding 2026-challenge-task-instances/")
    ap.add_argument("--bddl-root", default=None, help="bddl/activity_definitions (default: the installed bddl package)")
    ap.add_argument("--out", default=str(CACHE), help="cache path to write in --extract mode")
    ap.add_argument("--stack", default="BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1",
                    help="what the facts were read from, recorded on every page")
    ap.add_argument("--force", action="store_true",
                    help="rewrite every page even when the facts are unchanged (after a renderer change)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.extract:
        facts = extract(Path(args.data_root), find_bddl_root(args.bddl_root))
        payload = {
            "stack": args.stack,
            "extracted": dt.date.today().isoformat(),
            "source": "BDDL activity definitions + 2026-challenge-task-instances (licensed download)",
            "tasks": facts,
        }
        Path(args.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(f"wrote {args.out}")
        return 0

    if not CACHE.is_file():
        sys.exit(f"no cache at {CACHE}; run with --extract inside the simulator image first")
    payload = json.loads(CACHE.read_text())
    facts = payload["tasks"]

    written = unchanged = skipped = 0
    for task_id, rec in sorted(facts.items()):
        path = TASK_DIR / f"{task_id}.md"
        if not path.is_file():
            skipped += 1
            continue
        meta, body = read_page(path)
        block = {
            "source": payload["source"],
            "stack": payload["stack"],
            "checked": payload["extracted"],
            **rec,
        }
        if meta.get("verified") == block and not args.force:
            unchanged += 1
            continue
        meta["verified"] = block
        if not args.dry_run:
            write_page(path, meta, body)
        written += 1

    print(f"cached tasks : {len(facts)}")
    print(f"written      : {written}{' (dry run)' if args.dry_run else ''}")
    print(f"unchanged    : {unchanged}")
    if skipped:
        print(f"no page yet  : {skipped} (run scripts/import_behavior_tasks.py first)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

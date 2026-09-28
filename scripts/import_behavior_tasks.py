#!/usr/bin/env python3
"""Sync BEHAVIOR Challenge task pages from the official demo gallery.

The gallery at behavior.stanford.edu embeds its task list as a JSON literal in
the page source. We parse that literal rather than scraping the rendered DOM,
which keeps this resilient to styling changes upstream.

Re-running this is safe and expected:
  * new upstream task  -> a fresh page is scaffolded from the template
  * existing task      -> only the `upstream:` frontmatter block is rewritten
  * task pulled upstream -> reported, never deleted (a human decides)

Usage:
  python scripts/import_behavior_tasks.py              # fetch live, write pages
  python scripts/import_behavior_tasks.py --offline    # use the cached JSON
  python scripts/import_behavior_tasks.py --dry-run
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = "behavior-1k"
GALLERY_URL = "https://behavior.stanford.edu/challenge/tasks/index.html"
CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.upstream.json"
TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"

BODY_TEMPLATE = """
## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the `capabilities:` list in the frontmatter. One bullet per
     capability is plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- Watch the demo embedded above, then answer:
     - Does it actually satisfy the stated goal?
     - Is the trajectory clean, or does it contain recovery/idle segments?
     - Anything an imitation learner would be misled by? -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->
"""


def fetch_tasks(offline: bool) -> list[dict]:
    if offline:
        if not CACHE.exists():
            sys.exit(f"no cache at {CACHE}; run without --offline once")
        return json.loads(CACHE.read_text())

    req = urllib.request.Request(GALLERY_URL, headers={"User-Agent": "robobench-docs/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        page = resp.read().decode("utf-8", "replace")

    anchor = page.index("const tasks = [")
    start = page.index("[", anchor)
    depth = 0
    for i in range(start, len(page)):
        if page[i] == "[":
            depth += 1
        elif page[i] == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    else:
        sys.exit("could not find the end of the embedded task array")

    tasks = json.loads(html.unescape(page[start:end]))
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(tasks, indent=2) + "\n")
    return tasks


def cohort_of(task: dict) -> str:
    """Which challenge edition a task came from.

    Upstream does not publish this, but the split is unambiguous in the data:
    the 50 tasks carried over from 2025 have YouTube demos and no instruction
    text, the 50 tasks new in 2026 have Vimeo demos and a written instruction.
    Derived here rather than hand-maintained so it cannot drift.
    """
    video = task.get("video") or ""
    if "youtube" in video:
        return "2025-carryover"
    if "vimeo" in video:
        return "2026-new"
    return "unknown"


def upstream_block(task: dict, synced: str) -> dict:
    return {
        "source": GALLERY_URL,
        "synced": synced,
        "cohort": cohort_of(task),
        # Upstream ships no instruction for the 2025 carryover cohort. Empty here
        # means "missing upstream", and the triage board tracks it as open work.
        "instruction": task.get("instruction", ""),
        "scene_model": task["scene_model"],
        "rooms": list(task.get("rooms") or []),
        "demo_duration_s": task.get("duration"),
        "oracle_video": task.get("video") or "",
        "oracle_thumbnail": task.get("thumbnail") or "",
    }


def scaffold(task: dict, synced: str) -> dict:
    return {
        "title": task["name"],
        "task_id": task["id"],
        "benchmark": BENCHMARK,
        "upstream": upstream_block(task, synced),
        "status": "pending",
        "status_reason": "",
        "owner": "",
        "difficulty": "unrated",
        "capabilities": [],
        "skills": [],
        "media": [],
        "tags": [],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="use the cached JSON instead of the network")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tasks = fetch_tasks(args.offline)
    synced = dt.date.today().isoformat()
    TASK_DIR.mkdir(parents=True, exist_ok=True)

    created = updated = unchanged = 0
    for task in tasks:
        path = TASK_DIR / f"{task['id']}.md"
        if path.exists():
            meta, body = read_page(path)
            fresh = upstream_block(task, synced)
            current = dict(meta.get("upstream") or {})
            # `synced` alone is not a reason to rewrite the file.
            if {k: v for k, v in current.items() if k != "synced"} == {
                k: v for k, v in fresh.items() if k != "synced"
            }:
                unchanged += 1
                continue
            fresh["synced"] = synced
            meta["upstream"] = fresh
            meta.setdefault("title", task["name"])
            if not args.dry_run:
                write_page(path, meta, body)
            updated += 1
        else:
            if not args.dry_run:
                write_page(path, scaffold(task, synced), BODY_TEMPLATE)
            created += 1

    known = {t["id"] for t in tasks}
    orphans = sorted(p.stem for p in TASK_DIR.glob("*.md") if p.stem not in known and p.stem != "index")

    print(f"upstream tasks : {len(tasks)}")
    print(f"created        : {created}")
    print(f"updated        : {updated}")
    print(f"unchanged      : {unchanged}")
    if orphans:
        print(f"no longer upstream ({len(orphans)}): {', '.join(orphans)}")
        print("  -> left in place on purpose; decide whether to drop or keep them")
    if args.dry_run:
        print("(dry run, nothing written)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

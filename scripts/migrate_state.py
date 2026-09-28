#!/usr/bin/env python3
"""One-off: move curated frontmatter out of task pages into state/.

Before: status/difficulty/capabilities/owner lived in each of 100 task pages.
After:  they live in state/tasks/<benchmark>.yml, and task pages keep only
        upstream metadata plus prose.

Idempotent — running it again on already-migrated pages does nothing.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import statedb  # noqa: E402
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CURATED = ["status", "status_reason", "owner", "difficulty", "capabilities",
           "skills", "harness", "media", "tags"]


def main() -> int:
    total_moved = 0
    for task_dir in sorted((ROOT / "docs" / "benchmarks").glob("*/tasks")):
        benchmark = task_dir.parent.name
        records = statedb.load_tasks(benchmark)
        moved = 0
        for path in sorted(task_dir.glob("*.md")):
            meta, body = read_page(path)
            if not any(k in meta for k in CURATED):
                continue
            rec = dict(records.get(path.stem) or {})
            if meta.get("status"):
                rec["status"] = meta["status"]
            if meta.get("difficulty"):
                rec["difficulty"] = meta["difficulty"]
            if meta.get("capabilities"):
                rec["labels"] = list(meta["capabilities"])
            if meta.get("skills"):
                rec["skills"] = list(meta["skills"])
            if (meta.get("owner") or "").strip():
                rec["owner"] = meta["owner"].strip()
            if (meta.get("status_reason") or "").strip():
                rec["note"] = meta["status_reason"].strip()
            if meta.get("media"):
                rec["media"] = meta["media"]
            if meta.get("tags"):
                rec["tags"] = meta["tags"]
            if rec:
                records[path.stem] = rec
            for key in CURATED:
                meta.pop(key, None)
            write_page(path, meta, body)
            moved += 1
        if moved:
            statedb.save_tasks(benchmark, records)
            print(f"{benchmark}: moved curated state out of {moved} page(s)")
            total_moved += moved
    if not total_moved:
        print("nothing to migrate — already done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Propose labels for every task from what its benchmark already annotates.

`state/taxonomy.yml` records, per label, a `derived_from` mapping: which official
annotation of which benchmark implies it. This applies those rules to all 250
tasks and reports what the taxonomy would cover. Two uses:

  * **Checking the taxonomy.** A label nothing can reach is either aimed at a
    benchmark we do not have yet (fine, and worth knowing) or is not decidable
    from anything published (worth rewording).
  * **Speeding up triage.** A reviewer confirms or rejects a proposal instead of
    reading 35 labels per task.

It **writes nothing to `state/`**. Tagging is a judgement; this only ever
produces a report under `tmp/`, because a suggestion that wrote itself into the
review surface would be indistinguishable from a decision somebody made.

  python scripts/suggest_labels.py                 # report to tmp/label_coverage.md
  python scripts/suggest_labels.py --task can_meat # explain one task

A label is suggested when **any** of its rules for that benchmark matches; the
rules are deliberately generous, because a reviewer rejecting a wrong suggestion
is cheaper than one noticing a missing label.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import taskdb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OFFICIAL = ROOT / "tmp" / "official_labels"
REPORT = ROOT / "tmp" / "label_coverage.md"


def load_official() -> dict[str, dict]:
    out = {}
    for name in ("behavior-1k", "robowits", "robolab"):
        path = OFFICIAL / f"{name}.json"
        if path.is_file():
            out[name] = json.loads(path.read_text())["tasks"]
    if not out:
        sys.exit(f"no official extracts in {OFFICIAL}; run scripts/collect_official_labels.py first")
    return out


def rooms_of(benchmark: str, task_id: str) -> list[str]:
    """The rooms the activity happens in, as the benchmark publishes them."""
    bench = taskdb.benchmarks().get(benchmark)
    if not bench:
        return []
    task = next((t for t in bench.tasks if t.task_id == task_id), None)
    return task.rooms if task else []


def matches(rules: dict, facts: dict, benchmark: str, task_id: str, unknown: set | None = None) -> list[str]:
    """Which rules fire for this task, as readable reasons.

    A rule naming a field the extract does not have would otherwise fire never
    and look like an honest zero, which is how `success_predicates` (plural)
    quietly disabled the biggest label in the taxonomy. Unknown fields are
    collected and reported instead.
    """
    hits = []
    for key, want in (rules or {}).items():
        if key == "all_tasks":
            if want:
                hits.append("every task in this benchmark, by the benchmark's own claim")
            continue
        if key.endswith("_keywords"):
            field = key[: -len("_keywords")]
            text = str(facts.get(field, "")).lower()
            if field not in facts and unknown is not None:
                unknown.add(f"{benchmark}.{field}")
            found = [w for w in want if w.lower() in text]
            if found:
                hits.append(f"{field} mentions {', '.join(found)}")
            continue
        probe = key[: -len("_min")] if key.endswith("_min") else ("rooms" if key == "rooms_any" else key)
        if probe not in facts and probe != "rooms" and unknown is not None:
            unknown.add(f"{benchmark}.{probe}")
        if key.endswith("_min"):
            field = key[: -len("_min")]
            value = facts.get(field)
            if field == "rooms":
                value = len(rooms_of(benchmark, task_id))
            elif isinstance(value, list):
                value = len(value)
            if isinstance(value, (int, float)) and value >= want:
                hits.append(f"{field} {value} ≥ {want}")
            continue
        if key == "rooms_any":
            rooms = [r.lower() for r in rooms_of(benchmark, task_id)]
            found = [w for w in want if any(w in r for r in rooms)]
            if found:
                hits.append(f"rooms include {', '.join(found)}")
            continue
        have = facts.get(key)
        if isinstance(have, str):
            have = [have]
        overlap = sorted(set(have or []) & set(want))
        if overlap:
            hits.append(f"{key}: {', '.join(overlap)}")
    return hits


def suggest(taxonomy: dict, official: dict, unknown: set) -> dict[str, dict[str, dict[str, list[str]]]]:
    """benchmark -> task -> label -> reasons."""
    out: dict[str, dict[str, dict[str, list[str]]]] = {b: {} for b in official}
    for cap in taxonomy["capabilities"]:
        for sub in cap["subcapabilities"]:
            derived = sub.get("derived_from") or {}
            for benchmark, rules in derived.items():
                for task_id, facts in official.get(benchmark, {}).items():
                    hits = matches(rules, facts, benchmark, task_id, unknown)
                    if hits:
                        out[benchmark].setdefault(task_id, {})[sub["id"]] = hits

    # A graded facet is a ladder: its rungs are ordered in the file and a task
    # sits on the highest one that applies, not on all of them. Without this a
    # six-clause BEHAVIOR goal would come back as atomic AND composite AND
    # activity, which is three labels carrying one label's worth of meaning.
    # Labels marked `flag` live in a graded facet without being rungs.
    for cap in taxonomy["capabilities"]:
        if not cap.get("graded"):
            continue
        rungs = [s["id"] for s in cap["subcapabilities"] if not s.get("flag")]
        for tasks in out.values():
            for labels in tasks.values():
                on = [r for r in rungs if r in labels]
                for lower in on[:-1]:
                    labels.pop(lower)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", default=None, help="explain the proposal for one task and exit")
    args = ap.parse_args()

    taxonomy = taskdb.taxonomy()
    official = load_official()
    unknown: set[str] = set()
    proposed = suggest(taxonomy, official, unknown)
    if unknown:
        print("rules naming a field no extract has (they can never fire):")
        for field in sorted(unknown):
            print(f"  ! {field}")

    index = {s["id"]: (cap["id"], s) for cap in taxonomy["capabilities"] for s in cap["subcapabilities"]}

    if args.task:
        for benchmark, tasks in proposed.items():
            if args.task in official.get(benchmark, {}):
                print(f"{args.task} ({benchmark})")
                for label, reasons in sorted(tasks.get(args.task, {}).items()):
                    print(f"  {index[label][0]:12s} {label:24s} <- {'; '.join(reasons)}")
                if not tasks.get(args.task):
                    print("  (nothing proposed — needs a human read)")
                return 0
        sys.exit(f"unknown task {args.task!r}")

    lines = [
        "# What the taxonomy reaches, without anyone tagging",
        "",
        "Generated by `scripts/suggest_labels.py` from `state/taxonomy.yml`'s `derived_from` rules",
        "and the official annotations in `official_labels/`. **Proposals, not decisions** — nothing",
        "here is written to `state/`.",
        "",
        "| Benchmark | Tasks | Reached by ≥1 label | Labels per task (mean) |",
        "| --- | ---: | ---: | ---: |",
    ]
    for benchmark, tasks in official.items():
        got = proposed[benchmark]
        per = [len(v) for v in got.values()] or [0]
        lines.append(f"| {benchmark} | {len(tasks)} | {len(got)} ({len(got) / len(tasks):.0%}) | "
                     f"{sum(per) / max(1, len(tasks)):.1f} |")

    lines += ["", "## Per label", "",
              "| Facet | Label | BEHAVIOR-1K | RoboWits | RoboLab | Total |",
              "| --- | --- | ---: | ---: | ---: | ---: |"]
    for cap in taxonomy["capabilities"]:
        for sub in cap["subcapabilities"]:
            counts = {b: sum(1 for labels in proposed[b].values() if sub["id"] in labels) for b in official}
            total = sum(counts.values())
            row = " | ".join(str(counts.get(b, 0) or "—") for b in ("behavior-1k", "robowits", "robolab"))
            lines.append(f"| {cap['id']} | `{sub['id']}` | {row} | {total or '—'} |")

    unreached = [s["id"] for cap in taxonomy["capabilities"] for s in cap["subcapabilities"]
                 if not any(s["id"] in labels for b in official for labels in proposed[b].values())]
    lines += ["", "## Labels nothing reaches", "",
              "Each is either aimed at a benchmark we do not have yet, or needs a human to read the task:",
              "", ", ".join(f"`{u}`" for u in unreached) or "none", ""]

    lines += ["## A few tasks in full", ""]
    samples = [("behavior-1k", "picking_up_trash"), ("behavior-1k", "can_meat"),
               ("robowits", "water_into_mug"), ("robowits", "stack_cubes"),
               ("robolab", "block_stacking_specified_order"), ("robolab", "banana_in_bowl")]
    for benchmark, task_id in samples:
        if task_id not in official.get(benchmark, {}):
            continue
        labels = proposed[benchmark].get(task_id, {})
        lines.append(f"**{benchmark} / {task_id}** — " +
                     (", ".join(f"`{k}`" for k in sorted(labels)) if labels else "_nothing proposed_"))
        for label, reasons in sorted(labels.items()):
            lines.append(f"  - `{label}` ← {'; '.join(reasons)}")
        lines.append("")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT}")
    for benchmark, tasks in official.items():
        got = proposed[benchmark]
        print(f"  {benchmark:12s} {len(got):3d}/{len(tasks):3d} tasks reached, "
              f"{sum(len(v) for v in got.values()) / max(1, len(tasks)):.1f} labels/task")
    print(f"  labels nothing reaches: {len(unreached)} of {len(index)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Say, for every task we have, what it actually takes to solve it.

Written before proposing a label vocabulary, not after: the point is to read
250 tasks in one place and see which distinctions genuinely recur, instead of
inventing categories and then hunting for tasks that fit them.

Each line is derived mechanically from what the benchmark publishes — BEHAVIOR's
BDDL goal, RoboLab's attributes and success predicate, RoboWits' stated insight —
so the digest can be regenerated and argued with. Output lands in `tmp/`, which
is untracked: this is working material for designing `state/taxonomy.yml`.

  python scripts/task_skill_digest.py            # tmp/task_skills.md + a summary
  python scripts/task_skill_digest.py --verbs    # just the aggregate counts
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import taskdb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OFFICIAL = ROOT / "tmp" / "official_labels"
OUT = ROOT / "tmp" / "task_skills.md"

# What a BDDL goal predicate asks the robot to actually do.
PREDICATE_VERB = {
    "inside": "put something inside something",
    "ontop": "put something on something",
    "under": "put something under something",
    "nextto": "put something beside something",
    "touching": "bring two things into contact",
    "open": "open or close a hinged or sliding part",
    "toggled_on": "operate a switch or appliance",
    "cooked": "cook something",
    "frozen": "freeze something",
    "on_fire": "ignite something",
    "covered": "apply or remove particles over a surface",
    "filled": "fill a container with a substance",
    "contains": "get a substance into a container",
    "attached": "attach one thing to another",
    "real": "create something by cutting (half__ synsets)",
    "future": "create something that does not exist at the start",
    "broken": "break something",
    "folded": "fold something",
    "unfolded": "unfold something",
    "overlaid": "drape something over something",
    "draped": "drape something over something",
    "saturated": "soak something",
    "insource": "get something into a source region",
}

# RoboWits publishes prose; these are the physical strategies it names.
INSIGHT_STRATEGY = [
    ("use a tool to extend reach or grasp", ["as a tool", "tool extension", "use the rod",
                                             "use the dustpan", "spatula", "chopsticks", "tongs", "funnel"]),
    ("exploit friction or a surface property", ["friction", "slippery", "rough", "smooth surface"]),
    ("exploit weight, buoyancy or displacement", ["buoyan", "float", "sink", "archimed", "displac", "heavy"]),
    ("exploit elasticity or deformation", ["elastic", "compress", "deform", "squeeze", "flatten", "dough", "foam"]),
    ("reason about centre of mass or support", ["center of mass", "centre of mass", "support polygon",
                                                "balanc", "stabil", "topple", "tip over"]),
    ("reason about geometry and clearance", ["geometr", "clearance", "narrow", "fit through", "aperture",
                                             "restriction", "align"]),
    ("use momentum or a chain reaction", ["momentum", "domino", "chain", "swing", "roll"]),
    ("assemble a structure from parts", ["assembl", "stack", "platform", "deck", "support"]),
    ("contain or seal a liquid", ["water", "liquid", "pour", "leak", "seal"]),
]


def behavior_lines(tasks: dict) -> dict[str, dict]:
    out = {}
    for task_id, facts in sorted(tasks.items()):
        verbs, seen = [], set()
        for predicate in facts["goal_predicates"]:
            verb = PREDICATE_VERB.get(predicate)
            if verb and verb not in seen:
                seen.add(verb)
                verbs.append(verb)
        extras = []
        if facts["goal_quantifiers"]:
            extras.append("over a quantified set (" + ", ".join(facts["goal_quantifiers"]) + ")")
        if facts["goal_counts"]:
            extras.append("with an exact count")
        rooms = rooms_of("behavior-1k", task_id)
        if len(rooms) > 1:
            extras.append(f"across {len(rooms)} rooms")
        elif rooms:
            extras.append("in one room")
        out[task_id] = {
            "skills": verbs or ["(goal uses predicates we have no verb for)"],
            "extras": extras,
            "steps": f"{facts['goal_clauses']} goal clauses",
            "official": ", ".join(facts["goal_predicates"]),
        }
    return out


def robowits_lines(tasks: dict) -> dict[str, dict]:
    out = {}
    for task_id, facts in sorted(tasks.items()):
        text = (facts["paper_insight"] + " " + facts["instruction"]).lower()
        strategies = [name for name, words in INSIGHT_STRATEGY if any(w in text for w in words)]
        materials = [m for m in facts["physics_materials"] if m != "rigid"]
        extras = []
        if materials:
            extras.append("non-rigid physics: " + ", ".join(materials))
        if facts["paper_category"]:
            extras.append(f"paper calls it {facts['paper_category']}")
        out[task_id] = {
            "skills": strategies or ["(insight text names no strategy we match)"],
            "extras": extras,
            "steps": f"{facts['mutations']} mutations published",
            "official": facts["paper_category"] or "—",
        }
    return out


def robolab_lines(tasks: dict) -> dict[str, dict]:
    predicate_verb = {
        "object_in_container": "put an object in a container",
        "object_on_top": "put an object on top of another",
        "object_inside": "put an object inside another",
        "object_picked_up": "pick an object up and hold it",
        "object_outside_of": "take an object out of something",
        "object_outside_of_and_on_surface": "take an object out and set it down",
        "object_groups_in_containers": "sort groups of objects into containers",
        "objects_placed_in_container_in_order": "place objects in a required order",
        "stacked": "stack objects so they stay up",
        "object_upright": "stand an object upright",
        "object_left_of": "place an object to the left of another",
        "object_right_of": "place an object to the right of another",
        "object_behind": "place an object behind another",
        "object_in_front_of": "place an object in front of another",
        "object_on_center": "centre an object on a target",
    }
    attribute_demand = {
        "color": "identify the target by colour",
        "size": "identify the target by size",
        "semantics": "identify the target by category",
        "spatial": "resolve a spatial relation",
        "counting": "get a count right",
        "conjunction": "satisfy two conditions at once",
        "sorting": "sort into groups",
        "stacking": "keep a stack standing",
        "reorientation": "reorient the object",
        "affordance": "use an object's affordance",
        "vague": "interpret a vague instruction",
    }
    out = {}
    for task_id, facts in sorted(tasks.items()):
        skills = [predicate_verb.get(facts["success_predicate"], facts["success_predicate"] or "?")]
        skills += [attribute_demand[a] for a in facts["attributes"] if a in attribute_demand]
        out[task_id] = {
            "skills": skills,
            "extras": [f"{facts['subtasks']} subtasks"] if facts["subtasks"] > 1 else [],
            "steps": facts["difficulty_label"],
            "official": ", ".join(facts["attributes"]) or "—",
        }
    return out


def rooms_of(benchmark: str, task_id: str) -> list[str]:
    bench = taskdb.benchmarks().get(benchmark)
    if not bench:
        return []
    task = next((t for t in bench.tasks if t.task_id == task_id), None)
    return task.rooms if task else []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbs", action="store_true", help="print the aggregate only")
    args = ap.parse_args()

    payloads = {}
    for name in ("behavior-1k", "robowits", "robolab"):
        path = OFFICIAL / f"{name}.json"
        if not path.is_file():
            sys.exit(f"missing {path}; run scripts/collect_official_labels.py first")
        payloads[name] = json.loads(path.read_text())["tasks"]

    digests = {
        "behavior-1k": behavior_lines(payloads["behavior-1k"]),
        "robowits": robowits_lines(payloads["robowits"]),
        "robolab": robolab_lines(payloads["robolab"]),
    }

    counts = collections.Counter()
    for bench, rows in digests.items():
        for row in rows.values():
            for skill in row["skills"]:
                counts[(bench, skill)] += 1

    if not args.verbs:
        lines = ["# What each task actually takes", "",
                 "Derived by `scripts/task_skill_digest.py` from each benchmark's own published",
                 "annotation — not from our labels, which is the point: this is the evidence a",
                 "label vocabulary has to fit, read before the vocabulary was written.", ""]
        for bench, rows in digests.items():
            lines += [f"## {bench} ({len(rows)} tasks)", "",
                      "| Task | What it takes | Also | Scale | Official tags |",
                      "| --- | --- | --- | --- | --- |"]
            for task_id, row in rows.items():
                lines.append(f"| `{task_id}` | {'; '.join(row['skills'])} | {'; '.join(row['extras']) or '—'} "
                             f"| {row['steps']} | {row['official']} |")
            lines.append("")
        lines += ["## What recurs", ""]
        for bench in digests:
            lines += [f"### {bench}", "", "| Demand | Tasks |", "| --- | ---: |"]
            rows = sorted(((s, n) for (b, s), n in counts.items() if b == bench), key=lambda kv: -kv[1])
            lines += [f"| {skill} | {n} |" for skill, n in rows]
            lines.append("")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote {OUT}")

    for bench in digests:
        print(f"\n{bench}:")
        rows = sorted(((s, n) for (b, s), n in counts.items() if b == bench), key=lambda kv: -kv[1])
        for skill, n in rows:
            print(f"  {n:4d}  {skill}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

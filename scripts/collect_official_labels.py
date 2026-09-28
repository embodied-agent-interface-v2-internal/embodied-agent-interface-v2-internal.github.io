#!/usr/bin/env python3
"""Collect what each benchmark *officially* says about its own tasks.

Before proposing a label taxonomy that spans three benchmarks, it is worth
knowing how each of them describes capability today — in its own words, with
its own vocabulary, at its own level of granularity. This script gathers that
evidence into `tmp/official_labels/`, one JSON per benchmark plus a written
comparison. Nothing here is our judgement: every field records where it came
from, and the three vocabularies are deliberately left un-merged.

`tmp/` is untracked on purpose. This is reference material for designing our own
taxonomy in `state/taxonomy.yml`, not something the site publishes — re-run the
script whenever you want it back.

  python scripts/collect_official_labels.py behavior --data-root /data   # in the image
  python scripts/collect_official_labels.py robowits --source ~/src/RoboWits
  python scripts/collect_official_labels.py robolab  --source ~/src/RoboLab
  python scripts/collect_official_labels.py summary

What each benchmark actually publishes, and what we therefore take:

  BEHAVIOR-1K  A 31-primitive skill vocabulary, annotated per demonstration
               *segment* — those annotations live in the 1.44 TB raw dataset,
               not in anything downloadable per task. What is available per
               task is the BDDL definition the evaluator scores, and BDDL's
               object ontology, which annotates every synset with abilities
               (openable, deformable, liquid, cookable, toggleable, ...). So a
               task's capability profile here is: goal predicates + the
               abilities of the objects it names.
  RoboWits     No machine-readable annotation at all. The paper groups the ten
               evaluated tasks into geometry / assembly / material reasoning,
               and its appendix states, for all 30, the physical insight the
               task is built around. The source adds the physics material of
               every object, which is an official fact about what is simulated.
  RoboLab      The most explicit of the three: 11 attribute tags per task from
               a fixed vocabulary, mapped to 3 categories, weighted into a
               difficulty label — all in `robolab/constants.py`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "tmp" / "official_labels"   # untracked scratch; see .gitignore

# BDDL annotates every synset with a long tail of states that are true of
# almost everything (rustable, stainable, wetable ...). A property on nearly
# every object says nothing about a task, so only the discriminative ones are
# kept — the threshold is recorded in the output.
ABILITY_MAX_SHARE = 0.5

# A task's objects can do far more than the task asks for: a soda can is
# `freezable` and `heatable` whether or not anything is ever heated. The goal
# predicate is what the evaluator scores, so the ability it exercises is the
# sharper signal. This maps one official vocabulary onto the other; it is ours,
# not BEHAVIOR's, and is recorded in the output as such.
GOAL_PREDICATE_ABILITY = {
    "open": "openable",
    "cooked": "cookable",
    "frozen": "freezable",
    "on_fire": "flammable",
    "toggled_on": "toggleable",
    "filled": "fillable",
    "contains": "fillable",
    "covered": "particleApplier",
    "attached": "attachable",
    "real": "sliceable",          # BDDL builds cutting goals out of half__* synsets
}


# ─────────────────────────────────────────────────────────────── BEHAVIOR-1K

def collect_behavior(data_root: Path, bddl_root: Path | None) -> dict:
    import bddl  # noqa: F401  (import fails outside the simulator image, by design)
    from import_behavior_verified import goal_facts, read_scenes, sexp, section

    pkg = Path(bddl.__file__).parent
    definitions = Path(bddl_root) if bddl_root else pkg / "activity_definitions"
    annots = json.loads((pkg / "generated_data" / "propagated_annots_canonical.json").read_text())

    total = len(annots)
    share: dict[str, int] = {}
    for props in annots.values():
        for prop in (props.keys() if isinstance(props, dict) else props or []):
            share[prop] = share.get(prop, 0) + 1
    discriminative = {p for p, n in share.items() if n / total <= ABILITY_MAX_SHARE}

    def abilities_of(synset: str) -> list[str]:
        props = annots.get(synset)
        keys = props.keys() if isinstance(props, dict) else (props or [])
        return sorted(p for p in keys if p in discriminative)

    scenes = read_scenes(data_root)
    tasks: dict[str, dict] = {}
    for task in sorted(scenes):
        problem = definitions / task / "problem0.bddl"
        if not problem.is_file():
            continue
        text = problem.read_text(encoding="utf-8")
        facts = goal_facts(text)

        tree = sexp(text)
        objects = section(tree, ":objects")
        synsets = sorted({t for t in (objects or []) if isinstance(t, str) and re.fullmatch(r"[a-zA-Z_]+\.n\.\d+", t)})
        init = section(tree, ":init") or []
        init_predicates = sorted({n[0] for n in init[1:] if isinstance(n, list) and n and isinstance(n[0], str)
                                  and n[0] not in {"and", "or", "not", "inroom"}})

        per_object = {s: abilities_of(s) for s in synsets}
        goal_abilities = sorted({GOAL_PREDICATE_ABILITY[p] for p in facts["goal_predicates"]
                                 if p in GOAL_PREDICATE_ABILITY})
        tasks[task] = {
            "scene_model": scenes[task],
            "goal_predicates": facts["goal_predicates"],
            "goal_quantifiers": facts["goal_quantifiers"],
            "goal_counts": facts["goal_counts"],
            "goal_clauses": facts["goal_clauses"],
            "goal_synsets": facts["goal_categories"],
            "init_predicates": init_predicates,
            "object_synsets": synsets,
            # The union is the task's capability profile in BDDL's own ontology.
            "object_abilities": sorted({a for abilities in per_object.values() for a in abilities}),
            "goal_implied_abilities": goal_abilities,
            "object_abilities_by_synset": {k: v for k, v in per_object.items() if v},
        }

    return {
        "benchmark": "behavior-1k",
        "collected": dt.date.today().isoformat(),
        "source": "BDDL activity definitions + bddl/generated_data/propagated_annots_canonical.json "
                  "(BEHAVIOR-1K v3.9.2), plus the challenge task-instance metadata",
        "what_is_official": "The goal each task is scored against, and the abilities BDDL annotates on every "
                            "object synset. The benchmark's 31 skill primitives are annotated per demonstration "
                            "segment inside the 1.44 TB raw dataset and are not published per task.",
        "vocabularies": {
            "goal_predicates": sorted({p for t in tasks.values() for p in t["goal_predicates"]}),
            "goal_quantifiers": sorted({q for t in tasks.values() for q in t["goal_quantifiers"]}),
            "object_abilities": sorted({a for t in tasks.values() for a in t["object_abilities"]}),
            "object_abilities_excluded": sorted({p for p in share if p not in discriminative}),
            "goal_predicate_to_ability": GOAL_PREDICATE_ABILITY,
            "goal_predicate_to_ability_note": "ours, not BEHAVIOR's: which ability a goal predicate exercises, "
                                              "so `object_abilities` (what the objects can do) can be told apart "
                                              "from what the task actually scores",
            "ability_threshold": f"kept a property when at most {ABILITY_MAX_SHARE:.0%} of the "
                                 f"{total} annotated synsets carry it",
            "skill_primitives": [
                "attach", "chop", "close door", "close drawer", "close lid", "hand over", "hang", "hold",
                "ignite", "insert", "move to", "open door", "open drawer", "open lid", "pick up from",
                "place in", "place in next to", "place on", "place on next to", "place under", "pour",
                "press", "push to", "release", "spray", "sweep surface", "tip over", "turn off switch",
                "turn on switch", "turn to", "wipe hard",
            ],
        },
        "tasks": tasks,
    }


# ───────────────────────────────────────────────────────────────── RoboWits

PAPER_URL = "https://arxiv.org/html/2605.30326v1"


def _flatten(page: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page)))


def paper_rationales(page: str) -> dict[int, dict]:
    """The appendix entry for every seed task.

    Each is one list item: a bold number, a bold task name, the instruction, a
    line break, then the paragraph stating the insight the task is built around.
    Parsed from that structure rather than from flattened text, which happily
    matched section numbers ("1 Introduction ...") as task entries.
    """
    out: dict[int, dict] = {}
    for item in re.finditer(r'<li id="A1\.I1\.ix\d+".*?</li>', page, re.S):
        block = item.group(0)
        bolds = re.findall(r'<span[^>]*ltx_font_bold[^>]*>(.*?)</span>', block, re.S)
        if len(bolds) < 2 or not bolds[0].strip().isdigit():
            continue
        number = int(bolds[0].strip())
        name = _flatten(bolds[1]).strip()
        head, sep, tail = block.partition("<br")
        instruction = _flatten(head.split("</span>")[-1]).strip().lstrip(":").strip()
        # `partition` leaves the rest of the <br ...> tag on the tail.
        insight = tail.split(">", 1)[1] if sep and ">" in tail else tail
        out[number] = {
            "paper_name": name,
            "paper_instruction": instruction,
            "paper_insight": _flatten(insight).strip(),
        }
    return out


def paper_categories(page: str) -> dict[str, str]:
    """Table 3's grouping of the ten evaluated tasks.

    The header spans columns, not tasks: each task occupies two columns (SR and
    PS), so `Geometry Tasks colspan=10` means five tasks, not ten. Reading the
    flattened text instead of the colspans gets the group boundaries wrong —
    it put Stand Bulb under Assembly when the table has it under Geometry.
    """
    table_start = page.find("Geometry Tasks")
    if table_start < 0:
        return {}
    region = page[table_start - 3000: table_start + 12000]
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", region, re.S)

    def cells(row: str) -> list[tuple[str, int]]:
        out = []
        for m in re.finditer(r"<td([^>]*)>(.*?)</td>", row, re.S):
            span = re.search(r'colspan="(\d+)"', m.group(1))
            out.append((_flatten(m.group(2)).strip(), int(span.group(1)) if span else 1))
        return out

    group_row = next((r for r in rows if "Geometry Tasks" in r), "")
    name_row = next((r for r in rows[rows.index(group_row) + 1:] if "Align Blocks" in r), "")
    if not group_row or not name_row:
        return {}

    units: list[str] = []
    for label, span in cells(group_row):
        if label.endswith("Tasks"):
            units += [label.replace(" Tasks", "").lower()] * span
        elif label == "All":
            units += ["all"] * span

    out: dict[str, str] = {}
    offset = 0
    for label, span in cells(name_row):
        if not label:
            continue
        if offset < len(units) and units[offset] != "all":
            out[label] = units[offset]
        offset += span
    return out


def collect_robowits(source: Path, paper: Path | None) -> dict:
    import import_robowits_tasks as rw

    tasks_src = {t["number"]: t for t in rw.read_source(source)}

    page = ""
    if paper and Path(paper).is_file():
        page = Path(paper).read_text(encoding="utf-8", errors="replace")
    else:
        import urllib.request
        req = urllib.request.Request(PAPER_URL, headers={"User-Agent": "robobench-docs/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            page = resp.read().decode("utf-8", "replace")

    rationales = paper_rationales(page)
    categories = paper_categories(page)

    # Table 3 abbreviates and drops filler words ("Retr. Cube" for "Retrieve
    # Cube", "Cover Lid" for "Cover With Lid"), so a table name matches a task
    # when every word it prints is the start of one of the task's words. A name
    # that matches more than one task is dropped rather than guessed at.
    filler = {"with", "into", "onto", "up", "the", "a", "of"}

    def category_for(title: str) -> str:
        title_words = [w for w in title.lower().split() if w not in filler]
        hits = []
        for name, group in categories.items():
            printed = [w.strip(".") for w in name.lower().split() if w.strip(".") not in filler]
            if all(any(t.startswith(p) for t in title_words) for p in printed):
                hits.append(group)
        return hits[0] if len(hits) == 1 else ""

    tasks = {}
    for number, t in sorted(tasks_src.items()):
        rationale = rationales.get(number, {})
        tasks[t["id"]] = {
            "number": number,
            "title": t["title"],
            "instruction": t["instruction"],
            "success_criteria": t["success_criteria"],
            "objects": t["objects"],
            "physics_materials": t["object_materials"],
            "mutations": t["mutations"],
            "paper_category": category_for(t["title"]),
            "paper_insight": rationale.get("paper_insight", ""),
        }

    return {
        "benchmark": "robowits",
        "collected": dt.date.today().isoformat(),
        "source": f"RoboWits @ {rw.git_commit(source) or 'checkout'} (source) + {PAPER_URL} (paper)",
        "what_is_official": "No per-task annotation is published in machine-readable form. The paper groups the "
                            "ten evaluated tasks into three reasoning categories and states, for all 30, the "
                            "physical insight the task is built around; the source states the physics material "
                            "each object is simulated with.",
        "vocabularies": {
            "paper_categories": sorted({v for v in categories.values()}) or ["assembly", "geometry", "material"],
            "paper_categories_assigned": len([t for t in tasks.values() if t["paper_category"]]),
            "physics_materials": sorted({m for t in tasks.values() for m in t["physics_materials"]}),
            "mutation_axes": ["add irrelevant objects", "add an obstacle", "replace the tool",
                              "fix objects in place"],
            "mutation_axes_source": "captions on the project page's mutation examples; not an exhaustive list",
        },
        "tasks": tasks,
    }


# ────────────────────────────────────────────────────────────────── RoboLab

def collect_robolab(source: Path) -> dict:
    import import_robolab_tasks as rl

    weights, thresholds = rl.difficulty_rules(source)
    constants = (source / "robolab" / "constants.py").read_text(encoding="utf-8")
    m = re.search(r"BENCHMARK_TASK_CATEGORIES\s*=\s*\{(.*?)\}", constants, re.S)
    categories = dict(re.findall(r"'([\w]+)'\s*:\s*'([\w]+)'", m.group(1))) if m else {}

    tasks = {}
    for path in sorted((source / "robolab" / "tasks" / "benchmark").glob("*.py")):
        parsed = rl.parse_task_module(path, weights, thresholds)
        if not parsed:
            continue
        attributes = parsed["attributes"]
        tasks[parsed["id"]] = {
            "title": parsed["title"],
            "instruction": parsed["instruction"],
            "attributes": attributes,
            "attribute_categories": sorted({categories[a] for a in attributes if a in categories}),
            "difficulty_label": parsed["difficulty_label"],
            "difficulty_score": sum(weights.get(a, 0) for a in attributes),
            "success_predicate": parsed.get("predicate", ""),
            "subtask_predicates": parsed.get("subtask_predicates", []),
            "subtasks": parsed.get("subtasks", 0),
            "episode_length_s": parsed["episode_length_s"],
        }

    return {
        "benchmark": "robolab",
        "collected": dt.date.today().isoformat(),
        "source": f"RoboLab @ {rl.git_ref(source) or 'checkout'} — robolab/tasks/benchmark/*.py and robolab/constants.py",
        "what_is_official": "Every task carries attribute tags from a fixed 11-term vocabulary. The benchmark maps "
                            "them to three categories and weights them into a difficulty label, so the whole "
                            "annotation chain is published and reproducible.",
        "vocabularies": {
            "attributes": sorted(weights),
            "attribute_weights": weights,
            "attribute_categories": categories,
            "uncategorised_attributes": sorted(set(weights) - set(categories)),
            "difficulty_thresholds": list(thresholds),
            "success_predicates": sorted({t["success_predicate"] for t in tasks.values() if t["success_predicate"]}),
            "subtask_predicates": sorted({p for t in tasks.values() for p in t["subtask_predicates"]}),
        },
        "tasks": tasks,
    }


# ────────────────────────────────────────────────────────────────── summary

def counts(rows: list[list[str]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        for term in row:
            out[term] = out.get(term, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def table(pairs: dict[str, int], total: int, header: str) -> list[str]:
    out = [f"| {header} | Tasks | Share |", "| --- | ---: | ---: |"]
    out += [f"| `{term}` | {n} | {n / total:.0%} |" for term, n in pairs.items()]
    return out


def write_summary() -> None:
    data = {}
    for name in ("behavior-1k", "robowits", "robolab"):
        path = OUT_DIR / f"{name}.json"
        if path.is_file():
            data[name] = json.loads(path.read_text())
    if not data:
        sys.exit(f"nothing collected yet in {OUT_DIR}")

    lines = [
        "# What each benchmark officially calls a capability",
        "",
        "Collected by `scripts/collect_official_labels.py`, one JSON per benchmark beside this file.",
        "This is **evidence, not a proposal**: the three vocabularies are recorded as published, in their",
        "own words, un-merged. Designing a taxonomy that spans them is the next step and belongs in",
        "`state/taxonomy.yml`.",
        "",
        "| Benchmark | Tasks | What it publishes per task | Terms |",
        "| --- | ---: | --- | ---: |",
    ]
    rows = {
        "behavior-1k": ("a formal goal in BDDL, plus object abilities from BDDL's ontology", "object_abilities"),
        "robowits": ("a stated physical insight (paper); a reasoning category for 10 of 30", "paper_categories"),
        "robolab": ("attribute tags from a fixed vocabulary, weighted into a difficulty", "attributes"),
    }
    for name, payload in data.items():
        what, vocab_key = rows[name]
        vocab = payload["vocabularies"].get(vocab_key) or []
        lines.append(f"| {name} | {len(payload['tasks'])} | {what} | {len(vocab)} |")

    for name, payload in data.items():
        tasks = payload["tasks"]
        lines += ["", f"## {name}", "", payload["what_is_official"], "",
                  f"*Source: {payload['source']}*", ""]
        if name == "behavior-1k":
            lines += ["### Object abilities named by a task's objects (BDDL ontology)", ""]
            lines += table(counts([t["object_abilities"] for t in tasks.values()]), len(tasks), "Ability")
            lines += ["", "### What the goal actually exercises", "",
                      "The abilities above are what a task's objects *can* do — a soda can is `freezable` "
                      "whether or not anything is frozen. Mapping each goal predicate to the ability it "
                      "scores gives the sharper reading:", ""]
            lines += table(counts([t["goal_implied_abilities"] for t in tasks.values()]), len(tasks), "Exercised by the goal")
            pure = sum(1 for t in tasks.values() if not t["goal_implied_abilities"])
            lines += ["", f"The remaining **{pure} of {len(tasks)}** tasks have goals made only of spatial "
                          "predicates: rearrangement, however long the horizon.", ""]
            lines += ["", "### Goal predicates", ""]
            lines += table(counts([t["goal_predicates"] for t in tasks.values()]), len(tasks), "Predicate")
            lines += ["", "### Quantifiers in the goal", ""]
            lines += table(counts([t["goal_quantifiers"] for t in tasks.values()]), len(tasks), "Quantifier")
            excluded = payload["vocabularies"]["object_abilities_excluded"]
            lines += ["", f"Dropped as non-discriminative ({payload['vocabularies']['ability_threshold']}): "
                          + ", ".join(f"`{e}`" for e in excluded) + ".", ""]
        elif name == "robowits":
            lines += ["### Reasoning category (paper, Table 3)", ""]
            lines += table(counts([[t["paper_category"]] for t in tasks.values() if t["paper_category"]]),
                           len(tasks), "Category")
            lines += ["", "### Physics material simulated", ""]
            lines += table(counts([t["physics_materials"] for t in tasks.values()]), len(tasks), "Material")
            lines += ["", "Every task also carries a one-paragraph statement of the insight it tests "
                          "(`paper_insight`), which is the closest thing RoboWits has to a capability label.", ""]
        else:
            lines += ["### Attribute tags", ""]
            lines += table(counts([t["attributes"] for t in tasks.values()]), len(tasks), "Attribute")
            lines += ["", "### Attribute categories", ""]
            lines += table(counts([t["attribute_categories"] for t in tasks.values()]), len(tasks), "Category")
            lines += ["", "### Success predicate", ""]
            lines += table(counts([[t["success_predicate"]] for t in tasks.values() if t["success_predicate"]]),
                           len(tasks), "Predicate")

    lines += ["", "## Where the three overlap, and where they do not", "",
              "Read down the column to see what a benchmark can say about a task today; read across to see",
              "which axes a shared taxonomy would have to carry. A dash means the benchmark has no vocabulary",
              "for it — not that its tasks never do it.", "",
              "| Axis | BEHAVIOR-1K (100) | RoboWits (30) | RoboLab (120) |",
              "| --- | --- | --- | --- |"]

    def bh(key, term):
        return sum(1 for t in data["behavior-1k"]["tasks"].values() if term in t[key]) if "behavior-1k" in data else 0

    def rl_attr(term):
        return sum(1 for t in data["robolab"]["tasks"].values() if term in t["attributes"]) if "robolab" in data else 0

    def rl_pred(term):
        return sum(1 for t in data["robolab"]["tasks"].values() if t["success_predicate"] == term) if "robolab" in data else 0

    def rw_mat(term):
        return sum(1 for t in data["robowits"]["tasks"].values() if term in t["physics_materials"]) if "robowits" in data else 0

    def rw_cat(term):
        return sum(1 for t in data["robowits"]["tasks"].values() if t["paper_category"] == term) if "robowits" in data else 0

    pure = sum(1 for t in data.get("behavior-1k", {}).get("tasks", {}).values() if not t["goal_implied_abilities"])
    rows_axes = [
        ("Rearrangement / pick-and-place", f"{pure} goals are purely spatial", "ends in a placement in most tasks",
         f"`object_in_container` {rl_pred('object_in_container')}, `object_on_top` {rl_pred('object_on_top')}"),
        ("Articulated objects", f"`openable` in {bh('goal_implied_abilities','openable')} goals", "—", "—"),
        ("Object state (cook / freeze / burn)",
         f"{bh('goal_implied_abilities','cookable') + bh('goal_implied_abilities','freezable') + bh('goal_implied_abilities','flammable')} goals",
         "—", "—"),
        ("Cutting", f"`sliceable` in {bh('goal_implied_abilities','sliceable')} goals", "—", "—"),
        ("Particles / cleaning", f"`covered` in {bh('goal_implied_abilities','particleApplier')} goals", "—", "—"),
        ("Fluids and granular media", f"`fillable` in {bh('goal_implied_abilities','fillable')} goals",
         f"{rw_mat('sph') + rw_mat('mpm')} tasks simulate SPH or MPM", "—"),
        ("Deformables", f"`deformable`/`softBody` on objects in {bh('object_abilities','deformable')} tasks",
         "dough and foam, in the material category", "—"),
        ("Tool use", "no vocabulary", "the premise of the suite (per-task insight text)",
         f"`affordance` {rl_attr('affordance')}"),
        ("Spatial relations in the goal", "`nextto`, `under`, `touching`", "—", f"`spatial` {rl_attr('spatial')}"),
        ("Counting and quantifiers", "`forall`, `forn`, `exists` in the goal", "—", f"`counting` {rl_attr('counting')}"),
        ("Language grounding (colour, size, vagueness)", "—", "—",
         f"`color` {rl_attr('color')}, `size` {rl_attr('size')}, `vague` {rl_attr('vague')}, `semantics` {rl_attr('semantics')}"),
        ("Physical reasoning / dynamics", "—",
         f"geometry {rw_cat('geometry')}, assembly {rw_cat('assembly')}, material {rw_cat('material')} (10 of 30 assigned)", "—"),
        ("Navigation, multi-room", "implicit: house scenes, rooms loaded per task", "none — fixed base", "none — fixed base"),
        ("Bimanual", "not annotated (R1 Pro has two arms)", "not annotated (every task is bimanual)", "single arm"),
        ("Dexterous hands", "parallel grippers only", "parallel grippers only", "parallel gripper only"),
        ("Long horizon", "not annotated; mean episode 72–869 s", "not annotated; clips run 10–40 s",
         "not annotated; `episode_length_s` 20–300"),
    ]
    for axis, a, b, c in rows_axes:
        lines.append(f"| {axis} | {a} | {b} | {c} |")

    lines += ["", "Three things this makes concrete, before anyone argues about label names:", "",
              "1. **No benchmark annotates the axes we would most want to compare on.** Long horizon, bimanual "
              "coordination and dexterity are properties of all three suites and named by none of them.",
              "2. **The three vocabularies sit at different levels.** BEHAVIOR's is a formal goal language, "
              "RoboLab's is a flat attribute list about how the goal is *worded*, RoboWits' is a prose "
              "statement of the insight. Only the first two are mechanically usable.",
              "3. **Each suite is nearly blind outside its own emphasis.** BEHAVIOR says nothing about tool use, "
              "RoboLab nothing about physics, RoboWits nothing about language. A shared taxonomy has to carry "
              "all three axes or it will just re-describe whichever benchmark it was written against.", ""]

    (OUT_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_DIR / 'README.md'}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("benchmark", choices=["behavior", "robowits", "robolab", "summary"])
    ap.add_argument("--source", default=None, help="a checkout of the benchmark (robowits / robolab)")
    ap.add_argument("--data-root", default="/data", help="licensed BEHAVIOR download (behavior)")
    ap.add_argument("--bddl-root", default=None)
    ap.add_argument("--paper", default=None, help="a saved copy of the RoboWits paper HTML")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    # Not OUT_DIR: run inside the simulator image this file sits at /s, so the
    # repository-relative default would point at the read-only dataset mount.
    # The real destination comes from --out there.
    if args.benchmark == "summary":
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        write_summary()
        return 0

    if args.benchmark == "behavior":
        payload = collect_behavior(Path(args.data_root), args.bddl_root)
        name = "behavior-1k"
    elif args.benchmark == "robowits":
        if not args.source:
            sys.exit("--source <RoboWits checkout> is required")
        payload = collect_robowits(Path(args.source).expanduser(), args.paper)
        name = "robowits"
    else:
        if not args.source:
            sys.exit("--source <RoboLab checkout> is required")
        payload = collect_robolab(Path(args.source).expanduser())
        name = "robolab"

    out = Path(args.out) if args.out else OUT_DIR / f"{name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"{name}: {len(payload['tasks'])} tasks -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

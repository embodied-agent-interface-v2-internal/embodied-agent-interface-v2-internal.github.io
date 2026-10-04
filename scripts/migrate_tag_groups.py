#!/usr/bin/env python3
"""One-off: give every task its display tags, in two groups, Capability and
Task Domain (state/display_tags.yml), from what it already has.

The detailed labels stay as they are: `labels:` and state/taxonomy.yml are
read, never written. Only `display_tags:` is set, what the site shows.

Two tables decide it, both below and both meant to be argued with in review:

  OLD_TO_NEW   each detailed label -> the display tags it implies, with why.
               A task's tags are the union over its labels.
  UNLABELLED   for the benchmarks that have no labels: a rule per benchmark,
               and the tasks that need more than the rule gives.

In state/tasks/*.yml each record gets its `display_tags:` lines in place (where
the sorted order puts them in a record whose keys are sorted, else last), and the
file header its `display_tags` line; every other line, comments included, stays
byte for byte.

Idempotent: the tags are computed from the labels and the rules, so running it
again on migrated state changes nothing. It overwrites `display_tags:` that
differ, so tags edited by hand afterwards would be reset: run it once.

  python scripts/migrate_tag_groups.py            # migrate and print the counts
  python scripts/migrate_tag_groups.py --dry-run  # print the counts, write nothing
  python scripts/migrate_tag_groups.py --table    # the two tables as Markdown
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml  # noqa: E402

import statedb  # noqa: E402
import taskdb  # noqa: E402

PERC = "perception-understanding"
PLAN = "planning-reasoning"
CTRL = "control-coordination"
FEED = "feedback-adaptation"
MANIP = "manipulation"
LOCO = "locomotion-stability"
NAV = "navigation-exploration"
MOBILE = "mobile-whole-body-manipulation"
INTER = "interaction-collaboration"

# The vocabulary is state/display_tags.yml; the ids above must be the ones in it.
TAGS = taskdb.tag_index()
NEW_IDS = list(TAGS)
GROUP_OF = {tid: tag["group_id"] for tid, tag in TAGS.items()}
if sorted(NEW_IDS) != sorted([PERC, PLAN, CTRL, FEED, MANIP, LOCO, NAV, MOBILE, INTER]):
    sys.exit(f"state/display_tags.yml: expected the nine tags this script maps to, found {NEW_IDS}")

# Detailed label -> display tags, and why. An empty tuple maps to nothing: the
# label describes the episode, not a capability or a domain.
OLD_TO_NEW: dict[str, tuple[tuple[str, ...], str]] = {
    # Scale: where the task happens, so it decides the domain and never a capability.
    "scale-tabletop": ((MANIP,), "one workspace, the base never moves"),
    "scale-room": ((MOBILE,), "the base must move to reach what is manipulated"),
    "scale-building": ((MOBILE, NAV), "rooms or floors must be traversed between manipulations"),
    "scale-outdoor": ((MOBILE, NAV), "as building, with part of it outdoors"),
    # Body.
    "legged-locomotion": ((CTRL, LOCO), "a gait to maintain is locomotion control"),
    "rough-terrain": ((CTRL, LOCO), "terrain traversal"),
    "dynamic-balance": ((CTRL, FEED, LOCO), "staying up or getting back up is closed-loop correction"),
    "whole-body": ((CTRL, MOBILE), "whole-body coordination"),
    "bimanual": ((CTRL,), "multi-arm coordination"),
    "in-hand": ((CTRL,), "dexterous control"),
    # Contact: how the contact goes is execution.
    "transport": ((CTRL,), "grasp and carry"),
    "nonprehensile": ((CTRL,), "contact-rich execution"),
    "dynamics": ((CTRL,), "momentum and timing are control"),
    "articulated": ((CTRL,), "the object dictates the path"),
    "precision-fit": ((CTRL,), "contact-rich insertion"),
    "stability": ((CTRL,), "the settling is the work"),
    "force": ((CTRL,), "regulated force"),
    "deformable": ((CTRL,), "deformable-object interaction"),
    "fluid-granular": ((CTRL,), "containing or moving media"),
    "tool-use": ((PLAN, CTRL), "tool/affordance reasoning, then using the tool"),
    # Object state.
    "device-operation": ((CTRL,), "operate a switch, knob, lever or button"),
    "thermal": ((PLAN,), "reaching a state through an appliance or process is a plan, not a motion"),
    "cutting": ((PLAN, CTRL), "tool use"),
    "surface-treatment": ((CTRL,), "contact-rich wiping, sweeping, spraying"),
    # Goal: what makes it hard to read or to satisfy.
    "geometric-constraint": ((PLAN,), "geometric reasoning"),
    "relational-goal": ((PERC,), "spatial understanding"),
    "attribute-goal": ((PERC,), "object recognition by attribute"),
    "quantified-goal": ((PERC, PLAN), "count, then commit to a consistent choice"),
    "implicit-goal": ((PERC, PLAN), "ground a need, then choose what satisfies it"),
    "knowledge-goal": ((PERC, PLAN), "semantic grounding with facts not in the scene"),
    # Structure.
    "horizon-atomic": ((), "one skill: nothing beyond the contact labels it already has"),
    "horizon-composite": ((PLAN,), "two to five dependent steps: sequencing"),
    "horizon-activity": ((PLAN, FEED), "six or more steps; its definition: recovery matters more than any skill"),
    "ordered": ((PLAN,), "the order of the steps is fixed: sequencing"),
    "irreversible": ((PLAN,), "no retry, so the plan has to be right before acting"),
    # Perception.
    "partial-observability": ((PERC, FEED), "move or open something, then act on what it shows"),
    "active-perception": ((PERC, FEED), "act to find out: exploration based on feedback"),
    "fine-detail": ((PERC,), "recognition on print, texture or small geometry"),
    # Generalisation: what changes between episodes, not what the task asks.
    "gen-fixed": ((), "what varies between episodes, not what the task asks"),
    "gen-layout": ((), "what varies between episodes, not what the task asks"),
    "gen-appearance": ((), "what varies between episodes, not what the task asks"),
    "gen-objects": ((), "what varies between episodes, not what the task asks"),
    "gen-scenes": ((), "what varies between episodes, not what the task asks"),
    "gen-embodiment": ((), "what varies between episodes, not what the task asks"),
    "gen-language": ((), "what varies between episodes, not what the task asks"),
}

# Tasks the labels cannot reach: the spec names handover under Interaction &
# Collaboration, and these three are handovers (between a robot's two arms).
EXTRA_FOR_LABELLED: dict[tuple[str, str], tuple[tuple[str, ...], str]] = {
    ("robotwin-2", "handover_block"): ((INTER,), "handover"),
    ("robotwin-2", "handover_mic"): ((INTER,), "handover"),
    ("mujoco-playground", "aloha_hand_over"): ((INTER,), "handover"),
}

# HumanoidBench: by the capability class robot_coding_bench kept each task for
# (its `capability_class`, C1..C9), plus the paper's category: Locomotion is
# Locomotion & Stability; Manipulation is whole-body, since the H1 stands on its
# own legs while it manipulates.
HB_CLASS: dict[str, tuple[tuple[str, ...], str]] = {
    "C1": ((CTRL, LOCO), "flat-ground periodic gait"),
    "C2": ((CTRL, LOCO), "constrained gait: hurdles, stairs"),
    "C3": ((CTRL, FEED, LOCO), "quasi-static stabilisation: closed-loop balance"),
    "C4": ((CTRL, PLAN, NAV), "navigation and passage: a route or a sequence through a door"),
    "C5": ((CTRL, MOBILE), "whole-body power and momentum"),
    "C6": ((CTRL, MOBILE), "standing bimanual manipulation"),
    "C7": ((CTRL, MOBILE), "in-hand precision while standing"),
    "C8": ((CTRL, MOBILE), "mobile manipulation"),
    "C9": ((CTRL, PLAN, MOBILE), "long-horizon multi-subtask: sequencing"),
}
HB_CATEGORY = {"Locomotion": (LOCO,), "Manipulation": (MOBILE,)}

# RoboCasa365 tasks whose reference solution drives the base for at least 100
# control steps (5 s), measured from solution/oracle.npz (the `base` columns of
# environment/action_spec.json, |a| > 0.05) in robot_coding_bench at 8c5594a.
# The other 28 never move it, or only nudge it (at most 74 steps). RoboCasa
# (v0.2)'s 29 reference solutions never drive the base at all.
ROBOCASA365_MOBILE = {
    "add_lemon_to_fish", "assemble_cooking_array", "beverage_sorting", "candle_cleanup", "cookie_dough_prep",
    "deliver_brewed_coffee", "display_meat_variety", "drinkware_consolidation", "make_ice_lemonade",
    "make_loaded_potato", "meal_prep_staging", "microwave_defrost_meat", "plate_steak_meal", "reheat_meal",
    "retrieve_meat", "sanitize_prep_cutting_board", "searing_meat", "seasoning_spice_setup",
    "set_up_cutting_station", "stocking_breakfast_foods", "sweeten_coffee", "tong_buffet_setup",
}

# Benchmarks that have no labels: (tags every task gets, why, {task: (more tags, why)}).
UNLABELLED: dict[str, tuple[tuple[str, ...], str, dict[str, tuple[tuple[str, ...], str]]]] = {
    "humanoidbench": ((), "by capability class (HB_CLASS) and category (HB_CATEGORY)", {
        "manip_basketball": ((PERC, FEED), "catch a ball thrown at the robot, then throw"),
        "manip_highbar_simple": ((FEED,), "swing up: momentum managed in closed loop"),
        "loco_sit_hard": ((FEED,), "turn, walk and sit down without falling"),
        "manip_spoon": ((PLAN,), "tool use: stir with a spoon"),
        "manip_window": ((PLAN,), "tool use: wipe with a wiping tool"),
        "manip_package": ((PLAN,), "walk, pick up, carry, set down: a sequence"),
        "manip_room": ((PLAN,), "six objects to arrange: a sequence"),
    }),
    "kinder": ((PLAN, CTRL, MOBILE),
               "a physical-reasoning benchmark on TidyBot++, which commands its base and arm in one action", {
        "dynamo": ((PERC, FEED, NAV), "find a floor square the base camera cannot see at the start, past chairs"),
        "sort_blocks": ((PERC,), "sort by colour"),
    }),
    "robopaint": ((PERC, PLAN, CTRL, MANIP),
                  "a fixed Panda reproduces a given picture with a brush: read the picture, plan the strokes "
                  "(tool use), control the brush on the canvas", {}),
    "metaworldplus": ((CTRL, MANIP), "one fixed Sawyer arm, one skill per task", {
        "hammer": ((PLAN,), "tool use"),
        "stick_pull": ((PLAN,), "tool use"),
        "stick_push": ((PLAN,), "tool use"),
        "button_press_topdown_wall": ((PLAN,), "route around a wall: geometric reasoning"),
        "button_press_wall": ((PLAN,), "route around a wall: geometric reasoning"),
        "pick_place_wall": ((PLAN,), "route around a wall: geometric reasoning"),
        "push_wall": ((PLAN,), "route around a wall: geometric reasoning"),
        "reach_wall": ((PLAN,), "route around a wall: geometric reasoning"),
    }),
    "vlabench": ((CTRL, MANIP), "one fixed Panda at a table; categories Common sense, Semantic and Physical QA "
                 "add Perception + Planning (world knowledge or an indirect request names the target), Spatial "
                 "adds Perception", {
        "book_rearrange": ((PERC, PLAN), "order by publication date: world knowledge, fixed order"),
        "find_unseen_object": ((PERC, PLAN, FEED), "the apple is inside a closed cabinet: open, look, take"),
        "hammer_nail_and_hang_picture": ((PLAN,), "tool use, two dependent steps"),
        "heat_food": ((PLAN,), "into the microwave, close it, press start: ordered steps"),
        "play_math_game": ((PERC, PLAN), "answer a word problem with number cubes"),
        "put_box_on_painting": ((PERC,), "the painting is named by its title"),
        "select_billiards": ((PERC,), "the ball is named by number and stripe"),
        "select_chemistry_tube": ((PERC,), "the tube is named by its label"),
        "select_drink": ((PERC,), "the drink is named among others"),
        "select_fruit": ((PERC,), "the fruit is named among others"),
        "select_mahjong": ((PERC,), "the tile is named by its face"),
        "select_nth_largest_poker": ((PERC, PLAN), "rank the cards"),
        "select_painting": ((PERC, PLAN), "the painting is named by its style"),
        "select_poker": ((PERC,), "the card is named by its face"),
        "select_specific_type_book": ((PERC,), "the book is named by its genre"),
        "select_toy": ((PERC,), "the toy is named among others"),
        "select_unique_type_mahjong": ((PERC, PLAN), "compare every tile to find the odd one"),
        "take_out_cool_drink": ((PERC, PLAN), "a need, not an object (\"something healthy cool\"), then close the "
                                              "fridge"),
        "texas_holdem": ((PERC, PLAN), "cards named by a game's rules, several to place"),
    }),
    "robocasa": ((CTRL, MANIP), "PandaOmron in a kitchen, but no reference solution drives the base; "
                 "category Multi-stage adds Planning", {
        "restock_pantry": ((PERC,), "each can to its designated side"),
    }),
    "robocasa365": ((CTRL,), "PandaOmron; Mobile / Whole-body Manipulation where the reference solution drives "
                    "the base (ROBOCASA365_MOBILE), else Manipulation; category Composite adds Planning", {
        "beverage_sorting": ((PERC,), "alcoholic or not: world knowledge"),
        "choose_measuring_cup": ((PERC,), "the smaller cup"),
    }),
    "robocasa-gr1": ((CTRL, MANIP), "GR1's arms, waist and hands at a counter, its base fixed; category Pick and "
                     "place, then close adds Planning", {}),
}

# The line statedb.HEADER gained for the new field, added to each file's header after the `labels` one so the
# header still matches (statedb._own_comments keeps the comments under it only then).
LABELS_LINE = "#   labels      tier-2 ids from state/taxonomy.yml\n"
TAGS_LINE = next(line + "\n" for line in statedb.HEADER.splitlines() if line.startswith("#   display_tags"))


def by_rule(task: taskdb.Task) -> set[str]:
    """The tags an unlabelled benchmark's rule gives one task."""
    base, _, extra = UNLABELLED[task.benchmark]
    out = set(base) | set(extra.get(task.task_id, ((), ""))[0])
    up = task.upstream
    if task.benchmark == "humanoidbench":
        cls = re.search(r"C\d", str(up.get("capability_class", "")))
        if not cls or cls.group() not in HB_CLASS:
            sys.exit(f"humanoidbench/{task.task_id}: no capability class to go by")
        out |= set(HB_CLASS[cls.group()][0]) | set(HB_CATEGORY.get(up.get("category"), ()))
    elif task.benchmark == "vlabench":
        out |= {"Common sense": {PERC, PLAN}, "Semantic": {PERC, PLAN}, "Physical QA": {PERC, PLAN},
                "Spatial": {PERC}}.get(up.get("category"), set())
    elif task.benchmark == "robocasa":
        if str(up.get("category", "")).startswith("Multi-stage"):
            out.add(PLAN)
    elif task.benchmark == "robocasa365":
        out.add(MOBILE if task.task_id in ROBOCASA365_MOBILE else MANIP)
        if str(up.get("category", "")).startswith("Composite"):
            out.add(PLAN)
    elif task.benchmark == "robocasa-gr1":
        if up.get("category") == "Pick and place, then close":
            out.add(PLAN)
    return out


def new_tags(task: taskdb.Task) -> list[str]:
    old = task.capabilities
    out: set[str] = set()
    if old:
        for lid in old:
            if lid not in OLD_TO_NEW:
                sys.exit(f"{task.benchmark}/{task.task_id}: label {lid!r} has no row in OLD_TO_NEW")
            out.update(OLD_TO_NEW[lid][0])
        out.update(EXTRA_FOR_LABELLED.get((task.benchmark, task.task_id), ((), ""))[0])
    elif task.benchmark in UNLABELLED:
        out = by_rule(task)
    return [lid for lid in NEW_IDS if lid in out]


# ----------------------------------------------------------------------------- state files


def _set_tags(text: str, task_id: str, tags: list[str]) -> str:
    """Set one record's `display_tags:` lines, leaving every other line as is.

    An existing block is replaced. Otherwise the block goes where statedb.save_tasks would put it if the record's
    keys are sorted (that writer sorts them, so the next save from the site moves nothing), else at its end."""
    lines = text.splitlines(keepends=True)
    block = ["  display_tags:\n"] + [f"  - {tid}\n" for tid in tags]
    heads = (f"{task_id}:", f"'{task_id}':", f'"{task_id}":')
    start = next((i for i, line in enumerate(lines) if line.rstrip() in heads), None)
    if start is None:
        sys.exit(f"{task_id}: no record in the state file")
    end = start + 1
    while end < len(lines) and (lines[end].startswith((" ", "\t")) or not lines[end].strip()):
        end += 1
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    keys = [(i, m.group(1)) for i in range(start + 1, end) if (m := re.match(r"  ([A-Za-z_][\w-]*):", lines[i]))]
    for n, (i, key) in enumerate(keys):
        if key == "display_tags":
            j = keys[n + 1][0] if n + 1 < len(keys) else end
            return "".join(lines[:i] + block + lines[j:])
    names = [k for _, k in keys]
    at = end
    if names == sorted(names):
        at = next((i for i, key in keys if key > "display_tags"), end)
    return "".join(lines[:at] + block + lines[at:])


def migrate_state(bench: taskdb.Benchmark, dry_run: bool) -> dict[str, list[str]]:
    path = statedb.state_path(bench.id)
    text = path.read_text(encoding="utf-8")
    before = statedb.load_tasks(bench.id)
    result, changed = {}, 0
    for task in bench.tasks:
        tags = new_tags(task)
        result[task.task_id] = tags
        if tags != list(task.state.get("display_tags") or []):
            text = _set_tags(text, task.task_id, tags)
            changed += 1
    if TAGS_LINE not in text:
        if text.count(LABELS_LINE) != 1:
            sys.exit(f"{path}: header has no `labels` line to put the `display_tags` one after")
        text = text.replace(LABELS_LINE, LABELS_LINE + TAGS_LINE)
        changed += 1
    if not text.startswith(statedb.HEADER.format(benchmark=bench.id).rstrip("\n") + "\n"):
        sys.exit(f"{path}: header differs from statedb.HEADER — refusing to write")

    # Nothing but `display_tags` may differ, and every tag must be the one computed.
    after = yaml.safe_load(text) or {}
    for tid in set(before) | set(after):
        a = {k: v for k, v in (before.get(tid) or {}).items() if k != "display_tags"}
        b = {k: v for k, v in (after.get(tid) or {}).items() if k != "display_tags"}
        if a != b:
            sys.exit(f"{path}: {tid} changed beyond `display_tags` — refusing to write")
    for tid, tags in result.items():
        if list((after.get(tid) or {}).get("display_tags") or []) != tags:
            sys.exit(f"{path}: {tid} would not read back as {tags}")
    if changed and not dry_run:
        statedb._atomic_write(path, text)
    return result


# ----------------------------------------------------------------------------- reports


def table() -> str:
    names = {tid: tag["name"] for tid, tag in TAGS.items()}

    def show(ids):
        ids = set(ids)
        return ", ".join(names[i] for i in NEW_IDS if i in ids) or "—"

    out = ["| Detailed label | Capability | Task Domain | Why |", "| --- | --- | --- | --- |"]
    for old, (new, why) in OLD_TO_NEW.items():
        out.append(f"| `{old}` | {show(i for i in new if GROUP_OF[i] == 'capability')} "
                   f"| {show(i for i in new if GROUP_OF[i] == 'domain')} | {why} |")
    out += ["", "| Labelled task | Added | Why |", "| --- | --- | --- |"]
    for (bench, tid), (new, why) in EXTRA_FOR_LABELLED.items():
        out.append(f"| {bench} `{tid}` | {show(new)} | {why} |")
    out += ["", "| Benchmark (no labels before) | Every task | Rule |", "| --- | --- | --- |"]
    for bench, (base, why, _) in UNLABELLED.items():
        out.append(f"| {bench} | {show(base)} | {why} |")
    out += ["", "| HumanoidBench class | Tags | Why |", "| --- | --- | --- |"]
    for cls, (new, why) in HB_CLASS.items():
        out.append(f"| {cls} | {show(new)} | {why} |")
    out += ["", "| Task | Added to its benchmark's rule | Why |", "| --- | --- | --- |"]
    for bench, (_, _, extra) in UNLABELLED.items():
        for tid, (new, why) in extra.items():
            out.append(f"| {bench} `{tid}` | {show(new)} | {why} |")
    return "\n".join(out)


def counts(results: dict[str, dict[str, list[str]]]) -> str:
    short = {PERC: "Perc", PLAN: "Plan", CTRL: "Ctrl", FEED: "Feed", MANIP: "Manip", LOCO: "Loco", NAV: "Nav",
             MOBILE: "Mobile", INTER: "Inter"}
    head = f"{'benchmark':18s} {'tasks':>5s} " + " ".join(f"{short[i]:>6s}" for i in NEW_IDS)
    out = [head, "-" * len(head)]
    for bench, tasks in results.items():
        row = [sum(1 for tags in tasks.values() if tid in tags) for tid in NEW_IDS]
        out.append(f"{bench:18s} {len(tasks):5d} " + " ".join(f"{n:6d}" for n in row))
    total = [sum(1 for tasks in results.values() for tags in tasks.values() if tid in tags) for tid in NEW_IDS]
    out.append(f"{'all':18s} {sum(len(t) for t in results.values()):5d} " + " ".join(f"{n:6d}" for n in total))
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print the counts, write nothing")
    ap.add_argument("--table", action="store_true", help="print the mapping tables as Markdown and exit")
    args = ap.parse_args()
    if args.table:
        print(table())
        return 0

    rowless = [lid for lid in taskdb.capability_index() if lid not in OLD_TO_NEW]
    if rowless:
        sys.exit(f"state/taxonomy.yml: no row in OLD_TO_NEW for {', '.join(rowless)}")

    results: dict[str, dict[str, list[str]]] = {}
    for bench in taskdb.benchmarks().values():
        results[bench.id] = migrate_state(bench, args.dry_run)

    missing = [f"{b}/{tid}: no {gid} tag" for b, tasks in results.items() for tid, tags in tasks.items()
               for gid in taskdb.TAG_GROUPS if not any(GROUP_OF[t] == gid for t in tags)]
    print(counts(results))
    if missing:
        print("\n".join(missing))
        return 1
    print("every task has at least one Capability and one Task Domain tag"
          + (" (dry run: nothing written)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Sync MolmoSpaces' task pages from robot_coding_bench, where our selection of it is defined.

MolmoSpaces (allenai/molmospaces, molmo-spaces 0.2.9 on MuJoCo 3.5.0) evaluates robot policies on frozen episodes in
unseen houses: six Franka FR3 families (pick, three kinds of pick-and-place, open, close) and two Rainbow RB-Y1 families
(navigate-to, open-door). robot_coding_bench keeps one upstream episode per family (`scripts/molmospaces/families.json`,
`instances/`), as task pairs `tasks/molmospaces-<family>-i00-privileged` / `-standard` written by
`scripts/molmospaces/mk_tasks.py`. The site's task id is the family with underscores (`pick_and_place_next_to`).
There is no reference solution, so a row shows the starting scene: with --scenes, a results site's t = 0 camera images
(`<family>-i00/t0_<camera>.png`; the exterior camera on the Franka, the head camera on the RB-Y1). Everything else is
shared with the other robot_coding_bench selections: scripts/rcb_selection.py has the format and the state rules.

Usage:
  python scripts/import_molmospaces_tasks.py --source ../robot_coding_bench --commit <commit> --scenes <cameras dir>
  python scripts/import_molmospaces_tasks.py                  # from the cache
"""

import re
import sys
import tomllib

from rcb_selection import Bench, clean, main, section, table

ROBOTS = {   # robot_coding_bench's robot vocabulary -> (the site's wording, the camera of the starting-scene still)
    "franka-robotiq-2f85": ("Franka FR3 with a Robotiq 2F-85 gripper on a fixed base (the DROID setup)",
                            "randomized_zed2_analogue_1"),
    "rainbow-rby1": ("Rainbow RB-Y1: holonomic base, 6-joint torso, two 7-joint arms with parallel grippers",
                     "head_camera"),
}
FAMILIES = {"pick": "Pick", "pick_and_place": "Pick and place", "pick_and_place_next_to": "Pick and place next to",
            "pick_and_place_color": "Pick and place by colour", "open": "Open", "close": "Close",
            "navigate_to": "Navigate to", "open_door": "Open door"}


BODY = """
## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/{id}.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- MolmoSpaces publishes no per-task demonstration and we ship no reference
     solution; the row shows the starting scene. -->

_No demo._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->
"""


def _category(t: dict) -> str:
    return "Franka" if t["robot_key"] == "franka-robotiq-2f85" else "RB-Y1"


def _enrich(root, t: dict) -> None:
    """Our task texts' own layout: the task sentence (`**Task:**`), the success rule and horizon (`## Success`), the
    deliverable, and the upstream episode and house (the README's Details)."""
    priv = root / "tasks" / f"{t['task_dir']}-privileged"
    instr, readme = (priv / "instruction.md").read_text(), (priv / "README.md").read_text()

    def find(pattern: str, text: str, what: str, flags: int = 0) -> re.Match:
        m = re.search(pattern, text, flags)
        return m or sys.exit(f"{priv.name}: no {what} where the importer expects it (the task text's layout changed?)")
    rule = find(r"on the state\s+at that moment: (.+?)\. The task has to hold", instr, "success rule", re.S)
    steps = find(r"\*\*(\d+) control steps\*\* \(the benchmark's\s+(\S+ s) horizon", instr, "horizon")
    upstream = clean(table(section(readme, "Details")).get("upstream", ""))
    t["robot_key"] = tomllib.loads((priv / "task.toml").read_text())["metadata"]["robot"]
    t["instruction"] = clean(find(r"\*\*Task:\*\*\s*(.+)", instr, "task sentence").group(1))
    t["requirements"] = [clean(rule.group(1)),
                         "judged at the end of the episode: the trajectory's last row (privileged), `done` (standard) "
                         f"or {steps.group(1)} control steps (the benchmark's {steps.group(2)} horizon), whichever "
                         "comes first"]
    t["deliverable"] = clean(section(instr, "Deliverable").split(" in this order")[0])
    episode_re = r"benchmark (\S+), package (\S+) .*, episode (\d+)"
    bench, package, episode = find(episode_re, upstream, "upstream episode").groups()
    t["instance"] = f"{bench}, package {package}, episode {episode}"
    t["house"] = find(r"house (.+)$", upstream, "house").group(1)


BENCH = Bench(
    id="molmospaces",
    name="MolmoSpaces",
    prefix="molmospaces-",
    upstream="https://github.com/allenai/molmospaces @ molmo-spaces 0.2.9 (benchmark molmospaces-bench-v2/20260415)",
    robot="",
    scene_model="",
    category=_category,
    title=lambda t: f"{_category(t)} · {FAMILIES[t['id']]}",
    enrich=_enrich,
    extra=lambda t: {"robot": ROBOTS[t["robot_key"]][0], "scene_model": t["house"]},
    scene=lambda t: f"{t['task_dir'].removeprefix(BENCH.prefix)}/t0_{ROBOTS[t['robot_key']][1]}.png",
    body=BODY,
)

if __name__ == "__main__":
    raise SystemExit(main(BENCH, __doc__))

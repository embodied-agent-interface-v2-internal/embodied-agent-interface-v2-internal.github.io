#!/usr/bin/env python3
"""Sync RoboCasa's task pages from robot_coding_bench, where our selection of it is defined.

RoboCasa v0.2 (robocasa/robocasa @ 756598a, robosuite 1.5.1, MuJoCo 3.2.6) has kitchen tasks for a Franka Panda on an
Omron mobile base; robot_coding_bench keeps the 29 with an official demonstration that re-verifies on a frozen instance,
as task pairs `tasks/robocasa-<task>-i00-privileged` / `-standard` written by `scripts/robocasa/generate.py`. The site's
task id is the task part with underscores (`robocasa-open-drawer-i00-*` is `open_drawer`). Everything else is shared with
the other robot_coding_bench selections: scripts/rcb_selection.py has the format, the demos and the state rules.

Usage:
  python scripts/import_robocasa_tasks.py --source ../robot_coding_bench --commit origin/main --demos <oracle jobs>
  python scripts/import_robocasa_tasks.py                  # from the cache
"""

import re

from rcb_selection import Bench, main


def _category(t: dict) -> str:
    m = re.search(r"(single|multi)_stage/([a-z_]+)/", t.get("instance", ""))
    return f"{m[1].capitalize()}-stage · {m[2].replace('_', ' ')}" if m else "Kitchen"


BENCH = Bench(
    id="robocasa",
    name="RoboCasa",
    prefix="robocasa-",
    excludes=("robocasa-gr1-",),
    upstream="https://github.com/robocasa/robocasa @ 756598a (v0.2)",
    robot="Franka Panda on an Omron mobile base with a torso lift (PandaOmron)",
    scene_model="robocasa_kitchen",
    category=_category,
    title=lambda t: f"{_category(t).split(' · ')[0]} · {t['family'].split('/')[-1]}",
    demo_note="the scene camera",
)

if __name__ == "__main__":
    raise SystemExit(main(BENCH, __doc__))

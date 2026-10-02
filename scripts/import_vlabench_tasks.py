#!/usr/bin/env python3
"""Sync VLABench's task pages from robot_coding_bench, where our selection of it is defined.

VLABench (OpenMOSS/VLABench @ cf588fe, Franka Panda, MuJoCo + dm_control) has 96 native tasks; robot_coding_bench keeps
the 36 whose recorded expert re-verifies on a frozen instance (`scripts/vlabench/tasks.json`), as task pairs
`tasks/vlabench-<task>-i00-privileged` / `-standard` written by `scripts/vlabench/generate.py`. The site's task id is
VLABench's own task name (`select_fruit_common_sense`). Everything else is shared with the other robot_coding_bench
selections: scripts/rcb_selection.py has the format, the demos and the state rules.

Usage:
  python scripts/import_vlabench_tasks.py --source ../robot_coding_bench --commit origin/main --demos <oracle jobs>
  python scripts/import_vlabench_tasks.py                  # from the cache
"""

from rcb_selection import Bench, main


def _category(t: dict) -> str:
    for suffix, name in (("_qa", "Physical QA"), ("_common_sense", "Common sense"), ("_semantic", "Semantic"),
                         ("_spatial", "Spatial")):
        if t["id"].endswith(suffix):
            return name
    return "Manipulation"


BENCH = Bench(
    id="vlabench",
    name="VLABench",
    prefix="vlabench-",
    upstream="https://github.com/OpenMOSS/VLABench @ cf588fe",
    robot="Franka Panda (7-DoF arm, two-finger gripper)",
    scene_model="vlabench_table",
    category=_category,
    title=lambda t: f"{_category(t)} · {t['id']}",
    demo_note="the front camera",
)

if __name__ == "__main__":
    raise SystemExit(main(BENCH, __doc__))

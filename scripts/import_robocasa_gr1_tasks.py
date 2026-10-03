#!/usr/bin/env python3
"""Sync RoboCasa-GR1's task pages from robot_coding_bench, where our selection of it is defined.

RoboCasa's GR1 tabletop tasks (robocasa/robocasa-gr1-tabletop-tasks @ 4840e67, robosuite @ 51cc017 with its mink
whole-body IK controller, MuJoCo 3.2.6) have a Fourier GR1 humanoid at a kitchen counter; robot_coding_bench keeps all 24
environments with an official demonstration, one frozen instance each, as task pairs
`tasks/robocasa-gr1-<task>-i00-privileged` / `-standard` written by `scripts/robocasa-gr1/generate.py`. The site's task id
is the task part with underscores (`robocasa-gr1-plate-to-bowl-i00-*` is `plate_to_bowl`). Everything else is shared with
the other robot_coding_bench selections: scripts/rcb_selection.py has the format, the demos and the state rules.

Usage:
  python scripts/import_robocasa_gr1_tasks.py --source ../robot_coding_bench --commit origin/main --demos <oracle jobs>
  python scripts/import_robocasa_gr1_tasks.py                  # from the cache
"""

from rcb_selection import Bench, main


def _category(t: dict) -> str:
    env = t["family"].split("/")[-1]
    if env.startswith("PosttrainPnPNovel"):
        return "Pick and place (novel objects)"
    if env.endswith("Close"):
        return "Pick and place, then close"
    return "Pick and place"


BENCH = Bench(
    id="robocasa-gr1",
    name="RoboCasa-GR1",
    prefix="robocasa-gr1-",
    upstream="https://github.com/robocasa/robocasa-gr1-tabletop-tasks @ 4840e67",
    robot="Fourier GR1 humanoid: two arms, waist and two six-command Fourier hands; fixed base",
    scene_model="gr1_counter",
    category=_category,
    title=lambda t: f"GR1 · {t['family'].split('/')[-1]}",
    demo_note="the scene camera",
)

if __name__ == "__main__":
    raise SystemExit(main(BENCH, __doc__))

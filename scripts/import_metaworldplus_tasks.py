#!/usr/bin/env python3
"""Sync MetaWorld+'s task pages from robot_coding_bench, where the benchmark is defined (our own, after Meta-World v3).

MetaWorld+ is all 50 of Meta-World's v3 environments (Farama-Foundation/Metaworld @ 59fc34d, Sawyer arm, MuJoCo 3.3.0),
one frozen instance each, as task pairs `tasks/metaworldplus-<env>-i00-privileged` / `-standard` written by
`scripts/metaworldplus/generate.py`. The site's task id is the environment with underscores (`button-press-topdown-v3`
is `button_press_topdown`). Everything else is shared with the other robot_coding_bench selections:
scripts/rcb_selection.py has the format, the demos and the state rules.

Usage:
  python scripts/import_metaworldplus_tasks.py --source ../robot_coding_bench --commit origin/main \\
      --demos <the oracle's Harbor jobs>
  python scripts/import_metaworldplus_tasks.py                  # from the cache
"""

from rcb_selection import Bench, main

BENCH = Bench(
    id="metaworldplus",
    name="MetaWorld+",
    prefix="metaworldplus-",
    upstream="https://github.com/Farama-Foundation/Metaworld @ 59fc34d (Meta-World v3)",
    robot="Rethink Sawyer: a 7-DoF arm whose hand is a mocap body (the wrist does not rotate), two-finger gripper",
    scene_model="metaworld_table",
    category=lambda t: "Meta-World v3",
    title=lambda t: f"Meta-World · {t['id'].replace('_', ' ').capitalize()}",
    demo_note="the front camera",
)

if __name__ == "__main__":
    raise SystemExit(main(BENCH, __doc__))

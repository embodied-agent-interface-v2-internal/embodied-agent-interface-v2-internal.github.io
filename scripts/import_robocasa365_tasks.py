#!/usr/bin/env python3
"""Sync RoboCasa365's task pages from robot_coding_bench, where our selection of it is defined.

RoboCasa365 (robocasa/robocasa @ 4f8a298, robocasa 1.0.1, robosuite 1.5.2, MuJoCo 3.3.1) has 365 kitchen task families
for a Franka Panda on an Omron mobile base; robot_coding_bench keeps 50 of them by a fixed rule
(`scripts/robocasa365/select_instances.py`: 12 atomic and 38 composite), as task pairs
`tasks/robocasa365-<task>-i00-privileged` / `-standard` written by `scripts/robocasa365/generate.py`. The site's task id
is the task part with underscores. Everything else is shared with the other robot_coding_bench selections:
scripts/rcb_selection.py has the format, the demos and the state rules.

Usage:
  python scripts/import_robocasa365_tasks.py --source ../robot_coding_bench --commit origin/main --demos <oracle jobs>
  python scripts/import_robocasa365_tasks.py                  # from the cache
"""

import ast
import re
from pathlib import Path

from rcb_selection import Bench, main


def _enrich(root: Path, t: dict) -> None:
    """The family's group (atomic or composite) from the generator's own table, scripts/robocasa365/envs.py GROUP."""
    tree = ast.parse((root / "scripts" / "robocasa365" / "envs.py").read_text())
    groups = next(ast.literal_eval(n.value) for n in tree.body
                  if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "GROUP" for x in n.targets))
    t["group"] = groups.get(t["family"].split("/")[-1], "")


def _category(t: dict) -> str:
    m = re.search(r"/environments/kitchen/(atomic|composite)/([a-z_]+)(?:/|\.py)", t.get("env_source", ""))
    group = (m[1] if m else t.get("group", "")).capitalize() or "Kitchen"
    return group + (f" · {m[2].replace('_', ' ')}" if m else "")


BENCH = Bench(
    id="robocasa365",
    name="RoboCasa365",
    prefix="robocasa365-",
    upstream="https://github.com/robocasa/robocasa @ 4f8a298 (robocasa 1.0.1)",
    robot="Franka Panda on an Omron mobile base with a torso lift (PandaOmron)",
    scene_model="robocasa365_kitchen",
    category=_category,
    title=lambda t: f"{_category(t).split(' · ')[0]} · {t['family'].split('/')[-1]}",
    demo_note="the scene camera",
    sources=("scripts/robocasa365/envs.py",),
    enrich=_enrich,
)

if __name__ == "__main__":
    raise SystemExit(main(BENCH, __doc__))

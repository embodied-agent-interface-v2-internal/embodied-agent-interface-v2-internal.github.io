---
title: Long screwdriver · spin horizontal
task_id: screwdriver_long_screwdriver_spin_horizontal
benchmark: dextoolbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/tylerlum/simtoolreal @ 313d5ae
  synced: '2026-09-28'
  scene_model: tabletop
  category: screwdriver
  object: long_screwdriver
  task: spin_horizontal
  instruction: 'Pick up the long screwdriver and move it through the demonstrated motion (spinning it about a horizontal axis): bring it to each of the 31 goal poses in order.'
  n_goals: 31
  source_file: dextoolbench/trajectories/screwdriver/long_screwdriver/spin_horizontal.json
  tool_model: assets/urdf/dextoolbench/screwdriver/long_screwdriver/long_screwdriver.urdf
  table: table_narrow.urdf (plain)
  metric: 'task progress: goals reached / goals (8 grasp-box keypoints within 1.5 cm; 10 s per goal)'

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: run in our MuJoCo port (robot_coding_bench tasks/dextoolbench_screwdriver_long_screwdriver_spin_horizontal, image rcb-mujoco 0.1.1)
  stack: MuJoCo 3.3.7 (CPU, bit-exact replay), KUKA iiwa 14 (MuJoCo Menagerie 1b86ece) + Sharpa HA4, 600 Hz physics, 60 Hz control
  checked: '2026-09-28'
  harness_task: dextoolbench_screwdriver_long_screwdriver_spin_horizontal
  oracle: 'SimToolReal''s pretrained policy, recorded in this scene and replayed: 31/31 goals'
---

## Why this task is interesting

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/dextoolbench.yml. -->

_Not yet written._

## Oracle demo review

<!-- The row plays OUR replay of SimToolReal's pretrained policy in our MuJoCo port (four views: front, side, top,
     oblique). The policy is the benchmark's own method, not a scripted expert; how far it gets here is the facts
     table's `oracle` line. -->

_Not yet reviewed._

## Discussion

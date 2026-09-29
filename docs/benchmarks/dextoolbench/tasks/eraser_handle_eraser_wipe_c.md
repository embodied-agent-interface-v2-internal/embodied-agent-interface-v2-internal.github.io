---
title: Handle eraser · wipe c
task_id: eraser_handle_eraser_wipe_c
benchmark: dextoolbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/tylerlum/simtoolreal @ 313d5ae
  synced: '2026-09-28'
  scene_model: tabletop
  category: eraser
  object: handle_eraser
  task: wipe_c
  instruction: 'Pick up the handle eraser and move it through the demonstrated motion (wiping the letter C): bring it to each of the 31 goal poses in order.'
  n_goals: 31
  source_file: dextoolbench/trajectories/eraser/handle_eraser/wipe_c.json
  tool_model: assets/urdf/dextoolbench/eraser/handle_eraser/handle_eraser.urdf
  table: table_narrow_whiteboard.urdf (a whiteboard at the table's edge)
  metric: 'task progress: goals reached / goals (8 grasp-box keypoints within 1.5 cm; 10 s per goal)'

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: run in our MuJoCo port (robot_coding_bench tasks/dextoolbench_eraser_handle_eraser_wipe_c, image rcb-mujoco 0.1.1)
  stack: MuJoCo 3.3.7 (CPU, bit-exact replay), KUKA iiwa 14 (MuJoCo Menagerie 1b86ece) + Sharpa HA4, 600 Hz physics, 60 Hz control
  checked: '2026-09-28'
  harness_task: dextoolbench_eraser_handle_eraser_wipe_c
  oracle: 'SimToolReal''s pretrained policy, recorded in this scene and replayed: 12/31 goals'
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

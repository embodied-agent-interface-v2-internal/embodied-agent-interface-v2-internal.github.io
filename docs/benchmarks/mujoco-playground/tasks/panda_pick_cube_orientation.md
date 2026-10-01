---
title: Panda Pick Cube Orientation
task_id: panda_pick_cube_orientation
benchmark: mujoco-playground

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/google-deepmind/mujoco_playground @ 4057c14
  synced: '2026-09-28'
  scene_model: tabletop
  env: PandaPickCubeOrientation
  robot: Franka Panda
  instruction: Pick up the box and hold it at the target position, in the target orientation.
  control_hz: 50
  episode_s: 3.0
  source_file: mujoco_playground/_src/manipulation/franka_emika_panda/pick.py
  metric: 'Playground: dense RL reward, no success test'

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: run in plain MuJoCo (robot_coding_bench tasks/mujoco_playground_panda_pick_cube_orientation, image rcb-mujoco 0.1.1)
  stack: MuJoCo 3.3.7 (CPU, bit-exact replay), Playground's scene XML @ 4057c14 + MuJoCo Menagerie 1b86ece, 50 Hz control
  checked: '2026-09-28'
  harness_task: mujoco_playground_panda_pick_cube_orientation
  success_test: 'ours: box centre within 2 cm of the target and orientation within 15 degrees, at the end of the trajectory'
  oracle: 'scripted IK oracle (privileged state), replayed in the verifier: success 1, deterministic 1'
---

## Why this task is interesting

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/mujoco-playground.yml. -->

_Not yet written._

## Oracle demo review

<!-- The row plays OUR scripted oracle's replay (built tasks only); Playground ships no demos. -->

_Not yet reviewed._

## Discussion

---
title: Aero Cube Rotate Z Axis
task_id: aero_cube_rotate_z_axis
benchmark: mujoco-playground

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/google-deepmind/mujoco_playground @ 4057c14
  synced: '2026-09-28'
  scene_model: tabletop
  env: AeroCubeRotateZAxis
  robot: TetherIA Aero Hand Open
  instruction: Rotate the cube about the vertical axis as fast as possible without dropping it.
  control_hz: 20
  episode_s: 25.0
  source_file: mujoco_playground/_src/manipulation/aero_hand/rotate_z.py
  metric: 'Playground: dense RL reward, no success test'

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  harness_task: not built
  checked: '2026-09-28'
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

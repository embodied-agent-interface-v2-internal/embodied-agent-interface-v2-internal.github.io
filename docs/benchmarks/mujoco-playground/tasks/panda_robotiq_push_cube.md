---
title: Panda Robotiq Push Cube
task_id: panda_robotiq_push_cube
benchmark: mujoco-playground

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/google-deepmind/mujoco_playground @ 4057c14
  synced: '2026-09-28'
  scene_model: tabletop
  env: PandaRobotiqPushCube
  robot: Franka Panda + Robotiq 2F-85
  instruction: Push the cube across the table to the target.
  control_hz: 200
  episode_s: 15.0
  source_file: mujoco_playground/_src/manipulation/franka_emika_panda_robotiq/push_cube.py
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

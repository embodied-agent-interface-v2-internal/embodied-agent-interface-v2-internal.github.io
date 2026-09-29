---
title: Panda Pick Cube Cartesian
task_id: panda_pick_cube_cartesian
benchmark: mujoco-playground

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/google-deepmind/mujoco_playground @ 4057c14
  synced: '2026-09-28'
  scene_model: tabletop
  env: PandaPickCubeCartesian
  robot: Franka Panda (Cartesian controller)
  instruction: Pick up the box and lift it to a fixed location, with a Cartesian end-effector controller; built for pixel observations and sim2real.
  control_hz: 20
  episode_s: 10.0
  source_file: mujoco_playground/_src/manipulation/franka_emika_panda/pick_cartesian.py
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

---
title: Panda Open Cabinet
task_id: panda_open_cabinet
benchmark: mujoco-playground

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/google-deepmind/mujoco_playground @ 4057c14
  synced: '2026-09-28'
  scene_model: tabletop
  env: PandaOpenCabinet
  robot: Franka Panda
  instruction: Grasp the handle and pull it along its slide to the target.
  control_hz: 50
  episode_s: 3.0
  source_file: mujoco_playground/_src/manipulation/franka_emika_panda/open_cabinet.py
  metric: 'Playground: dense RL reward, no success test'

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: run in plain MuJoCo (robot_coding_bench tasks/mujoco_playground_panda_open_cabinet, image rcb-mujoco 0.1.1)
  stack: MuJoCo 3.3.7 (CPU, bit-exact replay), Playground's scene XML @ 4057c14 + MuJoCo Menagerie 1b86ece, 50 Hz control
  checked: '2026-09-28'
  harness_task: mujoco_playground_panda_open_cabinet
  success_test: 'ours: handle within 1.5 cm of the target along its slide, at the end of the trajectory'
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

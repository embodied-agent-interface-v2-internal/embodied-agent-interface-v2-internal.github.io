---
title: Aloha Hand Over
task_id: aloha_hand_over
benchmark: mujoco-playground

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/google-deepmind/mujoco_playground @ 4057c14
  synced: '2026-09-28'
  scene_model: tabletop
  env: AlohaHandOver
  robot: ALOHA 2 (two ViperX 300s arms)
  instruction: Pick up the box with the left arm, hand it over to the right arm, and hold it at the target.
  control_hz: 50
  episode_s: 5.0
  source_file: mujoco_playground/_src/manipulation/aloha/handover.py
  metric: 'Playground: dense RL reward, no success test'

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: run in plain MuJoCo (robot_coding_bench tasks/mujoco_playground_aloha_hand_over, image rcb-mujoco 0.1.1)
  stack: MuJoCo 3.3.7 (CPU, bit-exact replay), Playground's scene XML @ 4057c14 + MuJoCo Menagerie 1b86ece, 50 Hz control
  checked: '2026-09-28'
  harness_task: mujoco_playground_aloha_hand_over
  success_test: 'ours: box centre within 3 cm of the target, touching the right gripper and nothing of the left arm, off the table (z >= 0.05 m), at the end of the trajectory'
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

---
title: Locomotion · Sit simple
task_id: loco_sit_simple
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: Sit the robot down on the chair and keep it seated, upright and still.
  env_id: h1-sit_simple-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_loco
  scene_image: loco_sit_simple.png
  category: Locomotion
  capability_class: fixture (C3 · quasi-static stabilisation, too easy to score)
  role: fixture
  success_criteria:
    - the summed per-step reward over one episode reaches 750, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'A product: the average of two seat terms — how close the pelvis is to the height it has when seated, and whether the robot is over the seat rather than beside it — multiplied by staying upright, a seated posture (the head''s height above the torso), not moving, and low actuator force. Every step spent not yet sitting forfeits the reward that step could have paid, so both how fast and how steadily the robot sits matter.'
  ends_early: The episode ends early if the pelvis drops below about half its standing height — not far below its height when seated.
  zero_action_return: 637.64
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the chair's pose, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

A fixture: the chair is about 0.25 m straight behind the pelvis, so a symmetric squat seats the robot. It checks the whole pipeline end to end and is not scored.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Works as the pipeline fixture: passes both modes, limited mode in its first episode. (@williamzhangNU)

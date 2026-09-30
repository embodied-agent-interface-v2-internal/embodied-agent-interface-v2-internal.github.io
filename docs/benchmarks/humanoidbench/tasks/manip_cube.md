---
title: Manipulation · Cube
task_id: manip_cube
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 12fb1352
  synced: '2026-09-30'
  instruction: A cube starts just above and in front of each palm. Rotate both cubes to the goal orientation without dropping them.
  env_id: h1hand-cube-v0
  robot: Unitree H1 with two Shadow hands (61 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_cube.png
  category: Manipulation
  capability_class: C7 · in-hand precision
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 370, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 500 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'A weighted sum: the largest term is how closely each cube''s orientation matches the goal, averaged over the two hands; then how close each hand is to its cube; then a small share for standing steadily without moving. The orientation term is sharp — it falls away quickly as the orientation drifts, so approximate alignment earns much less than it looks like it should — and it compares orientations as quaternions, sign included: of the two ways to turn a cube onto the goal, only one scores, because the other ends at the same orientation with the opposite sign, which counts as far off.'
  ends_early: The episode ends the moment either cube drops below a height, or the pelvis does.
  zero_action_return: 5.0
  action_dim: 61
  control_rate_hz: 50
  limited_mode: head cameras (RGB 512×512), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the cubes' orientations, not the goal orientation, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Two Shadow hands must each turn a cube to a signed target orientation and hold it there. The starting pose does not stand by itself (it falls after about 84 steps), so the robot must first stay up for the 500-step episode, then turn the cubes early.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Out of reach in both modes: the robot has to stay up while turning two cubes in its hands, and no run did both. (@williamzhangNU)

---
title: Manipulation · Insert normal
task_id: manip_insert_normal
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 12fb1352
  synced: '2026-09-30'
  instruction: A bar and two small open sockets lie on the table in front of the robot. Fit each end of the bar into the socket of the matching colour, then lift the assembly to about 1.1 m and hold it there, without dropping anything.
  env_id: h1hand-insert_normal-v0
  robot: Unitree H1 with two Shadow hands (61 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_insert_normal.png
  category: Manipulation
  capability_class: C7 · in-hand precision
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 350, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 500 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'The step is a product of two groups: one covering posture and how close each end of the bar is to its socket, the other covering how high the sockets are and whether a hand is at a socket (the left hand at the dark one, or the right hand at the light one). Because the groups multiply, doing one of them well is worth little while the other is near zero — both have to come along together.'
  ends_early: The episode ends the moment the bar or either socket drops below a height, which a dropped part does immediately, or the pelvis does.
  zero_action_return: 2.51
  action_dim: 61
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the poses of the bar and the sockets, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Each end of a bar goes into the socket of its colour, then the robot lifts the assembly. The two groups of terms multiply, so getting only one of them right earns almost nothing.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Blocked on the grasp: the bar is never gripped in either mode. (@williamzhangNU)

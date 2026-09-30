---
title: Manipulation · Room
task_id: manip_room
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: 'Six loose objects — a chair, a trophy, a pair of headphones, two packages and a snow globe — are scattered around the room (the table and the bookshelf are fixed). Tidy up: gather them together, so they end up close to one another rather than spread out.'
  env_id: h1hand-room-v0
  robot: Unitree H1 with two Shadow hands (61 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_room.png
  category: Manipulation
  capability_class: C8 · mobile manipulation
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 400, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: Unusually, this task gives you no target positions at all. The dominant term measures how spread out the six objects are — the variance of their horizontal coordinates — and rewards making that small; a smaller term pays for standing steadily. Any arrangement that brings the objects close together scores, wherever in the room you do it.
  ends_early: The episode ends if the pelvis drops near the ground.
  zero_action_return: 8.84
  action_dim: 61
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not where the objects are, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Six loose objects lie scattered around the room, and the score rewards gathering them close together, so the robot has to walk over and carry them. Standing through the episode earns less than half the bar.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Blocked on walking: the objects, the nearest about 1.9 m away, are never reached in either mode. (@williamzhangNU)

---
title: Manipulation · Bookshelf simple
task_id: manip_bookshelf_simple
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 12fb1352
  synced: '2026-09-30'
  instruction: Put each of the five objects onto its assigned place on the bookshelf, one at a time, in order.
  env_id: h1hand-bookshelf_simple-v0
  robot: Unitree H1 with two Shadow hands (61 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_bookshelf_simple.png
  category: Manipulation
  capability_class: C9 · long-horizon multi-subtask
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 2000, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'Only the object you are currently on is scored: each step pays for standing steadily, for a hand being near that object and for its progress towards its assigned slot. Placing it pays a one-off bonus that grows with how many you have placed — together the bonuses are most of the bar — and moves the scoring on to the next one. So the return is cut into five plateaus and stalling on the first caps the episode low.'
  ends_early: The episode ends early if the pelvis drops too low or if the object currently being scored goes below about half a metre, and it ends once all five are placed.
  zero_action_return: 30.45
  action_dim: 61
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not where the objects or their places are, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Five objects go onto assigned places on a bookshelf, one at a time, in order. The robot has to stand close to the shelf before it can lift the first object from the second shelf to the top one.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Stands but never grasps: the first object is never lifted in either mode. (@williamzhangNU)

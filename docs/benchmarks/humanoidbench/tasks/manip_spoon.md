---
title: Manipulation · Spoon
task_id: manip_spoon
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 628c408
  synced: '2026-09-28'
  instruction: 'Take hold of the spoon, put it in the cup and stir: move its head around a small circle, continuously, for the rest of the episode.'
  env_id: h1hand-spoon-v0
  robot: Unitree H1 with two Shadow hands (61 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_spoon.png
  category: Manipulation
  capability_class: C6 · standing bimanual manipulation
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 650, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'A weighted sum of four things: standing steadily, getting a hand to the spoon''s handle, keeping the spoon''s head inside the cup, and — the largest single term — keeping that head close to a target point that *travels around a small circle at a fixed rate, completing a revolution every 40 steps* (centred in the cup just above its floor, counter-clockwise seen from above, starting on the side away from the robot). The spoon starts on the table beside the cup, so the last two terms pay nothing until it is in the cup.'
  ends_early: The episode ends if the pelvis drops too low.
  zero_action_return: 7.48
  action_dim: 61
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the spoon's pose, not the moving target point, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

A five-fingered hand has to pick a thin spoon up from the table, bring it over the cup's rim into the cup, then stir in circles of 40 steps.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Blocked on the grasp: the spoon never reaches the cup in either mode. (@williamzhangNU)

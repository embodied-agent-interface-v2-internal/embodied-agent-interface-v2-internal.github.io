---
title: Manipulation · Truck
task_id: manip_truck
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: Unload the five loose packages from the truck (the wall of boxes behind them is fixed) and put them on the table — all of them.
  env_id: h1-truck-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_truck.png
  category: Manipulation
  capability_class: C9 · long-horizon multi-subtask
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 3000, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'Each step is your uprightness multiplied by a base amount plus three progress terms: how close the robot is to a package still on the truck, how close it is to a package it has picked up, and how close a picked-up package is to the table. On top of that, lifting a package off the truck and placing one on the table each pay a one-off bonus (taken back if a package comes off the table again), and delivering the last package pays a larger one and ends the episode. Uprightness is a factor, so lying down costs a large part of every step. The one-off bonuses are most of the bar but not all of it, so the rest has to come from the per-step terms before the last delivery.'
  zero_action_return: 544.42
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not where the packages are, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Unload the five loose packages from a truck about 3 m away, up a ramp, and put them on a table. Lifting a package and placing it pay one-off bonuses on top of the per-step terms, so standing well earns little of the bar.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Blocked on walking: the robot stands but never gets up the ramp to the packages. (@williamzhangNU)

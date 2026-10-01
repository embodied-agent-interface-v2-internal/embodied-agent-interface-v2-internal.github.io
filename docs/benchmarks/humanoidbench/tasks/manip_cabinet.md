---
title: Manipulation · Cabinet
task_id: manip_cabinet
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: 'Open the cabinet''s compartments in order: slide open the sliding door, then pull out the drawer, then open one of the double doors and lift the cube from the drawer into that compartment, then open the flip-up door and lift the cube that started behind the double doors (not the one you put there) up into it.'
  env_id: h1hand-cabinet-v0
  robot: Unitree H1 with two Shadow hands (61 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_cabinet.png
  category: Manipulation
  capability_class: C9 · long-horizon multi-subtask
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 2500, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: Only the compartment you are currently on is scored. Each step pays a small share for standing steadily and the bulk for progress on that one compartment; completing it pays a one-off bonus and moves the scoring on to the next. Those bonuses grow with how many you have finished, and together they are a large fraction of the bar — so stalling on the first compartment caps the episode well short of it, however cleanly that compartment is opened.
  ends_early: The episode ends once the last compartment is done.
  zero_action_return: 10.43
  action_dim: 61
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the cabinet's or the cubes' state, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Four compartments open in order: the sliding door, the drawer, one of the double doors (moving a cube from the drawer into it) and the flip-up door (lifting a second cube). Only the current compartment is scored, and the completion bonuses, which grow along the way, are a large part of the bar of 2500, so stalling early caps the episode well short of it.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Stops at the first compartments: limited mode opens the sliding door, but no later compartment counts in either mode and the cubes are never touched. (@williamzhangNU)

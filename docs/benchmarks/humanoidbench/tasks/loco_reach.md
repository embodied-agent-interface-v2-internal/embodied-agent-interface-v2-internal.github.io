---
title: Locomotion · Reach
task_id: loco_reach
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: Bring the robot's left hand to the target point and keep it there for as much of the episode as possible.
  env_id: h1-reach-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_loco
  scene_image: loco_reach.png
  category: Locomotion
  capability_class: C8 · mobile manipulation
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 12000, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'There are two tiers, both paid per step rather than once on arrival: a moderate amount while the hand is within about a metre of the target, and a considerably larger amount on top while it is within a few centimetres. Staying upright is paid every step as well, and fast joint motion costs a little. Reaching the loose tier and holding it for the whole episode falls short of the bar — a meaningful fraction of the episode has to be spent inside the tight one.'
  zero_action_return: 275.22
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not where its hand is, not the target's coordinates, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

The left hand must reach a target and stay within a few centimetres of it long enough, while the robot stays up for all 1000 steps; even holding the starting pose falls after about 100 steps.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Passes in both modes, limited only just (12008 against 12000): a centre-of-mass crouch from `spec()` and a stereo-camera target let the arm reach without falling. (@williamzhangNU)

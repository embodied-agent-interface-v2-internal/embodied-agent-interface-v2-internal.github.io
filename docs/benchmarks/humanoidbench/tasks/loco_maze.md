---
title: Locomotion · Maze
task_id: loco_maze
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: Walk the robot along the maze's corridors from checkpoint to checkpoint, in order, turning at each corner, without hitting the walls.
  env_id: h1-maze-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_loco
  scene_image: loco_maze.png
  category: Locomotion
  capability_class: C4 · navigation and passage
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 1200, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'Most of the bar is not accumulated, it is jumped to: reaching a checkpoint pays a one-off bonus, and the bonuses grow with how many you have already reached, so the later corners are worth far more than the first. Between checkpoints each step pays a small amount for posture, for moving in the current corridor''s direction (the speed target is on the order of 2 m/s) and for nearing the next checkpoint; touching a wall multiplies that per-step amount down to a fraction (the bonuses are not reduced). Walking correctly but never reaching a checkpoint leaves the episode below the bar.'
  ends_early: The episode ends early if the pelvis drops near the ground.
  zero_action_return: 120.59
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the maze, not where the checkpoints are, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

The robot walks the corridors of a maze through checkpoints at three corners. Most of the reward is the checkpoint bonuses, which grow along the way, so upright walking with turns comes before anything else.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Passes in unlimited mode with whole-body control walking a planned route through every checkpoint without touching a wall; limited mode never gets past the first stage. (@williamzhangNU)

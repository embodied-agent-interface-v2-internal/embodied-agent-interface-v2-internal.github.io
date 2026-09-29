---
title: Locomotion · Stair
task_id: loco_stair
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 628c408
  synced: '2026-09-28'
  instruction: Walk the robot forward over the stairs, up each flight and down the other side, without falling.
  env_id: h1-stair-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_loco
  scene_image: loco_stair.png
  category: Locomotion
  capability_class: C2 · constrained gait
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 700, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'The same three multiplied requirements as walking on the flat — forward speed (the target is on the order of 1 m/s), staying upright, low actuator force — with one change that matters: the height part of "upright" is measured as the head''s height above the feet, not above the ground, because the ground rises and falls under you and so cannot be the yardstick, and the torso tilt it accepts is looser than on the flat.'
  ends_early: 'Termination is also different: the episode ends only when the torso tips close to horizontal, rather than when it drops to a fixed height.'
  zero_action_return: 8.63
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the stairs' geometry, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

The robot walks up a flight of stairs and down again at about 1 m/s. Each step up asks for a foot lifted onto the next tread without losing balance, so a flat-ground gait is not enough.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Out of reach for now: no run builds a stepping gait, so the stairs are never reached. (@williamzhangNU)

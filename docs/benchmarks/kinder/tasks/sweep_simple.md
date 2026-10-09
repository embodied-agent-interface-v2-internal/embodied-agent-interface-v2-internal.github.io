---
title: Dynamic3D · Sweep simple
task_id: sweep_simple
benchmark: kinder

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Princeton-Robot-Planning-and-Learning/kindergarden @ 5b2dbac, as defined in our task definitions @ 670383c4e
  synced: '2026-10-06'
  instruction: Get the ten small dark-red cubes scattered on the floor into the translucent grey box marked on the floor at the end of the kitchen island (the free-standing white-topped counter) nearest the robot; a wiper stands on the floor next to the cubes. The task succeeds the moment all ten cubes' centres are inside that box.
  env_id: kinder/SweepSimple3D-o10-sweep_the_blocks_to_the_left_side_of_the_kitchen_island-v0
  robot: 'TidyBot++: holonomic base, Kinova Gen3 7-DoF arm, Robotiq 2F-85 gripper'
  scene_model: kinder_dynamic3d
  scene_image: sweep_simple.jpg
  category: Dynamic3D (MuJoCo)
  instance: 'seed 0: the scene KinDER builds from it, pinned by its digest'
  success_criteria:
    - 'KinDER''s own goal check (the environment''s `terminated`) fires within the episode:
      at most 1000 control steps (100 s at 10 Hz); no partial credit'
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the one episode reaches it (no reset in our runs); the service records
      the episode, and it replays to the same state'
  holding_still: does not reach the goal (checked by running an episode of zero actions)
  action_dim: 11
  actions: base pos and yaw (3), arm joints (7), gripper pos (1); each base and joint delta at most 0.1 a step
  state_dim: 243
  limited_mode: base RGB and wrist RGB-D cameras (480×640), base odometry, the arm's joint angles and velocities, the fingers' position. Not where any object or the goal region is, not the goal check before the episode ends
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Ten 2 cm cubes on the floor go into a box marked at the end of the kitchen island, 0.6 to 1.1 m away. The base passes over the cubes without moving them, so only the gripper or a standing T-shaped wiper can.

## Capability notes

<!-- Justify the labels in state/tasks/kinder.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- KinDER publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Passed by carrying each cube to the box rather than sweeping it: GPT-6.1 Sol in both modes, GPT-6 Luna (2026-10-04) in unlimited mode. Luna's 2026-10-06 runs failed both modes, with 3 of the 10 cubes in the box in unlimited mode. (@williamzhangNU)

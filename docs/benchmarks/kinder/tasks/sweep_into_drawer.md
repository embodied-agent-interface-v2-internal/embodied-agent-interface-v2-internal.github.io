---
title: Dynamic3D · Sweep into drawer
task_id: sweep_into_drawer
benchmark: kinder

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Princeton-Robot-Planning-and-Learning/kindergarden @ 5b2dbac, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: Get the five small dark-red cubes on top of the kitchen island into the middle drawer of the island's upper row of drawers, which starts closed; a wiper lies next to the cubes. The task succeeds the moment all five cubes' centres are inside that drawer, each at least 2.5 cm from the drawer's two side walls.
  env_id: kinder/SweepIntoDrawer3D-o5-v0
  robot: 'TidyBot++: holonomic base, Kinova Gen3 7-DoF arm, Robotiq 2F-85 gripper'
  scene_model: kinder_dynamic3d
  scene_image: sweep_into_drawer.jpg
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
  state_dim: 163
  limited_mode: base RGB and wrist RGB-D cameras (480×640), base odometry, the arm's joint angles and velocities, the fingers' position. Not where any object or the goal region is, not the goal check before the episode ends
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

The drawer starts closed, and its pull is a thin bar lower than the cubes on the counter: the robot has to catch the pull and open the drawer first, then get five small cubes into it (a wiper is there if it wants one). The KinDER paper's best method reaches 0.14 on this variant.

## Capability notes

<!-- Justify the labels in state/tasks/kinder.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- KinDER publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Both modes pass: limited mode pulled the drawer open by its handle and moved the cubes in one by one; unlimited mode swept them in with the wiper. (@williamzhangNU)

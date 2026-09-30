---
title: Dynamic3D · Sort blocks
task_id: sort_blocks
benchmark: kinder

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Princeton-Robot-Planning-and-Learning/kindergarden @ 5b2dbac, as defined in our task definitions @ 12fb1352
  synced: '2026-09-30'
  instruction: 'Sort the four small cubes clustered in the middle of the white table into the four open bins on it by colour: the dark-red cube into the red bin, the dark-green one into the green bin, the dark-blue one into the blue bin and the yellow one into the yellow bin. The task succeeds the moment every cube''s centre is inside the bin of its own colour, at least 1 cm from each of its inner walls, at least 1 cm below its rim and at least 0.5 cm above its floor.'
  env_id: kinder/SortClutteredBlocks3D-o4-sort_the_cluttered_blocks_into_bins-v0
  robot: 'TidyBot++: holonomic base, Kinova Gen3 7-DoF arm, Robotiq 2F-85 gripper'
  scene_model: kinder_dynamic3d
  scene_image: sort_blocks.jpg
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
  state_dim: 157
  limited_mode: base RGB and wrist RGB-D cameras (480×640), base odometry, the arm's joint angles and velocities, the fingers' position. Not where any object or the goal region is, not the goal check before the episode ends
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Four cubes sit 2 to 4 cm apart in a cluster, so grasping one disturbs its neighbours; the four bins are loose and slide or topple when an arm or a held cube touches them; and no single base position reaches every cube and bin. Four picks and places have to fit in 1000 steps.

## Capability notes

<!-- Justify the labels in state/tasks/kinder.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- KinDER publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Unlimited mode passes on the last of its 1000 steps, with a jaw angle chosen per cube and two base positions; limited mode picked up only two cubes, spent 429 steps placing one, and ran out of steps at 34 minutes. (@williamzhangNU)

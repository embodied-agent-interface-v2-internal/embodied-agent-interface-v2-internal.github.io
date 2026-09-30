---
title: Kinematic3D · Obstruction 3D
task_id: obstruction_3d
benchmark: kinder

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Princeton-Robot-Planning-and-Learning/kindergarden @ 5b2dbac, as defined in our task definitions @ 12fb1352
  synced: '2026-09-30'
  instruction: Put the purple block (target_block) on the thin purple pad on the wooden table (target_region); three of the four small red blocks (obstruction0, obstruction1, obstruction3) sit on the pad and the fourth (obstruction2) is elsewhere on the table. The task succeeds the moment the robot holds nothing, the block's underside is within 5 mm of the pad's top surface, and all four of its bottom corners lie within the pad's outline enlarged by 5 mm on every side.
  limited_instruction: Put the purple block on the thin purple pad on the wooden table; three of the four small red blocks sit on the pad and the fourth is elsewhere on the table. The task succeeds the moment the robot holds nothing, the block's underside is within 5 mm of the pad's top surface, and all four of its bottom corners lie within the pad's outline enlarged by 5 mm on every side.
  env_id: kinder/Obstruction3D-o4-v0
  robot: 'TidyBot++, kinematic: holonomic base, Kinova Gen3 7-DoF arm, gripper; a move that would collide is not carried out'
  scene_model: kinder_kinematic3d
  scene_image: obstruction_3d.jpg
  category: Kinematic3D (PyBullet)
  instance: 'seed 0: the scene KinDER builds from it, pinned by its digest'
  success_criteria:
    - 'KinDER''s own goal check (the environment''s `terminated`) fires within the episode:
      at most 3000 control steps; no partial credit'
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the one episode reaches it (no reset in our runs); the service records
      the episode, and it replays to the same state'
  holding_still: does not reach the goal (checked by running an episode of zero actions)
  action_dim: 11
  actions: bounded relative base position, rotation, and joint positions, and open / close; each base and joint delta at most 0.2 a step
  state_dim: 91
  limited_mode: base RGB and wrist RGB-D cameras (480×640), base odometry, the arm's joint angles, the fingers' position; a move that would collide comes back `blocked`. Not where any object or the goal region is, not the goal check before the episode ends
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Three small blocks sit on a pad barely larger than the block that must go there (7.8 × 5.6 cm for a 6.3 × 4.5 cm block), so the robot has to clear them first. The rules are kinematic: a move that would collide is not carried out, and a grasp fails if the fingers touch the pad or a neighbouring block.

## Capability notes

<!-- Justify the labels in state/tasks/kinder.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- KinDER publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Unlimited mode passes in 11 minutes by checking collisions offline before each grasp; limited mode sent one step per tool call, 163 of its 3000 in the hour, and its descents onto the pad, still crowded with red blocks, were refused ten times. (@williamzhangNU)

---
title: Kinematic3D · Packing 3D
task_id: packing_3d
benchmark: kinder

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Princeton-Robot-Planning-and-Learning/kindergarden @ 5b2dbac, as defined in our task definitions @ 12fb1352
  synced: '2026-09-30'
  instruction: 'Put the three flat green parts on the grey table, a square (part0) and two right triangles (part1, part2), each with a small red peg on top, into the purple tray in the middle of the table (rack). The task succeeds the moment the robot holds nothing and every part rests in the tray: its flat body (peg excluded) lies within the tray''s inner outline, its underside is within 5 mm of the tray floor''s height and its top is no more than 5 mm above the tray''s rim, it is within 5 mm of the tray without penetrating it, and no two parts (pegs included) overlap.'
  limited_instruction: 'Put the three flat green parts on the grey table, a square and two right triangles, each with a small red peg on top, into the purple tray in the middle of the table. The task succeeds the moment the robot holds nothing and every part rests in the tray: its flat body (peg excluded) lies within the tray''s inner outline, its underside is within 5 mm of the tray floor''s height and its top is no more than 5 mm above the tray''s rim, it is within 5 mm of the tray without penetrating it, and no two parts (pegs included) overlap.'
  env_id: kinder/Packing3D-p3-v0
  robot: 'TidyBot++, kinematic: holonomic base, Kinova Gen3 7-DoF arm, gripper; a move that would collide is not carried out'
  scene_model: kinder_kinematic3d
  scene_image: packing_3d.jpg
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
  state_dim: 67
  limited_mode: base RGB and wrist RGB-D cameras (480×640), base odometry, the arm's joint angles, the fingers' position; a move that would collide comes back `blocked`. Not where any object or the goal region is, not the goal check before the episode ends
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

A square and two right triangles go into a tray, flat, inside its outline and without overlapping. The hard part is letting go: a held part is released only within 5 mm of a surface that supports it, a move that would collide is not carried out, and whether a part sits right can only be judged from the cameras.

## Capability notes

<!-- Justify the labels in state/tasks/kinder.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- KinDER publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Unlimited mode passes in 9 minutes by reading the parts' heights and supporting surfaces whenever a release failed; limited mode got all three parts into the tray only after the square took 30 minutes to place, and the goal check had not accepted them when its hour ran out at step 764. (@williamzhangNU)

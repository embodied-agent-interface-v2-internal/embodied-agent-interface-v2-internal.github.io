---
title: Dynamic3D · Constrained cupboard
task_id: constrained_cupboard
benchmark: kinder

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Princeton-Robot-Planning-and-Learning/kindergarden @ 5b2dbac, as defined in our task definitions @ 12fb1352
  synced: '2026-09-30'
  instruction: 'Put the six brown rods lying on the floor (30 cm long) into the six 40 cm-tall compartments of the row of eleven narrow cupboards standing side by side, one rod each, as the state names pair them: rod cuboid_i into cupboard cupboard_i for i = 0 to 5, whose tall compartment is the upper one in cupboard_0 to cupboard_2 and the lower one in cupboard_3 to cupboard_5. The task succeeds the moment every rod''s centre is inside its compartment: above that compartment''s shelf, below the shelf over it, and within the cupboard''s 10 cm width and 30 cm depth.'
  limited_instruction: 'Put the six brown rods lying on the floor (30 cm long) into the row of eleven narrow cupboards standing side by side ahead of the robot, one rod each, each into a cupboard''s 40 cm-tall compartment: taking the rods in order of their distance from where the centre of the robot''s base starts, nearest first, they go into the 11th, 5th, 2nd, 8th, 4th and 1st cupboard of the row, counted from the robot''s left as it faces the row at the start. The task succeeds the moment every rod''s centre is inside its compartment: above that compartment''s shelf, below the shelf over it, and within the cupboard''s 10 cm width and 30 cm depth.'
  env_id: kinder/ConstrainedCupboard3D-o6-v0
  robot: 'TidyBot++: holonomic base, Kinova Gen3 7-DoF arm, Robotiq 2F-85 gripper'
  scene_model: kinder_dynamic3d
  scene_image: constrained_cupboard.jpg
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
  state_dim: 195
  limited_mode: base RGB and wrist RGB-D cameras (480×640), base odometry, the arm's joint angles and velocities, the fingers' position. Not where any object or the goal region is, not the goal check before the episode ends
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Six 30 cm rods go into six compartments 10 cm wide and 30 cm deep, each into the one it is owed. Gripped in the middle, the wrist reaches the opening before the rod is in, so each rod has to be held by one end and turned to slide in along the cupboard's depth, six times within 1000 steps.

## Capability notes

<!-- Justify the labels in state/tasks/kinder.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- KinDER publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Unlimited mode passes only in its last minute, holding each rod by one end and fitting all six by step 935; limited mode's one episode lost 340 steps to two wasted arm motions and released its only rod outside the cupboard. (@williamzhangNU)

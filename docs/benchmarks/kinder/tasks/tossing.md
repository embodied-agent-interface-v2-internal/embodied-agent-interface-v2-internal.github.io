---
title: Dynamic3D · Tossing
task_id: tossing
benchmark: kinder

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Princeton-Robot-Planning-and-Learning/kindergarden @ 5b2dbac, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: Get the green cube lying on the floor into the yellow bin on the far side of the low wall that runs across the room. The task succeeds the moment the cube's centre is inside the bin's goal region, the translucent green box marked in the bin.
  env_id: kinder/Tossing3D-o1-v0
  robot: 'TidyBot++: holonomic base, Kinova Gen3 7-DoF arm, Robotiq 2F-85 gripper'
  scene_model: kinder_dynamic3d
  scene_image: tossing.jpg
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
  action_dim: 18
  actions: base pos and yaw (3), arm joints (7), gripper pos (1), and arm joint velocity targets (7, rad/s); each base and joint delta at most 0.1 a step
  state_dim: 61
  limited_mode: base RGB and wrist RGB-D cameras (480×640), base odometry, the arm's joint angles and velocities, the fingers' position. Not where any object or the goal region is, not the goal check before the episode ends
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

A low wall runs across the room and stops the base, so the robot has to stay on its side and send the cube over the wall into a bin about 2 m away with its arm. It first has to find where the bin is, then get the release speed and the moment it opens the gripper right: a little off, and the cube hits the bin's rim.

## Capability notes

<!-- Justify the labels in state/tasks/kinder.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- KinDER publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Unlimited mode passes with a throw found by searching thousands of candidates from an exact snapshot before release; limited mode found the bin with wrist depth and replayed a scripted throw for 43 episodes, tuning it by computed trajectories rather than by looking, and its late throws landed short of the bin. (@williamzhangNU)

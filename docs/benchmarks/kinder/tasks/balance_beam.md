---
title: Dynamic3D · Balance beam
task_id: balance_beam
benchmark: kinder

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Princeton-Robot-Planning-and-Learning/kindergarden @ 5b2dbac, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: Put the two small green cubes and the larger dark-red cube on the seesaw so that it balances. The task succeeds the moment all three cubes' centres are inside the translucent green region marked on the seesaw's beam and the beam is within 5° of level.
  env_id: kinder/BalanceBeam3D-o3-v0
  robot: 'TidyBot++: holonomic base, Kinova Gen3 7-DoF arm, Robotiq 2F-85 gripper'
  scene_model: kinder_dynamic3d
  scene_image: balance_beam.jpg
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
  state_dim: 86
  limited_mode: base RGB and wrist RGB-D cameras (480×640), base odometry, the arm's joint angles and velocities, the fingers' position. Not where any object or the goal region is, not the goal check before the episode ends
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Two light cubes and one twice as heavy go onto a narrow seesaw beam, all inside its marked region, and the beam must end within 5° of level. Getting them onto the beam is not enough: they have to balance about the pivot.

## Capability notes

<!-- Justify the labels in state/tasks/kinder.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- KinDER publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Unlimited mode passes by reading the seesaw's pose and balancing the moments about the pivot; limited mode grasped all three cubes on the first try and replayed its pick script with four placement layouts over 22 episodes, but never measured the beam's tilt, so it had nothing to steer the placement by. (@williamzhangNU)

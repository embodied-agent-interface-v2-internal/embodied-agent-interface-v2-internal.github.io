---
title: Dynamic3D · Scoop pour
task_id: scoop_pour
benchmark: kinder

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Princeton-Robot-Planning-and-Learning/kindergarden @ 5b2dbac, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: Move all 30 small dark-red cubes from the yellow bin into the green bin; a scoop is in the scene. The task succeeds the moment every cube's centre is inside the green bin, at least 1 cm from each of its inner walls and at least 0.5 cm below its rim.
  env_id: kinder/ScoopPour3D-o30-v0
  robot: 'TidyBot++: holonomic base, Kinova Gen3 7-DoF arm, Robotiq 2F-85 gripper'
  scene_model: kinder_dynamic3d
  scene_image: scoop_pour.jpg
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
  state_dim: 595
  limited_mode: base RGB and wrist RGB-D cameras (480×640), base odometry, the arm's joint angles and velocities, the fingers' position. Not where any object or the goal region is, not the goal check before the episode ends
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Thirty small cubes go from the yellow bin into the green one, each over the bin walls and inside the green bin's margins, on a counter about 0.46 m high. A small scoop is there; loading it is a contact problem, not a grasp.

## Capability notes

<!-- Justify the labels in state/tasks/kinder.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- KinDER publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Both modes pass by pouring rather than scooping: limited mode tipped the yellow bin over the green one, unlimited mode moved the green bin to the floor and tipped the yellow bin into it. (@williamzhangNU)

---
title: Ball Onto Tower
task_id: ball_onto_tower
benchmark: robowits

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/UMass-Embodied-AGI/RoboWits @ 9cc30ae
  synced: '2026-09-21'
  instruction: Place the ball stably on top of the tower.
  scene_model: robowits_table
  registry_id: robowits/17-ball-onto-tower-v0
  task_number: 17
  source_file: gs_gym/envs/robowits/17_ball_onto_tower.py
  env_class: BallOntoTowerEnv
  success_criteria:
    - Ball is stable (low velocity)
    - Ball is on top of the tower base (XY projection over base footprint)
    - Ball center is above the top of the tower base
    - Ball is not being held by either gripper
  objects: [ball, large ring, medium ring, small ring, tower base]
  object_materials: [rigid]
  eval_scenes: 50
  mutations: 8
  blenderkit_assets: 1
  episode_steps_default: 200
  control_mode_default: EE_ABS
  oracle_video: https://umass-embodied-agi.github.io/RoboWits/static/videos/17.mp4
  oracle_video_source: https://umass-embodied-agi.github.io/RoboWits/
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/robowits.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- RoboWits ships no oracle demonstrations: the reference solutions are ours,
     written against the task's own success predicate. If this task has one,
     say whether the trajectory is clean and what it relies on. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

---
title: Pinch Card
task_id: pinch_card
benchmark: robowits

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/UMass-Embodied-AGI/RoboWits @ 9cc30ae
  synced: '2026-09-21'
  instruction: Pick the bank card up from the 'small table' surface.
  scene_model: robowits_table
  registry_id: robowits/04-pinch-card-v0
  task_number: 4
  source_file: gs_gym/envs/robowits/04_pinch_card.py
  env_class: PinchCardEnv
  success_criteria:
    - Bank card's 2D footprint overlaps target area by at least 50%
    - Bank card is resting on the target surface (not floating)
    - Bank card is not being held by either gripper
  objects: [bank card, eraser, small table, target area, target cube]
  object_materials: [rigid]
  eval_scenes: 50
  mutations: 5
  blenderkit_assets: 3
  episode_steps_default: 200
  control_mode_default: EE_ABS
  oracle_video: https://umass-embodied-agi.github.io/RoboWits/static/videos/04.mp4
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

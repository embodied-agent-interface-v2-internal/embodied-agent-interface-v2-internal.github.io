---
title: Stand Bulb
task_id: stand_bulb
benchmark: robowits

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/UMass-Embodied-AGI/RoboWits @ 9cc30ae
  synced: '2026-09-21'
  instruction: Stand the tall object with curved bottom stably within the green target area.
  scene_model: robowits_table
  registry_id: robowits/16-stand-bulb-v0
  task_number: 16
  source_file: gs_gym/envs/robowits/16_stand_bulb.py
  env_class: StandBulbEnv
  success_criteria:
    - Tall object overlaps target patch by at least 80%
    - Tall object is upright (Z extent dominates XY extents)
    - Tall object is stable (low velocity)
    - Objects remain within table bounds
    - Tall object is not being held
  objects: [stabilizing ring, tall object with curved bottom, target patch]
  object_materials: [rigid]
  eval_scenes: 50
  mutations: 7
  blenderkit_assets: 2
  episode_steps_default: 200
  control_mode_default: EE_ABS
  oracle_video: https://umass-embodied-agi.github.io/RoboWits/static/videos/16.mp4
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

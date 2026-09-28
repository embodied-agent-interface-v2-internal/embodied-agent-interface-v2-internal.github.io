---
title: Water Into Mug
task_id: water_into_mug
benchmark: robowits

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/UMass-Embodied-AGI/RoboWits @ 9cc30ae
  synced: '2026-09-21'
  instruction: Collect water in the mug without moving the pitcher.
  scene_model: robowits_table
  registry_id: robowits/25-water-into-mug-v0
  task_number: 25
  source_file: gs_gym/envs/robowits/25_water_into_mug.py
  env_class: WaterIntoMugEnv
  success_criteria:
    - At least 1 water particle is inside the mug's interior (circular proxy, z within
      mug bounds)
    - Mug remains within table XY bounds
    - Mug is resting on the table (not floating)
    - At least 70% of water particles remain over the table
  objects: [heavy_large_object, mug, pitcher]
  object_materials: [rigid, sph]
  eval_scenes: 50
  mutations: 7
  blenderkit_assets: 1
  episode_steps_default: 200
  control_mode_default: EE_ABS
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

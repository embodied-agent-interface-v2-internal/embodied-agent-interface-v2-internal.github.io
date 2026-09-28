---
title: Stabilize Bottle
task_id: stabilize_bottle
benchmark: robowits

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/UMass-Embodied-AGI/RoboWits @ 9cc30ae
  synced: '2026-09-21'
  instruction: Make the tube stand upright in the bowl without falling for a short time.
  scene_model: robowits_table
  registry_id: robowits/22-stabilize-bottle-v0
  task_number: 22
  source_file: gs_gym/envs/robowits/22_stabilize_bottle.py
  env_class: StabilizeBottleEnv
  success_criteria:
    - Tube's base is inside the bowl's footprint
    - Tube is upright (tilt <= 5 degrees from vertical)
    - Tube is stationary (low velocity)
    - Objects remain within table bounds
  objects: [bowl, sand_container, tube]
  object_materials: [mpm, rigid]
  eval_scenes: 50
  mutations: 5
  blenderkit_assets: 3
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

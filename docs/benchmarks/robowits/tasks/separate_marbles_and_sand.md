---
title: Separate Marbles And Sand
task_id: separate_marbles_and_sand
benchmark: robowits

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/UMass-Embodied-AGI/RoboWits @ 9cc30ae
  synced: '2026-09-21'
  instruction: Remove sand from the jar and keep the marbles in the jar.
  scene_model: robowits_table
  registry_id: robowits/15-separate-marbles-and-sand-v0
  task_number: 15
  source_file: gs_gym/envs/robowits/15_separate_marbles_and_sand.py
  env_class: SeparateMarblesAndSandEnv
  success_criteria:
    - All five marbles are inside the jar's 3D AABB
    - At least 80% of sand particles are outside the jar's 3D AABB
  objects: [bowl, colander, jar, marble 1, marble 2, marble 3, marble 4, marble 5]
  object_materials: [mpm, rigid]
  eval_scenes: 50
  mutations: 4
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

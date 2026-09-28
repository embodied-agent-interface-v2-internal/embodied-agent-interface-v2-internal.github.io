---
title: Stack Cubes
task_id: stack_cubes
benchmark: robowits

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/UMass-Embodied-AGI/RoboWits @ 9cc30ae
  synced: '2026-09-21'
  instruction: Build a stable two-layer stack so the red cube's center is above the green colored dot.
  scene_model: robowits_table
  registry_id: robowits/14-stack-cubes-v0
  task_number: 14
  source_file: gs_gym/envs/robowits/14_stack_cubes.py
  env_class: StackCubesEnv
  success_criteria:
    - Base cubes are on the table and touching with >= 50% face overlap
    - Apex cube sits on top of base cubes
    - Apex cube center is within tolerance of target marker
    - Apex-target overlap >= 20%
  objects: [apex cube, apex target, base cube 1, base cube 2]
  object_materials: [rigid]
  eval_scenes: 50
  mutations: 5
  episode_steps_default: 200
  control_mode_default: EE_ABS
  oracle_video: https://umass-embodied-agi.github.io/RoboWits/static/videos/14.mp4
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

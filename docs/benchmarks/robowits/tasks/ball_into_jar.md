---
title: Ball Into Jar
task_id: ball_into_jar
benchmark: robowits

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/UMass-Embodied-AGI/RoboWits @ 9cc30ae
  synced: '2026-09-21'
  instruction: Put the foam ball fully into the jar.
  scene_model: robowits_table
  registry_id: robowits/20-ball-into-jar-v0
  task_number: 20
  source_file: gs_gym/envs/robowits/20_ball_into_jar.py
  env_class: BallIntoJarEnv
  success_criteria:
    - 'At least 90% of foam ball particles lie inside the glass jar''s axis-aligned bounding
      box (rigid fallback: the ball''s AABB is fully contained in the jar''s)'
    - Objects haven't fallen off the table
  objects: [glass jar]
  object_materials: [mpm, rigid]
  eval_scenes: 50
  mutations: 5
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

---
title: Cover With Lid
task_id: cover_with_lid
benchmark: robowits

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/UMass-Embodied-AGI/RoboWits @ 9cc30ae
  synced: '2026-09-21'
  instruction: Cover the pot precisely using one lid.
  scene_model: robowits_table
  registry_id: robowits/13-cover-with-lid-v0
  task_number: 13
  source_file: gs_gym/envs/robowits/13_cover_with_lid.py
  env_class: CoverWithLidEnv
  success_criteria:
    - Exactly one lid is above the pot
    - Lid overlaps pot by at least 80%
    - Lid size is appropriate (85%-140% of pot area)
  objects: [lid large, lid medium, pot without lid, small lid]
  object_materials: [rigid]
  eval_scenes: 50
  mutations: 5
  blenderkit_assets: 2
  episode_steps_default: 200
  control_mode_default: EE_ABS
  oracle_video: https://umass-embodied-agi.github.io/RoboWits/static/videos/13.mp4
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

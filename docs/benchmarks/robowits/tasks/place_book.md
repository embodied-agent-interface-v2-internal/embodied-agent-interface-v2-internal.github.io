---
title: Place Book
task_id: place_book
benchmark: robowits

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/UMass-Embodied-AGI/RoboWits @ 9cc30ae
  synced: '2026-09-21'
  instruction: Move the 'thin book' onto the 'blue target mat' without moving the heavy block from its place.
  scene_model: robowits_table
  registry_id: robowits/23-place-book-v0
  task_number: 23
  source_file: gs_gym/envs/robowits/23_place_book.py
  env_class: PlaceBookEnv
  success_criteria:
    - Thin book is on the blue target mat (95% overlap)
    - Heavy block remains in place (displacement <= 10mm)
    - Book is free of heavy block (no overlap)
    - Objects remain within table bounds
  objects:
    - board
    - book
    - book on shelf 1
    - book on shelf 2
    - book on shelf 3
    - book on shelf 4
    - book on shelf 5
    - shelf back
    - shelf left
    - shelf right
    - shelf top
  object_materials: [rigid]
  eval_scenes: 50
  mutations: 5
  blenderkit_assets: 2
  episode_steps_default: 200
  control_mode_default: EE_ABS
  oracle_video: https://umass-embodied-agi.github.io/RoboWits/static/videos/23.mp4
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

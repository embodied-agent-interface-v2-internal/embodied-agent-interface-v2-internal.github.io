---
title: Smaller Object Butter In Bin
task_id: smaller_object_butter_in_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Place the smaller object in the grey bin.
  scene_model: butter_raisin_box_grey_bin
  scene_usda: butter_raisin_box_grey_bin.usda
  scene_image: butter_raisin_box_grey_bin.jpg
  env_class: SmallerObjectButterInBinTask
  task_name: SmallerObjectButterInBinTask
  source_file: robolab/tasks/benchmark/smaller_object.py
  episode_length_s: 30
  attributes: [size]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object: butter
    container: grey_bin
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [butter, grey_bin, raisin_box]
  instruction_variants:
    vague: Put one in the bin
    specific: Compare the objects on the table, identify the smaller one, and place it
      in the grey bin
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/robolab.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- RoboLab ships no per-task oracle video; the row shows its scene instead.
     If we have recorded a reference solution, say whether the trajectory is
     clean and what it relies on. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

---
title: Mustard In Left Bin
task_id: mustard_in_left_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the mustard in the left bin
  scene_model: two_bin
  scene_usda: two_bin.usda
  scene_image: two_bin.jpg
  env_class: MustardInLeftBinTask
  task_name: MustardInLeftBinTask
  source_file: robolab/tasks/benchmark/mustard_in_left_bin.py
  episode_length_s: 30
  attributes: [spatial]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object: mustard
    container: grey_bin_left
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [mustard, grey_bin_right, grey_bin_left]
  instruction_variants:
    vague: Use the left bin for mustard
    specific: Pick up the mustard bottle and place it in the bin on the left side
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

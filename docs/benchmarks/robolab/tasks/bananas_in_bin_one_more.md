---
title: Bananas In Bin One More
task_id: bananas_in_bin_one_more
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put one (1) more bananas in the grey bin.
  scene_model: bananas_5_grey_bin
  scene_usda: bananas_5_grey_bin.usda
  scene_image: bananas_5_grey_bin.jpg
  env_class: BananasInBinOneMoreTask
  task_name: BananasInBinOneMoreTask
  source_file: robolab/tasks/benchmark/bananas_in_bin_one_more.py
  episode_length_s: 60
  attributes: [semantics, counting]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - banana
    - banana_01
    - banana_03
    container: grey_bin
    logical: choose
    K: 1
    require_gripper_detached: true
    require_contact_with: false
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [banana, banana_01, banana_02, banana_03, banana_04, grey_bin]
  instruction_variants:
    vague: Add a banana to the bin
    specific: Pick up one additional banana and place it in the grey bin alongside the
      ones already there
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

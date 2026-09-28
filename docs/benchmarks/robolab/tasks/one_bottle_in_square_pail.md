---
title: One Bottle In Square Pail
task_id: one_bottle_in_square_pail
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put any white plastic bottle in the square pail
  scene_model: shelf_with_cleaning_products
  scene_usda: shelf_with_cleaning_products.usda
  scene_image: shelf_with_cleaning_products.jpg
  env_class: OneBottleInSquarePailTask
  task_name: OneBottleInSquarePailTask
  source_file: robolab/tasks/benchmark/one_bottle_in_square_pail.py
  episode_length_s: 60
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - whitepackerbottle_a01
    - whitepackerbottle_a02
    - whitepackerbottle_a03
    container: squarepail_a01
    logical: any
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - squarepail_a01
    - whitepackerbottle_a01
    - whitepackerbottle_a02
    - utilityjug_a01
    - utilityjug_a02
    - plasticpail_a02
    - whitepackerbottle_a03
    - large_storage_rack
  instruction_variants:
    vague: Put a bottle in the square pail
    specific: Pick up one of the three white plastic bottles and place it inside the square
      pail
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

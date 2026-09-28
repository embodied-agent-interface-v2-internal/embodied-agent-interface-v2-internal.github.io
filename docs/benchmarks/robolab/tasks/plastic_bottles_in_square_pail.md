---
title: Plastic Bottles In Square Pail
task_id: plastic_bottles_in_square_pail
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put all the small plastic bottles in the square pail
  scene_model: shelf_with_cleaning_products
  scene_usda: shelf_with_cleaning_products.usda
  scene_image: shelf_with_cleaning_products.jpg
  env_class: PlasticBottlesInSquarePailTask
  task_name: PlasticBottlesInSquarePailTask
  source_file: robolab/tasks/benchmark/bottles_on_shelf_task.py
  episode_length_s: 180
  attributes: [semantics, sorting, size]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - whitepackerbottle_a01
    - whitepackerbottle_a02
    - whitepackerbottle_a03
    container: squarepail_a01
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - large_storage_rack
    - whitepackerbottle_a01
    - whitepackerbottle_a02
    - utilityjug_a01
    - utilityjug_a02
    - squarepail_a01
    - plasticpail_a02
    - whitepackerbottle_a03
  instruction_variants:
    vague: Clean up small bottles in the square pail
    specific: Pick up the three small plastic bottles and place them inside the square
      shaped pail
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

---
title: Pick Orange Object
task_id: pick_orange_object
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Pick up the orange measuring cup
  scene_model: cooking_table
  scene_usda: cooking_table.usda
  scene_image: cooking_table.jpg
  env_class: PickOrangeObjectTask
  task_name: PickOrangeObjectTask
  source_file: robolab/tasks/benchmark/cooking_orange_object.py
  episode_length_s: 60
  attributes: [color]
  difficulty_label: simple
  success_predicate: object_picked_up
  success_params:
    object: measuring_cups_1
    surface: table
  subtasks: 1
  subtask_predicates: [Subtask]
  objects:
    - redonion
    - serving_bowl
    - clay_plates
    - wooden_spoons
    - spatula
    - storage_box
    - tomato_sauce_can
    - measuring_cups_1
    - pink_spaghetti_spoon
    - spoon_1
    - green_serving_spoon
    - storage_box_01
    - ladle
    - wooden_bowl
    - potato_masher
  instruction_variants:
    vague: Pick up orange-colored thing
    specific: Identify and pick up the orange-colored object from the cooking area
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

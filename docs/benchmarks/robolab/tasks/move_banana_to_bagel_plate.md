---
title: Move Banana To Bagel Plate
task_id: move_banana_to_bagel_plate
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Move the bananas to the bagel plate
  scene_model: breakfast_table
  scene_usda: breakfast_table.usda
  scene_image: breakfast_table.jpg
  env_class: MoveBananaToBagelPlateTask
  task_name: MoveBananaToBagelPlateTask
  source_file: robolab/tasks/benchmark/move_banana_to_bagel_plate.py
  episode_length_s: 90
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_on_top
  success_params:
    object:
    - banana
    - banana_01
    reference_object: plate_small
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place_on_surface]
  objects:
    - bowl
    - banana
    - bagel_07
    - coffee_can
    - banana_01
    - yogurt_cup
    - coffee_pot
    - ceramic_mug
    - pitcher
    - fork_big
    - spoon_big
    - apple_01
    - orange2
    - milk_carton
    - orange_juice_carton
    - bagel_01
    - bagel_02
    - plate_small
    - plate_large
  instruction_variants:
    vague: Put the bananas with the bagels
    specific: Pick up the yellow bananas and transfer them onto the plate containing the
      bagels
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

---
title: Food Packing1 Boxes
task_id: food_packing1_boxes
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Pack boxed foods into the bin
  scene_model: foodpacking_1bin_1box_1can
  scene_usda: foodpacking_1bin_1box_1can.usda
  scene_image: foodpacking_1bin_1box_1can.jpg
  env_class: FoodPacking1BoxesTask
  task_name: FoodPacking1BoxesTask
  source_file: robolab/tasks/benchmark/foodpacking_1bin_1box.py
  episode_length_s: 60
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - cheez_it
    container: bin_a06
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [bin_a06, cheez_it, mustard, tomato_soup_can]
  instruction_variants:
    vague: Pack boxes
    specific: Pick up the boxed food item and place it inside the bin
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

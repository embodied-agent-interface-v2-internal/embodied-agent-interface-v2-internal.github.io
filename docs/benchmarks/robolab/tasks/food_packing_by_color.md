---
title: Food Packing By Color
task_id: food_packing_by_color
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Pack yellow objects in right container and blue object in the left container
  scene_model: food_packing
  scene_usda: food_packing.usda
  scene_image: food_packing.jpg
  env_class: FoodPackingByColorTask
  task_name: FoodPackingByColorTask
  source_file: robolab/tasks/benchmark/food_packing_by_color_task.py
  episode_length_s: 120
  attributes: [spatial, sorting, color]
  difficulty_label: moderate
  success_predicate: object_groups_in_containers
  subtasks: 2
  subtask_predicates: [pick_and_place]
  objects:
    - bin_a06
    - cheez_it
    - chocolate_pudding
    - coffee_can
    - mustard
    - spam_can
    - sugar_box
    - tomato_soup_can
    - bin_b03
  instruction_variants:
    vague: Sort things by color
    specific: Pick up the yellow can and place it in the right container, then pick up
      the blue object and place it in the left container
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

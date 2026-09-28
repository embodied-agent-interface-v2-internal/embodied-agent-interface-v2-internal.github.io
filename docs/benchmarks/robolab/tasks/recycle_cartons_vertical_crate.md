---
title: Recycle Cartons Vertical Crate
task_id: recycle_cartons_vertical_crate
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the cartons that can be recycled in the vertical crate
  scene_model: cartons_in_vertical_crate
  scene_usda: cartons_in_vertical_crate.usda
  scene_image: cartons_in_vertical_crate.jpg
  env_class: RecycleCartonsVerticalCrateTask
  task_name: RecycleCartonsVerticalCrateTask
  source_file: robolab/tasks/benchmark/recycle_cartons_vertical_crate.py
  episode_length_s: 90
  attributes: [semantics, spatial]
  difficulty_label: simple
  success_predicate: object_inside
  success_params:
    object:
    - milk_carton
    - orange_juice_carton
    container: container_a01
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - container_a01
    - milk_carton
    - orange_juice_carton
    - alphabet_soup_can
    - smartphone
    - mayonnaise_bottle
    - ketchup_bottle
    - mug
  instruction_variants:
    vague: Recycle the cartons in the crate
    specific: Pick up the food cartons that can be recycled and place them into the vertical
      crate in the center of the table
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

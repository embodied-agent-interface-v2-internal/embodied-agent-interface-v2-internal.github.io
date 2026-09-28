---
title: Recycle Cartons On Box
task_id: recycle_cartons_on_box
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the cartons that can be recycled on the box
  scene_model: cartons_on_box
  scene_usda: cartons_on_box.usda
  scene_image: cartons_on_box.jpg
  env_class: RecycleCartonsOnBoxTask
  task_name: RecycleCartonsOnBoxTask
  source_file: robolab/tasks/benchmark/recycle_cartons_on_box.py
  episode_length_s: 90
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - milk_carton
    - orange_juice_carton
    container: cubebox_a02
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place_on_surface]
  objects:
    - cubebox_a02
    - milk_carton
    - orange_juice_carton
    - alphabet_soup_can
    - smartphone
    - mayonnaise_bottle
    - ketchup_bottle
    - mug
  instruction_variants:
    vague: Put the carton recyclables on the box
    specific: Identify the food cartons that can be recycled and put them on top of the
      brown square box.
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

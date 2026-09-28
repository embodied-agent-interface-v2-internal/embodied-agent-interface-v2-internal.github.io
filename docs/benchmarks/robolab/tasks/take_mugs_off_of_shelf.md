---
title: Take Mugs Off Of Shelf
task_id: take_mugs_off_of_shelf
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Take the mugs off the shelf
  scene_model: mugs_on_shelf
  scene_usda: mugs_on_shelf.usda
  scene_image: mugs_on_shelf.jpg
  env_class: TakeMugsOffOfShelfTask
  task_name: TakeMugsOffOfShelfTask
  source_file: robolab/tasks/benchmark/take_mugs_off_of_shelf.py
  episode_length_s: 180
  attributes: [semantics, affordance]
  difficulty_label: simple
  success_predicate: object_outside_of_and_on_surface
  success_params:
    object:
    - ceramic_mug
    - mug
    container: rack_l04
    surface: table
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place_on_surface]
  objects: [ceramic_mug, mug, rack_l04, serving_bowl, utilityjug_a01]
  instruction_variants:
    vague: Clear the shelf
    specific: Remove each mug from the second level of the shelf and place them on the
      table below
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

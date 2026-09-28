---
title: Take Spatula Off Shelf
task_id: take_spatula_off_shelf
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Take the spatula off the shelf and put it on the table
  scene_model: wire_shelf_mugs_plate_spatula
  scene_usda: wire_shelf_mugs_plate_spatula.usda
  scene_image: wire_shelf_mugs_plate_spatula.jpg
  env_class: TakeSpatulaOffShelfTask
  task_name: TakeSpatulaOffShelfTask
  source_file: robolab/tasks/benchmark/take_spatula_off_shelf.py
  episode_length_s: 60
  attributes: [affordance, spatial]
  difficulty_label: moderate
  success_predicate: object_outside_of_and_on_surface
  success_params:
    object:
    - spatula_01
    container: wireshelving_a01
    surface: table
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place_on_surface]
  objects:
    - wireshelving_a01
    - spatula_01
    - plate_small
    - fork_big
    - fork_small
    - ceramic_mug
    - mug
    - mug_01
  instruction_variants:
    vague: Take the spatula off the shelf
    specific: Reach up and remove the spatula from the shelf, then place it flat on the
      table surface
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

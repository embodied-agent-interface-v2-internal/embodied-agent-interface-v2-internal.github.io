---
title: Banana On Plate
task_id: banana_on_plate
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Pick up the banana and put it on the plate
  scene_model: bagel_plate_banana_bowl
  scene_usda: bagel_plate_banana_bowl.usda
  scene_image: bagel_plate_banana_bowl.jpg
  env_class: BananaOnPlateTask
  task_name: BananaOnPlateTask
  source_file: robolab/tasks/benchmark/banana_on_plate_task.py
  episode_length_s: 40
  difficulty_label: simple
  success_predicate: object_on_top
  success_params:
    object:
    - banana
    reference_object: plate_large
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place_on_surface]
  objects: [bagel_00, bagel_06, banana, bowl, plate_large]
  instruction_variants:
    vague: Put fruit on the dish
    specific: Pick up the yellow banana and place it flat on the white ceramic plate
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

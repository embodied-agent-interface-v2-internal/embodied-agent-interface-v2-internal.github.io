---
title: Fruits Green Limes On Plate
task_id: fruits_green_limes_on_plate
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put all the green fruit on the plate
  scene_model: fruits_out_of_basket
  scene_usda: fruits_out_of_basket.usda
  scene_image: fruits_out_of_basket.jpg
  env_class: FruitsGreenLimesOnPlateTask
  task_name: FruitsGreenLimesOnPlateTask
  source_file: robolab/tasks/benchmark/fruits_green_limes_on_plate.py
  episode_length_s: 90
  attributes: [color]
  difficulty_label: simple
  success_predicate: object_on_top
  success_params:
    object:
    - lime01
    - lime01_01
    reference_object: clay_plates
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place_on_surface]
  objects:
    - lemon_01
    - lemon_02
    - lime01
    - lime01_01
    - orange_01
    - orange_02
    - pomegranate01
    - pumpkinlarge
    - pumpkinsmall
    - redonion
    - serving_bowl
    - clay_plates
    - wooden_spoons
    - spatula
    - storage_box
  instruction_variants:
    vague: Plate green fruits
    specific: Put all green limes on the table and place them on the flat, beige colored
      plate
  oracle_video: https://research.nvidia.com/labs/srl/projects/robolab/static/videos/Put_all_the_green_fruit_on_the_plate_2_viewport_3X.mp4
  oracle_video_instruction: default
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

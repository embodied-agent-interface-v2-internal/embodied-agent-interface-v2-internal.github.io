---
title: Cooking Clear Plate
task_id: cooking_clear_plate
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the two measuring cups outside of the plate
  scene_model: cooking_table
  scene_usda: cooking_table.usda
  scene_image: cooking_table.jpg
  env_class: CookingClearPlateTask
  task_name: CookingClearPlateTask
  source_file: robolab/tasks/benchmark/cooking_clear_plate_specific.py
  episode_length_s: 180
  attributes: [color, sorting]
  difficulty_label: simple
  success_predicate: object_outside_of
  success_params:
    object:
    - spoon_1
    - measuring_cups_1
    container: clay_plates
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place_on_surface]
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
    vague: Clear the plate
    specific: Pick up the orange measuring cup and the blue measuring cup from the plate
      and place each on the table surface
  oracle_video: https://research.nvidia.com/labs/srl/projects/robolab/static/videos/captioned/Put_the_orange_measuring_cup_and_the_blue_measuring_cup_outside_of_the_plate.mp4
  oracle_video_instruction: default
  oracle_video_matched: paraphrase of the default wording (0.73)
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

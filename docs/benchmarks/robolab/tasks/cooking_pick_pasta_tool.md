---
title: Cooking Pick Pasta Tool
task_id: cooking_pick_pasta_tool
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Move the pink tool from this utensil container to the other utensil holder
  scene_model: cooking_table
  scene_usda: cooking_table.usda
  scene_image: cooking_table.jpg
  env_class: CookingPickPastaToolTask
  task_name: CookingPickPastaToolTask
  source_file: robolab/tasks/benchmark/cooking_pick_pasta_tool.py
  episode_length_s: 60
  attributes: [spatial, vague, color]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - pink_spaghetti_spoon
    container: storage_box_01
    logical: all
    require_contact_with: true
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
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
    vague: Move the pink tool over to the other container
    specific: Remove the pink pasta tool from its current utensil container and place
      it in the other utensil holder
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

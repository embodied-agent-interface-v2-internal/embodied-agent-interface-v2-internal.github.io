---
title: Wood Spatula To Bowl
task_id: wood_spatula_to_bowl
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the wooden spatula in the bowl
  scene_model: fruits_in_basket
  scene_usda: fruits_in_basket.usda
  scene_image: fruits_in_basket.jpg
  env_class: WoodSpatulaToBowlTask
  task_name: WoodSpatulaToBowlTask
  source_file: robolab/tasks/benchmark/wood_spatula_to_bowl.py
  episode_length_s: 60
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - wooden_spoons
    container: wooden_bowl
    logical: all
    require_contact_with: true
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
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
    - wooden_bowl
    - wooden_spoons
    - spatula
    - storage_box
  instruction_variants:
    vague: Put the wood utensil in the bowl
    specific: Pick up the wooden spatula from the utensils box on the table and place
      it inside the wooden bowl in the center of the table
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

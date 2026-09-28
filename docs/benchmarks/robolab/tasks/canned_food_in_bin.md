---
title: Canned Food In Bin
task_id: canned_food_in_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the canned food in the grey bin
  scene_model: bin_condiments
  scene_usda: bin_condiments.usda
  scene_image: bin_condiments.jpg
  env_class: CannedFoodInBinTask
  task_name: CannedFoodInBinTask
  source_file: robolab/tasks/benchmark/canned_food_in_bin_task.py
  episode_length_s: 60
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object: canned_tuna
    container: grey_bin
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - grey_bin
    - mug
    - mustard
    - bowl
    - ranch_dressing
    - bbq_sauce_bottle
    - oatmeal_raisin_cookies
    - canned_tuna
    - soft_scrub
    - wood_block
    - coffee_pot
    - bbq_sauce_bottle_01
  instruction_variants:
    vague: Put away cans
    specific: Put the small canned tuna in the grey bin
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

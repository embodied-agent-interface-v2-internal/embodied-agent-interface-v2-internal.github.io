---
title: Dishes In Bin
task_id: dishes_in_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the dishware in the grey bin
  scene_model: mugs2_bananas2_ketchup_rubiks3_bin
  scene_usda: mugs2_bananas2_ketchup_rubiks3_bin.usda
  scene_image: mugs2_bananas2_ketchup_rubiks3_bin.jpg
  env_class: DishesInBinTask
  task_name: DishesInBinTask
  source_file: robolab/tasks/benchmark/dishes_in_bin.py
  episode_length_s: 180
  attributes: [vague, semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - mug
    - mug_01
    - bowl
    container: grey_bin
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - mug
    - mug_01
    - bowl
    - grey_bin
    - banana_near
    - banana_far
    - rubiks_cube_top
    - rubiks_cube_middle
    - rubiks_cube_bottom
    - ketchup_bottle
  instruction_variants:
    vague: Put away dishes
    specific: Pick up the two mugs and a bowl from the table and place them into the grey
      bin
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

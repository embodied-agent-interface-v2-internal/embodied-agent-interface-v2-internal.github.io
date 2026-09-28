---
title: Red Dishes In Bin
task_id: red_dishes_in_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the red dishware in the grey bin
  scene_model: rubiks_cube_banana_bowl_mug_bin
  scene_usda: rubiks_cube_banana_bowl_mug_bin.usda
  scene_image: rubiks_cube_banana_bowl_mug_bin.jpg
  env_class: RedDishesInBinTask
  task_name: RedDishesInBinTask
  source_file: robolab/tasks/benchmark/red_dishes_in_bin.py
  episode_length_s: 60
  attributes: [color, semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - mug
    - bowl
    container: grey_bin
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [mug, bowl, grey_bin, banana, rubiks_cube]
  instruction_variants:
    vague: Clean up red dishware
    specific: Pick up each red mug and bowl from the table and place them in the grey
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

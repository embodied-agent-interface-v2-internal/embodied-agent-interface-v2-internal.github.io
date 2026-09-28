---
title: Yellow And White Objects In Bin
task_id: yellow_and_white_objects_in_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put all white objects and yellow objects in the grey bin
  scene_model: mug_banana_ketchup_bowl_rubiks3_bin
  scene_usda: mug_banana_ketchup_bowl_rubiks3_bin.usda
  scene_image: mug_banana_ketchup_bowl_rubiks3_bin.jpg
  env_class: YellowAndWhiteObjectsInBinTask
  task_name: YellowAndWhiteObjectsInBinTask
  source_file: robolab/tasks/benchmark/yellow_and_white_objects_in_bin.py
  episode_length_s: 60
  attributes: [color, conjunction]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - mug
    - banana
    container: grey_bin
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - mug
    - banana
    - grey_bin
    - bowl
    - ketchup_bottle
    - rubiks_cube_top
    - rubiks_cube_middle
    - rubiks_cube_bottom
  instruction_variants:
    vague: Clean up white and yellow objects
    specific: Identify the white-colored and yellow-colored object on the table and place
      each one into the grey bin
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

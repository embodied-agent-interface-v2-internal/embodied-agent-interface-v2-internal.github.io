---
title: Rubiks Cubes In Bin
task_id: rubiks_cubes_in_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Sort all rubiks cubes into the bin
  scene_model: toys_cleanup
  scene_usda: toys_cleanup.usda
  scene_image: toys_cleanup.jpg
  env_class: RubiksCubesInBinTask
  task_name: RubiksCubesInBinTask
  source_file: robolab/tasks/benchmark/rubiks_cubes_in_bin.py
  episode_length_s: 120
  attributes: [sorting]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - rubiks_cube
    - rubiks_cube_1
    - rubiks_cube_2
    container: grey_bin
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - rubiks_cube
    - rubiks_cube_1
    - rubiks_cube_2
    - grey_bin
    - lizard_figurine
    - birdhouse
    - yellow_block
    - red_block
    - green_block
    - blue_block
    - lizard_figurine_01
  instruction_variants:
    vague: Put away rubiks cubes
    specific: Pick up only the three rubiks cube from the table and place them all into
      the grey bin
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

---
title: Stack3 Rubiks Cube
task_id: stack3_rubiks_cube
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Stack the rubiks cubes in a tower
  scene_model: rubiks_cube_3
  scene_usda: rubiks_cube_3.usda
  scene_image: rubiks_cube_3.jpg
  env_class: Stack3RubiksCubeTask
  task_name: Stack3RubiksCubeTask
  source_file: robolab/tasks/benchmark/rubiks_cube_stacking_task.py
  episode_length_s: 60
  attributes: [stacking]
  difficulty_label: simple
  success_predicate: stacked
  success_params:
    objects:
    - rubiks_cube
    - rubiks_cube_1
    - rubiks_cube_2
    order: None
  subtasks: 2
  subtask_predicates: [Subtask, stacked]
  objects: [rubiks_cube, rubiks_cube_1, rubiks_cube_2]
  instruction_variants:
    vague: Stack everything in a tower
    specific: Pick up the rubiks cubes and stack them vertically on top of each other
      on the table
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

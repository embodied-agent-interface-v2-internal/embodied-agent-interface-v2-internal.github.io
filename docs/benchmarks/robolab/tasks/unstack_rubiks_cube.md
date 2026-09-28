---
title: Unstack Rubiks Cube
task_id: unstack_rubiks_cube
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Unstack the rubiks cube tower
  scene_model: mug_banana_ketchup_bowl_rubiks3_bin
  scene_usda: mug_banana_ketchup_bowl_rubiks3_bin.usda
  scene_image: mug_banana_ketchup_bowl_rubiks3_bin.jpg
  env_class: UnstackRubiksCubeTask
  task_name: UnstackRubiksCubeTask
  source_file: robolab/tasks/benchmark/unstack_rubiks_cube.py
  episode_length_s: 90
  attributes: [stacking]
  difficulty_label: simple
  success_predicate: object_outside_of_and_on_surface
  success_params:
    object:
    - rubiks_cube_middle
    - rubiks_cube_top
    - rubiks_cube_bottom
    container: grey_bin
    surface: table
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place_on_surface]
  objects:
    - mug
    - banana
    - ketchup_bottle
    - rubiks_cube_middle
    - rubiks_cube_top
    - rubiks_cube_bottom
    - bowl
    - grey_bin
  instruction_variants:
    vague: Unstack the tower
    specific: Remove each rubiks cube from the stacked tower one at a time and place them
      separately on the table
  oracle_video: https://research.nvidia.com/labs/srl/projects/robolab/static/videos/Unstack_the_rubiks_cube_tower_2_viewport_3X.mp4
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

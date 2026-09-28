---
title: White Mug In Center Of Table
task_id: white_mug_in_center_of_table
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the white mug in the center of the table.
  scene_model: objects_around_table
  scene_usda: objects_around_table.usda
  scene_image: objects_around_table.jpg
  env_class: WhiteMugInCenterOfTableTask
  task_name: WhiteMugInCenterOfTableTask
  source_file: robolab/tasks/benchmark/white_mug_in_center_of_table.py
  episode_length_s: 30
  attributes: [color, spatial]
  difficulty_label: simple
  success_predicate: object_on_center
  success_params:
    object: mug
    reference_object: table
    require_contact_with: true
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [Subtask]
  objects:
    - mug
    - bowl
    - alphabet_soup_can
    - orange_juice_carton
    - smartphone
    - milk_carton
    - banana
    - rubiks_cube
  instruction_variants:
    vague: Move the mug to the center
    specific: Pick up the white ceramic mug and place it in the center of the table surface
      away from the other objects
  oracle_video: https://research.nvidia.com/labs/srl/projects/robolab/static/videos/Put_the_white_mug_in_the_center_of_the_table_1_viewport_3X.mp4
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

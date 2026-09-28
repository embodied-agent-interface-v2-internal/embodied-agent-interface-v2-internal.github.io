---
title: Rubiks Cube
task_id: rubiks_cube
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the cube in the bowl
  scene_model: rubiks_cube_bowl
  scene_usda: rubiks_cube_bowl.usda
  scene_image: rubiks_cube_bowl.jpg
  env_class: RubiksCubeTask
  task_name: RubiksCubeTask
  source_file: robolab/tasks/benchmark/rubiks_cube_task.py
  episode_length_s: 40
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object: rubiks_cube
    container: bowl
    require_contact_with: true
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [rubiks_cube, bowl]
  instruction_variants:
    vague: Put it in the bowl
    specific: Pick up the rubiks cube that's on the table and place it inside the bowl
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

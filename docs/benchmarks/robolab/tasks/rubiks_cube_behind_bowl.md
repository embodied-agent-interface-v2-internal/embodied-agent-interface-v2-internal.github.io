---
title: Rubiks Cube Behind Bowl
task_id: rubiks_cube_behind_bowl
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the rubiks cube behind the bowl
  scene_model: rubiks_cube_banana_bowl
  scene_usda: rubiks_cube_banana_bowl.usda
  scene_image: rubiks_cube_banana_bowl.jpg
  env_class: RubiksCubeBehindBowlTask
  task_name: RubiksCubeBehindBowlTask
  source_file: robolab/tasks/benchmark/rubiks_cube_behind_bowl.py
  episode_length_s: 30
  attributes: [spatial]
  difficulty_label: simple
  success_predicate: object_behind
  success_params:
    object: rubiks_cube
    reference_object: bowl
    require_contact_with: table
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [Subtask]
  objects: [rubiks_cube, banana, bowl]
  instruction_variants:
    vague: Put the cube behind the bowl
    specific: Pick up the rubiks cube and place it on the table directly behind the bowl,
      further from you
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

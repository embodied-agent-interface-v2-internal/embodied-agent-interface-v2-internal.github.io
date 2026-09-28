---
title: Banana Then Rubiks Cube
task_id: banana_then_rubiks_cube
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: put the banana then the cube in the bowl
  scene_model: rubiks_cube_banana_bowl
  scene_usda: rubiks_cube_banana_bowl.usda
  scene_image: rubiks_cube_banana_bowl.jpg
  env_class: BananaThenRubiksCubeTask
  task_name: BananaThenRubiksCubeTask
  source_file: robolab/tasks/benchmark/banana_then_rubiks_cube.py
  episode_length_s: 60
  attributes: [conjunction]
  difficulty_label: simple
  success_predicate: objects_placed_in_container_in_order
  success_params:
    objects:
    - banana
    - rubiks_cube
    container: bowl
    require_contact_with: true
    require_gripper_detached: true
  subtasks: 2
  subtask_predicates: [pick_and_place]
  objects: [rubiks_cube, banana, bowl]
  instruction_variants:
    vague: put banana then cube away
    specific: First pick up the yellow banana and place it in the bowl, then pick up the
      rubiks cube and place it in the bowl after
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

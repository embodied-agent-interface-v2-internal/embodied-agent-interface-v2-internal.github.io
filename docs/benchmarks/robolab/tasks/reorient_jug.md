---
title: Reorient Jug
task_id: reorient_jug
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Stand the jug upright
  scene_model: shelf_with_cleaning_products
  scene_usda: shelf_with_cleaning_products.usda
  scene_image: shelf_with_cleaning_products.jpg
  env_class: ReorientJugTask
  task_name: ReorientJugTask
  source_file: robolab/tasks/benchmark/reorient_jug.py
  episode_length_s: 60
  attributes: [semantics, reorientation, affordance]
  difficulty_label: complex
  success_predicate: object_upright
  success_params:
    object:
    - utilityjug_a02
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [Subtask]
  objects:
    - large_storage_rack
    - whitepackerbottle_a01
    - whitepackerbottle_a02
    - utilityjug_a01
    - utilityjug_a02
    - squarepail_a01
    - plasticpail_a02
    - whitepackerbottle_a03
  instruction_variants:
    vague: Fix the jug
    specific: Grasp the jug that is tipped on its side place it upright
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

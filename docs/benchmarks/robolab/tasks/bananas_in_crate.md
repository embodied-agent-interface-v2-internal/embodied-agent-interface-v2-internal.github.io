---
title: Bananas In Crate
task_id: bananas_in_crate
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put 2 bananas in the crate
  scene_model: bananas_5_in_crate
  scene_usda: bananas_5_in_crate.usda
  scene_image: bananas_5_in_crate.jpg
  env_class: BananasInCrateTask
  task_name: BananasInCrateTask
  source_file: robolab/tasks/benchmark/bananas_in_crate.py
  episode_length_s: 60
  attributes: [counting]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - banana
    - banana_01
    - banana_02
    - banana_03
    - banana_04
    container: purple_crate
    logical: choose
    K: 2
    require_gripper_detached: true
    require_contact_with: false
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [banana, banana_01, banana_02, banana_03, banana_04, purple_crate]
  instruction_variants:
    vague: Put 2 bananas in the container
    specific: Put 2 bananas in the purple crate. Make sure there are exactly 2 (two) bananas
      in the crate.
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

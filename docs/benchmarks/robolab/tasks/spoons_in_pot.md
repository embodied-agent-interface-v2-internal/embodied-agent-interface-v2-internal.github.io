---
title: Spoons In Pot
task_id: spoons_in_pot
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put all of the serving spoons with no holes in the pot
  scene_model: ladle_pot
  scene_usda: ladle_pot.usda
  scene_image: ladle_pot.jpg
  env_class: SpoonsInPotTask
  task_name: SpoonsInPotTask
  source_file: robolab/tasks/benchmark/spoons_in_pot.py
  episode_length_s: 180
  attributes: [reorientation, semantics, affordance]
  difficulty_label: complex
  success_predicate: object_in_container
  success_params:
    object:
    - ladle
    - ladle_01
    - red_serving_spoon
    container: anza_medium
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - anza_medium
    - ladle
    - plate_large
    - plate_small
    - fork_big
    - fork_small
    - spatula_13
    - spatula_14
    - spatula_15
    - pink_spaghetti_spoon
    - ladle_01
    - red_serving_spoon
    - green_serving_spoon
  instruction_variants:
    vague: Put the spoons with no holes in the pot
    specific: Pick up all of the serving spoons (two green, one red) with no holes from
      the table and place them inside the cooking pot
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

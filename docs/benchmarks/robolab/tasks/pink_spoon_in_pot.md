---
title: Pink Spoon In Pot
task_id: pink_spoon_in_pot
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the pink spaghetti spoon in the pot
  scene_model: ladle_pot
  scene_usda: ladle_pot.usda
  scene_image: ladle_pot.jpg
  env_class: PinkSpoonInPotTask
  task_name: PinkSpoonInPotTask
  source_file: robolab/tasks/benchmark/pink_spoon_in_pot.py
  episode_length_s: 60
  attributes: [color, affordance]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - pink_spaghetti_spoon
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
    vague: Put the pink spoon in the pot
    specific: Pick up the pink spaghetti serving spoon that's on the left plate and place
      it inside the pot in the center of the table
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

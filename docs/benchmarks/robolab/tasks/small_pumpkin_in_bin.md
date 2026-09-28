---
title: Small Pumpkin In Bin
task_id: small_pumpkin_in_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the small pumpkin in the bin
  scene_model: clutter_fruit_bottle_bluebin
  scene_usda: clutter_fruit_bottle_bluebin.usda
  scene_image: clutter_fruit_bottle_bluebin.jpg
  env_class: SmallPumpkinInBinTask
  task_name: SmallPumpkinInBinTask
  source_file: robolab/tasks/benchmark/clutter_small_pumpkin_task.py
  episode_length_s: 60
  attributes: [size]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object: pumpkinsmall
    container: right_bin
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - lemon_01
    - lemon_02
    - lime01
    - lime01_01
    - orange_01
    - orange_02
    - pomegranate01
    - pumpkinlarge
    - pumpkinsmall
    - red_onion
    - whitepackerbottle_a01
    - avocado01
    - crabbypenholder
    - milkjug_a01
    - serving_bowl
    - utilityjug_a03
    - right_bin
  instruction_variants:
    vague: Put away the small pumpkin
    specific: Identify the smaller pumpkin of the two pumpkins on the table and place
      it in the bin
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

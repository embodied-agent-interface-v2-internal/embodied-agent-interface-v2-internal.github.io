---
title: Black Items In Bin
task_id: black_items_in_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the black items in the grey bin
  scene_model: workdesk_bin
  scene_usda: workdesk_bin.usda
  scene_image: workdesk_bin.jpg
  env_class: BlackItemsInBinTask
  task_name: BlackItemsInBinTask
  source_file: robolab/tasks/benchmark/black_items_in_bin.py
  episode_length_s: 120
  attributes: [color, sorting]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - keyboard
    - remote_control
    - computer_mouse
    - smartphone
    - glasses
    container: grey_bin
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - ceramic_mug
    - glasses
    - keyboard
    - lizard_figurine
    - marker
    - remote_control
    - smartphone
    - wooden_bowl
    - spoon_big
    - computer_mouse
    - yogurt_cup
    - granola_bars
    - grey_bin
  instruction_variants:
    vague: Clean up the dark items
    specific: Identify all black-colored objects on the table and place them into the
      grey bin
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

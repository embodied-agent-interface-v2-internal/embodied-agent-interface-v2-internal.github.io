---
title: Mouse On Keyboard
task_id: mouse_on_keyboard
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the computer mouse on the keyboard
  scene_model: workdesk
  scene_usda: workdesk.usda
  scene_image: workdesk.jpg
  env_class: MouseOnKeyboardTask
  task_name: MouseOnKeyboardTask
  source_file: robolab/tasks/benchmark/mouse_on_keyboard.py
  episode_length_s: 60
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_on_top
  success_params:
    object:
    - computer_mouse
    reference_object: keyboard
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
    - rubiks_cube
    - smartphone
    - wooden_bowl
    - spoon_big
    - computer_mouse
    - yogurt_cup
    - oatmeal_raisin_cookies
    - granola_bars
  instruction_variants:
    vague: Put the mouse on the keyboard
    specific: Pick up the computer mouse and place it on top of the keyboard
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

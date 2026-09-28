---
title: Pick Glasses
task_id: pick_glasses
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Pick up the eye glasses
  scene_model: workdesk
  scene_usda: workdesk.usda
  scene_image: workdesk.jpg
  env_class: PickGlassesTask
  task_name: PickGlassesTask
  source_file: robolab/tasks/benchmark/pick_glasses_task.py
  episode_length_s: 30
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_picked_up
  success_params:
    object: glasses
    surface: table
  subtasks: 1
  subtask_predicates: [Subtask]
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
    vague: Grab the glasses
    specific: Pick up the pair of black eyeglasses that's sitting on the table
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

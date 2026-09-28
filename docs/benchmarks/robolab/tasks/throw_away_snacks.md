---
title: Throw Away Snacks
task_id: throw_away_snacks
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put away the snacks in the bin
  scene_model: workdesk_snacks
  scene_usda: workdesk_snacks.usda
  scene_image: workdesk_snacks.jpg
  env_class: ThrowAwaySnacksTask
  task_name: ThrowAwaySnacksTask
  source_file: robolab/tasks/benchmark/throw_away_snacks_task.py
  episode_length_s: 120
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - apple_01
    - yogurt_cup
    container: plasticpail_a02
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - ceramic_mug
    - glasses
    - keyboard
    - marker
    - remote_control
    - smartphone
    - wooden_bowl
    - spoon_big
    - computer_mouse
    - yogurt_cup
    - pitcher
    - plasticpail_a02
    - apple_01
  instruction_variants:
    vague: Throw away the snacks
    specific: Pick up each snack item from the table and drop it into the bin to discard
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

---
title: Throw Away Apple
task_id: throw_away_apple
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Throw away the apple
  scene_model: workdesk_snacks
  scene_usda: workdesk_snacks.usda
  scene_image: workdesk_snacks.jpg
  env_class: ThrowAwayAppleTask
  task_name: ThrowAwayAppleTask
  source_file: robolab/tasks/benchmark/throw_away_apple_task.py
  episode_length_s: 60
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object: apple_01
    container: plasticpail_a02
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
    vague: Toss the apple
    specific: Pick up the red apple from the table and drop it into the grey bin to discard
      it
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

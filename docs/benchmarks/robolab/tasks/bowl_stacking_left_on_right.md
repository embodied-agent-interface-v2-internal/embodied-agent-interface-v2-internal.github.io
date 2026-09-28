---
title: Bowl Stacking Left On Right
task_id: bowl_stacking_left_on_right
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Stack the left bowl on the right bowl
  scene_model: bowls_2_table
  scene_usda: bowls_2_table.usda
  scene_image: bowls_2_table.jpg
  env_class: BowlStackingLeftOnRightTask
  task_name: BowlStackingLeftOnRightTask
  source_file: robolab/tasks/benchmark/bowl_stacking_left_on_right.py
  episode_length_s: 20
  attributes: [spatial]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - bowl_2
    container: bowl_1
    require_contact_with: true
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [object_in_container]
  objects: [bowl_1, bowl_2]
  instruction_variants:
    vague: Stack the left bowl on the right
    specific: Pick up the bowl to the left of the robot and place it on top of the bowl
      to the right of the robot
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

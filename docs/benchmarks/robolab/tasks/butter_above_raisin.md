---
title: Butter Above Raisin
task_id: butter_above_raisin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Pick up the butter box and place it on top of the raisin box
  scene_model: butter_raisin_box
  scene_usda: butter_raisin_box.usda
  scene_image: butter_raisin_box.jpg
  env_class: ButterAboveRaisinTask
  task_name: ButterAboveRaisinTask
  source_file: robolab/tasks/benchmark/butter_above_raisin_task.py
  episode_length_s: 40
  attributes: [spatial]
  difficulty_label: simple
  success_predicate: object_on_top
  success_params:
    object: butter
    reference_object: raisin_box
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [butter, raisin_box]
  instruction_variants:
    specific: Place the butter on top of the raisin box. The butter should end up on the
      raisin box.
    vague: Put butter on raisin box
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

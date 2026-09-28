---
title: Mustard Above Raisin
task_id: mustard_above_raisin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Place the mustard on the raisin box.
  scene_model: mustard_raisin_box
  scene_usda: mustard_raisin_box.usda
  scene_image: mustard_raisin_box.jpg
  env_class: MustardAboveRaisinTask
  task_name: MustardAboveRaisinTask
  source_file: robolab/tasks/benchmark/mustard_above_raisin_task.py
  episode_length_s: 40
  attributes: [spatial]
  difficulty_label: simple
  success_predicate: object_on_top
  success_params:
    object: mustard_bottle
    reference_object: raisin_box
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [mustard_bottle, raisin_box]
  instruction_variants:
    vague: Put bottle on box
    specific: Pick up the mustard bottle and put it on top of the raisin box. The mustard
      should end up directly above the raisin box.
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

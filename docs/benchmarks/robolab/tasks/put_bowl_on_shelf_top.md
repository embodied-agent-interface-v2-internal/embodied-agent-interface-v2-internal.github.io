---
title: Put Bowl On Shelf Top
task_id: put_bowl_on_shelf_top
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the serving bowl anywhere on the shelf in front of you
  scene_model: shelf_mugs_jug_bowl
  scene_usda: shelf_mugs_jug_bowl.usda
  scene_image: shelf_mugs_jug_bowl.jpg
  env_class: PutBowlOnShelfTopTask
  task_name: PutBowlOnShelfTopTask
  source_file: robolab/tasks/benchmark/put_bowl_on_shelf.py
  episode_length_s: 60
  attributes: [spatial]
  difficulty_label: simple
  success_predicate: object_on_top
  success_params:
    object:
    - serving_bowl
    reference_object: rack_l04
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [ceramic_mug, mug, rack_l04, serving_bowl, utilityjug_a01]
  instruction_variants:
    vague: Put the bowl on shelf
    specific: Pick up the white serving bowl that's on the table to the right and place
      it on any open space on the shelf on the center of the table
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

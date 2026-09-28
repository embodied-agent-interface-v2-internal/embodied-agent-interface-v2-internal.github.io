---
title: Clamp In Right Bin
task_id: clamp_in_right_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the spring clamp in the right bin
  scene_model: tools_container
  scene_usda: tools_container.usda
  scene_image: tools_container.jpg
  env_class: ClampInRightBinTask
  task_name: ClampInRightBinTask
  source_file: robolab/tasks/benchmark/clamp_in_right_bin.py
  episode_length_s: 60
  attributes: [semantics, spatial]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object: spring_clamp
    container: right_bin
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [left_bin, right_bin, red_hammer, husky_hammer, cordless_drill, spring_clamp]
  instruction_variants:
    vague: Put the clamp in the right bin
    specific: Pick up the spring clamp from the table and place it in the bin on the right
      side
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

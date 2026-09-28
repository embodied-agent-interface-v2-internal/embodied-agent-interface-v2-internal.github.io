---
title: Non Hammer Tools In Right Bin
task_id: non_hammer_tools_in_right_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the non-hammer tools in the right bin
  scene_model: tools_container
  scene_usda: tools_container.usda
  scene_image: tools_container.jpg
  env_class: NonHammerToolsInRightBinTask
  task_name: NonHammerToolsInRightBinTask
  source_file: robolab/tasks/benchmark/non_hammer_tools_in_right_bin.py
  episode_length_s: 180
  attributes: [semantics, spatial, sorting]
  difficulty_label: moderate
  success_predicate: object_in_container
  success_params:
    object:
    - cordless_drill
    - spring_clamp
    container: right_bin
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [left_bin, right_bin, red_hammer, husky_hammer, cordless_drill, spring_clamp]
  instruction_variants:
    vague: Sort non-hammer tools to the right
    specific: Pick up the cordless drill and the spring clamp and place both in the bin
      on the right side, leaving the hammers untouched
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

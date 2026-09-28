---
title: Tools Picking All Hammers
task_id: tools_picking_all_hammers
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Take out all the hammers and put them on the table
  scene_model: tools_picking
  scene_usda: tools_picking.usda
  scene_image: tools_picking.jpg
  env_class: ToolsPickingAllHammersTask
  task_name: ToolsPickingAllHammersTask
  source_file: robolab/tasks/benchmark/tools_picking_all_hammers.py
  episode_length_s: 240
  attributes: [semantics, spatial]
  difficulty_label: simple
  success_predicate: object_outside_of_and_on_surface
  success_params:
    object:
    - husky_hammer
    - blue_hammer
    - red_hammer
    - wood_hammer
    container: left_bin
    surface: table
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place_on_surface]
  objects:
    - clamp
    - cordless_drill
    - spring_clamp
    - husky_hammer
    - blue_hammer
    - red_hammer
    - wood_hammer
    - left_bin
    - center_bin
    - right_bin
    - clamp_01
  instruction_variants:
    vague: Empty the hammers bin
    specific: Remove every hammer from the left bin and place each one on the table in
      front of you
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

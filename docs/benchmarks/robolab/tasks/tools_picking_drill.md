---
title: Tools Picking Drill
task_id: tools_picking_drill
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Select the cordless drill and put it on the table
  scene_model: tools_picking
  scene_usda: tools_picking.usda
  scene_image: tools_picking.jpg
  env_class: ToolsPickingDrillTask
  task_name: ToolsPickingDrillTask
  source_file: robolab/tasks/benchmark/tools_picking_drill.py
  episode_length_s: 60
  attributes: [spatial, semantics]
  difficulty_label: simple
  success_predicate: object_outside_of_and_on_surface
  success_params:
    object:
    - cordless_drill
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
    vague: Get the drill
    specific: Pick up the cordless electric drill and place it on the table surface
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

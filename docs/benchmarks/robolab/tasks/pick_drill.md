---
title: Pick Drill
task_id: pick_drill
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Pick up the cordless drill.
  scene_model: mugs4_measuringcup_drill_bowl
  scene_usda: mugs4_measuringcup_drill_bowl.usda
  scene_image: mugs4_measuringcup_drill_bowl.jpg
  env_class: PickDrillTask
  task_name: PickDrillTask
  source_file: robolab/tasks/benchmark/pick_drill.py
  episode_length_s: 40
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_picked_up
  success_params:
    object: cordless_drill
    surface: table
  subtasks: 1
  subtask_predicates: [object_grabbed]
  objects:
    - red_mug
    - bowl
    - ceramic_mug
    - upright_white_mug
    - sideways_white_mug
    - cordless_drill
    - measuring_cup
  instruction_variants:
    vague: Get the drill
    specific: Pick up the orange cordless electric drill and lift it off the table
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

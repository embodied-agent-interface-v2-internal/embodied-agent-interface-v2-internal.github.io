---
title: Take Measuring Spoon Out
task_id: take_measuring_spoon_out
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Take the white colored measuring spoon out of the red bowl and put it on the table.
  scene_model: mugs4_measuringcup_drill_bowl_v2
  scene_usda: mugs4_measuringcup_drill_bowl_v2.usda
  scene_image: mugs4_measuringcup_drill_bowl_v2.jpg
  env_class: TakeMeasuringSpoonOutTask
  task_name: TakeMeasuringSpoonOutTask
  source_file: robolab/tasks/benchmark/take_measuring_spoon_out.py
  episode_length_s: 40
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_outside_of
  success_params:
    object:
    - measuring_cup
    container: bowl
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [Subtask]
  objects:
    - red_mug
    - bowl
    - ceramic_mug
    - upright_white_mug
    - sideways_white_mug
    - cordless_drill
    - measuring_cup
  instruction_variants:
    vague: Take the measuring spoon out of the bowl
    specific: Reach into the bowl, grasp the measuring spoon, lift it out, and place it
      on the table surface
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

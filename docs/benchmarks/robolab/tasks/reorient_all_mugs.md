---
title: Reorient All Mugs
task_id: reorient_all_mugs
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Reorient all the mugs upright so that the opening is facing upwards.
  scene_model: mugs4_measuringcup_drill_bowl
  scene_usda: mugs4_measuringcup_drill_bowl.usda
  scene_image: mugs4_measuringcup_drill_bowl.jpg
  env_class: ReorientAllMugsTask
  task_name: ReorientAllMugsTask
  source_file: robolab/tasks/benchmark/reorient_all_mugs_task.py
  episode_length_s: 90
  attributes: [reorientation]
  difficulty_label: moderate
  success_predicate: object_upright
  success_params:
    object:
    - red_mug
    - ceramic_mug
    - sideways_white_mug
    - upright_white_mug
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
    vague: Make sure the mugs are upright
    specific: Check each mug on the table and if any are tipped over or inverted, rotate
      them so the opening faces upward. Leave it if it's already upright.
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

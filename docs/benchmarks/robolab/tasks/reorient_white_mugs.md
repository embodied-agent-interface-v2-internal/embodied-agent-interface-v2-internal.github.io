---
title: Reorient White Mugs
task_id: reorient_white_mugs
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Make sure all the white mugs are upright so that the opening is facing upwards.
  scene_model: mugs4_measuringcup_drill_bowl_v2
  scene_usda: mugs4_measuringcup_drill_bowl_v2.usda
  scene_image: mugs4_measuringcup_drill_bowl_v2.jpg
  env_class: ReorientWhiteMugsTask
  task_name: ReorientWhiteMugsTask
  source_file: robolab/tasks/benchmark/reorient_white_mugs.py
  episode_length_s: 60
  attributes: [reorientation, color]
  difficulty_label: moderate
  success_predicate: object_upright
  success_params:
    object:
    - upright_white_mug
    - sideways_white_mug
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
    vague: Fix the cups
    specific: For each white mug that is tipped over or upside down, rotate it so the
      opening faces straight up
  oracle_video: https://research.nvidia.com/labs/srl/projects/robolab/static/videos/captioned/Make_sure_all_the_white_mugs_are_upright_so_that_the_opening_is_facing_upwards.mp4
  oracle_video_instruction: default
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

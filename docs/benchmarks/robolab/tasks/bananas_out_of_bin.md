---
title: Bananas Out Of Bin
task_id: bananas_out_of_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Take the bananas out
  scene_model: bananas_5_grey_bin
  scene_usda: bananas_5_grey_bin.usda
  scene_image: bananas_5_grey_bin.jpg
  env_class: BananasOutOfBinTask
  task_name: BananasOutOfBinTask
  source_file: robolab/tasks/benchmark/bananas_out_of_bin.py
  episode_length_s: 90
  attributes: [semantics, spatial]
  difficulty_label: simple
  success_predicate: object_outside_of
  success_params:
    object:
    - banana_02
    - banana_04
    container: grey_bin
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [Subtask]
  objects: [banana, banana_01, banana_02, banana_03, banana_04, grey_bin]
  instruction_variants:
    specific: Take all the bananas out of the grey bin and put it on the table.
    vague: Empty the grey bin
  oracle_video: https://research.nvidia.com/labs/srl/projects/robolab/static/videos/Take_the_bananas_out_1_viewport_3X.mp4
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

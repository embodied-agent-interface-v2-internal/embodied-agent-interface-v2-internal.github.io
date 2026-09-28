---
title: Phone Or Remote In Bin
task_id: phone_or_remote_in_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the phone or the remote in the grey bin
  scene_model: workdesk_bin
  scene_usda: workdesk_bin.usda
  scene_image: workdesk_bin.jpg
  env_class: PhoneOrRemoteInBinTask
  task_name: PhoneOrRemoteInBinTask
  source_file: robolab/tasks/benchmark/phone_or_remote_in_bin_task.py
  episode_length_s: 60
  attributes: [conjunction]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - smartphone
    - remote_control
    container: grey_bin
    logical: any
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - ceramic_mug
    - glasses
    - keyboard
    - lizard_figurine
    - marker
    - remote_control
    - smartphone
    - wooden_bowl
    - spoon_big
    - computer_mouse
    - yogurt_cup
    - granola_bars
    - grey_bin
  instruction_variants:
    vague: Put the phone or the remote away
    specific: Choose either the black phone or the remote control and it into the grey
      bin next to the keyboard
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

---
title: Bowl In Bin
task_id: bowl_in_bin
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: put the bowl in the grey bin
  scene_model: bin_mug_mustard_marker_bowl
  scene_usda: bin_mug_mustard_marker_bowl.usda
  scene_image: bin_mug_mustard_marker_bowl.jpg
  env_class: BowlInBinTask
  task_name: BowlInBinTask
  source_file: robolab/tasks/benchmark/bowl_in_bin_task.py
  episode_length_s: 60
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object: bowl
    container: grey_bin
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [mustard, bowl, dry_erase_marker, mug, grey_bin]
  instruction_variants:
    vague: put away bowl
    specific: Pick up the bowl from the table and place it inside the grey bin
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

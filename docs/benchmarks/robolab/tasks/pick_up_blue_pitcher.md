---
title: Pick Up Blue Pitcher
task_id: pick_up_blue_pitcher
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Pick up the large blue pitcher
  scene_model: blue
  scene_usda: blue.usda
  scene_image: blue.jpg
  env_class: PickUpBluePitcherTask
  task_name: PickUpBluePitcherTask
  source_file: robolab/tasks/benchmark/pick_up_blue_pitcher.py
  episode_length_s: 30
  attributes: [color, affordance]
  difficulty_label: simple
  success_predicate: object_picked_up
  success_params:
    object: pitcher
    surface: table
  subtasks: 1
  subtask_predicates: [Subtask]
  objects: [plasticjerrican_a02, plasticpail_a02, pitcher]
  instruction_variants:
    vague: Pick up blue object
    specific: Pick up the large blue pitcher on the table by the side handle and lift
      it off the table
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

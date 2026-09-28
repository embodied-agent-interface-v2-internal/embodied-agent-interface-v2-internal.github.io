---
title: Block Stacking Order Agnostic
task_id: block_stacking_order_agnostic
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Stack the blocks into a tower
  scene_model: colored_blocks
  scene_usda: colored_blocks.usda
  scene_image: colored_blocks.jpg
  env_class: BlockStackingOrderAgnosticTask
  task_name: BlockStackingOrderAgnosticTask
  source_file: robolab/tasks/benchmark/block_stacking_order_agnostic_task.py
  episode_length_s: 90
  attributes: [stacking]
  difficulty_label: simple
  success_predicate: stacked
  success_params:
    objects:
    - red_block
    - blue_block
    - green_block
    - yellow_block
    order: None
  subtasks: 3
  subtask_predicates: [Subtask, stacked]
  objects: [red_block, blue_block, green_block, yellow_block]
  instruction_variants:
    vague: Build a tower
    specific: Pick up the colored blocks and stack them vertically on top of each other,
      forming one tower
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

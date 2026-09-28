---
title: Block Stacking Specified Order
task_id: block_stacking_specified_order
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: 'Stack the blocks in the order from bottom to top: red, blue, green, yellow'
  scene_model: colored_blocks
  scene_usda: colored_blocks.usda
  scene_image: colored_blocks.jpg
  env_class: BlockStackingSpecifiedOrderTask
  task_name: BlockStackingSpecifiedOrderTask
  source_file: robolab/tasks/benchmark/block_stacking_specified_order_task.py
  episode_length_s: 90
  attributes: [stacking, color]
  difficulty_label: simple
  success_predicate: stacked
  success_params:
    objects:
    - red_block
    - blue_block
    - green_block
    - yellow_block
    order: bottom_to_top
  subtasks: 3
  subtask_predicates: [stacked]
  objects: [red_block, blue_block, green_block, yellow_block]
  instruction_variants:
    vague: Stack in the order of red, blue, green, yellow
    specific: Build a tower by placing the red block first, then the blue block on top,
      then the green, and finally the yellow block on top as a single tower
  oracle_video: https://research.nvidia.com/labs/srl/projects/robolab/static/videos/Stack_the_blocks_in_the_order_from_bottom_to_top_red_blue_green_yellow_4_viewport_3X.mp4
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

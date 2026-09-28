---
title: Stack Yellow On Red
task_id: stack_yellow_on_red
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Stack the yellow block on the red block
  scene_model: toys_cleanup
  scene_usda: toys_cleanup.usda
  scene_image: toys_cleanup.jpg
  env_class: StackYellowOnRedTask
  task_name: StackYellowOnRedTask
  source_file: robolab/tasks/benchmark/stack_yellow_on_red.py
  episode_length_s: 60
  attributes: [stacking]
  difficulty_label: simple
  success_predicate: stacked
  success_params:
    objects:
    - red_block
    - yellow_block
    order: bottom_to_top
  subtasks: 1
  subtask_predicates: [Subtask]
  objects:
    - rubiks_cube
    - rubiks_cube_1
    - rubiks_cube_2
    - grey_bin
    - lizard_figurine
    - birdhouse
    - yellow_block
    - red_block
    - green_block
    - blue_block
    - lizard_figurine_01
  instruction_variants:
    vague: 'Stack blocks: yellow on red'
    specific: Pick up the yellow block on the left and place it precisely on top of the
      red block in front of the birdhouse
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

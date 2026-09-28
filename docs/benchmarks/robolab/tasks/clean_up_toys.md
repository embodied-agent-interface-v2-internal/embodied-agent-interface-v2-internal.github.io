---
title: Clean Up Toys
task_id: clean_up_toys
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Clean up all the smaller toys and leave the birdhouse on the table
  scene_model: toys_cleanup
  scene_usda: toys_cleanup.usda
  scene_image: toys_cleanup.jpg
  env_class: CleanUpToysTask
  task_name: CleanUpToysTask
  source_file: robolab/tasks/benchmark/clean_up_toys.py
  episode_length_s: 300
  attributes: [sorting, semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object:
    - rubiks_cube
    - rubiks_cube_1
    - rubiks_cube_2
    - lizard_figurine
    - yellow_block
    - red_block
    - green_block
    - blue_block
    - lizard_figurine_01
    container: grey_bin
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
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
    vague: Clean up everything except the birdhouse
    specific: Pick up every toy object (rubiks cube, lizard figurines, colored blocks)
      from the table and place them all into the bin. Please ignore the birdhouse and
      don't touch it.
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

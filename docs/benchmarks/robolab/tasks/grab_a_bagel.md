---
title: Grab A Bagel
task_id: grab_a_bagel
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Grab a bagel
  scene_model: breakfast_table
  scene_usda: breakfast_table.usda
  scene_image: breakfast_table.jpg
  env_class: GrabABagelTask
  task_name: GrabABagelTask
  source_file: robolab/tasks/benchmark/grab_a_bagel.py
  episode_length_s: 30
  attributes: [semantics]
  difficulty_label: simple
  subtasks: 1
  subtask_predicates: [Subtask]
  objects:
    - bowl
    - banana
    - bagel_07
    - coffee_can
    - banana_01
    - yogurt_cup
    - coffee_pot
    - ceramic_mug
    - pitcher
    - fork_big
    - spoon_big
    - apple_01
    - orange2
    - milk_carton
    - orange_juice_carton
    - bagel_01
    - bagel_02
    - plate_small
    - plate_large
  instruction_variants:
    vague: Grab some bread
    specific: Reach for one of the bagels on the table and pick it up
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

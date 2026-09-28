---
title: Sauce Bottles Crate
task_id: sauce_bottles_crate
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the red bbq sauce bottle in the crate
  scene_model: bottles_crate
  scene_usda: bottles_crate.usda
  scene_image: bottles_crate.jpg
  env_class: SauceBottlesCrateTask
  task_name: SauceBottlesCrateTask
  source_file: robolab/tasks/benchmark/sauce_bottles_crate_task.py
  episode_length_s: 40
  attributes: [color, semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object: bbq_sauce_bottle
    container: purple_crate
    logical: all
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [bbq_sauce_bottle, purple_crate, ceramic_mug, salad_dressing_bottle]
  instruction_variants:
    vague: Put the red bottle away
    specific: Pick up the red BBQ sauce bottle and place it inside the wooden crate
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

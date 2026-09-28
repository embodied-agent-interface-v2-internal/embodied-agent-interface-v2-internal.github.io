---
title: Banana In Bowl
task_id: banana_in_bowl
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Pick up the banana and place it in the bowl
  scene_model: banana_bowl
  scene_usda: banana_bowl.usda
  scene_image: banana_bowl.jpg
  env_class: BananaInBowlTask
  task_name: BananaInBowlTask
  source_file: robolab/tasks/benchmark/banana_in_bowl_task.py
  episode_length_s: 50
  attributes: [semantics]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object: banana
    container: bowl
    require_contact_with: true
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects: [banana, bowl]
  instruction_variants:
    vague: Put the fruit in the bowl
    specific: Grasp the yellow banana and place it inside the red bowl on the table
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

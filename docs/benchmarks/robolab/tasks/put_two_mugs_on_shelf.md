---
title: Put Two Mugs On Shelf
task_id: put_two_mugs_on_shelf
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put two (2) mugs on the wire shelf
  scene_model: wire_shelf_mugs_plate_spatula
  scene_usda: wire_shelf_mugs_plate_spatula.usda
  scene_image: wire_shelf_mugs_plate_spatula.jpg
  env_class: PutTwoMugsOnShelfTask
  task_name: PutTwoMugsOnShelfTask
  source_file: robolab/tasks/benchmark/put_two_mugs_on_shelf.py
  episode_length_s: 180
  attributes: [affordance, spatial, counting]
  difficulty_label: complex
  success_predicate: object_in_container
  success_params:
    object:
    - ceramic_mug
    - mug
    - mug_01
    container: wireshelving_a01
    require_contact_with: true
    require_gripper_detached: true
    logical: choose
    K: 2
  subtasks: 1
  subtask_predicates: [pick_and_place]
  objects:
    - wireshelving_a01
    - spatula_01
    - plate_small
    - fork_big
    - fork_small
    - ceramic_mug
    - mug
    - mug_01
  instruction_variants:
    vague: Put the mugs on shelf
    specific: Select two mugs from the right side of the table and place them on the wire
      shelf in front of you
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

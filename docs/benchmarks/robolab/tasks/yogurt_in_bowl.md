---
title: Yogurt In Bowl
task_id: yogurt_in_bowl
benchmark: robolab

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/NVlabs/RoboLab @ v0.3.1
  synced: '2026-09-21'
  instruction: Put the small red yogurt in the red bowl
  scene_model: breakfast_table
  scene_usda: breakfast_table.usda
  scene_image: breakfast_table.jpg
  env_class: YogurtInBowlTask
  task_name: YogurtInBowlTask
  source_file: robolab/tasks/benchmark/yogurt_in_bowl.py
  episode_length_s: 40
  attributes: [color, size]
  difficulty_label: simple
  success_predicate: object_in_container
  success_params:
    object: yogurt_cup
    container: bowl
    require_gripper_detached: true
  subtasks: 1
  subtask_predicates: [pick_and_place]
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
    vague: Put the yogurt in the bowl
    specific: Pick up the small red yogurt container and place it inside the red bowl
  oracle_video: https://research.nvidia.com/labs/srl/projects/robolab/static/videos/Put_the_small_yogurt_in_the_red_bowl_0_viewport_3X.mp4
  oracle_video_instruction: default
  oracle_video_matched: paraphrase of the default wording (0.95)
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

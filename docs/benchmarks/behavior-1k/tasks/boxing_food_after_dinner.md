---
title: Boxing Food After Dinner
task_id: boxing_food_after_dinner
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2025-carryover
  instruction: ''
  scene_model: house_single_floor
  rooms: [dining_room, kitchen]
  demo_duration_s: 240
  oracle_video: https://www.youtube.com/embed/OmpbFiXPwMo
  oracle_thumbnail: https://img.youtube.com/vi/OmpbFiXPwMo/hqdefault.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 16.11
  demo_eef_m: [11.16, 17.7]
  demo_episodes: 200
  demo_mean_s: 223
  demo_mean_steps: 6697.7
  goal_categories: [electric_refrigerator.n.01, plate.n.04, sink.n.01, taco.n.02, tupperware.n.01]
  goal_clauses: 5
  goal_predicates: [inside, ontop, open]
  goal_quantifiers: [forall]
  object_categories: 9
  objects: 11
  rooms_loaded:
    - corridor_0
    - dining_room_0
    - entryway_0
    - garden_0
    - kitchen_0
    - living_room_0
    - living_room_1
  scene_model: house_single_floor
  test_instance_ids: [301, 320]
  test_instances: 20
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the `capabilities:` list in the frontmatter. One bullet per
     capability is plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- Watch the demo embedded above, then answer:
     - Does it actually satisfy the stated goal?
     - Is the trajectory clean, or does it contain recovery/idle segments?
     - Anything an imitation learner would be misled by? -->

_Not yet reviewed._


## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

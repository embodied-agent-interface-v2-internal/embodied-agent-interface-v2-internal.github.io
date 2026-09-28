---
title: Cook Bacon
task_id: cook_bacon
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Take the tray with six slices of bacon out of the refrigerator in the kitchen, cook all six slices in the frying pan on the stove until they're cooked, and make sure the refrigerator is closed when you're done.
  scene_model: house_single_floor
  rooms: [kitchen]
  demo_duration_s: 256
  oracle_video: https://player.vimeo.com/video/1114061497
  oracle_thumbnail: https://vumbnail.com/1114061497.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 20.92
  demo_eef_m: [8.2, 11.26]
  demo_episodes: 200
  demo_mean_s: 256
  demo_mean_steps: 7679.5
  goal_categories: [bacon.n.01, electric_refrigerator.n.01]
  goal_clauses: 2
  goal_predicates: [cooked, open]
  goal_quantifiers: [forall]
  object_categories: 7
  objects: 12
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

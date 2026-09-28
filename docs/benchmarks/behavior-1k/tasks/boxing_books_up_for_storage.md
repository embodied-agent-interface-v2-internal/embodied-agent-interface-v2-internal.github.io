---
title: Boxing Books Up for Storage
task_id: boxing_books_up_for_storage
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Put all six books from the bookcases in the living room into the box on the living room floor.
  scene_model: house_double_floor_upper
  rooms: [living_room]
  demo_duration_s: 808
  oracle_video: https://player.vimeo.com/video/1114059113
  oracle_thumbnail: https://vumbnail.com/1114059113.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 72.27
  demo_eef_m: [26.05, 24.47]
  demo_episodes: 200
  demo_mean_s: 808
  demo_mean_steps: 24227.5
  goal_categories: [book.n.02, box.n.01]
  goal_clauses: 1
  goal_predicates: [inside]
  goal_quantifiers: [forall]
  object_categories: 5
  objects: 13
  rooms_loaded: [living_room_0]
  scene_model: house_double_floor_upper
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

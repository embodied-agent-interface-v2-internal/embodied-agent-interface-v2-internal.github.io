---
title: Sorting Vegetables
task_id: sorting_vegetables
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: 'Sort the vegetables from the two wicker baskets on the kitchen floor into the mixing bowls on the kitchen countertop: put all three bok choy and all three Vidalia onions together into one mixing bowl; put both leeks and both broccoli together into a second mixing bowl; and put all three sweet corn into a third mixing bowl.'
  scene_model: house_single_floor
  rooms: [kitchen]
  demo_duration_s: 397
  oracle_video: https://player.vimeo.com/video/1114058741
  oracle_thumbnail: https://vumbnail.com/1114058741.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 33.95
  demo_eef_m: [46.3, 22.88]
  demo_episodes: 200
  demo_mean_s: 397
  demo_mean_steps: 11903.7
  goal_categories:
    - bok_choy.n.02
    - broccoli.n.02
    - leek.n.02
    - mixing_bowl.n.01
    - sweet_corn.n.02
    - vidalia_onion.n.01
  goal_clauses: 3
  goal_predicates: [inside]
  goal_quantifiers: [exists, forall]
  object_categories: 10
  objects: 21
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

---
title: Spraying Fruit Trees
task_id: spraying_fruit_trees
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: In the garden, pick up the pesticide atomizer on the floor and spray pesticide onto both trees until each tree trunk is fully covered.
  scene_model: house_double_floor_lower
  rooms: [garden]
  demo_duration_s: 278
  oracle_video: https://player.vimeo.com/video/1114060748
  oracle_thumbnail: https://vumbnail.com/1114060748.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 23.5
  demo_eef_m: [21.59, 7.56]
  demo_episodes: 200
  demo_mean_s: 278
  demo_mean_steps: 8345.9
  goal_categories: [pesticide.n.01, tree.n.01]
  goal_clauses: 2
  goal_predicates: [covered]
  object_categories: 5
  objects: 6
  rooms_loaded: [corridor_0, garden_0, kitchen_0, living_room_0]
  scene_model: house_double_floor_lower
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

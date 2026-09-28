---
title: Hanging Pictures
task_id: hanging_pictures
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Pick up the poster from the kitchen countertop and hang it on one of the wall nails in the kitchen.
  scene_model: house_double_floor_lower
  rooms: [kitchen]
  demo_duration_s: 80
  oracle_video: https://player.vimeo.com/video/1114060330
  oracle_thumbnail: https://vumbnail.com/1114060330.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 6.63
  demo_eef_m: [2.37, 3.94]
  demo_episodes: 200
  demo_mean_s: 80
  demo_mean_steps: 2387.4
  goal_categories: [poster.n.01, wall_nail.n.01]
  goal_clauses: 1
  goal_predicates: [attached]
  goal_quantifiers: [exists]
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

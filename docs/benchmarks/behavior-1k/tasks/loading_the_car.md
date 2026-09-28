---
title: Loading The Car
task_id: loading_the_car
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Put the digital camera from the living room table into the container on the living room floor. Then take the container and the tennis racket to the garage, place both in the car trunk, and close it.
  scene_model: house_double_floor_lower
  rooms: [living_room, garage]
  demo_duration_s: 641
  oracle_video: https://player.vimeo.com/video/1114057519
  oracle_thumbnail: https://vumbnail.com/1114057519.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 48.32
  demo_eef_m: [18.59, 22.1]
  demo_episodes: 200
  demo_mean_s: 641
  demo_mean_steps: 19226.4
  goal_categories: [car.n.01, container.n.01, digital_camera.n.01, tennis_racket.n.01]
  goal_clauses: 3
  goal_predicates: [inside]
  object_categories: 7
  objects: 8
  rooms_loaded: [corridor_0, garage_0, garden_0, kitchen_0, living_room_0]
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

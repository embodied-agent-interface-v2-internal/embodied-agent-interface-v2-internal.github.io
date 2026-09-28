---
title: Wash Dog Toys
task_id: wash_dog_toys
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: In the utility room, take the two teddy toys, the tennis ball, and the softball out of the cabinet and wash them in the washer so that both teddies are free of dirt and dust, the tennis ball has no debris, and the softball has no dirt.
  scene_model: house_single_floor
  rooms: [utility_room]
  demo_duration_s: 374
  oracle_video: https://player.vimeo.com/video/1114060219
  oracle_thumbnail: https://vumbnail.com/1114060219.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 46.58
  demo_eef_m: [16.0, 15.88]
  demo_episodes: 200
  demo_mean_s: 374
  demo_mean_steps: 11222.8
  goal_categories: [debris.n.01, dirt.n.02, dust.n.01, softball.n.01, teddy.n.01, tennis_ball.n.01]
  goal_clauses: 3
  goal_predicates: [covered]
  goal_quantifiers: [forall]
  object_categories: 10
  objects: 11
  rooms_loaded: [corridor_0, dining_room_0, entryway_0, garden_0, utility_room_0]
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

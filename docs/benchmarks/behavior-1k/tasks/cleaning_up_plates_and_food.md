---
title: Cleaning Up Plates and Food
task_id: cleaning_up_plates_and_food
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: From the breakfast table in the kitchen, move both pizzas - keeping each on its plate - into the same refrigerator, put both bowls into one sink, and make sure the refrigerator is closed.
  scene_model: house_double_floor_lower
  rooms: [kitchen]
  demo_duration_s: 457
  oracle_video: https://player.vimeo.com/video/1114054554
  oracle_thumbnail: https://vumbnail.com/1114054554.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 35.97
  demo_eef_m: [14.59, 19.94]
  demo_episodes: 200
  demo_mean_s: 457
  demo_mean_steps: 13696.2
  goal_categories: [bowl.n.01, electric_refrigerator.n.01, pizza.n.01, plate.n.04, sink.n.01]
  goal_clauses: 4
  goal_predicates: [inside, ontop, open]
  goal_quantifiers: [exists, forall, forpairs]
  object_categories: 8
  objects: 13
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

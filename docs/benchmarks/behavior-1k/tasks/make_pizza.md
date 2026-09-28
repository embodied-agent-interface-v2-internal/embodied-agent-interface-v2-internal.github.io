---
title: Make Pizza
task_id: make_pizza
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: 'Make a pizza on the cookie sheet in the kitchen: take the grated cheese, the four pieces of pepperoni, and the two mushrooms from their tupperware containers in the refrigerator; chop the Vidalia onion on the chopping board with the knife, and also chop the two whole mushrooms in half; top the pizza dough that''s already on the cookie sheet with the cheese, pepperoni, halved mushrooms, and chopped onion; bake it in the oven until it becomes a pizza, and leave the finished pizza on the cookie sheet.'
  scene_model: house_double_floor_lower
  rooms: [kitchen]
  demo_duration_s: 640
  oracle_video: https://player.vimeo.com/video/1114061917
  oracle_thumbnail: https://vumbnail.com/1114061917.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 56.87
  demo_eef_m: [33.52, 44.07]
  demo_episodes: 200
  demo_mean_s: 640
  demo_mean_steps: 19186.9
  goal_categories: [cookie_sheet.n.01, pizza.n.01]
  goal_clauses: 2
  goal_predicates: [ontop, real]
  object_categories: 17
  objects: 23
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

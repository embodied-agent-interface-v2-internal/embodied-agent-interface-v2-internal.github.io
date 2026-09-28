---
title: Set Up A Coffee Station In Your Kitchen
task_id: set_up_a_coffee_station_in_your_kitchen
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: 'Set up a coffee station on the kitchen countertop: keep the coffee maker on the countertop, move the bottle of coffee from the kitchen shelf to the counter next to the coffee maker, place a paper coffee filter on top of the coffee maker, put the saucer next to the coffee maker with the coffee cup on the saucer, and place the electric kettle next to the coffee maker.'
  scene_model: house_single_floor
  rooms: [kitchen]
  demo_duration_s: 209
  oracle_video: https://player.vimeo.com/video/1114056931
  oracle_thumbnail: https://vumbnail.com/1114056931.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 17.36
  demo_eef_m: [9.57, 10.72]
  demo_episodes: 200
  demo_mean_s: 209
  demo_mean_steps: 6266.2
  goal_categories:
    - bottle__of__coffee.n.01
    - coffee_cup.n.01
    - coffee_maker.n.01
    - countertop.n.01
    - electric_kettle.n.01
    - paper_coffee_filter.n.01
    - saucer.n.02
  goal_clauses: 6
  goal_predicates: [nextto, ontop]
  object_categories: 11
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

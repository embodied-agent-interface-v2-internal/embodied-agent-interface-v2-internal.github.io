---
title: Sorting Household Items
task_id: sorting_household_items
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: 'From the two baskets on the bedroom floor, take out the items and organize them in the bathroom: place both detergent bottles under the bathroom sink next to each other; put the box of sanitary napkins on the bathroom shelf; set the soap dispenser on the sink; make sure the cup remains on the sink; put both the toothpaste tube and the toothbrush inside the cup.'
  scene_model: house_single_floor
  rooms: [bedroom, bathroom]
  demo_duration_s: 527
  oracle_video: https://player.vimeo.com/video/1114059574
  oracle_thumbnail: https://vumbnail.com/1114059574.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 50.91
  demo_eef_m: [25.34, 28.24]
  demo_episodes: 200
  demo_mean_s: 527
  demo_mean_steps: 15807.8
  goal_categories:
    - bottle__of__detergent.n.01
    - box__of__sanitary_napkin.n.01
    - cup.n.01
    - shelf.n.01
    - sink.n.01
    - soap_dispenser.n.01
    - toothbrush.n.01
    - tube__of__toothpaste.n.01
  goal_clauses: 7
  goal_predicates: [inside, nextto, ontop, under]
  goal_quantifiers: [forall]
  object_categories: 11
  objects: 13
  rooms_loaded: [bathroom_0, bathroom_1, bedroom_0, corridor_0, dining_room_0, entryway_0, garden_0]
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

---
title: Preparing Lunch Box
task_id: preparing_lunch_box
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Put both apple halves, the club sandwich, and the chocolate chip cookie from the chopping board on the kitchen countertop into the packing box on the countertop. Then take the bottle of tea out of the refrigerator, put it into the same box, and close the refrigerator when you're done.
  scene_model: house_single_floor
  rooms: [kitchen]
  demo_duration_s: 275
  oracle_video: https://player.vimeo.com/video/1114057330
  oracle_thumbnail: https://vumbnail.com/1114057330.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 21.4
  demo_eef_m: [14.09, 17.24]
  demo_episodes: 200
  demo_mean_s: 275
  demo_mean_steps: 8245.3
  goal_categories:
    - bottle__of__tea.n.01
    - chocolate_chip_cookie.n.01
    - club_sandwich.n.01
    - electric_refrigerator.n.01
    - half__apple.n.01
    - packing_box.n.02
  goal_clauses: 5
  goal_predicates: [inside, open]
  goal_quantifiers: [forall]
  object_categories: 10
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

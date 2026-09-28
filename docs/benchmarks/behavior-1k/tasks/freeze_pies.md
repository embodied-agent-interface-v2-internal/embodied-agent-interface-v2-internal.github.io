---
title: Freeze Pies
task_id: freeze_pies
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: In the kitchen, take the two apple pies from the plates on the countertop, put each pie into a separate tupperware container taken from the cabinet, place both tupperwares inside the refrigerator, close the refrigerator, and leave them until the pies are frozen.
  scene_model: house_single_floor
  rooms: [kitchen]
  demo_duration_s: 415
  oracle_video: https://player.vimeo.com/video/1114061625
  oracle_thumbnail: https://vumbnail.com/1114061625.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 35.44
  demo_eef_m: [26.41, 31.14]
  demo_episodes: 200
  demo_mean_s: 415
  demo_mean_steps: 12455.2
  goal_categories: [apple_pie.n.01, electric_refrigerator.n.01, tupperware.n.01]
  goal_clauses: 4
  goal_predicates: [frozen, inside, open]
  goal_quantifiers: [forall, forpairs]
  object_categories: 8
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

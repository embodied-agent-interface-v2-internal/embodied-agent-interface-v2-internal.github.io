---
title: Composting Waste
task_id: composting_waste
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2025-carryover
  instruction: ''
  scene_model: Rs_int
  rooms: [entryway, kitchen, living_room]
  demo_duration_s: 115
  oracle_video: https://www.youtube.com/embed/RR3PLEFcdYg
  oracle_thumbnail: https://img.youtube.com/vi/RR3PLEFcdYg/hqdefault.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 6.44
  demo_eef_m: [10.55, 4.44]
  demo_episodes: 200
  demo_mean_s: 121
  demo_mean_steps: 3638.6
  goal_categories: [ashcan.n.01, half__banana.n.01, half__pomegranate.n.01]
  goal_clauses: 2
  goal_predicates: [inside]
  object_categories: 6
  objects: 8
  rooms_loaded: [entryway_0, kitchen_0, bedroom_0, living_room_0]
  scene_model: Rs_int
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

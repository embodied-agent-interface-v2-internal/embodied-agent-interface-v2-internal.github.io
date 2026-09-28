---
title: Store Honey
task_id: store_honey
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2025-carryover
  instruction: ''
  scene_model: Rs_int
  rooms: [bedroom, entryway, kitchen, living_room]
  demo_duration_s: 193
  oracle_video: https://www.youtube.com/embed/oFu38YPgVEU
  oracle_thumbnail: https://img.youtube.com/vi/oFu38YPgVEU/hqdefault.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 12.07
  demo_eef_m: [7.56, 15.32]
  demo_episodes: 200
  demo_mean_s: 226
  demo_mean_steps: 6766.8
  goal_categories: [cabinet.n.01, jar__of__honey.n.01]
  goal_clauses: 1
  goal_predicates: [inside]
  object_categories: 5
  objects: 5
  rooms_loaded: [bedroom_0, entryway_0, kitchen_0, living_room_0]
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

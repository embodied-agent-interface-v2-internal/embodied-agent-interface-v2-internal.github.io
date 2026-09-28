---
title: Polishing Shoes
task_id: polishing_shoes
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2025-carryover
  instruction: ''
  scene_model: hotel_suite_large
  rooms: [bedroom]
  demo_duration_s: 363
  oracle_video: https://www.youtube.com/embed/bSCbEvVJykI
  oracle_thumbnail: https://img.youtube.com/vi/bSCbEvVJykI/hqdefault.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 17.16
  demo_eef_m: [20.1, 21.11]
  demo_episodes: 200
  demo_mean_s: 358
  demo_mean_steps: 10738.0
  goal_categories: [dust.n.01, footstool.n.01, scrub_brush.n.01, shoe.n.01, stand.n.04]
  goal_clauses: 5
  goal_predicates: [covered, nextto, ontop]
  goal_quantifiers: [exists]
  object_categories: 7
  objects: 9
  rooms_loaded: [bedroom_0, bathroom_0]
  scene_model: hotel_suite_large
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

---
title: Cook Broccolini
task_id: cook_broccolini
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2025-carryover
  instruction: ''
  scene_model: restaurant_diner
  rooms: [kitchen]
  demo_duration_s: 137
  oracle_video: https://www.youtube.com/embed/NXoYiAs_KCs
  oracle_thumbnail: https://img.youtube.com/vi/NXoYiAs_KCs/hqdefault.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 10.87
  demo_eef_m: [5.91, 6.31]
  demo_episodes: 200
  demo_mean_s: 154
  demo_mean_steps: 4617.8
  goal_categories: [broccolini.n.01, clove.n.03, frying_pan.n.01, stove.n.01]
  goal_clauses: 3
  goal_predicates: [cooked, ontop]
  goal_quantifiers: [forall]
  object_categories: 8
  objects: 11
  rooms_loaded: [kitchen_0]
  scene_model: restaurant_diner
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

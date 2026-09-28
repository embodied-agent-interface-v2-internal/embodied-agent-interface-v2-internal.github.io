---
title: Organizing Art Supplies
task_id: organizing_art_supplies
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2025-carryover
  instruction: ''
  scene_model: house_double_floor_upper
  rooms: [bedroom]
  demo_duration_s: 228
  oracle_video: https://www.youtube.com/embed/M1D9oCKBJZg
  oracle_thumbnail: https://img.youtube.com/vi/M1D9oCKBJZg/hqdefault.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 11.51
  demo_eef_m: [12.29, 12.36]
  demo_episodes: 200
  demo_mean_s: 206
  demo_mean_steps: 6194.4
  goal_categories:
    - carryall.n.01
    - desk.n.01
    - glue_stick.n.01
    - marker.n.03
    - paintbrush.n.01
    - rubber_eraser.n.01
  goal_clauses: 5
  goal_predicates: [inside, ontop]
  object_categories: 8
  objects: 8
  rooms_loaded: [bathroom_0, bedroom_0, bedroom_1, bedroom_2, living_room_0]
  scene_model: house_double_floor_upper
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

---
title: Tidying Living Room
task_id: tidying_living_room
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2025-carryover
  instruction: ''
  scene_model: house_double_floor_upper
  rooms: [living_room]
  demo_duration_s: 316
  oracle_video: https://www.youtube.com/embed/aTCNKnjR03c
  oracle_thumbnail: https://img.youtube.com/vi/aTCNKnjR03c/hqdefault.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 20.65
  demo_eef_m: [18.47, 18.56]
  demo_episodes: 200
  demo_mean_s: 419
  demo_mean_steps: 12565.9
  goal_categories:
    - bookcase.n.01
    - coffee_table.n.01
    - desk.n.01
    - hardback.n.01
    - newspaper.n.03
    - notebook.n.01
    - pot_plant.n.01
  goal_clauses: 4
  goal_predicates: [inside, ontop]
  goal_quantifiers: [exists]
  object_categories: 9
  objects: 9
  rooms_loaded: [living_room_0]
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

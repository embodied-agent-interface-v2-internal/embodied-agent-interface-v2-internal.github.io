---
title: Organizing School Stuff
task_id: organizing_school_stuff
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2025-carryover
  instruction: ''
  scene_model: house_single_floor
  rooms: [bedroom]
  demo_duration_s: 426
  oracle_video: https://www.youtube.com/embed/GO2Bw-0OY7M
  oracle_thumbnail: https://img.youtube.com/vi/GO2Bw-0OY7M/hqdefault.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 26.16
  demo_eef_m: [24.24, 27.61]
  demo_episodes: 200
  demo_mean_s: 486
  demo_mean_steps: 14591.9
  goal_categories:
    - bed.n.01
    - book.n.02
    - calculator.n.02
    - carryall.n.01
    - folder.n.02
    - pen.n.01
    - pencil.n.01
  goal_clauses: 6
  goal_predicates: [inside, ontop]
  object_categories: 10
  objects: 10
  rooms_loaded: [bedroom_0, closet_0, closet_1, garden_0, corridor_0, bathroom_1]
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

---
title: Installing A Scanner
task_id: installing_a_scanner
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2025-carryover
  instruction: ''
  scene_model: office_cubicles_right
  rooms: [private_office]
  demo_duration_s: 122
  oracle_video: https://www.youtube.com/embed/fVy3dPNOBYk
  oracle_thumbnail: https://img.youtube.com/vi/fVy3dPNOBYk/hqdefault.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 6.41
  demo_eef_m: [7.07, 7.89]
  demo_episodes: 200
  demo_mean_s: 142
  demo_mean_steps: 4258.5
  goal_categories: [laptop.n.01, scanner.n.02]
  goal_clauses: 2
  goal_predicates: [nextto, toggled_on]
  object_categories: 5
  objects: 5
  rooms_loaded:
    - corridor_0
    - private_office_0
    - private_office_1
    - private_office_2
    - private_office_3
    - copy_room_0
    - shared_office_0
  scene_model: office_cubicles_right
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

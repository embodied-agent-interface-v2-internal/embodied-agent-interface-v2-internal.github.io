---
title: Clean a Trumpet
task_id: clean_a_trumpet
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: In the bedroom, pick up the scrub brush from the desk and scrub the cornet (trumpet) on the desk until it's no longer covered in dust.
  scene_model: house_double_floor_upper
  rooms: [bedroom]
  demo_duration_s: 177
  oracle_video: https://player.vimeo.com/video/1114060606
  oracle_thumbnail: https://vumbnail.com/1114060606.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 12.39
  demo_eef_m: [7.66, 11.5]
  demo_episodes: 200
  demo_mean_s: 177
  demo_mean_steps: 5307.2
  goal_categories: [cornet.n.01, dust.n.01]
  goal_clauses: 1
  goal_predicates: [covered]
  object_categories: 6
  objects: 6
  rooms_loaded: [bedroom_0, bedroom_1, bedroom_2]
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

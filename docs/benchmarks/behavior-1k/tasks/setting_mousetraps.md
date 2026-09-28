---
title: Setting Mousetraps
task_id: setting_mousetraps
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Take the four mousetraps from the cabinet in the bathroom and place them on the bathroom floor. Make sure all four end up on the same floor surface, and ensure that at least two of them are either under or directly next to the same bathroom sink.
  scene_model: house_double_floor_upper
  rooms: [bathroom]
  demo_duration_s: 339
  oracle_video: https://player.vimeo.com/video/1114054686
  oracle_thumbnail: https://vumbnail.com/1114054686.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 31.6
  demo_eef_m: [13.15, 12.38]
  demo_episodes: 200
  demo_mean_s: 340
  demo_mean_steps: 10196.1
  goal_categories: [floor.n.01, mousetrap.n.01, sink.n.01]
  goal_clauses: 2
  goal_counts: [2]
  goal_predicates: [nextto, ontop, under]
  goal_quantifiers: [exists, forall, forn]
  object_categories: 5
  objects: 10
  rooms_loaded: [bathroom_0]
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

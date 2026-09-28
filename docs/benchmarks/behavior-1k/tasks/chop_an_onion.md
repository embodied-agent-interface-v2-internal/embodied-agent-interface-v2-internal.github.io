---
title: Chop an Onion
task_id: chop_an_onion
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: In the kitchen, take the Vidalia onion out of the sink, dice it on the chopping board with the paring knife, put the diced onion into the bowl on the countertop, then place both the paring knife and the chopping board into the sink.
  scene_model: house_double_floor_lower
  rooms: [kitchen]
  demo_duration_s: 213
  oracle_video: https://player.vimeo.com/video/1114061062
  oracle_thumbnail: https://vumbnail.com/1114061062.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 17.0
  demo_eef_m: [6.37, 11.05]
  demo_episodes: 200
  demo_mean_s: 213
  demo_mean_steps: 6399.8
  goal_categories: [bowl.n.01, chopping_board.n.01, diced__vidalia_onion.n.01, parer.n.02, sink.n.01]
  goal_clauses: 4
  goal_predicates: [contains, inside, real]
  object_categories: 9
  objects: 9
  rooms_loaded: [corridor_0, garden_0, kitchen_0, living_room_0]
  scene_model: house_double_floor_lower
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

---
title: Rearranging Kitchen Furniture
task_id: rearranging_kitchen_furniture
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Move the toaster, food processor, and French press from the kitchen countertop into the same kitchen cabinet, and make sure that cabinet is closed at the end.
  scene_model: house_double_floor_lower
  rooms: [kitchen]
  demo_duration_s: 298
  oracle_video: https://player.vimeo.com/video/1114056046
  oracle_thumbnail: https://vumbnail.com/1114056046.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 25.89
  demo_eef_m: [14.53, 16.37]
  demo_episodes: 200
  demo_mean_s: 298
  demo_mean_steps: 8943.0
  goal_categories: [cabinet.n.01, food_processor.n.01, french_press.n.01, toaster.n.02]
  goal_clauses: 1
  goal_predicates: [inside, open]
  goal_quantifiers: [exists]
  object_categories: 7
  objects: 8
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

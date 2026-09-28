---
title: Slicing Vegetables
task_id: slicing_vegetables
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: From the refrigerator in the kitchen, take out the two bell peppers, the two beets, and the zucchini. Then, on either chopping board on the countertop, use the parer to dice all of them so that only diced bell pepper, diced beet, and diced zucchini remain. Make sure the refrigerator is closed when you finish.
  scene_model: house_single_floor
  rooms: [kitchen]
  demo_duration_s: 495
  oracle_video: https://player.vimeo.com/video/1114061183
  oracle_thumbnail: https://vumbnail.com/1114061183.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 40.63
  demo_eef_m: [17.75, 22.47]
  demo_episodes: 200
  demo_mean_s: 495
  demo_mean_steps: 14844.9
  goal_categories:
    - beet.n.02
    - bell_pepper.n.02
    - diced__beet.n.01
    - diced__bell_pepper.n.01
    - diced__zucchini.n.01
    - electric_refrigerator.n.01
    - zucchini.n.02
  goal_clauses: 7
  goal_predicates: [open, real]
  goal_quantifiers: [forall]
  object_categories: 12
  objects: 15
  rooms_loaded:
    - corridor_0
    - dining_room_0
    - entryway_0
    - garden_0
    - kitchen_0
    - living_room_0
    - living_room_1
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

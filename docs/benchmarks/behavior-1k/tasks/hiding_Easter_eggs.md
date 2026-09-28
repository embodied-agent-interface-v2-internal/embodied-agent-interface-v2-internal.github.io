---
title: Hiding Easter Eggs
task_id: hiding_Easter_eggs
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Take the three Easter eggs out of the wicker basket on the lawn in the garden, then place them on the lawn next to a single tree (choose any tree) so that all three eggs are next to the same tree and none are left in the basket.
  scene_model: house_double_floor_lower
  rooms: [garden]
  demo_duration_s: 254
  oracle_video: https://player.vimeo.com/video/1114055436
  oracle_thumbnail: https://vumbnail.com/1114055436.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 21.9
  demo_eef_m: [10.72, 12.23]
  demo_episodes: 200
  demo_mean_s: 254
  demo_mean_steps: 7619.7
  goal_categories: [easter_egg.n.01, lawn.n.01, tree.n.01, wicker_basket.n.01]
  goal_clauses: 2
  goal_predicates: [inside, nextto, ontop]
  goal_quantifiers: [exists, forall]
  object_categories: 5
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

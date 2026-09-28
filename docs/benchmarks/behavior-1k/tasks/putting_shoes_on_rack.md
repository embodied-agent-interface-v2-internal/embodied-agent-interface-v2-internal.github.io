---
title: Putting Shoes On Rack
task_id: putting_shoes_on_rack
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Pick up the two gym shoes and the two sandals from the corridor floor and place them onto the hallstand (shoe rack) in the corridor, making sure they are on the rack and not on the floor. Arrange them so the two gym shoes are next to each other and the two sandals are next to each other.
  scene_model: house_double_floor_lower
  rooms: [corridor]
  demo_duration_s: 258
  oracle_video: https://player.vimeo.com/video/1114058985
  oracle_thumbnail: https://vumbnail.com/1114058985.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 27.02
  demo_eef_m: [8.85, 9.75]
  demo_episodes: 200
  demo_mean_s: 258
  demo_mean_steps: 7726.1
  goal_categories: [floor.n.01, gym_shoe.n.01, hallstand.n.01, sandal.n.01]
  goal_clauses: 4
  goal_predicates: [nextto, touching]
  goal_quantifiers: [forall]
  object_categories: 5
  objects: 7
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

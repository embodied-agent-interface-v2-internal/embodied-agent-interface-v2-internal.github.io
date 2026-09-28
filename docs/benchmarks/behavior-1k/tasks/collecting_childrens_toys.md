---
title: Collecting Children's Toys
task_id: collecting_childrens_toys
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Pick up the two dice from the bed, the two teddy bears from the floor, and the two board games (one from the desk and one from the bed), and place them all inside the same bookcase in the child's room.
  scene_model: house_single_floor
  rooms: [childs_room]
  demo_duration_s: 640
  oracle_video: https://player.vimeo.com/video/1114058872
  oracle_thumbnail: https://vumbnail.com/1114058872.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 58.4
  demo_eef_m: [24.15, 25.81]
  demo_episodes: 200
  demo_mean_s: 640
  demo_mean_steps: 19186.3
  goal_categories: [board_game.n.01, bookcase.n.01, die.n.01, teddy.n.01, train_set.n.01]
  goal_clauses: 1
  goal_predicates: [inside]
  goal_quantifiers: [exists, forall]
  object_categories: 9
  objects: 13
  rooms_loaded:
    - childs_room_0
    - childs_room_1
    - childs_room_2
    - corridor_0
    - dining_room_0
    - entryway_0
    - garden_0
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

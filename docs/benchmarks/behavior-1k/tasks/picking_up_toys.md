---
title: Picking Up Toys
task_id: picking_up_toys
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Put all the toys in the child's room - the three board games (two on the bed and one on the table), the two jigsaw puzzles on the table, and the tennis ball on the table - inside the toy box on the table in the child's room.
  scene_model: house_single_floor
  rooms: [childs_room]
  demo_duration_s: 630
  oracle_video: https://player.vimeo.com/video/1114054920
  oracle_thumbnail: https://vumbnail.com/1114054920.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 47.05
  demo_eef_m: [20.41, 21.55]
  demo_episodes: 200
  demo_mean_s: 630
  demo_mean_steps: 18890.5
  goal_categories: [board_game.n.01, jigsaw_puzzle.n.01, tennis_ball.n.01, toy_box.n.01]
  goal_clauses: 3
  goal_predicates: [inside]
  goal_quantifiers: [exists, forall]
  object_categories: 8
  objects: 11
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

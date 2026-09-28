---
title: Putting Up Christmas Decorations Inside
task_id: putting_up_Christmas_decorations_inside
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: In the living room, take the wreath, three candy canes, and two pillar candles out of the wicker basket. Place the wreath and two of the candy canes on the same living-room sofa. Put the remaining candy cane on top of a dining-room table. Put both pillar candles together on top of one dining-room table (they can share the same table). Finally, place all three gift boxes under or right next to the Christmas tree in the living room.
  scene_model: house_single_floor
  rooms: [kitchen, living_room]
  demo_duration_s: 457
  oracle_video: https://player.vimeo.com/video/1114056731
  oracle_thumbnail: https://vumbnail.com/1114056731.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 41.33
  demo_eef_m: [16.75, 22.54]
  demo_episodes: 200
  demo_mean_s: 457
  demo_mean_steps: 13718.8
  goal_categories:
    - candy_cane.n.01
    - christmas_tree.n.05
    - gift_box.n.01
    - pillar_candle.n.01
    - sofa.n.01
    - table.n.02
    - wreath.n.01
  goal_clauses: 5
  goal_counts: [1, 2]
  goal_predicates: [nextto, ontop, touching, under]
  goal_quantifiers: [exists, forall, forn]
  object_categories: 10
  objects: 17
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

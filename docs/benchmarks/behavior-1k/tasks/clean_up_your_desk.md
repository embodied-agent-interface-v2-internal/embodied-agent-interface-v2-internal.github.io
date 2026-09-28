---
title: Clean Up Your Desk
task_id: clean_up_your_desk
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: 'In the child''s room, clean up the desk: put both folders and both paperback books into the bookcase; put the pencil and both pens into the pencil case and leave the case on the desk; take the stapler out of the bookcase and place it on the desk; move the laptop from the bed onto the desk and close it.'
  scene_model: house_single_floor
  rooms: [childs_room]
  demo_duration_s: 714
  oracle_video: https://player.vimeo.com/video/1114059839
  oracle_thumbnail: https://vumbnail.com/1114059839.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 60.51
  demo_eef_m: [38.18, 35.57]
  demo_episodes: 200
  demo_mean_s: 714
  demo_mean_steps: 21417.9
  goal_categories:
    - bookcase.n.01
    - desk.n.01
    - folder.n.02
    - laptop.n.01
    - paperback_book.n.01
    - pen.n.01
    - pencil.n.01
    - pencil_box.n.01
    - stapler.n.01
  goal_clauses: 8
  goal_predicates: [inside, ontop, open]
  goal_quantifiers: [forall]
  object_categories: 13
  objects: 16
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

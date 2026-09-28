---
title: Outfit A Basic Toolbox
task_id: outfit_a_basic_toolbox
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: In the utility room, put the drill, pliers, flashlight, Allen wrench, and screwdriver from the tabletop into the toolbox, keep the toolbox on the tabletop, and close the toolbox.
  scene_model: house_single_floor
  rooms: [utility_room]
  demo_duration_s: 355
  oracle_video: https://player.vimeo.com/video/1114058641
  oracle_thumbnail: https://vumbnail.com/1114058641.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 31.68
  demo_eef_m: [18.18, 20.07]
  demo_episodes: 200
  demo_mean_s: 355
  demo_mean_steps: 10638.0
  goal_categories:
    - allen_wrench.n.01
    - drill.n.01
    - flashlight.n.01
    - pliers.n.01
    - screwdriver.n.01
    - tabletop.n.01
    - toolbox.n.01
  goal_clauses: 7
  goal_predicates: [inside, ontop, open]
  object_categories: 9
  objects: 9
  rooms_loaded: [corridor_0, dining_room_0, entryway_0, garden_0, utility_room_0]
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

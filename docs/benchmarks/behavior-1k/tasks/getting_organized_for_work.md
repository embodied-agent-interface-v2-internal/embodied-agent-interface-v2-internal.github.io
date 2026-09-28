---
title: Getting Organized For Work
task_id: getting_organized_for_work
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: In the bedroom, organize the workspace by keeping the computer under the desk, ensuring the monitor is on the desk, placing the keyboard on the desk next to the monitor, placing the mouse on the desk next to the keyboard, moving the folder from the swivel chair onto the desk next to the mouse, stacking the notebook on top of the folder with the pen on top of the notebook, and positioning the swivel chair next to the desk.
  scene_model: house_double_floor_upper
  rooms: [bedroom]
  demo_duration_s: 522
  oracle_video: https://player.vimeo.com/video/1114059683
  oracle_thumbnail: https://vumbnail.com/1114059683.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 47.34
  demo_eef_m: [17.27, 26.59]
  demo_episodes: 200
  demo_mean_s: 522
  demo_mean_steps: 15671.0
  goal_categories:
    - computer.n.01
    - desk.n.01
    - folder.n.02
    - keyboard.n.01
    - monitor.n.04
    - mouse.n.04
    - notebook.n.01
    - pen.n.01
    - swivel_chair.n.01
  goal_clauses: 10
  goal_predicates: [nextto, ontop, under]
  object_categories: 11
  objects: 11
  rooms_loaded: [bedroom_0, bedroom_1, bedroom_2]
  scene_model: house_double_floor_upper
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

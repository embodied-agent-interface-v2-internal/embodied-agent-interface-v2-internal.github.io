---
title: Hammer Loose Nail
task_id: hammer_loose_nail
benchmark: vlabench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/OpenMOSS/VLABench @ cf588fe (assets @ 08d7a44)
  synced: '2026-09-28'
  instruction: There is a loose nail on the wall, strenthen it.
  scene_model: vlabench_composite
  native_task: hammer_loose_nail
  group: composite
  tier: privileged
  seed: 0
  registered_at: https://github.com/OpenMOSS/VLABench/blob/cf588fe60c0c7282174fe979f5913170cfe69017/VLABench/tasks/hierarchical_tasks/composite/hammer_nail_series.py#L151
  source_file: VLABench/tasks/hierarchical_tasks/composite/hammer_nail_series.py
  robot: 'Franka Panda: 9 absolute actuator targets (7 arm joints in radians, 2 finger slides in metres)'
  control: 10 Hz (each control held 0.1 s, 100 physics substeps); at most 4000 controls
  observation: 'privileged state: object and robot poses, official skills, IK and planning'
  success_criteria:
    - the native VLABench success condition of hammer_loose_nail, when the trajectory
      ends (controls after native termination are rejected)
    - both fresh-process replays of the trajectory meet it and end in the same exact state
  frozen_instance: our task directory vlabench-hammer-loose-nail-i00 (initial state sha256 a3ff8fdeaa53)
  reference_solution: 'none validated: our reference replays exactly but does not meet the native condition'
  reference_note: our reference trajectory was replayed and does not meet the native condition
  agent_budget: 3600 s of wall clock per mode
  scene_image: hammer_loose_nail.jpg
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/vlabench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- Where there is a demo, it is the validated reference solution's controls for this frozen
     instance, replayed by our trusted renderer (camera 2, 10 fps = real time). Say whether
     the trajectory is clean and what it relies on. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

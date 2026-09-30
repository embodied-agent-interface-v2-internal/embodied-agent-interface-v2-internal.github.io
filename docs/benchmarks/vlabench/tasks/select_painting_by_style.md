---
title: Select Painting By Style
task_id: select_painting_by_style
benchmark: vlabench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/OpenMOSS/VLABench @ cf588fe (assets @ 08d7a44)
  synced: '2026-09-28'
  scene_model: vlabench_primitive
  native_task: select_painting_by_style
  group: primitive
  tier: privileged
  seed: 0
  registered_at: https://github.com/OpenMOSS/VLABench/blob/cf588fe60c0c7282174fe979f5913170cfe69017/VLABench/tasks/hierarchical_tasks/primitive/select_painting_series.py#L207
  source_file: VLABench/tasks/hierarchical_tasks/primitive/select_painting_series.py
  robot: 'Franka Panda: 9 absolute actuator targets (7 arm joints in radians, 2 finger slides in metres)'
  observation: 'privileged state: object and robot poses, official skills, IK and planning'
  frozen_instance: 'not frozen: the native task could not be built at this commit'
  reference_solution: 'none: the task could not be frozen at this commit'
  reference_note: 'KeyError: ''task'''
  agent_budget: 3600 s of wall clock per mode
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

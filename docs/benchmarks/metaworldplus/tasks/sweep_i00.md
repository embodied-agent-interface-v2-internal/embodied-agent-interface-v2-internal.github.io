---
title: Sweep · i00
task_id: sweep_i00
benchmark: metaworldplus

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Farama-Foundation/Metaworld @ 59fc34d
  synced: '2026-09-28'
  instruction: Sweep the object to the target position.
  scene_model: sweep-v3
  environment_id: sweep-v3
  family: sweep
  instance: 0
  seed: 0
  instance_sha: d8d2dd0b1b84a201136323d92bff199cf0ed3c79a022a7cdfdfbe77038b5af31
  robot: Sawyer, fixed wrist, two-finger gripper; mocap XYZ control
  action: '[dx, dy, dz, grip] in [-1, 1]: 0.01 m per unit, grip +1 closes; 80 Hz (5 physics steps of 2.5 ms)'
  horizon: 500 controls (6.25 s simulated)
  success_criteria:
    - the native v3 / reward-v2 success flag, attained at any control of the trajectory
    - both fresh-process replays of the trajectory meet this and end in the same exact
      state
  success_check: '"success": float(target_to_obj <= 0.05)'
  source_file: metaworld/envs/sawyer_sweep_v3.py
  env_class: SawyerSweepEnvV3
  limited_target: 'in privileged state only: no native marker renders and the task sentence does not name it: target is (0.5, object y, 0.01): the table right edge; the native goal site stays at the world origin (0 rendered pixels in every camera, also in a fresh upstream env) and the language only says "the target position"'
  limited_mode: 'not evaluated: the goal is in privileged state only'
  frozen_instance: full MuJoCo state, model arrays, task caches and RNG; our task directory metaworldplus-sweep-privileged-i00 (tree sha256 a66909ea0eb0)
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/metaworldplus.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- The demo is the upstream scripted policy's controls for this frozen instance, replayed
     by our trusted renderer (corner and corner3 cameras, 80 fps = real time). Say whether
     the trajectory is clean and what it relies on. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

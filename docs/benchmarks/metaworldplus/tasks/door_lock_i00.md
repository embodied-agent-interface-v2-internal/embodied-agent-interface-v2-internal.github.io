---
title: Door Lock · i00
task_id: door_lock_i00
benchmark: metaworldplus

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Farama-Foundation/Metaworld @ 59fc34d
  synced: '2026-09-28'
  instruction: Move the door lock into its locked position.
  scene_model: door-lock-v3
  environment_id: door-lock-v3
  family: door_lock
  instance: 0
  seed: 0
  instance_sha: 65f1e0f5303ad7b62d9d315068126b5eb91bcec902208dd2e5e3c9c087ec0ede
  robot: Sawyer, fixed wrist, two-finger gripper; mocap XYZ control
  action: '[dx, dy, dz, grip] in [-1, 1]: 0.01 m per unit, grip +1 closes; 80 Hz (5 physics steps of 2.5 ms)'
  horizon: 500 controls (6.25 s simulated)
  success_criteria:
    - the native v3 / reward-v2 success flag, attained at any control of the trajectory
    - both fresh-process replays of the trajectory meet this and end in the same exact
      state
  success_check: '"success": float(obj_to_target <= 0.02)'
  source_file: metaworld/envs/sawyer_door_lock_v3.py
  env_class: SawyerDoorLockEnvV3
  limited_target: 'set by visible object or mechanism geometry and the task sentence (audited correction): goal_lock marker is 0.113 m from the target in x/y (2-6 pixels per fixed camera); success is on lock height only; the lock mechanism and the language define the goal.'
  limited_mode: 'evaluated: RGB-D, calibration and proprioception, one sealed episode'
  frozen_instance: full MuJoCo state, model arrays, task caches and RNG; our task directory metaworldplus-door-lock-privileged-i00 (tree sha256 07fe1b7ddac2)
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

---
title: Door Unlock · i00
task_id: door_unlock_i00
benchmark: metaworldplus

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Farama-Foundation/Metaworld @ 59fc34d
  synced: '2026-09-28'
  instruction: Move the door lock into its unlocked position.
  scene_model: door-unlock-v3
  environment_id: door-unlock-v3
  family: door_unlock
  instance: 0
  seed: 0
  instance_sha: 59de1ac839074eaf7526db637a7143a800ef2cb5bc00aae236937d640ec675cc
  robot: Sawyer, fixed wrist, two-finger gripper; mocap XYZ control
  action: '[dx, dy, dz, grip] in [-1, 1]: 0.01 m per unit, grip +1 closes; 80 Hz (5 physics steps of 2.5 ms)'
  horizon: 500 controls (6.25 s simulated)
  success_criteria:
    - the native v3 / reward-v2 success flag, attained at any control of the trajectory
    - both fresh-process replays of the trajectory meet this and end in the same exact
      state
  success_check: '"success": float(obj_to_target <= 0.02)'
  source_file: metaworld/envs/sawyer_door_unlock_v3.py
  env_class: SawyerDoorUnlockEnvV3
  limited_target: 'set by visible object or mechanism geometry and the task sentence (audited correction): goal_unlock/goal_lock sites are fixed world-body sites at XML defaults; nearest marker 0.104 m from the native target; success is |target_x - lock_x| <= 0.02 and the marker x (0.09) differs from target x (0.0033) by 0.087 m. The lock mechanism and the language define the goal.'
  limited_mode: 'evaluated: RGB-D, calibration and proprioception, one sealed episode'
  frozen_instance: full MuJoCo state, model arrays, task caches and RNG; our task directory metaworldplus-door-unlock-privileged-i00 (tree sha256 a3135741e592)
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

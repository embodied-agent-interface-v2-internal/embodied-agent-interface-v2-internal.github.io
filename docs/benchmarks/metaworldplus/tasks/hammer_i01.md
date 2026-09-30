---
title: Hammer · i01
task_id: hammer_i01
benchmark: metaworldplus

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Farama-Foundation/Metaworld @ 59fc34d
  synced: '2026-09-28'
  instruction: Use the hammer to drive the nail.
  scene_model: hammer-v3
  environment_id: hammer-v3
  family: hammer
  instance: 1
  seed: 1
  instance_sha: 776a9f7b604336d14208ba6a9e892c64d1e1d5475208064ac24b085d3e309d05
  robot: Sawyer, fixed wrist, two-finger gripper; mocap XYZ control
  action: '[dx, dy, dz, grip] in [-1, 1]: 0.01 m per unit, grip +1 closes; 80 Hz (5 physics steps of 2.5 ms)'
  horizon: 500 controls (6.25 s simulated)
  success_criteria:
    - the native v3 / reward-v2 success flag, attained at any control of the trajectory
    - both fresh-process replays of the trajectory meet this and end in the same exact
      state
  success_check: '"success": float(success)

    success = bool(self.data.joint("NailSlideJoint").qpos > 0.09)'
  source_file: metaworld/envs/sawyer_hammer_v3.py
  env_class: SawyerHammerEnvV3
  limited_target: 'set by visible object or mechanism geometry and the task sentence: visible nail driven past 0.09 m'
  limited_mode: 'evaluated: RGB-D, calibration and proprioception, one sealed episode'
  frozen_instance: full MuJoCo state, model arrays, task caches and RNG; our task directory metaworldplus-hammer-privileged-i01 (tree sha256 4515e7b196d4)
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

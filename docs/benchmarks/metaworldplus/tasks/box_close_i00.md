---
title: Box Close · i00
task_id: box_close_i00
benchmark: metaworldplus

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Farama-Foundation/Metaworld @ 59fc34d
  synced: '2026-09-28'
  instruction: Move the lid onto the box to close it.
  scene_model: box-close-v3
  environment_id: box-close-v3
  family: box_close
  instance: 0
  seed: 0
  instance_sha: a0fb6bb2776ab1a4d2cd749cf1766739553e745fc5db6edc3ffe96222b396c56
  robot: Sawyer, fixed wrist, two-finger gripper; mocap XYZ control
  action: '[dx, dy, dz, grip] in [-1, 1]: 0.01 m per unit, grip +1 closes; 80 Hz (5 physics steps of 2.5 ms)'
  horizon: 500 controls (6.25 s simulated)
  success_criteria:
    - the native v3 / reward-v2 success flag, attained at any control of the trajectory
    - both fresh-process replays of the trajectory meet this and end in the same exact
      state
  success_check: '"success": float(success)

    success = bool(np.linalg.norm(obs[4:7] - self._target_pos) < 0.08)'
  source_file: metaworld/envs/sawyer_box_close_v3.py
  env_class: SawyerBoxCloseEnvV3
  limited_target: 'a native goal marker that renders in the fixed cameras: lid within 0.08 m of the box goal'
  limited_mode: 'evaluated: RGB-D, calibration and proprioception, one sealed episode'
  frozen_instance: full MuJoCo state, model arrays, task caches and RNG; our task directory metaworldplus-box-close-privileged-i00 (tree sha256 8be23b2c1763)
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

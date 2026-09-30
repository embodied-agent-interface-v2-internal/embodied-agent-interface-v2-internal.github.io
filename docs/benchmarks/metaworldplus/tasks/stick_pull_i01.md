---
title: Stick Pull · i01
task_id: stick_pull_i01
benchmark: metaworldplus

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Farama-Foundation/Metaworld @ 59fc34d
  synced: '2026-09-28'
  instruction: Use the stick to pull the target object.
  scene_model: stick-pull-v3
  environment_id: stick-pull-v3
  family: stick_pull
  instance: 1
  seed: 1
  instance_sha: 8b81bab414f9ae4c6bb690e19e91bad24a144c7f74c8ff068f4903ef5ef2ac39
  robot: Sawyer, fixed wrist, two-finger gripper; mocap XYZ control
  action: '[dx, dy, dz, grip] in [-1, 1]: 0.01 m per unit, grip +1 closes; 80 Hz (5 physics steps of 2.5 ms)'
  horizon: 500 controls (6.25 s simulated)
  success_criteria:
    - the native v3 / reward-v2 success flag, attained at any control of the trajectory
    - both fresh-process replays of the trajectory meet this and end in the same exact
      state
  success_check: "success = float(\n            (np.linalg.norm(handle - self._target_pos) <= 0.12)\n            and self._stick_is_inserted(handle, end_of_stick)\n        )\n\"success\": success"
  source_file: metaworld/envs/sawyer_stick_pull_v3.py
  env_class: SawyerStickPullEnvV3
  limited_target: 'a native goal marker that renders in the fixed cameras: container within threshold of the goal site'
  limited_mode: 'evaluated: RGB-D, calibration and proprioception, one sealed episode'
  frozen_instance: full MuJoCo state, model arrays, task caches and RNG; our task directory metaworldplus-stick-pull-privileged-i01 (tree sha256 e05ade63ccf9)
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

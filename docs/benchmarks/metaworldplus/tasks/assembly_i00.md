---
title: Assembly · i00
task_id: assembly_i00
benchmark: metaworldplus

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Farama-Foundation/Metaworld @ 59fc34d
  synced: '2026-09-28'
  instruction: Place the nut onto the peg.
  scene_model: assembly-v3
  environment_id: assembly-v3
  family: assembly
  instance: 0
  seed: 0
  instance_sha: fa0155dbb9be847916a3504e9ba6268c85e33f96a9d9d8b121576131d83f984e
  robot: Sawyer, fixed wrist, two-finger gripper; mocap XYZ control
  action: '[dx, dy, dz, grip] in [-1, 1]: 0.01 m per unit, grip +1 closes; 80 Hz (5 physics steps of 2.5 ms)'
  horizon: 500 controls (6.25 s simulated)
  success_criteria:
    - the native v3 / reward-v2 success flag, attained at any control of the trajectory
    - both fresh-process replays of the trajectory meet this and end in the same exact
      state
  success_check: "\"success\": float(success)\nsuccess = bool(aligned and hooked)\nsuccess = (\n                abs(objPos[0] - placingGoal[0]) < 0.03\n                and abs(objPos[1] - placingGoal[1]) < 0.03\n                and placingDistFinal <= 0.04\n            )"
  source_file: metaworld/envs/sawyer_assembly_peg_v3.py
  env_class: SawyerNutAssemblyEnvV3
  limited_target: 'set by visible object or mechanism geometry and the task sentence: nut aligned and hooked on the visible peg'
  limited_mode: 'evaluated: RGB-D, calibration and proprioception, one sealed episode'
  frozen_instance: full MuJoCo state, model arrays, task caches and RNG; our task directory metaworldplus-assembly-privileged-i00 (tree sha256 7c2a9f3af517)
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

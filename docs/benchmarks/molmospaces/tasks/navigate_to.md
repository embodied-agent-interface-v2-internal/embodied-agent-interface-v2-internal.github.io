---
title: RB-Y1 · Navigate to
task_id: navigate_to
benchmark: molmospaces

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/allenai/molmospaces @ molmo-spaces 0.2.9 (benchmark molmospaces-bench-v2/20260415), as defined in our task definitions @ e46be110c
  synced: '2026-10-04'
  instruction: Navigate to any bed (2 available).
  family: navigate-to
  robot: 'Rainbow RB-Y1: holonomic base, 6-joint torso, two 7-joint arms with parallel grippers'
  scene_model: holodeck-objaverse val 1430
  category: RB-Y1
  instance: molmospaces-bench-v2/20260415, package holodeck-objaverse/NavToObjDataGenConfig/NavToObjHolodeckBench_20260115_json_benchmark, episode 94
  success_criteria:
    - for the one of the 2 target objects nearest to the robot base (horizontal distance),
      the horizontal distance from the base to its position (the origin of its body, not
      its nearest surface) is less than 1.5 m and at least one of its pixels shows in
      head_camera
    - 'judged at the end of the episode: the trajectory''s last row (privileged), `done`
      (standard) or 500 control steps (the benchmark''s 100 s horizon), whichever comes
      first'
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  deliverable: '/app/output/trajectory.npz with actions: float64 (T, 25), one row per control step, the targets of upstream''s joint-position controllers'
  reference_solution: 'None is shipped. Upstream''s scripted experts (molmo_spaces/policy/solvers) are reference solutions and are not in the image; neither are grasp files nor the public MolmoBot trajectories (agent egress: the model APIs only).'
  limited_mode: 'Standard-mode twin of molmospaces-navigate-to-i00-privileged (the same frozen MolmoSpaces episode): Navigate to any bed (2 available). The agent gets only the eai-standard/2.2 client (docs/STANDARD_MODE_2_2.md); the simulator runs in the sim sidecar (environment/docker-compose.yaml), which owns the episode, serves cameras, proprioception and upstream''s kinematic model, and records every executed row. The collect hook (environment/sim/finalize.sh) ends the episode, lets the service exit, replays the trajectory in two fresh processes and writes final.json; the verifier grades those artifacts in a separate sandbox (tests/Dockerfile).'
  oracle: 'none — upstream record: learned policies are evaluated on the MolmoSpaces benchmark episodes in arXiv 2602.11337 (MolmoSpaces) and arXiv 2603.16861 (MolmoBot); no reference solution is shipped'
  base_image: ghcr.io/mll-lab-nu/eai-molmospaces:0.2.0
  agent_budget: 3600 s of wall clock per mode
  task_dirs: molmospaces-navigate-to-i00-privileged, molmospaces-navigate-to-i00-standard
  scene_image: navigate_to.jpg
---

## Why this task is interesting

Drive the RB-Y1 to either of two beds that start more than 7 m away and out of view, through doorways in an unseen Holodeck house, and stop close to one with it in the head camera's view.

## Capability notes

<!-- Justify the labels in state/tasks/molmospaces.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- MolmoSpaces publishes no per-task demonstration and we ship no reference
     solution; the row shows the starting scene. -->

_No demo._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

Exercises real multi-room navigation. The success distance is measured to the bed's position, not its edge, which the instruction now states. (@williamzhangNU)

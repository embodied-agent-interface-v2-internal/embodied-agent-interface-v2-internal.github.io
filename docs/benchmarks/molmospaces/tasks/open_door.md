---
title: RB-Y1 · Open door
task_id: open_door
benchmark: molmospaces

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/allenai/molmospaces @ molmo-spaces 0.2.9 (benchmark molmospaces-bench-v2/20260415), as defined in our task definitions @ e46be110c
  synced: '2026-10-04'
  instruction: Pull the door open.
  family: open-door
  robot: 'Rainbow RB-Y1: holonomic base, 6-joint torso, two 7-joint arms with parallel grippers'
  scene_model: procthor-10k val 0
  category: RB-Y1
  instance: molmospaces-bench-v2/20260415, package procthor-10k/rby1_benchmarks/door_opening_benchmark, episode 0
  success_criteria:
    - the door's hinge is open at least 67% of its 90-degree range
    - 'judged at the end of the episode: the trajectory''s last row (privileged), `done`
      (standard) or 400 control steps (the benchmark''s 40 s horizon), whichever comes
      first'
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  deliverable: '/app/output/trajectory.npz with actions: float64 (T, 25), one row per control step, the targets of upstream''s joint-position controllers'
  reference_solution: 'None is shipped. Upstream''s scripted experts (molmo_spaces/policy/solvers) are reference solutions and are not in the image; neither are grasp files nor the public MolmoBot trajectories (agent egress: the model APIs only).'
  limited_mode: 'Standard-mode twin of molmospaces-open-door-i00-privileged (the same frozen MolmoSpaces episode): Pull the door open. The agent gets only the eai-standard/2.2 client (docs/STANDARD_MODE_2_2.md); the simulator runs in the sim sidecar (environment/docker-compose.yaml), which owns the episode, serves cameras, proprioception and upstream''s kinematic model, and records every executed row. The collect hook (environment/sim/finalize.sh) ends the episode, lets the service exit, replays the trajectory in two fresh processes and writes final.json; the verifier grades those artifacts in a separate sandbox (tests/Dockerfile).'
  oracle: 'none — upstream record: learned policies are evaluated on the MolmoSpaces benchmark episodes in arXiv 2602.11337 (MolmoSpaces) and arXiv 2603.16861 (MolmoBot); no reference solution is shipped'
  base_image: ghcr.io/mll-lab-nu/eai-molmospaces:0.2.0
  agent_budget: 3600 s of wall clock per mode
  task_dirs: molmospaces-open-door-i00-privileged, molmospaces-open-door-i00-standard
  scene_image: open_door.jpg
---

## Why this task is interesting

Pull a closed room door past two thirds of its range with the RB-Y1: grasp the handle, then pull along the door's arc while the base follows.

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

The hardest family: grasps slip on the first pull. Unlike the push door, it cannot be rammed open with the base. (@williamzhangNU)

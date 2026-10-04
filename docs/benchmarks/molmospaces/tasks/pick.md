---
title: Franka · Pick
task_id: pick
benchmark: molmospaces

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/allenai/molmospaces @ molmo-spaces 0.2.9 (benchmark molmospaces-bench-v2/20260415), as defined in our task definitions @ e46be110c
  synced: '2026-10-04'
  instruction: Pick up the wooden pestle with jagged top.
  family: pick
  robot: Franka FR3 with a Robotiq 2F-85 gripper on a fixed base (the DROID setup)
  scene_model: procthor-objaverse val 1053
  category: Franka
  instance: molmospaces-bench-v2/20260415, package procthor-objaverse/FrankaPickHardBench/FrankaPickHardBench_20260206_json_benchmark, episode 12
  success_criteria:
    - the object touches the robot and nothing else, and it is at least 1 cm higher than
      where it started
    - 'judged at the end of the episode: the trajectory''s last row (privileged), `done`
      (standard) or 303 control steps (the benchmark''s 20 s horizon), whichever comes
      first'
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  deliverable: '/app/output/trajectory.npz with actions: float64 (T, 8), one row per control step, the targets of upstream''s joint-position controllers'
  reference_solution: 'None is shipped. Upstream''s scripted experts (molmo_spaces/policy/solvers) are reference solutions and are not in the image; neither are grasp files nor the public MolmoBot trajectories (agent egress: the model APIs only).'
  limited_mode: 'Standard-mode twin of molmospaces-pick-i00-privileged (the same frozen MolmoSpaces episode): Pick up the wooden pestle with jagged top. The agent gets only the eai-standard/2.2 client (docs/STANDARD_MODE_2_2.md); the simulator runs in the sim sidecar (environment/docker-compose.yaml), which owns the episode, serves cameras, proprioception and upstream''s kinematic model, and records every executed row. The collect hook (environment/sim/finalize.sh) ends the episode, lets the service exit, replays the trajectory in two fresh processes and writes final.json; the verifier grades those artifacts in a separate sandbox (tests/Dockerfile).'
  oracle: 'none — upstream record: learned policies are evaluated on the MolmoSpaces benchmark episodes in arXiv 2602.11337 (MolmoSpaces) and arXiv 2603.16861 (MolmoBot); no reference solution is shipped'
  base_image: ghcr.io/mll-lab-nu/eai-molmospaces:0.2.0
  agent_budget: 3600 s of wall clock per mode
  task_dirs: molmospaces-pick-i00-privileged, molmospaces-pick-i00-standard
  scene_image: pick.jpg
---

## Why this task is interesting

A wooden pestle with a jagged head stands on a counter close to a wall, among other objects. Finding it is easy; reaching it is not: a top-down grasp catches on the head and the wall leaves little room for the wrist, so the approach has to be planned.

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

The hardest of the three pick candidates: an agent that sees the pestle clearly still has to find an approach the wall allows. (@williamzhangNU)

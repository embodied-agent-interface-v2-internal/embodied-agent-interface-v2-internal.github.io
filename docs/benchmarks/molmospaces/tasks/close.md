---
title: Franka · Close
task_id: close
benchmark: molmospaces

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/allenai/molmospaces @ molmo-spaces 0.2.9 (benchmark molmospaces-bench-v2/20260415), as defined in our task definitions @ 6aa89c6d2
  synced: '2026-10-06'
  instruction: Close the cabinet.
  family: close
  robot: Franka FR3 with a Robotiq 2F-85 gripper on a fixed base (the DROID setup)
  scene_model: ithor val 14
  category: Franka
  instance: molmospaces-bench-v2/20260415, package ithor/FrankaCloseHardBench/FrankaCloseHardBench_20260206_json_benchmark, episode 51
  success_criteria:
    - the target's joint is open at most 15% of its range (it starts 50% open)
    - 'judged at the end of the episode: the trajectory''s last row (privileged), `done`
      (standard) or 455 control steps (the benchmark''s 30 s horizon), whichever comes
      first'
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  deliverable: '/app/output/trajectory.npz with actions: float64 (T, 8), one row per control step, the targets of upstream''s joint-position controllers'
  reference_solution: 'None is shipped. Upstream''s scripted experts (molmo_spaces/policy/solvers) are reference solutions and are not in the image; neither are grasp files nor the public MolmoBot trajectories (agent egress: the model APIs only).'
  limited_mode: 'Standard-mode twin of molmospaces-close-i00-privileged (the same frozen MolmoSpaces episode): Close the cabinet. The agent gets only the eai-standard/2.2 client (docs/STANDARD_MODE_2_2.md); the simulator runs in the sim sidecar (environment/docker-compose.yaml), which owns the episode, serves cameras, proprioception and upstream''s kinematic model, and records every executed row. The collect hook (environment/sim/finalize.sh) ends the episode, lets the service exit, replays the trajectory in two fresh processes and writes final.json; the verifier grades those artifacts in a separate sandbox (tests/Dockerfile).'
  oracle: 'none — no reference solution (MolmoSpaces'' planners and grasp files are not shipped); positive example graded 1 by the separate verifier: molmospaces-close-i00-privileged__HWWFXrw (run codex-gpt6_luna-medium, batch molmospaces-luna-1006; https://embodied-agent-interface-v2-internal.github.io/runs/molmospaces/codex-gpt6_luna-medium-openrouter/close/unlimited/); human review in PR #47'
  base_image: ghcr.io/mll-lab-nu/eai-molmospaces:0.2.3
  agent_budget: 3600 s of wall clock per mode
  task_dirs: molmospaces-close-i00-privileged, molmospaces-close-i00-standard
  scene_image: close.jpg
---

## Why this task is interesting

Close a drawer that starts half open, in upstream's Hard configuration. The drawer is easy to see; telling from the cameras which way closes it is not.

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

A half-open hinged door can be pushed shut with closed fingers: GPT-6 Luna (2026-10-06) passed both modes that way. (@williamzhangNU)

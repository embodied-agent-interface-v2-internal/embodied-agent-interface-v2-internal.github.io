---
title: Franka · Pick and place
task_id: pick_and_place
benchmark: molmospaces

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/allenai/molmospaces @ molmo-spaces 0.2.9 (benchmark molmospaces-bench-v2/20260415), as defined in our task definitions @ 6aa89c6d2
  synced: '2026-10-06'
  instruction: Pick up the realistic small white bird with feathers and place it in or on the black bowl with colorful grid.
  family: pick-and-place
  robot: Franka FR3 with a Robotiq 2F-85 gripper on a fixed base (the DROID setup)
  scene_model: procthor-objaverse val 1609
  category: Franka
  instance: molmospaces-bench-v2/20260415, package procthor-objaverse/FrankaPickandPlaceHardBench/FrankaPickandPlaceHardBench_20260206_json_benchmark, episode 134
  success_criteria:
    - the robot does not touch the object; the receptacle supports the object (it carries
      at least 50% of the object's weight through contact, or the object lies on it by
      upstream's on-receptacle test, or the object is within 5 mm and 10 degrees, relative
      to the receptacle, of a pose in which it was supported at an earlier control step);
      and the receptacle has moved at most 15 cm and tilted at most 60 degrees from its
      start pose
    - 'judged at the end of the episode: the trajectory''s last row (privileged), `done`
      (standard) or 606 control steps (the benchmark''s 40 s horizon), whichever comes
      first'
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  deliverable: '/app/output/trajectory.npz with actions: float64 (T, 8), one row per control step, the targets of upstream''s joint-position controllers'
  reference_solution: 'None is shipped. Upstream''s scripted experts (molmo_spaces/policy/solvers) are reference solutions and are not in the image; neither are grasp files nor the public MolmoBot trajectories (agent egress: the model APIs only).'
  limited_mode: 'Standard-mode twin of molmospaces-pick-and-place-i00-privileged (the same frozen MolmoSpaces episode): Pick up the realistic small white bird with feathers and place it in or on the black bowl with colorful grid. The agent gets only the eai-standard/2.2 client (docs/STANDARD_MODE_2_2.md); the simulator runs in the sim sidecar (environment/docker-compose.yaml), which owns the episode, serves cameras, proprioception and upstream''s kinematic model, and records every executed row. The collect hook (environment/sim/finalize.sh) ends the episode, lets the service exit, replays the trajectory in two fresh processes and writes final.json; the verifier grades those artifacts in a separate sandbox (tests/Dockerfile).'
  oracle: 'none — no reference solution (MolmoSpaces'' planners and grasp files are not shipped); positive example graded 1 by the separate verifier: molmospaces-pick-and-place-i00-p__rfd3V6M (run codex-gpt6_luna-medium, batch molmospaces-luna-1006b; https://embodied-agent-interface-v2-internal.github.io/runs/molmospaces/codex-gpt6_luna-medium-openrouter/pick_and_place/unlimited/); human review in PR #47'
  base_image: ghcr.io/mll-lab-nu/eai-molmospaces:0.2.3
  agent_budget: 3600 s of wall clock per mode
  task_dirs: molmospaces-pick-and-place-i00-privileged, molmospaces-pick-and-place-i00-standard
  scene_image: pick_and_place.jpg
---

## Why this task is interesting

A small handheld GPS stands upright beside a shallow wooden bowl. It tips over easily, and once it lies flat the grasp has to be planned again at a new height; carrying it into the bowl and letting go without knocking the bowl is the rest.

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

A small figurine among other objects: GPT-6 Luna (2026-10-06) needs six trajectories in unlimited mode to get its fingers past the statue beside it, and its limited run never lifts it in nine closes. (@williamzhangNU)

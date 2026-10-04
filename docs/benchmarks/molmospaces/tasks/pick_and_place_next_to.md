---
title: Franka · Pick and place next to
task_id: pick_and_place_next_to
benchmark: molmospaces

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/allenai/molmospaces @ molmo-spaces 0.2.9 (benchmark molmospaces-bench-v2/20260415), as defined in our task definitions @ e46be110c
  synced: '2026-10-04'
  instruction: Pick up the lepidopteran and place it next to the brown rectangular bread.
  family: pick-and-place-next-to
  robot: Franka FR3 with a Robotiq 2F-85 gripper on a fixed base (the DROID setup)
  scene_model: procthor-objaverse val 1058
  category: Franka
  instance: molmospaces-bench-v2/20260415, package procthor-objaverse/FrankaPickandPlaceNextToHardBench/FrankaPickandPlaceNextToHardBench_20260305_json_benchmark, episode 5
  success_criteria:
    - the horizontal gap between the two objects' axis-aligned bounding boxes is between
      0 and 6 cm; both rest on the same supporting body; and the reference object has
      moved at most 15 cm and rotated at most 60 degrees from its start pose
    - 'judged at the end of the episode: the trajectory''s last row (privileged), `done`
      (standard) or 455 control steps (the benchmark''s 30 s horizon), whichever comes
      first'
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  deliverable: '/app/output/trajectory.npz with actions: float64 (T, 8), one row per control step, the targets of upstream''s joint-position controllers'
  reference_solution: 'None is shipped. Upstream''s scripted experts (molmo_spaces/policy/solvers) are reference solutions and are not in the image; neither are grasp files nor the public MolmoBot trajectories (agent egress: the model APIs only).'
  limited_mode: 'Standard-mode twin of molmospaces-pick-and-place-next-to-i00-privileged (the same frozen MolmoSpaces episode): Pick up the lepidopteran and place it next to the brown rectangular bread. The agent gets only the eai-standard/2.2 client (docs/STANDARD_MODE_2_2.md); the simulator runs in the sim sidecar (environment/docker-compose.yaml), which owns the episode, serves cameras, proprioception and upstream''s kinematic model, and records every executed row. The collect hook (environment/sim/finalize.sh) ends the episode, lets the service exit, replays the trajectory in two fresh processes and writes final.json; the verifier grades those artifacts in a separate sandbox (tests/Dockerfile).'
  oracle: 'none — upstream record: learned policies are evaluated on the MolmoSpaces benchmark episodes in arXiv 2602.11337 (MolmoSpaces) and arXiv 2603.16861 (MolmoBot); no reference solution is shipped'
  base_image: ghcr.io/mll-lab-nu/eai-molmospaces:0.2.0
  agent_budget: 3600 s of wall clock per mode
  task_dirs: molmospaces-pick-and-place-next-to-i00-privileged, molmospaces-pick-and-place-next-to-i00-standard
  scene_image: pick_and_place_next_to.jpg
---

## Why this task is interesting

A flat moth, about 2 cm thick, has to end up beside a loaf of bread: on the same surface, within 6 cm. The flat object is hard to grasp from above, and "next to" is judged on bounding boxes, so a few centimetres decide.

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

The family's own difficulty, the 6 cm placement, decides it. Upstream's check also accepts the object while it is still held just above the counter; kept as upstream defines it. (@williamzhangNU)

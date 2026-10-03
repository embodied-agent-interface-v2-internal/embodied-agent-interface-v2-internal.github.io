---
title: Multi-stage · PrepareCoffee
task_id: prepare_coffee
benchmark: robocasa

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/robocasa/robocasa @ 756598a (v0.2), as defined in our task definitions @ 8c5594a43
  synced: '2026-10-02'
  instruction: Pick the mug from the cabinet, place it under the coffee machine dispenser, and press the start button.
  family: robocasa/PrepareCoffee
  robot: Franka Panda on an Omron mobile base with a torso lift (PandaOmron)
  scene_model: robocasa_kitchen
  category: Multi-stage · brewing
  instance: the initial state of official demonstration episode 0 (demo_1, v0.1/multi_stage/brewing/PrepareCoffee/2024-05-07); MuJoCo state, model arrays, task state and RNG frozen in instance.npz (SHA-256 c8921c3021e4…, checked on load)
  success_criteria:
    - The mug's centre is within 4 cm (horizontally) and 10 cm (vertically) of the coffee
      machine's mug spot under the dispenser.
    - 'The coffee machine is on: it switches on the first time the gripper touches its
      start button and then stays on.'
    - 'The gripper''s grip site (between the fingertips) is more than 25 cm from the mug''s
      centre: let go and move the hand away.'
    - The gripper's grip site is also more than 15 cm from the start button. A "centre"
      is a body's origin; "touches" means a MuJoCo contact.
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  deliverable: (T, 12) native controller commands, 1 ≤ T ≤ 3000, 20 Hz
  reference_solution: 'The demonstration''s own actions (original: 500 actions), executed from the frozen scene by the robot''s own controller: 500 actions in solution/oracle.npz. The demonstration is a reference solution: it is not in the image and the agent cannot reach it.'
  limited_mode: 'Standard mode (robot as a service, eai-standard/2.1) of robocasa-prepare-coffee-i00-privileged: the same frozen instance and success check, served by the sim sidecar (images/robocasa/standard/server_casa.py, tool module casa_tool), which records the episode, replays it in a fresh simulator and judges it; the verifier grades the sidecar''s record in a container of its own. The agent sees the robot''s cameras (RGB-D, calibrated), its own joints and end effector, and the instruction.'
  oracle: full
  base_image: ghcr.io/mll-lab-nu/eai-robocasa:0.1.0
  agent_budget: 3600 s of wall clock per mode
  environment_source: https://github.com/robocasa/robocasa/blob/756598a5be52e052339bb2d957426e39015c2afb/robocasa/environments/kitchen/multi_stage/brewing/prepare_coffee.py#L4
  task_dirs: robocasa-prepare-coffee-i00-privileged, robocasa-prepare-coffee-i00-standard
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/robocasa.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- The demo is the verifier's replay of our reference solution on this
     task's frozen instance (privileged mode). Say here if it looks wrong. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

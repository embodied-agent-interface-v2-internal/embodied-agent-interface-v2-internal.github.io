---
title: Multi-stage · MicrowaveThawing
task_id: microwave_thawing
benchmark: robocasa

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/robocasa/robocasa @ 756598a (v0.2), as defined in our task definitions @ 8c5594a43
  synced: '2026-10-02'
  instruction: Pick the squash from the counter and place it in the microwave. Then turn on the microwave.
  family: robocasa/MicrowaveThawing
  robot: Franka Panda on an Omron mobile base with a torso lift (PandaOmron)
  scene_model: robocasa_kitchen
  category: Multi-stage · defrosting food
  instance: the initial state of official demonstration episode 1 (demo_2, v0.1/multi_stage/defrosting_food/MicrowaveThawing/2024-05-11); MuJoCo state, model arrays, task state and RNG frozen in instance.npz (SHA-256 0ef66e26d964…, checked on load)
  success_criteria:
    - The object is entirely inside the microwave (all eight corners of its bounding box
      within the interior, with a 5 cm tolerance).
    - 'The microwave is on; the microwave only registers a button while its door is closed
      (at most 0.5% open), and opening the door switches it off: close the door fully,
      then press the start button.'
    - 'The gripper''s grip site (between the fingertips) is more than 25 cm from the object''s
      centre: let go and move the hand away. A "centre" is a body''s origin; "touches"
      means a MuJoCo contact.'
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  deliverable: (T, 12) native controller commands, 1 ≤ T ≤ 3000, 20 Hz
  reference_solution: 'The demonstration''s own actions (original: 763 actions), executed from the frozen scene by the robot''s own controller: 763 actions in solution/oracle.npz. The demonstration is a reference solution: it is not in the image and the agent cannot reach it.'
  limited_mode: 'Standard mode (robot as a service, eai-standard/2.1) of robocasa-microwave-thawing-i00-privileged: the same frozen instance and success check, served by the sim sidecar (images/robocasa/standard/server_casa.py, tool module casa_tool), which records the episode, replays it in a fresh simulator and judges it; the verifier grades the sidecar''s record in a container of its own. The agent sees the robot''s cameras (RGB-D, calibrated), its own joints and end effector, and the instruction.'
  oracle: full
  base_image: ghcr.io/mll-lab-nu/eai-robocasa:0.1.0
  agent_budget: 3600 s of wall clock per mode
  environment_source: https://github.com/robocasa/robocasa/blob/756598a5be52e052339bb2d957426e39015c2afb/robocasa/environments/kitchen/multi_stage/defrosting_food/microwave_thawing.py#L4
  task_dirs: robocasa-microwave-thawing-i00-privileged, robocasa-microwave-thawing-i00-standard
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

---
title: GR1 · PosttrainPnPNovelFromCuttingboardToBasketSplitA
task_id: cuttingboard_to_basket
benchmark: robocasa-gr1

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/robocasa/robocasa-gr1-tabletop-tasks @ 4840e67, as defined in our task definitions @ 8c5594a43
  synced: '2026-10-02'
  instruction: Pick the croissant from the cutting board and place it in the basket.
  family: robocasa-gr1/PosttrainPnPNovelFromCuttingboardToBasketSplitA
  robot: 'Fourier GR1 humanoid: two arms, waist and two six-command Fourier hands; fixed base'
  scene_model: gr1_counter
  category: Pick and place (novel objects)
  instance: the initial state of official demonstration episode 0 (demo_1, HDF5/PosttrainPnPNovelFromCuttingboardToBasketSplitA.hdf5); MuJoCo state, model arrays, task state and RNG frozen in instance.npz (SHA-256 2f1908edac25…, checked on load)
  success_criteria:
    - 'the croissant is in the basket: touching the basket, with its centre horizontally
      within 0.7 x the basket''s horizontal radius of the basket''s centre'
    - the croissant does not touch the counter
    - the basket is upright (its z axis has a world-z component above 0.8)
    - 'both hands are clear: each grip site (left and right) is more than 0.25 m from
      the croissant''s origin and more than 0.25 m from the basket''s origin (any_gripper_obj_far,
      th = 0.25) -- release the croissant and move both hands away before the end.'
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  deliverable: (T, 24) native controller commands, 1 ≤ T ≤ 3000, 20 Hz
  reference_solution: 'The demonstration''s own actions (original: 123 actions), executed from the frozen scene by the robot''s own controller: 123 actions in solution/oracle.npz. The demonstration is a reference solution: it is not in the image and the agent cannot reach it.'
  limited_mode: 'Standard mode (robot as a service, eai-standard/2.1) of robocasa-gr1-cuttingboard-to-basket-i00-privileged: the same frozen instance and success check, served by the sim sidecar (images/robocasa-gr1/standard/server_casa.py, tool module casa_tool), which records the episode, replays it in a fresh simulator and judges it; the verifier grades the sidecar''s record in a container of its own. The agent sees the robot''s cameras (RGB-D, calibrated), its own joints and end effector, and the instruction.'
  oracle: full
  base_image: ghcr.io/mll-lab-nu/eai-robocasa-gr1:0.1.0
  agent_budget: 3600 s of wall clock per mode
  environment_source: https://github.com/robocasa/robocasa-gr1-tabletop-tasks/blob/4840e671596f93ca03651524b9f72ffb1aadfeff/README.md#L105
  task_dirs: robocasa-gr1-cuttingboard-to-basket-i00-privileged, robocasa-gr1-cuttingboard-to-basket-i00-standard
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/robocasa-gr1.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- The demo is the verifier's replay of our reference solution on this
     task's frozen instance (privileged mode). Say here if it looks wrong. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

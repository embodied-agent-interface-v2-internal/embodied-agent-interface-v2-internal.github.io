---
title: Composite · DivideBasins
task_id: divide_basins
benchmark: robocasa365

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/robocasa/robocasa @ 4f8a298 (robocasa 1.0.1), as defined in our task definitions @ 8c5594a43
  synced: '2026-10-02'
  instruction: Move any existing items from the left basin to the right basin for drying. Then move the cup from the counter to the left basin of the sink for washing.
  family: robocasa365/DivideBasins
  robot: Franka Panda on an Omron mobile base with a torso lift (PandaOmron)
  scene_model: robocasa365_kitchen
  category: Composite · washing dishes
  instance: the initial state of official demonstration episode 0 (demo_0); MuJoCo state, model arrays, task state and RNG frozen in instance.npz (SHA-256 fed4a1b61d19…, checked on load)
  success_criteria:
    - The check for DivideBasins requires that the item that was in the left basin is
      in the right basin, the cup is in the left basin, and the gripper ends more than
      0.25 m from both.
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  deliverable: (T, 13) native controller commands, 1 ≤ T ≤ 3000, 20 Hz
  reference_solution: 'Retargeted by PR #4 from official demonstration episode 0 (demo_0, 627 recorded actions; RoboCasa365''s demonstrations use a different arm controller): it follows the demonstration''s recorded arm joint positions as this controller''s absolute joint targets (PR #4 method demo_joint). Executed from the frozen scene by the robot''s own controller: 627 actions in solution/oracle.npz. Neither the demonstration nor the reference is in the image; the agent cannot reach them.'
  limited_mode: 'Standard mode (robot as a service, eai-standard/2.1) of robocasa365-divide-basins-i00-privileged: the same frozen instance and success check, served by the sim sidecar (images/robocasa365/standard/server_casa.py, tool module casa_tool), which records the episode, replays it in a fresh simulator and judges it; the verifier grades the sidecar''s record in a container of its own. The agent sees the robot''s cameras (RGB-D, calibrated), its own joints and end effector, and the instruction.'
  oracle: full
  base_image: ghcr.io/mll-lab-nu/eai-robocasa365:0.1.0
  agent_budget: 3600 s of wall clock per mode
  environment_source: https://github.com/robocasa/robocasa/blob/4f8a2980def75a55dff96b990745b83540425f09/robocasa/environments/kitchen/composite/washing_dishes/divide_basins.py#L4
  task_dirs: robocasa365-divide-basins-i00-privileged, robocasa365-divide-basins-i00-standard
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/robocasa365.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- The demo is the verifier's replay of our reference solution on this
     task's frozen instance (privileged mode). Say here if it looks wrong. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

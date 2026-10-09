---
title: Locomotion · Balance hard
task_id: loco_balance_hard
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 7e1b8687d
  synced: '2026-10-08'
  instruction: Stand on the balance board and stay on it, upright and still, for the whole episode.
  env_id: h1-balance_hard-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_loco
  scene_image: loco_balance_hard.png
  category: Locomotion
  capability_class: C3 · quasi-static stabilisation
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 800, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment an episode reaches it (50 resets in our runs
      since 2026-10-07, none from 2026-10-04; the recorded episode replays to the same
      state)'
  scoring: A good step asks for only three things, multiplied together — low actuator force, staying upright (head at full standing height on the board, torso vertical), and near-zero horizontal velocity — so scoring well for one step is not the difficulty. The difficulty is that the episode ends the moment the pelvis drops too low, anything but the rolling sphere touches the ground — the board included — or the sphere touches anything other than the ground and the board, and every step after that is worth nothing.
  zero_action_return: 30.42
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the board's or the roller's pose, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

The board rests on a rolling ball, so the robot has to keep itself and the board balanced at once, for the whole episode.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Still out of reach: the board stays up at most 277 steps in unlimited mode (GPT-6.1 Sol, image 0.1.6, mesh feet); GPT-6 Luna (2026-10-08, box feet) steps off the board onto the floor at step 52, and none of its 51 limited episodes lasts past step 79. (@williamzhangNU)

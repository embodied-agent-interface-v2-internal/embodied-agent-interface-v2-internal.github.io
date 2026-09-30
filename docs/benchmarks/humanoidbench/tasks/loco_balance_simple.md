---
title: Locomotion · Balance simple
task_id: loco_balance_simple
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: Stand on the balance board and stay on it, upright and still, for the whole episode.
  env_id: h1-balance_simple-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_loco
  scene_image: loco_balance_simple.png
  category: Locomotion
  capability_class: C3 · quasi-static stabilisation
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 800, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: A good step asks for only three things, multiplied together — low actuator force, staying upright (head at full standing height on the board, torso vertical), and near-zero horizontal velocity — so scoring well for one step is not the difficulty. The difficulty is that the episode ends the moment the pelvis drops too low, anything but the fulcrum sphere touches the ground — the board included — or the sphere touches anything other than the ground and the board, and every step after that is worth nothing.
  zero_action_return: 37.05
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the board's pose, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Standing on a seesaw board is easy for a step or two; the task is to keep the board level and the robot upright and still for nearly the whole 1000-step episode.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Out of reach for now: no run keeps the board off the floor for long; it needs a balancing controller none built. (@williamzhangNU)

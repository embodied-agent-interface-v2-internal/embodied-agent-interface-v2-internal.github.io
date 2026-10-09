---
title: Locomotion · Walk
task_id: loco_walk
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 7e1b8687d
  synced: '2026-10-08'
  instruction: Walk the robot forward and keep walking, without falling.
  env_id: h1-walk-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_loco
  scene_image: loco_walk.png
  category: Locomotion
  capability_class: C1 · flat-ground periodic gait
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 700, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment an episode reaches it (50 resets in our runs
      since 2026-10-07, none from 2026-10-04; the recorded episode replays to the same
      state)'
  scoring: Each step is judged on three things at once — how fast the centre of mass is moving forward, how upright the robot is (head at standing height, torso vertical), and how little actuator force it is using — and they multiply. Not being upright is what makes a step worth nothing; heavy actuator force costs part of it. The forward-speed target is on the order of 1 m/s.
  ends_early: The episode ends early if the pelvis drops near the ground.
  zero_action_return: 6.56
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not how fast it is moving, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Walking has to be a limit cycle: the first step out of a standing pose is locally worse than not taking it, because the centre of mass must leave the support polygon before the robot gains anything. The reward multiplies forward speed, uprightness and low actuator force, so standing still earns little.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Passes in unlimited mode with a whole-body inverse-dynamics walker at about 1 m/s (GPT-6.1 Sol, image 0.1.6); GPT-6 Luna (2026-10-08) walks 5.4 m at about 0.46 m/s and falls at step 582 in unlimited mode (247 of 700), and none of its 51 limited episodes lasts past step 200 or gets more than 1.3 m forward. (@williamzhangNU)

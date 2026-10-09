---
title: Locomotion · Hurdle
task_id: loco_hurdle
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 7e1b8687d
  synced: '2026-10-08'
  instruction: Run the robot forward down the walled track, past the hurdles, without touching the side or back walls and without falling.
  env_id: h1-hurdle-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_loco
  scene_image: loco_hurdle.png
  category: Locomotion
  capability_class: C2 · constrained gait
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
  scoring: 'Forward speed, staying upright (head at standing height, torso vertical) and low actuator force, multiplied together — but the speed target is a sprint rather than a walk, on the order of 5 m/s. On top of that, touching any barrier''s collision geometry multiplies that entire step down to a small fraction of its value: contact is a gate to be respected, not a penalty to be traded off. Only the walls that line the track on both sides and behind the start count as barriers here; the hurdles carry no such penalty, and in upstream''s model they have no collision geometry at all (drawn, not solid): the robot runs through them.'
  ends_early: The episode ends early if the pelvis drops near the ground.
  zero_action_return: 18.05
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is on the track, not where the hurdles and walls are, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

A sprint of about 5 m/s down a walled track, with hurdles from x = 7 m. The robot has to run fast and stably first, then clear each hurdle without touching the walls or falling.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Speed is the gap: GPT-6.1 Sol's unlimited run (image 0.1.6) covers the whole episode at about 1.4 m/s, while GPT-6 Luna (2026-10-08, after the task text was corrected) crouches at the start, against the back wall for 521 steps, for the whole unlimited episode (79 of 700), and gets 0.8 m forward at most in limited mode. (@williamzhangNU)

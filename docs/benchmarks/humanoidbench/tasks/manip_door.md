---
title: Manipulation · Door
task_id: manip_door
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ be39e53bb
  synced: '2026-10-06'
  instruction: Walk to the door, press the handle, pull the door open towards the robot, and walk through it.
  env_id: h1-door-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_door.png
  category: Manipulation
  capability_class: C4 · navigation and passage
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 600, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment its one episode reaches it (no reset in our
      runs since 2026-10-04; the recorded episode replays to the same state)'
  scoring: 'This one is a weighted sum rather than a product, so partial credit is real: getting the door open and getting the torso past the doorway are the two large terms, with reaching for the handle, moving the handle, and posture as small ones. The bar cannot be reached without opening the door.'
  ends_early: The episode ends early if the pelvis drops too low.
  zero_action_return: 30.86
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the door's or the handle's angle, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

The door opens towards the robot on a spring-loaded hinge: the robot must press the handle, pull the door open and step past the door leaf, while the stable crouches it finds tend to lean on the door and push it shut.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Hard in both modes: GPT-6 Luna (2026-10-06) opens the door about 8° in unlimited mode without walking through (153 of 600), and its limited episode fell at step 90 before the hand reached the handle. (@williamzhangNU)

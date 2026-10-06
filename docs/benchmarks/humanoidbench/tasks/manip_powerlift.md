---
title: Manipulation · Powerlift
task_id: manip_powerlift
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ be39e53bb
  synced: '2026-10-06'
  instruction: Lift the dumbbell from the floor to overhead — close to two metres up — and hold it there.
  env_id: h1hand-powerlift-v0
  robot: Unitree H1 with two Shadow hands (61 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_powerlift.png
  category: Manipulation
  capability_class: C5 · whole-body power and momentum
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 800, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment its one episode reaches it (no reset in our
      runs since 2026-10-04; the recorded episode replays to the same state)'
  scoring: 'A weighted sum of two things: a small share for standing steadily, and the bulk for how high the dumbbell is, measured against a target band around two metres. Be warned that the height term is broad. Clearing the bar means lifting it high and keeping it there for most of the episode, not improving the height a little.'
  ends_early: The episode ends early if the pelvis drops near the ground.
  zero_action_return: 20.39
  action_dim: 61
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the dumbbell's pose, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Squat, grip a 104 kg dumbbell and lift it overhead: the robot must not fall while it reaches down to the bar, and must hold on once it gets there.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Blocked on the grasp: the dumbbell never leaves the floor in either mode; GPT-6 Luna (2026-10-06) stands the whole unlimited episode (333 of 800), and its limited episode fell at step 32. (@williamzhangNU)

---
title: Manipulation · Highbar simple
task_id: manip_highbar_simple
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 841996303
  synced: '2026-10-04'
  instruction: 'The robot starts hanging from a high bar. Swing up: get inverted and drive the feet as high as you can.'
  env_id: h1-highbar_simple-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_highbar_simple.png
  category: Manipulation
  capability_class: C5 · whole-body power and momentum
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 750, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment its one episode reaches it (no reset in our
      runs since 2026-10-04; the recorded episode replays to the same state)'
  scoring: 'Three multiplied requirements: how far the torso is towards inverted, how high the feet are, and low actuator force. Read the first one carefully — it rewards being upside down, so hanging the right way up scores nothing at all no matter how steady it is. The feet-height term saturates only when the feet are well above the bar. On this robot the forearms are fixed to the bar, so it cannot fall off.'
  ends_early: The episode still ends if the head drops too low, which an inverted hang under the bar can do.
  zero_action_return: 0.08
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not the robot's position or heading in the room, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Hanging from a high bar, the robot swings up into a handstand with its feet well above the bar. Swinging through the handstand is not enough: it has to stop there.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Out of reach for now: the robot swings up to a partial inversion but never holds the handstand; GPT-6 Luna's feedback-held swing (2026-10-04) came closest, 526 of 750. (@williamzhangNU)

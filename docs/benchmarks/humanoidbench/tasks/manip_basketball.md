---
title: Manipulation · Basketball
task_id: manip_basketball
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 12fb1352
  synced: '2026-09-30'
  instruction: A ball is thrown at the robot. Catch it, then throw it through the hoop.
  env_id: h1-basketball-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_basketball.png
  category: Manipulation
  capability_class: C5 · whole-body power and momentum
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 1200, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 500 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'Scoring runs in two stages and switches by itself the first time the robot contacts the ball. Before that it rewards standing steadily and getting both hands to the ball; after it, the dominant term is how close the ball is to the hoop. Sinking it pays a one-off bonus that covers most of the bar but not all of it, and ends the episode immediately, so the rest has to be earned per step before the ball goes in. That bonus is not optional: no amount of good positioning reaches the bar without it.'
  ends_early: The episode also ends if the ball drops low or the robot falls.
  zero_action_return: 10.77
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not where the ball or the hoop is, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Catch a ball thrown at the robot at about 7.5 m/s, then throw it through the hoop. The basket pays a bonus, but the rest of the bar has to be earned step by step before it.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Close in unlimited mode, where the ball goes in but too little is earned before it; out of reach in limited mode, where the throw is never aimed at the hoop. (@williamzhangNU)

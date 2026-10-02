---
title: Manipulation · Window
task_id: manip_window
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 7d6a7a44
  synced: '2026-09-30'
  instruction: Grasp the wiping tool — it starts in the air just in front of the hands and falls within the first second unless it is held — and wipe the window with it, moving steadily up and down.
  env_id: h1hand-window-v0
  robot: Unitree H1 with two Shadow hands (61 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_window.png
  category: Manipulation
  capability_class: C6 · standing bimanual manipulation
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 650, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: A large share of each step is paid only while the tool is in contact with the glass — while it is not, that share is zero, so the bar cannot be reached without contact. The rest pays for moving the tool vertically at a target speed on the order of half a metre per second, for keeping both hands near the tool, and for standing with the head about 40 cm from where it started.
  ends_early: The episode ends immediately if the pelvis drops or the tool falls, i.e. if it is dropped.
  zero_action_return: 1.56
  action_dim: 61
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the tool's pose, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Hold a wiper against the glass and move it up and down at about half a metre per second while standing, without letting the tool slip out of the hand.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Close in unlimited mode, 32 short of the bar: the wiper stays on the glass for 866 steps but moves at about half the asked speed. (@williamzhangNU)

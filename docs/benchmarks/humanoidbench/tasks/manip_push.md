---
title: Manipulation · Push
task_id: manip_push
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 628c408
  synced: '2026-09-28'
  instruction: Push the box on the table to the target position marked in the observation.
  env_id: h1-push-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_push.png
  category: Manipulation
  capability_class: C6 · standing bimanual manipulation
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 700, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 500 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'Every step here is negative: it costs the box''s distance to the target, plus a smaller charge for the left hand''s distance to the box. The only positive term is a one-off bonus, paid when the box lands within a few centimetres of the target — and that also ends the episode. So the bar is not reached by scoring well for a long time; it is reached by finishing, and finishing early, because every extra step subtracts.'
  zero_action_return: -253.71
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not where the hand or the box is, not the target's coordinates, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

The box is out of reach from where the robot stands: it has to bring its body closer, then push the box into a target a few centimetres wide as early as it can, since the reward counts the steps.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

The easiest scored task: four of five runs pass, and in limited mode it separates the models by whether they find a leaning stance that reaches the table. (@williamzhangNU)

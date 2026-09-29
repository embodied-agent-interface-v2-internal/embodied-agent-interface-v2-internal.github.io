---
title: Manipulation · Kitchen
task_id: manip_kitchen
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 628c408
  synced: '2026-09-28'
  instruction: 'Complete the four kitchen tasks, in order: microwave, kettle, bottom burner, light switch. Their goal configurations are not part of the observation; they are defined in the task''s source (OBS_ELEMENT_GOALS in humanoid_bench/envs/kitchen.py), which is in the image.'
  env_id: h1hand-kitchen-v0
  robot: Unitree H1 with two Shadow hands (61 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_kitchen.png
  category: Manipulation
  capability_class: C9 · long-horizon multi-subtask
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 4, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 500 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: '🚩 *This task has no partial credit whatsoever. A step scores 1 for each subtask that becomes* complete on it and nothing otherwise — there is no shaping, no distance term, no posture term. The bar is 4: all four subtasks, each worth exactly 1, once. Moving an appliance most of the way towards its goal configuration scores exactly zero, as does standing perfectly still; the only event that scores is a subtask crossing its completion threshold.'
  zero_action_return: 0.0
  action_dim: 61
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not the appliances' joint positions, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

Four steps in order: the microwave, the kettle, the bottom burner and the light switch; all four are needed to pass, and the microwave's handle is out of reach from where the robot starts.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

No subtask done in either mode: the microwave door, the first of four, never opens. (@williamzhangNU)

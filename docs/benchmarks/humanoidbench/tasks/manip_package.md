---
title: Manipulation · Package
task_id: manip_package
benchmark: humanoidbench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/carlosferrazza/humanoid-bench @ cb11890, as defined in our task definitions @ 12fb1352
  synced: '2026-09-30'
  instruction: Walk to the package, pick it up, carry it to the destination marker and set it down there, standing upright.
  env_id: h1-package-v0
  robot: Unitree H1 (19 actuators)
  scene_model: humanoidbench_manip
  scene_image: manip_package.png
  category: Manipulation
  capability_class: C8 · mobile manipulation
  role: scored
  success_criteria:
    - the summed per-step reward over one episode reaches 1500, HumanoidBench's own success
      bar (a total of rewards, not a number of steps; an episode is at most 1000 control
      steps)
    - 'unlimited: both fresh-process replays of the handed-in trajectory reach it and
      end in the same state'
    - 'limited: the run passes the moment a live episode reaches it (the recorded episode
      replays to the same state); otherwise the last episode is graded'
  scoring: 'Every step charges you for the distance from the package to its destination — the largest term by far — and a little for the distance from each hand to the package; against that you earn a share for standing steadily and a share for how high the package is off the ground. So the return is strongly negative while the package sits on the floor away from its destination, and improves as you close the distance with it lifted. Landing the package on the destination pays a one-off bonus and ends the episode, but the bonus alone is short of the bar: the rest has to come from the per-step terms before the landing, and those only turn positive once the package is close to the destination.'
  zero_action_return: -2191.95
  action_dim: 19
  control_rate_hz: 50
  limited_mode: head cameras (RGB 256×256), joint angles and velocities; a pelvis IMU and a camera fixed in the room when the run turns them on. Not where the robot is in the room, not where the package or the destination is, not the reward
  agent_budget: 3600 s of wall clock per mode
---

## Why this task is interesting

The package, a tall box of 0.4 × 0.2 × 0.7 m, stands about 0.86 m to the robot's left and about 0.7 m from the goal: the robot has to side-step to it and move it to the goal, while holding the starting pose falls after about 100 steps.

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

Blocked on standing next to the package: the unlimited score comes from sweeping it in while falling. (@williamzhangNU)

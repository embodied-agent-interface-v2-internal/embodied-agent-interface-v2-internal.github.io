---
title: About RoboCasa-GR1
---

# About RoboCasa-GR1

[RoboCasa's GR1 tabletop tasks](https://github.com/robocasa/robocasa-gr1-tabletop-tasks) (@ 4840e67, robosuite @ 51cc017 with its mink whole-body IK controller, MuJoCo 3.2.6) put a **Fourier GR1** humanoid (two arms, waist, two six-command Fourier hands, fixed base) at a counter: picking objects from one container or surface and placing them in another, including novel objects, and placing into a cabinet, drawer or microwave and closing it.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/robocasa-gr1.md){ .md-button }

## What the agent gets

**Unlimited (privileged).** The agent drives the environment in Python with the whole simulator state, resets as often as it likes and hands in one trajectory of the robot's native whole-body commands (24 numbers per 20 Hz step: each hand's grip-site pose and six finger commands; at most 3000), which the verifier replays twice in fresh processes.

**Limited (standard).** The simulator runs in a service the agent cannot open. It sees the humanoid's six cameras (current calibration), its joints, the grip sites' positions, its last command and the task's language; never an object's pose or the success check. One episode, no reset, no step limit.

Both modes have 60 minutes of wall clock, and the agent reaches the model APIs and nothing else (the references are
public upstream).

## Scoring

The environment's own `_check_success` on the state after the last action, and not solved at the start. Each instruction lists what it requires: the object in the container, not touching the counter, the container upright, both hands more than 25 cm away, no distractor in the container; for the closing tasks, the object inside and the door shut.

## The tasks

All 24 GR1 tabletop environments with an official demonstration, one frozen instance each (the initial state of the demonstration's first episode). The demonstrations are removed from the image. 24 tasks here, each a pair in robot_coding_bench: `tasks/robocasa-gr1-<task>-i00-privileged` and
`-standard` @ 8c5594a43, written by `scripts/robocasa-gr1/generate.py`; their notes are in robot_coding_bench's
`docs/benchmarks/robocasa-gr1.md`. The task pages are synced by `scripts/import_robocasa_gr1_tasks.py`
(`make sync-robocasa-gr1`).

## The demos

Each row's video is ours: the verifier's replay of the task's reference solution on its frozen instance in the
privileged mode, re-encoded for the site. It shows that the task can be done as specified; it is not the benchmark's
own demonstration video.

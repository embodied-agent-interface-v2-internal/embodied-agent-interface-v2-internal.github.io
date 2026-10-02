---
title: About RoboCasa
---

# About RoboCasa

[RoboCasa](https://github.com/robocasa/robocasa) v0.2 (@ 756598a, robosuite 1.5.1, MuJoCo 3.2.6) has everyday kitchen tasks for a **PandaOmron**, a Franka Panda on an Omron mobile base with a torso lift, in procedurally generated kitchens: doors, drawers, knobs, faucets, buttons, and picking and placing between counters, cabinets, sinks, stoves and appliances, single- and multi-stage. Each of our tasks is frozen at the initial state of the task's first official demonstration.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/robocasa.md){ .md-button }

## What the agent gets

**Unlimited (privileged).** The agent drives RoboCasa in Python with the whole simulator state, resets as often as it likes and hands in one trajectory of the robot's native controller commands (12 numbers per 20 Hz step; at most 3000), which the verifier replays twice in fresh processes.

**Limited (standard).** The simulator runs in a service the agent cannot open. It sees the robot's four cameras (three agent views and the wrist; RGB-D with the current calibration, since they move with the robot), its joints, end-effector position, last command and the task's language; never an object's pose, the kitchen layout or the success check. One episode, no reset, no step limit.

Both modes have 60 minutes of wall clock, and the agent reaches the model APIs and nothing else (the references are
public upstream).

## Scoring

The environment's own `_check_success` on the state after the last action, and not solved at the start. Each instruction states what the check requires (thresholds and implicit conditions, such as the hand being more than 25 cm from a placed object).

## The tasks

We keep the 29 tasks with an official demonstration at the pinned commit whose demonstration re-verifies as a reference on its frozen instance. Left out: 79 without an official demonstration at this commit (so without a reference), 2 that could not be frozen reproducibly, and `NavigateKitchen` (navigation only, a different action interface). The demonstrations and their download links are removed from the image. 29 tasks here, each a pair in robot_coding_bench: `tasks/robocasa-<task>-i00-privileged` and
`-standard` @ 8c5594a43, written by `scripts/robocasa/generate.py`; their notes are in robot_coding_bench's
`docs/benchmarks/robocasa.md`. The task pages are synced by `scripts/import_robocasa_tasks.py`
(`make sync-robocasa`).

## The demos

Each row's video is ours: the verifier's replay of the task's reference solution on its frozen instance in the
privileged mode, re-encoded for the site. It shows that the task can be done as specified; it is not the benchmark's
own demonstration video.

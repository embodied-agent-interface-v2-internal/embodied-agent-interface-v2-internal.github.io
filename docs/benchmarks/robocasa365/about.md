---
title: About RoboCasa365
---

# About RoboCasa365

[RoboCasa365](https://github.com/robocasa/robocasa) (robocasa 1.0.1 @ 4f8a298, robosuite 1.5.2, MuJoCo 3.3.1) is RoboCasa's 365-task kitchen suite for the same **PandaOmron**: atomic skills and long composite activities across cooking, cleaning, storing and serving. Each of our tasks is frozen at the initial state of an official demonstration.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/robocasa365.md){ .md-button }

## What the agent gets

**Unlimited (privileged).** The agent drives the environment in Python with the whole simulator state, resets as often as it likes and hands in one trajectory of the robot's native controller commands (13 numbers per 20 Hz step: 7 arm joint targets, gripper, base, torso, mode; at most 3000), which the verifier replays twice in fresh processes.

**Limited (standard).** As in RoboCasa: the robot's four cameras with the current calibration, its joints, end-effector position, last command and the task's language, behind a service; one episode, no reset, no step limit.

Both modes have 60 minutes of wall clock, and the agent reaches the model APIs and nothing else (the references are
public upstream).

## Scoring

The environment's own `_check_success` on the state after the last action, and not solved at the start. Each instruction states what the check requires and how its terms are computed (on / in, touching, inside, the gripper's distance), and the timers some checks keep.

## The tasks

RoboCasa365 has 365 task families; 256 had a validated demonstration-based reference. We take 50 by a fixed rule (robot_coding_bench `scripts/robocasa365/select_instances.py`): 12 atomic and 38 composite slots, in proportion to the two groups, filled in SHA-256 order of the environment names with those whose reference re-verifies. `OrganizeMugsByHandle` was skipped (its reference fails once MuJoCo's mesh cache is off, which every rebuild needs to be bit-exact). In `PlateSteakMeal` the success state does not persist by itself; its instruction says so. 50 tasks here, each a pair in robot_coding_bench: `tasks/robocasa365-<task>-i00-privileged` and
`-standard` @ 8c5594a43, written by `scripts/robocasa365/generate.py`; their notes are in robot_coding_bench's
`docs/benchmarks/robocasa365.md`. The task pages are synced by `scripts/import_robocasa365_tasks.py`
(`make sync-robocasa365`).

## The demos

Each row's video is ours: the verifier's replay of the task's reference solution on its frozen instance in the
privileged mode, re-encoded for the site. It shows that the task can be done as specified; it is not the benchmark's
own demonstration video.

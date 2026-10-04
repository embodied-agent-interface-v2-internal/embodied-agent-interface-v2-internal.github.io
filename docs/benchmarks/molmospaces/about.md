---
title: About MolmoSpaces
---

# About MolmoSpaces

[MolmoSpaces](https://github.com/allenai/molmospaces) (molmo-spaces 0.2.9, benchmark
molmospaces-bench-v2/20260415) is Ai2's set of zero-shot evaluation episodes for robot policies in
unseen houses, on **MuJoCo** ([paper](https://arxiv.org/abs/2602.11337); its MolmoBot benchmarks:
[paper](https://arxiv.org/abs/2603.16861)). A **Franka FR3** with a Robotiq 2F-85 gripper (the DROID
setup) picks, places into a receptacle, next to an object or by colour, opens and closes fixtures; a
**Rainbow RB-Y1** mobile manipulator navigates to an object and opens a room door. Each of our tasks
is one upstream episode, unchanged, run by upstream's own evaluation code.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/molmospaces.md){ .md-button }

## What the agent gets

**Unlimited (privileged).** The agent drives upstream's episode in Python with its full state (every
body, joint and contact), upstream's kinematics and unlimited resets, and hands in one trajectory of
joint-position control steps, which the verifier replays twice in fresh processes.

**Limited (standard).** The simulator runs in a service the agent cannot open. It sees the episode's
robot cameras (the Franka's wrist camera and four exterior cameras; the RB-Y1's head and wrist
cameras; RGB, depth and calibration) and the robot's joints and grippers, and can ask upstream's
kinematic model for FK and IK; never an object's pose or the success check. One episode, no reset,
ended by the agent (`done`) or by the episode's own horizon.

Both modes have 60 minutes of wall clock, and the agent reaches the model APIs and nothing else
(upstream's scripted experts and the MolmoBot trajectories are public).

## Scoring

Upstream's own `judge_success()` on the final state, at the end of the episode (upstream's
evaluation default), with no partial credit. The episode ends at the trajectory's last row
(privileged), at `done` (standard), or at the episode's horizon (20–100 s of simulated time,
depending on the family).

## The tasks

Eight families, one episode each. For every family a fixed rule walks upstream's package and takes
three candidates from three different houses, among episodes whose house has no public MolmoBot
trajectory, that build with every object they list and are not done at the start, and that pass
measurable difficulty filters: at least three objects within 30 cm of the target (the pick
families), upstream's Hard configurations (open, close), a navigation target at least 5 m away and
out of view. Of the three, we keep the hardest and most representative in GPT-6 Luna's runs of all
24 candidates in both modes. Each is a pair in robot_coding_bench:
`tasks/molmospaces-<family>-i00-privileged` and `-standard` @ e46be110c (robot_coding_bench #47),
written by `scripts/molmospaces/mk_tasks.py`; the selection and its notes are in
robot_coding_bench's `docs/benchmarks/molmospaces.md`. The task pages are synced by
`scripts/import_molmospaces_tasks.py` (`make sync-molmospaces`).

## The stills

MolmoSpaces publishes no per-task demonstration, and we ship no reference solution. Each row shows
the episode's starting scene as the limited mode's cameras see it at t = 0: an exterior camera on
the Franka, the head camera on the RB-Y1.

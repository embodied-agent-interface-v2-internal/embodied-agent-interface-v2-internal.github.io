---
title: About KinDER
---

# About KinDER

**KinDER** (RSS 2026) tests physical reasoning for robot planning and control, kept apart from
perception and language: tool use, non-prehensile multi-object manipulation, geometric and dynamic
constraints. A simulated **TidyBot++** mobile manipulator (a holonomic base, a Kinova Gen3 7-DoF arm
and a Robotiq 2F-85 gripper) works in **MuJoCo**, in KinDER's MimicLabs lab (two tasks that have
left the benchmark ran in **PyBullet**, where the robot is kinematic). Every episode passes or fails
on KinDER's own goal check, with no partial credit. We keep 5 of its 31 task families, one variant
each at seed 0 (the 4 hardest, scored, plus one fixture), and run each in two modes.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/kinder.md){ .md-button }

## What the agent gets

**Unlimited.** The agent drives the simulator in Python with KinDER's whole object-centric state
(`get_state`, `set_state`) and its goal check, resets as often as it likes, and hands in one
trajectory, which the verifier replays.

**Limited.** The simulator runs in a service the agent cannot open, as on a real robot. It gets
what a real TidyBot++ would give, and nothing else:

| Given | What | On the real robot |
| --- | --- | --- |
| The task text | the goal and when it counts: which objects, which place, the margins; never how to do it | the task's own requirements |
| Base camera | RGB, 480×640, on the base looking down 45°, on request | the base's RGB camera |
| Wrist camera | RGB-D, 480×640, depth in metres, on the arm's last link, on request; to see further, turn the base or raise the wrist | the Gen3's RealSense D410 |
| Odometry and encoders | the base's pose and velocity from where it started; the 7 arm joints' angles and velocities; the fingers' position | odometry and joint encoders |
| `spec()` | the action layout and bounds; each arm joint's axis, position, limits and torque; the gripper's grasp point; each camera's field of view and pose; 10 Hz, the episode length, the resets allowed | the robot's documentation and URDF |
| Each step's status | the step, whether the episode ended and why (`success`, `failed`, `timeout`, `error`), the seconds since the first request | the controller's own state |
| **Not given** | any object's or goal region's position, world coordinates, the goal check before the episode ends, masses and friction, the simulator itself; no camera in the room | not there on a real robot |

It acts through the robot service's client (protocol `eai-standard/2.1`): chunks of control steps of
base and arm-joint deltas and a gripper command, and observations on request. Since 2026-10-04 the
run is one episode with no reset, as on a real robot (protocol v1.0's standard configuration), and
passes the moment the episode reaches the goal. Our earlier runs gave it **50 resets**, each back to
the same start: KinDER's episode (1000 steps, 100 s of robot time; PyBullet: 3000 steps) is the time
to carry the task out with the whole state known, and finding things and calibrating were never part
of it. Both modes have 60 minutes of wall clock, and
simulated time stands still between requests.

In the two PyBullet tasks the robot is the same TidyBot++, kinematic: the same two cameras on the same
links, odometry, joint angles and the fingers' position (no velocities). `spec()` states its grasp,
release and collision rules, and a move it refuses comes back `blocked` and stops a batch there, as a
real controller stops its queue.

## Scoring

KinDER's own goal check decides: an object's centre inside a goal region, a beam within 5° of level,
parts flat in a tray without overlap, and the like. The task text states it exactly as KinDER checks
it. The episode ends the moment it holds; there is no reward and no partial credit, and holding still
for a whole episode never passes. The unlimited mode's trajectory must reach the goal in both
fresh-process replays and end in the same state; the limited mode's episode is recorded by the
service and replayed the same way.

## The tasks

KinDER has 31 task families (123 variants) across the five challenges its paper names: spatial
relations, non-prehensile multi-object manipulation, tool use, combinatorial geometric constraints
and dynamic constraints (each task page's note lists its family's). Upstream, the kinematic families
are near-solved; on the dynamic ones the paper's best methods stay low (at most 0.14 on
SweepIntoDrawer3D-o5). Until 2026-10-04 we kept one variant of 11 families:

- **Six Dynamic3D tasks** in which physics decides the outcome and a camera can see the goal or a
  sentence can name it, so the limited mode is fair: tossing, balance beam, sweep into drawer, scoop
  pour, shelf, and `dynamo`, a fixture that checks the whole pipeline and is not scored.
- **Five from a screening** of every other family (2026-09-29, GPT-6 Luna once per mode, each at the
  hardest variant upstream's baselines configure, else the hardest with at most 10 objects): the ones
  it failed in limited mode. Constrained cupboard, sweep simple and sort blocks run in MuJoCo;
  obstruction 3D and packing 3D in PyBullet, 3000 steps each.

The screening's other families left the benchmark. The six Kinematic3D ones passed in both modes
within minutes, some by releasing objects in mid-air; Rearrange3D, PickPlace3D and FrankaPickPlace3D
passed in both modes; the ten 2D ones passed in unlimited mode and have no limited mode, since a
camera image of a 2D scene is nearly its state; LimbRepositioning3D drives another robot interface
and its IKFast solver does not build in our image.

Since 2026-10-04 the benchmark is the hardest 4 of those 10 scored families, plus `dynamo`: sweep into
drawer, scoop pour, sweep simple and constrained cupboard, the four whose unlimited run took GPT-6 Luna
its whole hour (it failed three; constrained cupboard passed in the last minute), also the four GPT-6.1
Sol took longest on. The other six stay on the site, greyed, each with the reason it left.

## What we run it on

| | |
| --- | --- |
| Image | our KinDER image 0.1.6: MuJoCo 3.3.7, PyBullet and kindergarden at 5b2dbac, with the MimicLabs lab |
| Physics | MuJoCo on the CPU (EGL on the GPU renders the limited mode's cameras); PyBullet on the CPU |
| Determinism | Bit-exact: both fresh-process replays of a trajectory end in the same state |
| Network | the agent reaches the model APIs and nothing else: KinDER and its baselines are public |

### Model runs so far

GPT-6 Luna (Codex, through OpenRouter, reasoning effort medium) on the 4 tasks on 2026-10-04, one
attempt per task and mode, 60 minutes each, on robot_coding_bench's protocol v1.0.1 (limited: one
episode, no reset). Tasks passed, out of the 4:

| Model | Limited | Unlimited |
| --- | --- | --- |
| GPT-6 Luna | 0 | 2 (sweep into drawer, sweep simple) |

In unlimited mode it opened the drawer and swept the five cubes in (goal at step 922), and carried
the ten cubes of sweep simple to the box one by one (step 914); scoop pour (at best 14 of 30 cubes
across) and constrained cupboard (five of six rods placed) ran out of the hour. Every limited
episode ran its 1000 steps without reaching the goal. A separate run with 50 resets
(robot_coding_bench PR #45; reported apart, not on this site) passed none either.

Before 2026-10-04, on all 11 tasks as they were then: one attempt per task and mode, 60 minutes each,
reasoning effort medium, GPT-6.1 Sol (Codex, through OpenRouter), limited mode with 50 resets, limited
on 2026-09-30, unlimited on 2026-10-01. Tasks passed, out of the 10 scored:

| Model | Limited | Unlimited |
| --- | --- | --- |
| GPT-6.1 Sol | 10 (all) | 10 (all) |

In limited mode it locates objects and goals by back-projecting the wrist camera's depth through the
arm's kinematics from `spec()`, and checks its work in the images; it used 0 to 16 of its 50 resets
and a median 12 minutes. Unlimited mode reads the state and the goal check and plans offline, in a
median 6 minutes. The subset no longer separates a model this strong: a harder variant or family is
needed. Every run and its log are on the [Runs](../../runs/kinder.md) page; each task page's
Discussion sums up its runs.

GPT-6 Luna's earlier trials on all 11 tasks (2026-09-28 to 10-01: before protocol v1.0, and its v1.0
sweep with 50 resets in limited mode, which passed none) stay in its run: the latest of them is each
task's history beside the 2026-10-04 trial, and the only one on the 6 tasks that left the benchmark.

## Upstream links

- [KinDER](https://github.com/Princeton-Robot-Planning-and-Learning/kindergarden): the environments, pinned at commit 5b2dbac (MIT)
- [Paper](https://arxiv.org/abs/2604.25788)

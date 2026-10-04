---
title: About HumanoidBench
---

# About HumanoidBench

**HumanoidBench** puts a simulated **Unitree H1** humanoid, bare or with two **Shadow
dexterous hands**, through locomotion and whole-body manipulation in **MuJoCo**. Every episode is
scored by HumanoidBench's own dense reward, summed over the episode, against its own success
bar. We keep the 9 hardest of its 32 registered tasks plus one fixture, and run each in two modes.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/humanoidbench.md){ .md-button }

## What the agent gets

**Unlimited.** The agent drives the simulator in Python with the whole physical state, resets as
often as it likes, and hands in one trajectory, which the verifier replays.

**Limited.** The simulator runs in a service the agent cannot open, as on a real robot. It gets
what a real H1 would give, and nothing else:

| Given | What | On the real robot |
| --- | --- | --- |
| The task text | the goal, when an episode ends, the pass mark, which terms the reward combines (in words, no formula) | the task's own requirements |
| Head cameras | two RGB images, 256×256 (cube 512×512), 45° field of view, on request | the H1's head cameras |
| Room camera | one RGB camera fixed in the room, placed per task | a camera set up in the lab |
| Joint readings | every joint's angle and velocity (19 joints; 69 with the hands) | joint encoders |
| Pelvis IMU | angular velocity and the gravity direction, in the pelvis frame | the body IMU |
| `spec()` | each servo's range, each joint's axis and position, each link's mass and centre of mass, the feet's collision boxes, the IMU's frame and signs, each camera's field of view and pose; 50 Hz, the episode length, the resets allowed | the robot's documentation and URDF |
| Each step's status | the step, whether the episode ended and why (`success`, `failed`, `timeout`, `error`), the resets left, the seconds since the first request | the controller's own state |
| **Not given** | the reward, the robot's position in the room, any object's pose, contact forces, the simulator itself | not there on a real robot |

It acts through the robot service's client (protocol `eai-standard/2.1`): chunks of position targets in
[−1, 1] per servo at 50 Hz, and observations on request. The run is one episode with no reset, as on a
real robot (protocol v1.0's standard configuration; our runs before 2026-10-04 allowed 50 resets, each
back to the same starting state). The run passes the moment the episode reaches the bar. Both modes have
60 minutes of wall clock, and simulated time stands still between requests.

## Scoring

HumanoidBench's reward for each task is a product or a weighted sum of terms (upright posture, speed,
distance to a target, low actuator force, ...), paid at every control step; the task passes when
the sum over one episode reaches its success bar. The environments we ship have every
`get_reward()` removed, so the agent never sees the formula or a reward: the task text describes
the terms in words, and the verifier puts the reward back to grade. The unlimited mode's
trajectory must reach the bar in both fresh-process replays and end in the same state; the
limited mode's episodes are recorded by the service and replayed the same way.

## The tasks

HumanoidBench registers 32 tasks. We dropped the duplicates (`stair` and `slide` share one reward
function) and the give-aways (`pole` pays 71% of its bar for standing still), which left 23 in
nine capability classes (each task page names its class), plus `sit_simple`, a fixture that checks
the whole pipeline and is not scored. Since 2026-10-04 the benchmark is the 9 hardest of them, in
five classes (stair, hurdle, balance_hard, highbar_simple, powerlift, package, room, truck,
bookshelf_simple): the 13 that no model passed in either mode, minus window, which came within 5% of
the bar, and spoon, insert_normal and cabinet, whose bar does not measure the task. The other 14 stay
on the site, greyed, each with the reason it left. 6 of the 9 use the bare H1 (19 actuators), 3 add the Shadow hands (61 actuators).

## What we run it on

| | |
| --- | --- |
| Image | our HumanoidBench image 0.1.6: MuJoCo and humanoid-bench at cb11890, every `get_reward()` removed |
| Physics | MuJoCo on the CPU; EGL on the GPU renders the limited mode's cameras |
| Determinism | Bit-exact: both fresh-process replays of a trajectory end in the same state |

### Model runs so far

GPT-6 Luna (Codex, through OpenRouter, reasoning effort medium) on the 9 tasks on 2026-10-04, one
attempt per task and mode, 60 minutes each, on robot_coding_bench's protocol v1.0.1 (limited: one
episode, no reset). Tasks passed, out of the 9:

| Model | Limited | Unlimited |
| --- | --- | --- |
| GPT-6 Luna | 0 | 0 |

Without resets there is no second try after a fall: the three locomotion tasks, whose episode ends
when the robot falls, ended within 43 to 49 control steps, room and bookshelf_simple at 123 and 301.
A separate run with 50 resets (robot_coding_bench PR #44; reported apart, not on this site) passed
none either, using all 50 resets on 8 of the 9 tasks. In unlimited mode the best returns are
highbar_simple's 526 of 750 (a swing held by torso-angle feedback) and package's 870 of 1500 (a
lunge that pushes the box to 8 cm from the marker), the closest any model has come on these two
(stair's 175 of 700 is the best yet too), yet the locomotion tasks stay far off (balance_hard 56 of
800, hurdle 68 of 700).

Before 2026-10-04, on all 24 tasks as they were then: one attempt per task and mode on 2026-09-30, 60
minutes each, reasoning effort medium, GPT-6.1 Sol (Codex, through OpenRouter), limited mode with 50
resets. Tasks passed, out of the 23 scored (none of the 9 kept):

| Model | Limited | Unlimited |
| --- | --- | --- |
| GPT-6.1 Sol | 3 (push, reach, sit_hard) | 9 (walk, balance_simple, push, cube, maze, basketball, reach, sit_hard, kitchen) |

Limited mode is held back by locomotion: the agent turns `spec()`'s link masses and joint positions into a
centre-of-mass estimate and can stand a whole episode, but builds no gait that moves forward, and the
graded episode is the last one, often still running when the hour ends. Unlimited mode gets much
further with whole-body control and search on the full state; two caveats: the agent rebuilds
several upstream rewards from memory almost exactly, the one leak no scrub can stop, and two passes
are close calls (reach 12008 against 12000 in limited mode, basketball 1239 against 1200). Every
run and its log are on the [Runs](../../runs/humanoidbench.md) page; each task page's Discussion
sums up its runs.

GPT-6 Luna's earlier trials on all 24 tasks (2026-09-28, and its protocol v1.0 sweep with 50 resets in
limited mode, which passed push and sit_hard) stay in its run: the latest of them is each task's history
beside the 2026-10-04 trial, and the only one on the 14 tasks that left the benchmark. The run picker also
has GPT-6 Sol and Claude Opus 5.5 (five tasks each, 2026-09-28).

## Upstream links

- [HumanoidBench](https://github.com/carlosferrazza/humanoid-bench): the environments, pinned at commit cb11890
- [Project page](https://humanoid-bench.github.io)
- [Paper](https://arxiv.org/abs/2403.10506)

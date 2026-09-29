---
title: About HumanoidBench
---

# About HumanoidBench

**HumanoidBench** puts a simulated **Unitree H1** humanoid, bare or with two **Shadow
dexterous hands**, through locomotion and whole-body manipulation in **MuJoCo**. Every episode is
scored by HumanoidBench's own dense reward, summed over the episode, against its own success
bar. We keep 23 of its 32 registered tasks plus one fixture, and run each in two modes.

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

It acts through `step` (one position target in [−1, 1] per servo, one 50 Hz step, batches allowed)
and `reset` (back to the same starting state, as often as the run allows: 50 in our runs). A run passes the moment an episode
reaches the bar; otherwise its last episode is graded. Both modes have 60 minutes of wall clock,
and simulated time stands still between requests.

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
function) and the give-aways (`pole` pays 71% of its bar for standing still), which leaves 23 in
nine capability classes (each task page names its class), plus `sit_simple`, a fixture that checks
the whole pipeline and is not scored. 15 tasks use the bare H1 (19 actuators), 9 add the Shadow
hands (61 actuators).

## What we run it on

| | |
| --- | --- |
| Image | our HumanoidBench image 0.1.6: MuJoCo and humanoid-bench at cb11890, every `get_reward()` removed |
| Physics | MuJoCo on the CPU; EGL on the GPU renders the limited mode's cameras |
| Determinism | Bit-exact: both fresh-process replays of a trajectory end in the same state |

### Model runs so far

One attempt per task and mode on 2026-09-28, 60 minutes each, reasoning effort medium, through
OpenRouter: GPT-6 Luna (Codex) on all 24 tasks; GPT-6 Sol (Codex) and Claude Opus 5.5 (Claude Code)
on five, one per class. Tasks passed, out of the scored ones:

| Model | Tasks | Limited | Unlimited |
| --- | --- | --- | --- |
| GPT-6 Luna | all 23 | 0 | 3 (push, reach, sit_hard) |
| GPT-6 Sol | walk, door, push, cube, sit_hard | 1 (push) | 1 (sit_hard; only walk and sit_hard were run) |
| Claude Opus 5.5 | the same five | 2 (push, sit_hard) | 4 (all but cube) |

Limited mode is held back by balance, not by information: nearly every failed limited run could not
stand, or fell as soon as it stepped, and of the link masses and centres of mass `spec()` gives, only
one run computed a centre of mass. Unlimited mode gets further on the full state and unlimited
retries, and loses on the agent's own objective: without the reward, the proxies it writes pay for
standing still or rank by the wrong term. Claude Opus 5.5 is the strongest on the shared five; it
rebuilt three upstream rewards from memory, the one leak no scrub can stop, and it often stopped with
most of its budget left. Every run and its log are on the [Runs](../../runs/humanoidbench.md) page;
each task page's Discussion sums up its runs.

## Upstream links

- [HumanoidBench](https://github.com/carlosferrazza/humanoid-bench): the environments, pinned at commit cb11890
- [Project page](https://humanoid-bench.github.io)
- [Paper](https://arxiv.org/abs/2403.10506)

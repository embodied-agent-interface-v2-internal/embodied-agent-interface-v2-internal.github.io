---
title: About MuJoCo Playground
---

# About MuJoCo Playground

**MuJoCo Playground** (Google DeepMind, arXiv 2502.08844) is a GPU-accelerated suite of RL environments on MJX and
MuJoCo Warp. Its manipulation part has ten environments: ALOHA 2 bimanual **hand-over** and **peg insertion**; Franka
Panda **pick cube** (with and without orientation, plus a Cartesian-control pixels variant), **open cabinet** and
**push cube** (with a Robotiq gripper); and in-hand **cube reorientation / z-rotation** with the LEAP and Aero hands.

[All 10 tasks](index.md){ .md-button .md-button--primary }
[Capability coverage](coverage.md){ .md-button }

## How we run it

Playground is built to train policies: each env defines a dense reward and an episode length, but no success test.
We load its scene XMLs (@ 4057c14, with the MuJoCo Menagerie commit it pins) in plain MuJoCo on the CPU, which replays a
recorded actuator trajectory bit-exactly, randomize the start as Playground does with a fixed seed, and add a success
test per task (on each page). The tasks run in robot_coding_bench's two modes:

- **unlimited**: the agent drives the simulator directly (privileged state) and hands in an actuator trajectory,
  replayed by a separate verifier;
- **limited**: the simulator is a robot service; the agent gets camera RGB-D and proprioception.

The oracle is a script of ours (damped-least-squares IK on the privileged object poses, gravity feedforward); it
succeeds on all four built tasks. The in-hand cube tasks are not built: they have no scripted solution short of an RL
policy.

## Upstream

- Paper: <https://arxiv.org/abs/2502.08844>
- Project page: <https://playground.mujoco.org/>
- Code: <https://github.com/google-deepmind/mujoco_playground> @ 4057c14 (Apache-2.0)

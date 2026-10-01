---
title: About DexToolBench
---

# About DexToolBench

**DexToolBench** comes with SimToolReal (arXiv 2602.16863): 6 tool categories (hammer, marker, eraser, brush, spatula,
screwdriver) × 2 real objects × 2 motions = 24 tasks, each a tool start pose and a sequence of goal poses taken from a
human RGB-D demonstration. The robot is a **KUKA iiwa 14** with a left **Sharpa HA4** hand (22 joints). The score is
**task progress**: the fraction of goals the tool reaches in order, each within a 1.5 cm keypoint tolerance and 10 s. We relax the time limit (2026-09-29): 30 s per goal in the unlimited mode, where the trajectory is replayed offline and the agent can reset freely, and none in the limited mode, where it gets one episode and no reset.

[All 24 tasks](index.md){ .md-button .md-button--primary }
[Capability coverage](coverage.md){ .md-button }

## How we run it

Upstream runs in Isaac Sim / Isaac Gym. Its repository also ships a MuJoCo sim2sim scene; we rebuilt that scene
without the training stack (bit-exact: SimToolReal's pretrained policy ends claw_hammer/swing_down in the same state in
both), added each category's table props from SimToolReal's table URDFs (a nail; a whiteboard; a bowl and a plate,
the last two as primitive stand-ins because the YCB meshes are not in the repository), and wrapped it as
robot_coding_bench tasks in both evaluation modes:

- **unlimited**: the agent drives the simulator directly (privileged state) and hands in a joint-target trajectory,
  replayed by a separate verifier;
- **limited**: the simulator is a robot service; the agent gets camera RGB-D, proprioception and the current goal.

The oracle is SimToolReal's own pretrained policy, recorded in our scene. It is the benchmark's method, not a scripted
expert, so its progress is a reference, not a ceiling: it reaches every goal on 6 tasks, some on 15 and none on 3
(those 3 are not built). The policy is publicly downloadable, so agents run without internet access apart from the
model API.

## Upstream

- Paper: <https://arxiv.org/abs/2602.16863>
- Project page: <https://simtoolreal.github.io/>
- Code and data: <https://github.com/tylerlum/simtoolreal> @ 313d5ae (MIT)

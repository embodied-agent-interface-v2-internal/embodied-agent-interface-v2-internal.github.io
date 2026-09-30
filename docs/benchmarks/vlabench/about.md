---
title: About VLABench
---

# About VLABench

**VLABench** (OpenMOSS/VLABench, commit cf588fe; assets from LeRobot's VLABench release, 08d7a44): language-conditioned
tabletop manipulation with a **Franka Panda** in **MuJoCo 3.2.2 / dm_control 1.0.22**. The 96 tasks registered at
that commit, 60 primitive and 36 composite, each as one frozen instance.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/vlabench.md){ .md-button }

## What the agent gets

- **The native action.** Nine absolute actuator targets: seven arm joints in radians and two finger slides in metres,
  each held 0.1 s (100 physics substeps). At most 4000 controls per trajectory.
- **Unlimited (privileged state).** `from vlb_traj import Session`: object and robot poses, cameras, IK, planning and
  VLABench's official general skills. The agent resets to the identical instance as often as it likes and submits one
  recorded trajectory. The complete task experts are excluded.
- **Limited (one sealed episode).** The agent's container holds a client only; a separate simulator container keeps
  the instance and records every control. Four calls: `spec()`, `observe(camera)` (RGB-D, calibration, robot
  proprioception), `step(action)`, `status()`. No reset and no object state.

## Scoring

Success is the task's own native condition at the pinned commit, when the trajectory ends; controls after native
termination are rejected. The graders replay the trajectory in **two fresh processes** from the frozen instance and
require the same exact final state.

## Reference solutions and frozen instances

Of the 96 tasks, 39 have a validated reference solution (it meets the native condition in two fresh-process
replays); their rows play it. 44 are frozen but have none: our reference replays exactly without meeting the
condition, so their rows show the instance's first frame. 13 could not be built at this commit (missing native
configuration, invalid geometry or initial physics, an initial reset that never returns, a constructor that no
longer matches), so they have no instance and no media. Two tasks carry no instruction text upstream; their pages say so.

## What we run it on

| | |
| --- | --- |
| Image | our VLABench image, 15 GB with the assets (Python 3.10, MuJoCo 3.2.2); CPU rendering (OSMesa), no GPU |
| Frozen instance | the native construction and initial state, bound by a SHA256 of the initial state |
| Determinism | Bit-exact: two fresh-process replays end in the same state |

## Upstream links

- [VLABench at the pinned commit](https://github.com/OpenMOSS/VLABench/tree/cf588fe60c0c7282174fe979f5913170cfe69017)
- [Project page](https://vlabench.github.io/)
- [VLABench paper](https://arxiv.org/abs/2412.18194)

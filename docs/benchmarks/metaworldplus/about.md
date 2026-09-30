---
title: About MetaWorld+
---

# About MetaWorld+

**Upstream Meta-World 3.1.1** (Farama-Foundation/Metaworld, commit 59fc34d), its v3 environments with reward v2, on
the **Sawyer arm** in **MuJoCo 3.3.0**. "MetaWorld+" is our suite's name for all 50 environments of that set as 70
frozen instances; there is no separate "+" release. Every instance runs in two modes.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/metaworldplus.md){ .md-button }

## What the agent gets

- **The native action, nothing else.** `[dx, dy, dz, grip]` in [-1, 1]: the hand controller's target moves 0.01 m
  per unit and the hand follows, with a fixed wrist; grip +1 closes. 80 Hz, five 2.5 ms physics steps per control.
  At most 500 controls per episode, upstream's `max_path_length`.
- **Unlimited (privileged state).** `from mw_runtime import Session`: the native observation, the goal, every body's
  pose, joint positions and velocities; `move()` is plain proportional XYZ control. The agent resets to the identical
  instance as often as it likes and submits one trajectory of at most 500 controls. No planner, no expert policy: the
  upstream scripted policies are removed from the agent's image.
- **Limited (one sealed episode).** The agent's container holds a client only; a separate simulator container keeps
  the instance and records every control. Four calls: `spec()`, `observe(camera)` (RGB, metric depth, the camera's
  intrinsics and pose, robot proprioception), `step(action)`, `status()`. No reset and no object or goal state. The
  episode ends at native success, at 500 controls, or after 60 minutes, and is sealed from its first control.

## Scoring

Success is the environment's own success flag (`evaluate_state` at the pinned commit; each task page quotes the
statement), attained at **any** control of the trajectory, as upstream evaluates it. The dense reward is shown for
diagnosis only. The graders replay the trajectory in **two fresh processes** from the frozen instance and require
the same exact final state; in the limited mode the sealed online state must match too.

In the limited mode the goal must be visible or implied by the task sentence. For 69 of the 70 instances it is: a native
goal marker renders in the fixed cameras, or the goal is set by visible geometry (a button, a nail, a socket).
`sweep-v3` puts its target at the table's right edge with no marker (its goal site sits at the world origin) and a
sentence that says only "the target position", so its limited mode is not evaluated. Each task page says which case
it is.

## Families and instances

All 50 environment families of the v3 set are here, one instance each, and three instances (seeds 0 to 2, or 1 to 3
for stick-pull, whose seed 0 has no working reference) for assembly, button-press-wall, door-open, drawer-open,
hammer, peg-insert-side, pick-place, push, stick-pull and stick-push. The instance number and the seed are different
fields: soccer's instance 0 is seed 1.

## What we run it on

| | |
| --- | --- |
| Image | our Meta-World image, 1.1 GB (Python 3.11, MuJoCo 3.3.0); CPU rendering (OSMesa), no GPU |
| Frozen instance | full MuJoCo integration state, model arrays, task caches and RNG, bound by a SHA256 |
| Determinism | Bit-exact: the live run equals two fresh-process replays |

## Upstream links

- [Meta-World at the pinned commit](https://github.com/Farama-Foundation/Metaworld/tree/59fc34d7768af9785e4688c3e1db671424f4a6c3)
- [Documentation](https://metaworld.farama.org/)
- [Meta-World paper](https://arxiv.org/abs/1910.10897)

---
title: About RoboWits
---

# About RoboWits

30 seed tasks on a **fixed bimanual robot** (two 7-DoF arms, two-finger grippers) in
**Genesis**, plus 163 published mutations that vary the scene while keeping the parent
task's success predicate. The premise is that a task should need an *insight*, not a
longer motion: align three cubes by pushing them against a ruler, sweep a screw into a
dustpan, pour a ball through a funnel, reach a roll with a rod.

[All 30 tasks](index.md){ .md-button .md-button--primary }
[Capability coverage](coverage.md){ .md-button }

## Why we are looking at it

It is the opposite end of the axis from BEHAVIOR-1K. There is no navigation, no house,
and an episode is seconds rather than minutes — so a task fails for one legible reason,
which makes it a good instrument for a coding agent. Several tasks are unsolvable by
pick-and-place no matter how precise the arm is, which is exactly the property we want
to measure.

## The embodiment

| | |
| --- | --- |
| Robot | Marvin, bimanual — 2 × 7-DoF arms, 2 × 2-finger Pika grippers (18 DoF) |
| Base | Fixed at a table; no navigation |
| Control | `EE_ABS` (default), `EE_DELTA`, `JOINT_ABS`, `JOINT_DELTA` at 30 Hz |
| Cameras | ego + both wrists, 848 × 480 |
| Privileged state | Available in simulation; a task can be run state-based or from pixels |

## How a task defines success

Every environment class carries its own `_check_success`, and states the criteria in its
docstring. Those criteria are mirrored verbatim into each task page's `upstream:` block —
that list is the benchmark's definition, not our paraphrase. `14 stack cubes`, for example:

> Base cubes are on the table and touching with ≥ 50% face overlap · Apex cube sits on top
> of base cubes · Apex cube centre is within tolerance of target marker · Apex-target
> overlap ≥ 20%

Each task ships **50 evaluation scenes** (`dataset/robowits/eval_dataset_50/<NN>.json`),
which is where placement variation comes from: same predicate, different object poses.

## Demo coverage

23 of the 30 tasks have a clip on the [project page](https://umass-embodied-agi.github.io/RoboWits/),
downloaded by `make demos` and played inline. The **seven without one are exactly the seven
that use non-rigid physics** — dough (MPM), sand, water and marbles (SPH/PBD):

`round_dough_sheet` · `separate_marbles_and_sand` · `ball_into_jar` · `seal_colander` ·
`stabilize_bottle` · `water_into_mug` · `differentiate_cubes`

They are also the ones we have not run, and the correlation is worth keeping in mind when
triaging: the deformable tasks are the least evidenced part of the suite.

The project page also publishes two mutation clips for several seed tasks (same predicate,
added distractors, a replaced tool). We do not mirror those; they are one click away from
the task's own row.

## What we run it on

Pinned to the commit our image builds from, **9cc30ae** (the 2026-06-04 code release), and
measured on an RTX 4090 laptop:

| | |
| --- | --- |
| Image | `nvidia/cuda` 12.9 + RoboWits from its own `uv.lock`, ~20 GB |
| Physics | **CPU backend** — Genesis' GPU backend settles contacts differently run to run |
| Determinism | Bit-exact across processes on the CPU backend |
| Throughput | ~700 control steps/s headless, ~30 with three cameras rendering |
| Scene build | ~60 s per process |

!!! warning "27 of 30 tasks need BlenderKit assets"

    Their meshes are paid assets that may not be redistributed, so they are not in the
    image: the host owner downloads them with a personal API key. Only `06 dominos`,
    `07 stand pages` and `14 stack cubes` run from the Apache-2.0 bundle alone — which is
    why `14 stack cubes` is the task we integrated first.

## Upstream links

- [Project page](https://umass-embodied-agi.github.io/RoboWits/) — the source of the demo clips
- [Paper](https://arxiv.org/abs/2605.30326)
- [Repository](https://github.com/UMass-Embodied-AGI/RoboWits) — the source our task pages sync from
- [Demonstration dataset](https://huggingface.co/datasets/XHRlyb2001/RoboWits_lerobot_dataset) — ~50 demos on 24 seed tasks
- [Asset bundle](https://huggingface.co/datasets/XHRlyb2001/RoboWits_assets)

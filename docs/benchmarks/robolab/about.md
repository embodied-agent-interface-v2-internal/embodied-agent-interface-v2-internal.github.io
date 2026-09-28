---
title: About RoboLab
---

# About RoboLab

120 tabletop tasks on a **fixed-base Franka with a Robotiq 2F-85 gripper**, simulated in
**Isaac Lab / Isaac Sim**. The manipulation is deliberately ordinary — almost every task is
pick-and-place. What varies is how the goal is *stated*: by colour, by size, by category, by
count, by spatial relation, by order, or vaguely enough that the agent has to interpret it.

[All 120 tasks](index.md){ .md-button .md-button--primary }
[Capability coverage](coverage.md){ .md-button }

## Why we are looking at it

It isolates language grounding from motor difficulty. A suite where the physical act is
constant and the instruction changes is the cleanest way to ask whether an agent understood
the goal, and it is the axis BEHAVIOR-1K does not test (its instructions are long but each
names its objects). Three wordings ship per task — `default`, `vague`, `specific` — which
makes "did it understand, or did it pattern-match?" a measurable question rather than a
rhetorical one.

## The embodiment

| | |
| --- | --- |
| Robot | Franka Panda + Robotiq 2F-85 (RoboLab's "DROID" configuration) |
| Action | 7 absolute joint-position targets + 1 binary gripper command, at 15 Hz |
| Cameras | Wrist 1280 × 720; an egocentric viewport camera for recording |
| Privileged state | Available (`--enable-gt-state`); tasks can be run state-based or from pixels |
| Episode budget | 20–300 s, declared per task (`episode_length_s`) |

Tasks are not tied to the embodiment — any Isaac Lab robot can be dropped in, which is
unusual and makes the suite reusable if we change robots.

## How a task defines success

A task is a dataclass: a scene, three instruction wordings, an episode budget, attribute
tags, one success predicate and a list of scored subtasks. Success is a composable predicate
over object state — `object_in_container` (72 tasks), `object_on_top` (13),
`object_outside_of_and_on_surface` (7), `stacked` (5), `object_upright` (4), and spatial
relations. All of it is mirrored into each task page's `upstream:` block.

**Partial credit** comes from the subtask list: 7 tasks score in fractions, the rest are
all-or-nothing.

## Upstream's attribute tags, and its difficulty label

RoboLab tags every task from an 11-term vocabulary and derives a difficulty label from it
(`SKILL_WEIGHTS` over the attributes against `DIFFICULTY_THRESHOLDS`). We mirror both:

| Attribute | Tasks | | Attribute | Tasks |
| --- | --- | --- | --- | --- |
| `semantics` | 60 | | `conjunction` | 8 |
| `spatial` | 29 | | `counting` | 7 |
| `color` | 26 | | `vague` | 7 |
| `affordance` | 12 | | `size` | 6 |
| `sorting` | 12 | | `stacking` | 6 |
| | | | `reorientation` | 6 |

Those tags are what a task page's `skills:` records, seeded from upstream.

!!! important "`difficulty_label` is theirs; `difficulty` is ours"

    Upstream's label (108 simple, 8 moderate, 4 complex) is computed from the attribute
    weights above — it measures how much *language* the task involves. Our `difficulty` in
    `state/tasks/robolab.yml` asks a different question: how hard is this for a coding agent
    driving the robot? Do not copy one into the other.

## Demo coverage

13 of the 120 tasks have a clip on the
[project page](https://research.nvidia.com/labs/srl/projects/robolab), downloaded by
`make demos`. RoboLab distributes no demonstration dataset — it evaluates policies rather
than shipping teleoperation — so the other 107 rows show **the scene the task starts from**
instead, taken from the scene previews that ship with the repository. A still is not a
demonstration, and the row says so; it is the difference between reviewing a task and
guessing at it.

One row plays a video that is **ours, not upstream's**: `banana_in_bowl`, the task we
integrated into `robot_coding_bench`. The credit line under the player says so.

## What we run it on

Pinned to **v0.3.1**, the tag our image builds from, measured on an RTX 4090 laptop:

| | |
| --- | --- |
| Image | `nvidia/cuda` 12.8 + RoboLab v0.3.1 from our `uv.lock` + its asset library, 14.5 GB |
| Physics | **CPU PhysX** — bit-exact live, in-process and across processes |
| GPU PhysX | Reproduces a live run in a fresh process, but drifts ~1 mm across in-process replays after `reset_to`; `enable_enhanced_determinism` does not change that |
| Throughput | ~15 control steps/s with the wrist and viewport cameras rendering |
| Startup | ~70 s Isaac Sim launch + ~30 s scene build per process, ~5 GB VRAM |

Version matters here: v0.3.1 moved the canonical ground plane and made
`ee_recorder_bodies` mandatory, so recordings do not transfer from v0.2.x.

## Upstream links

- [Project page](https://research.nvidia.com/labs/srl/projects/robolab) — the source of the demo clips
- [Paper](https://arxiv.org/abs/2604.09860) · [Leaderboard](https://research.nvidia.com/labs/srl/projects/robolab/leaderboard.html)
- [Repository](https://github.com/NVlabs/RoboLab) — the source our task pages sync from
- [Upstream task table](https://github.com/NVlabs/RoboLab/blob/main/robolab/tasks/README.md)

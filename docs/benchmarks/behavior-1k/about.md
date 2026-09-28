---
title: About BEHAVIOR-1K
---

# About BEHAVIOR-1K

100 full-length household activities in house-scale scenes, simulated in
**OmniGibson** (built on NVIDIA Isaac Sim). Agents must combine
high-level reasoning, long-horizon navigation, and dexterous bimanual
manipulation. Scoring is average task success with **BDDL partial credit**, so
a task is not simply pass/fail.

[All 100 tasks](index.md){ .md-button .md-button--primary }
[Capability coverage](coverage.md){ .md-button }

## Why we are looking at it

It is the closest public benchmark to what we want to measure. The tasks are
long (5.9 minutes of teleoperation on average), the goals are specified
declaratively in BDDL rather than as a fixed trajectory, and evaluation is
restricted to onboard sensing. That combination makes it hard to solve by
memorising a motion and rewards agents that can actually plan.

## The embodiment

| | |
| --- | --- |
| Robot | R1 Pro |
| Teleoperation interface | JoyLo — whole-body control of base, torso, arms, grippers |
| Observations at eval | RGB + depth + proprioception, **onboard only** |
| Head camera | 720 × 720 |
| Wrist cameras | 480 × 480 (left and right) |
| Depth range | 0–10 m, float32, log-quantised during collection |

!!! important "No privileged state"

    Evaluation exposes no ground-truth object poses and no simulator internals.
    Anything an agent needs to know, it has to see. This is the constraint that
    most often invalidates an otherwise reasonable policy design, so keep it in
    mind when labelling a task
    [Partial observability](../../reference/capabilities.md#cap-partial-observability).

## The two task cohorts

The 100 tasks are not homogeneous, and the split matters for anyone planning work:

| Cohort | Count | Demos hosted on | Instruction text |
| --- | --- | --- | --- |
| `2026-new` | 50 | Vimeo | Published upstream |
| `2025-carryover` | 50 | YouTube | **Not published** |

The 2025 carryover tasks reuse the 50 tasks from the previous challenge, and
the public gallery ships no natural-language instruction for them. We record
that as an empty `instruction` rather than inventing one. Reconstructing those
goals from the oracle demos is tracked as open work on the
task list — see the [task page guide](../../contributing/task-page-guide.md#reconstructing-a-missing-instruction)
for how to do it without passing a guess off as the official goal.

## Scenes

Seven scenes, four of them new for 2026. Scene is a useful unit of work: if you
are setting up the environment anyway, triaging every task in one scene at once
amortises the load time.

| Scene | Tasks |
| --- | --- |
| `house_single_floor` | 34 |
| `house_double_floor_lower` | 32 |
| `house_double_floor_upper` | 10 |
| `restaurant_diner` | 8 |
| `Rs_int` | 6 |
| `hotel_suite_large` | 5 |
| `office_cubicles_right` | 5 |

Filter the task list by scene: [`house_single_floor`](index.md?scene=house_single_floor).

## Demonstration data

| | |
| --- | --- |
| Trajectories | 20,000 across 100 tasks |
| Total | 1,950 hours |
| Mean trajectory | 351.54 s (~5.9 min) |
| Annotated skill instances | 270,600, from a 31-primitive vocabulary |
| Raw HDF5 replay | [`2026-challenge-rawdata`](https://huggingface.co/datasets/behavior-1k/2026-challenge-rawdata) — 1.44 TB |
| LeRobot v3 | [`2026-challenge-demos`](https://huggingface.co/datasets/behavior-1k/2026-challenge-demos) — 3.27 TB |

The 31 skill primitives are the benchmark's own annotation vocabulary and are
listed on the [coverage page](coverage.md#skill-primitives). They are
*descriptive* — what the demo does. Our
[capability taxonomy](../../reference/capabilities.md) is *normative* — what an
agent must be able to do. Keep them apart; they are different columns for a
reason.

## Checked against the distribution we actually run

The pages above are synced from the public gallery. We also run the benchmark
itself — BEHAVIOR-1K v3.9.2 on OmniGibson 3.9.2 / Isaac Sim 5.1, with the
licensed asset bundle and the challenge task-instance download — so every task
page carries a second machine-written block, `verified:`, read from that copy by
`scripts/import_behavior_verified.py`: the BDDL goal the evaluator scores, the
dataset's own per-task statistics, and the public test instances that ship.

Cross-checking the two sources on 21 September 2026 found the gallery accurate,
with one exception and one thing that is easy to misread:

| Check | Result |
| --- | --- |
| Task set | 100 in the gallery, 100 in the dataset, same ids |
| `scene_model` | 100/100 agree |
| Room lists | 99/100 agree; see below |
| Published duration | Exactly explained, see below |
| Instruction | 50 published; the other 50 now have their BDDL goal instead |

**The published duration means different things in the two cohorts.** For the 50
`2026-new` tasks it is the dataset's mean episode length, to the second (50/50) —
and the Vimeo video is an edited version running 42–100% of it. For the 50
`2025-carryover` tasks it is the *video's* length (50/50), which is not the mean
episode length. So a row's duration label (the probed video) and `verified.demo_mean_s`
(200 teleoperated episodes) are both right and will differ for half the suite.

**One room list disagrees.** `turning_out_all_lights_before_sleep` is published with
`bathroom`, `bedroom` and `childs_room` among its rooms, but the challenge metadata
loads `corridor`, `utility_room`, `dining_room`, `entryway`, `garden`, `kitchen` and
two living rooms for it — none of the three. Its goal is two `toggled_on` clauses over
switches and table lamps, so which rooms are loaded decides what the task even contains.
Worth resolving upstream before anyone uses that task.

## Baselines and dates

Two baselines ship with the challenge: **π0.5** and **GR00T N1.7**, both
vision-language-action models.

| Milestone | Date |
| --- | --- |
| Launch | 2 July 2026 |
| Submission deadline | **16 October 2026** |

## Upstream links

- [Challenge overview](https://behavior.stanford.edu/challenge/index.html)
- [Official demo gallery](https://behavior.stanford.edu/challenge/tasks/index.html) — the source our task pages sync from
- [Dataset documentation](https://behavior.stanford.edu/challenge/dataset.html)
- [Call for participation](https://behavior.stanford.edu/challenge/call_for_participation.html)
- [Leaderboard](https://huggingface.co/spaces/behavior-1k/2026-challenge-leaderboard) · [Submission portal](https://behavior-1k-2026-challenge-leaderboard.hf.space/submit)
- [BEHAVIOR-1K repository](https://github.com/StanfordVL/BEHAVIOR-1K)

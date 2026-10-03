---
title: About VLABench
---

# About VLABench

[VLABench](https://github.com/OpenMOSS/VLABench) (@ cf588fe) is a language-conditioned manipulation benchmark for a **Franka Panda** in **MuJoCo** with dm_control: selecting by attribute, common sense, semantic or spatial description, answering physical questions by pressing a button, and multi-step tasks. Each of our tasks is one native task on one frozen scene (VLABench's own episode configuration, seed 0), with an instruction that states exactly what the success check requires.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/vlabench.md){ .md-button }

## What the agent gets

**Unlimited (privileged).** The agent drives VLABench in Python with every entity's pose, grasp and place points, VLABench's general skills (pick, place, pull, press, ...) as planning primitives, inverse kinematics and unlimited resets, and hands in one trajectory of joint-position control steps (at most 4000), which the verifier replays twice in fresh processes.

**Limited (standard).** The simulator runs in a service the agent cannot open. It sees four cameras (forward, left and right fixed, one on the wrist; RGB 320×320, depth on request, calibration) and the arm's joints, fingers and last command; never an object's pose or the success check. One episode, no reset; the episode stops at 9000 control steps (a technical cap, so that the grading replay fits its time).

Both modes have 60 minutes of wall clock, and the agent reaches the model APIs and nothing else (the references are
public upstream).

## Scoring

VLABench's own success check, the task's termination condition: the episode ends the moment it holds, so the graded state is the trajectory's last. A privileged trajectory that goes on after the task has terminated is invalid.

## The tasks

VLABench has 96 native tasks. We keep the 36 whose recorded expert (VLABench's own `get_expert_skill_sequence`, recorded as control steps) re-verifies on a frozen instance, one instance each. Left out: 41 whose expert fails on the frozen instance, 13 that could not be frozen bit-exactly, 3 whose earlier references re-verify as failures, and 3 dropped in review (a duplicate of another task and two whose upstream instruction is an unfilled template). The per-task experts are removed from the image. 36 tasks here, each a pair in robot_coding_bench: `tasks/vlabench-<task>-i00-privileged` and
`-standard` @ 8c5594a43, written by `scripts/vlabench/generate.py`; their notes are in robot_coding_bench's
`docs/benchmarks/vlabench.md`. The task pages are synced by `scripts/import_vlabench_tasks.py`
(`make sync-vlabench`).

## The demos

Each row's video is ours: the verifier's replay of the task's reference solution on its frozen instance in the
privileged mode, re-encoded for the site. It shows that the task can be done as specified; it is not the benchmark's
own demonstration video.

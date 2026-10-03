---
title: About MetaWorld+
---

# About MetaWorld+

**MetaWorld+** is our benchmark built on [Meta-World](https://github.com/Farama-Foundation/Metaworld) v3 (@ 59fc34d, reward v2): all 50 environments for a **Sawyer** arm in **MuJoCo 3.3.0**, one frozen instance each (Meta-World's own reset randomization drawn with seed 0; seed 1 for soccer and stick-pull, where the scripted policy fails on seed 0). The arm is driven through its hand: Meta-World's native action moves a mocap target that the arm follows, and the wrist does not rotate.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/metaworldplus.md){ .md-button }

## What the agent gets

**Unlimited (privileged).** The agent drives Meta-World in Python with its whole state (object and goal positions, joints, contacts), resets as often as it likes, and hands in one trajectory of at most 500 native actions (Meta-World's episode length), which the verifier replays twice in fresh processes.

**Limited (standard).** The simulator runs in a service the agent cannot open. It sees four fixed cameras (front, left, right and Meta-World's top view; RGB, depth and calibration), the hand's position, the gripper opening, the hand target, the arm and finger joints, its last command and the task's target point (`target_pos`); never an object's pose or the success check. One episode, no reset, no step limit: only the 60 minutes of wall clock.

Both modes have 60 minutes of wall clock, and the agent reaches the model APIs and nothing else (the references are
public upstream).

## Scoring

Meta-World's own success check (`evaluate_state`) on the state after the last action; a success reached earlier and then lost does not count. In three environments (handle-press, handle-pull-side, stick-pull) the success state does not persist by itself, so a trajectory must end while it holds. The privileged mode is reported as a control, not in the main (standard-mode) table: it is saturated under final-state grading (decision on the benchmark proposal).

## The tasks

All 50 v3 environments (`ENV_CLS_MAP`), no selection. The reference solution of each is Meta-World's scripted policy for it, run on the frozen instance up to its first success (41 to 136 actions), and re-verified by two fresh-process replays; the policies are removed from the image. 50 tasks here, each a pair in robot_coding_bench: `tasks/metaworldplus-<task>-i00-privileged` and
`-standard` @ 8c5594a43, written by `scripts/metaworldplus/generate.py`; their notes are in robot_coding_bench's
`docs/benchmarks/metaworldplus.md`. The task pages are synced by `scripts/import_metaworldplus_tasks.py`
(`make sync-metaworldplus`).

## The demos

Each row's video is ours: the verifier's replay of the task's reference solution on its frozen instance in the
privileged mode, re-encoded for the site. It shows that the task can be done as specified; it is not the benchmark's
own demonstration video.

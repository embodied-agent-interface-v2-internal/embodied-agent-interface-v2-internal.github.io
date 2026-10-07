---
title: About RoboPaint
---

# About RoboPaint

A benchmark we built for coding agents: a **Franka Panda holding a brush or pen** writes or paints
the exemplar it is shown onto a sheet of paper. **ManiSkill 3.0.1** (SAPIEN 3.0.3, PhysX on the
CPU) simulates the robot; brush models turn the path the tip actually took into ink or paint (a
calligraphy brush model, a broad nib for lettering, **libmypaint 1.6.1** for acrylic and oil). 82
brush targets — 楷书 kaishu 35, 行书 xingshu 16, lettering 10, acrylic 10, oil 11 — each in both
modes. The verifier scores the sheet against the picture **and checks how it was made**: the
exemplar has to be written or painted with strokes, the way a person does, not coloured in.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/robopaint.md){ .md-button }

!!! note "Since 2026-10-07 (robot_coding_bench PR #68)"

    RoboPaint is what was briefly listed here as RoboPaint-strict: the same scenes, pictures,
    tooling, picture rule and reference solutions, with the process rules below added to the
    verifier. The first version scored the final sheet only; its tasks and results are retired
    (they are not comparable with these). Its nine line drawings stay on the site for the record and
    are not run.

## What the agent gets

- **A picture, never a vector.** The exemplar is an RGB image, `target.png`, at the paper's true
  size and place. The drawing's geometry stays with the graders.
- **Thin primitives**: tip moves on per-step IK, joint moves, hold. Everything between the picture
  and a trajectory is the agent's.
- **A main sheet and a practice sheet** (practice strokes are free), an ink stone or paint wells,
  and 7200 s of wall clock per mode. Strokes cannot be undone.

## Scoring

The final sheet is scored against the picture, in both fresh-process replays; each task page lists
its thresholds. Every family first aligns the sheet with the picture (the best single shift, at
most 5 mm along each axis). **Calligraphy and lettering**: IoU, boundary F within 1 mm, how much of
each stroke is covered, stray ink and a stroke limit; the IoU is the continuous score. **Acrylic and
oil**: CIELAB ΔE (mean and p90), SSIM of L\*, edge correlation, paint IoU and a stroke limit;
1 − mean ΔE / 20 is the continuous score. `success` = the picture rule **and** the process rules;
`final_reward` is the continuous score, scaled down when a rule fails.

In the unlimited mode `s.score()` gives this feedback without giving the target away: a **scoring
sidecar**, a separate container with the graders' copy of the instance, replays the agent's actions
and returns only the metrics (the rule metrics included). The limited mode has no score: cameras and
proprioception only, and no reset.

## The process rules

Only inked strokes on the main sheet count; practice-sheet strokes are free. `path_mm` is the total
length of the brush (pen) tip's path while it presses on the main sheet.

- **Writing** (kaishu, xingshu, lettering): colouring in fails — a path longer than `max_path_mm`
  (3 × the reference solution's) made of marks narrower than `min_mark_width_mm` (0.3 × the
  reference's) on average.
- **Painting** (acrylic, oil): a path budget, `path_mm` ≤ `max_path_mm` (3 × the reference's), and
  strokes are sweeps: at most 10 % of the path in strokes longer than 2.5 × the diagonal of their
  bounding box (zigzags, back-and-forth fills, spirals, loops).

Each task page states its own numbers. `success` = the picture rule and the process rules.
`final_reward` is the picture's continuous score, scaled down when a rule fails, so rule-abiding work
keeps its score. `s.score()` returns the rule metrics in the unlimited mode, so an agent can
check itself.


## Why the process rules

On the first version, GPT-6 Astra passed most of its tasks without writing or painting: it set one light
press that draws a thin line and filled the exemplar's area with long back-and-forth or
contour-offset paths. The first version scored only the final sheet against the picture, so colouring
in passed. The rules measure the strokes themselves, and they are placed so that colouring in fails
while ordinary attempts, good or poor, keep their picture-rule verdict.


## Calibration

The rules were calibrated on the 82 reference solutions and on recorded runs of the first version: every
reference solution passes; GPT-6 Astra's 109 first-version successes keep 7 (its real lettering), the
other 102 being colour-in; GPT-6 Luna's 53 successes keep 49 (three acrylic serpentine fills and
one zigzag lettering fill flip). No failure turns into a success.

## What we run it on

| | |
| --- | --- |
| Image | our RoboPaint image (eai-robopaint 0.2.0: ManiSkill 3.0.1, SAPIEN 3.0.3, a patched libmypaint 1.6.1) |
| Physics | PhysX on the CPU; the GPU (Vulkan) only renders the cameras |
| Determinism | Bit-exact: the live run equals two fresh-process replays |

libmypaint is ISC (patched), mypaint-brushes CC0-1.0; the targets are ours (CC0) or public-domain works.

## Upstream links

- [ManiSkill](https://github.com/haosulab/ManiSkill): the robot simulator
- [libmypaint](https://github.com/mypaint/libmypaint): the paint model for acrylic and oil

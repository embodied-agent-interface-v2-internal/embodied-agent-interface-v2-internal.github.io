---
title: About RoboPaint-strict
---

# About RoboPaint-strict

[RoboPaint](../robopaint/about.md)'s 82 brush targets — 楷书 kaishu 35, 行书 xingshu 16, lettering 10,
acrylic 10, oil 11, each in both modes — with **process rules** added to the verifier: the exemplar
has to be written or painted with strokes, the way a person does, not coloured in. Everything else
is RoboPaint's: the scene and frozen instance, the picture, the tooling, the picture rule, the
reference solution, the image and the 7200 s budget. RoboPaint's tasks and results stay as they
are, and a RoboPaint trajectory is graded by the strict verifier as it is, so the two compare one
to one.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/robopaint-strict.md){ .md-button }

## Why

On RoboPaint, GPT-6 Astra passed most of its tasks without writing or painting: it set one light
press that draws a thin line and filled the exemplar's area with long back-and-forth or
contour-offset paths. RoboPaint scores only the final sheet against the picture, so colouring in
passed. The rules measure the strokes themselves, and they are placed so that colouring in fails
while ordinary attempts, good or poor, keep their RoboPaint verdict.

## The rules

Only inked strokes on the main sheet count; practice-sheet strokes are free. `path_mm` is the total
length of the brush (pen) tip's path while it presses on the main sheet.

- **Writing** (kaishu, xingshu, lettering): colouring in fails — a path longer than `max_path_mm`
  (3 × the reference solution's) made of marks narrower than `min_mark_width_mm` (0.3 × the
  reference's) on average.
- **Painting** (acrylic, oil): a path budget, `path_mm` ≤ `max_path_mm` (3 × the reference's), and
  strokes are sweeps: at most 10 % of the path in strokes longer than 2.5 × the diagonal of their
  bounding box (zigzags, back-and-forth fills, spirals, loops).

Each task page states its own numbers. `success` = RoboPaint's picture rule and the process rules.
`final_reward` is RoboPaint's continuous score, scaled down when a rule fails, so rule-abiding work
keeps RoboPaint's score. `s.score()` returns the rule metrics in the unlimited mode, so an agent can
check itself.

## Calibration

The rules were calibrated on the 82 reference solutions and on recorded RoboPaint runs: every
reference solution passes; GPT-6 Astra's 109 RoboPaint successes keep 7 (its real lettering), the
other 102 being colour-in; GPT-6 Luna's 53 successes keep 49 (three acrylic serpentine fills and
one zigzag lettering fill flip). No failure turns into a success.

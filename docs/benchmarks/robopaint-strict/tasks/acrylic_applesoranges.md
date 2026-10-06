---
title: Acrylic · Applesoranges
task_id: acrylic_applesoranges
benchmark: robopaint-strict

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: our RoboPaint-strict task definitions
  synced: '2026-10-06'
  instruction: Copy the painting shown in the picture /app/target.png (a small acrylic painting after Paul Cezanne's Still Life with Apples and Oranges, c. 1899) onto the main sheet, in at most 390 strokes.
  scene_model: robopaint_acrylic
  scene_image: acrylic_applesoranges.png
  family: acrylic
  picture: a small acrylic painting after Paul Cezanne's Still Life with Apples and Oranges, c. 1899
  difficulty: hard
  success_criteria:
    - scored at a 1 mm scale against the picture after the best single shift of the sheet,
      at most 5 mm along each axis
    - mean CIELAB ΔE <= 2.0
    - p90 ΔE <= 6.0
    - SSIM of L* >= 0.92
    - edge correlation >= 0.8
    - paint IoU >= 0.95
    - at most 390 strokes
    - both fresh-process replays of the trajectory meet this and end in the same state
    - 'process rules: paint with brush strokes the way a person paints; colouring in or
      filling areas with a thin line, zigzag, serpentine or contour-offset fills fail;
      the brush tip''s path pressed on the main sheet with paint is at most 33900 mm in
      total, and at most 10 % of it in strokes longer than 2.5 x the diagonal of their
      bounding box'
  continuous_score: 1 - mean ΔE / 20
  grader_facts:
    name: applesoranges
    alpha: truth_alpha.npz
    n_strokes: 300
    source: painted by a hidden stroke program (solution/) with this instance's robot
      and brush, made by P's optimiser from File:Nature morte aux pommes et aux oranges,
      par Paul Cézanne.jpg
    license: CC0-1.0
    area_mm2: 49083.4
  scoring: 's.score() is served by a separate scoring container: it replays the actions the agent executed since its last reset on the graders'' copy and returns the metrics, never images or target data'
  agent_budget: 7200 s of wall clock per mode
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/robopaint-strict.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- The demo is our reference solution, replayed by the verifier: canvas camera,
     scene camera, side camera and the exact canvas. Say whether
     the trajectory is clean and what it relies on. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

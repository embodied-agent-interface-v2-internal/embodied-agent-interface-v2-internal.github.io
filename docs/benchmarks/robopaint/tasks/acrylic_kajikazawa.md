---
title: Acrylic · Kajikazawa
task_id: acrylic_kajikazawa
benchmark: robopaint

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: our RoboPaint task definitions
  synced: '2026-09-28'
  instruction: Copy the painting shown in the picture /app/target.png (a small acrylic painting after Katsushika Hokusai's woodblock print Kajikazawa in Kai Province, c. 1830-32) onto the main sheet, in at most 377 strokes.
  scene_model: robopaint_acrylic
  scene_image: acrylic_kajikazawa.png
  family: acrylic
  picture: a small acrylic painting after Katsushika Hokusai's woodblock print Kajikazawa in Kai Province, c. 1830-32
  difficulty: hard
  tier: privileged
  success_criteria:
    - scored at a 1 mm scale against the picture after the best single shift of the sheet,
      at most 5 mm along each axis
    - mean CIELAB ΔE <= 2.0
    - p90 ΔE <= 6.0
    - SSIM of L* >= 0.92
    - edge correlation >= 0.8
    - paint IoU >= 0.95
    - at most 377 strokes
    - both fresh-process replays of the trajectory meet this and end in the same state
  continuous_score: 1 - mean ΔE / 20
  grader_facts:
    name: kajikazawa
    alpha: truth_alpha.npz
    n_strokes: 290
    source: painted by a hidden stroke program (solution/) with this instance's robot
      and brush, made by P's optimiser from File:Kajikazawa in Kai province.jpg
    license: CC0-1.0
    area_mm2: 49526.3
  scoring: 's.score() is served by a separate scoring container: it replays the actions the agent executed since its last reset on the graders'' copy and returns the metrics, never images or target data'
  agent_budget: 7200 s of wall clock per mode
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/robopaint.yml. One bullet per label is
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

---
title: Oil · Bathers
task_id: oil_bathers
benchmark: robopaint

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: our RoboPaint task definitions
  synced: '2026-09-28'
  instruction: Paint the picture shown in /app/target.png (a square crop of Georges Seurat's Bathers at Asnières, 1884) onto the main sheet with brush and oil paints, in at most 449 strokes.
  scene_model: robopaint_oil
  scene_image: oil_bathers.png
  family: oil
  picture: a square crop of Georges Seurat's Bathers at Asnières, 1884
  difficulty: extreme
  tier: privileged
  success_criteria:
    - scored at a 1 mm scale against the picture, all after the best single shift of the
      sheet, at most 5 mm along each axis, inside the central area 8 mm in from the sheet's
      edges
    - mean CIELAB ΔE <= 7.1
    - p90 ΔE <= 13.0
    - SSIM of L* >= 0.71
    - edge correlation >= 0.5
    - paint IoU >= 0.96
    - at most 449 strokes
    - both fresh-process replays of the trajectory meet this and end in the same state
  continuous_score: 1 - mean ΔE / 20
  grader_facts:
    name: bathers
    alpha: truth_alpha.npz
    n_strokes: 299
    source: 'the reference picture: File:Baigneurs a Asnieres.jpg (public domain), cropped
      and downscaled'
    license: Public domain
    area_mm2: 51612.8
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

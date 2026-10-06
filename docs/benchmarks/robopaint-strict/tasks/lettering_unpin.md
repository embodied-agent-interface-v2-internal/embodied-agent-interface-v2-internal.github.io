---
title: Lettering · Unpin
task_id: lettering_unpin
benchmark: robopaint-strict

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: our RoboPaint-strict task definitions
  synced: '2026-10-06'
  instruction: Copy the lettering shown in the picture /app/target.png onto the main sheet with pen and ink, in at most 8 strokes.
  scene_model: robopaint_lettering
  scene_image: lettering_unpin.png
  family: lettering
  difficulty: hard
  success_criteria:
    - scored against the picture after the best single shift of the sheet, at most 5 mm
      along each axis
    - IoU >= 0.86
    - boundary F within 1 mm >= 0.80
    - every stroke of the exemplar covered >= 0.75
    - stray ink <= 0.04 of its inked area
    - at most 8 strokes
    - both fresh-process replays of the trajectory meet this and end in the same state
    - 'process rules: letter with pen strokes the way a scribe writes; colouring in or
      filling the letters, zigzag, serpentine or contour-offset fills fail: a pen-tip
      path on the main sheet longer than 960 mm made of marks narrower than 0.77 mm on
      average is colouring in'
  continuous_score: IoU
  grader_facts:
    word: unpin
    hand: italic
    n_strokes: 8
    source: letter skeletons authored for this benchmark
    license: CC0-1.0
    tol_mm: 1.0
    area_mm2: 742.9
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

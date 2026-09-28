---
title: Xingshu · Nian
task_id: xingshu_nian
benchmark: robopaint

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: our RoboPaint task definitions
  synced: '2026-09-28'
  instruction: Copy the exemplar character 年 in running script (行书), shown in the picture /app/target.png, onto the main sheet with brush and ink, in at most 7 strokes.
  scene_model: robopaint_xingshu
  scene_image: xingshu_nian.png
  family: xingshu
  difficulty: hard
  tier: privileged
  success_criteria:
    - scored against the picture after the best single shift of the sheet, at most 5 mm
      along each axis
    - IoU >= 0.80
    - boundary F within 1 mm >= 0.75
    - every region of the exemplar's ink covered >= 0.80
    - stray ink <= 0.04 of its inked area
    - at most 7 strokes (continuous brush contacts)
    - both fresh-process replays of the trajectory meet this and end in the same state
  continuous_score: IoU
  grader_facts:
    character: 年
    n_strokes: 10
    license: Public domain ({{PD-Art|PD-old-100-1923|deathyear=672}} on the Commons file
      page)
    tol_mm: 1.0
    area_mm2: 3381.8
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

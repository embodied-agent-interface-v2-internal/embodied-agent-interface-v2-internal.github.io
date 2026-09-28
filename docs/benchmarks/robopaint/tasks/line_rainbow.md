---
title: Line · Rainbow
task_id: line_rainbow
benchmark: robopaint

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: our RoboPaint task definitions
  synced: '2026-09-28'
  instruction: Paint the coloured line drawing shown in the picture /app/target.png onto the paper sheet in front of the robot, loading the brush with paint from the palette beside the paper.
  scene_model: robopaint_line
  scene_image: line_rainbow.png
  family: line
  picture: a rainbow between rain clouds, the sun and a hatched hill
  difficulty: easy
  line_complexity: hard
  tier: privileged
  colours: [black, red, blue, yellow, green]
  line_width: 2.5 mm
  line_length: 1802 mm
  line_length_by_colour:
    black: 240 mm
    red: 245 mm
    blue: 359 mm
    yellow: 289 mm
    green: 669 mm
  success_criteria:
    - 'precision >= 0.90: painted pixels within 1 mm of a line of their colour'
    - 'recall >= 0.95: the drawing''s line length with paint of its colour within 1 mm'
    - every colour's own recall >= 0.95
    - (reported) every element of the drawing counts as complete at recall >= 0.90
    - both fresh-process replays of the trajectory meet this and end in the same state
  continuous_score: F1
  scoring: 's.score() is served by a separate scoring container: it replays the actions the agent executed since its last reset on the graders'' copy and returns the metrics, never images or target data'
  agent_budget: 5400 s of wall clock per mode
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

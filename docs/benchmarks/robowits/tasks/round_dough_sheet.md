---
title: Round Dough Sheet
task_id: round_dough_sheet
benchmark: robowits

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/UMass-Embodied-AGI/RoboWits @ 9cc30ae
  synced: '2026-09-21'
  instruction: Flattern the dough ball and make a perfect round sheet
  scene_model: robowits_table
  registry_id: robowits/08-round-dough-sheet-v0
  task_number: 8
  source_file: gs_gym/envs/robowits/08_round_dough_sheet.py
  env_class: RoundDoughSheetEnv
  success_criteria:
    - At least 95% of particles are within table bounds
    - Dough height (z_95 - z_5) ≤ 0.035m (must be genuinely flattened, not just gravity-settled
      ~4.4cm)
    - At least 70% of particles within the target cylinder (radius ~0.053m, height 0.03m)
    - XY convex hull circularity ≥ 0.85 (4π·Area/Perimeter² == 1 for perfect circle)
  objects: [large flat board, round cutter]
  object_materials: [mpm, rigid]
  eval_scenes: 50
  mutations: 6
  blenderkit_assets: 2
  episode_steps_default: 200
  control_mode_default: EE_ABS
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/robowits.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- RoboWits ships no oracle demonstrations: the reference solutions are ours,
     written against the task's own success predicate. If this task has one,
     say whether the trajectory is clean and what it relies on. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

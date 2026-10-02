---
title: Meta-World · Handle press
task_id: handle_press
benchmark: metaworldplus

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/Farama-Foundation/Metaworld @ 59fc34d (Meta-World v3), as defined in our task definitions @ 8c5594a43
  synced: '2026-10-02'
  instruction: Press the handle downward.
  family: metaworld/handle-press
  robot: 'Rethink Sawyer: a 7-DoF arm whose hand is a mocap body (the wrist does not rotate), two-finger gripper'
  scene_model: metaworld_table
  category: Meta-World v3
  instance: Meta-World's reset randomization with seed 0; MuJoCo state, model arrays, env caches and RNG frozen in instance.npz (SHA-256 4f773337a385…, checked on load)
  success_criteria:
    - 'The verifier replays your actions from the frozen start in a separate sandbox (twice,
      in fresh processes; MuJoCo on the CPU is bit-exact) and applies Meta-World''s own
      success check for handle-press-v3 (evaluate_state) to the state after the last action.
      A success reached earlier and then lost does not count: end the trajectory while
      the task is achieved.'
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  deliverable: (T, 4) native actions [dx, dy, dz, grip], 1 ≤ T ≤ 500 (Meta-World's max_path_length)
  reference_solution: 'Meta-World''s scripted policy for handle-press-v3 (metaworld/policies/, removed from the image), run on this instance up to its first success: 41 actions in solution/oracle.npz (recorded by scripts/metaworldplus/freeze.sh). In this environment the success state does not persist on its own: after the oracle''s last action, holding still for 10 control steps loses it. Graded on the final state, a trajectory must end at that moment.'
  limited_mode: 'Standard-mode twin of metaworldplus-handle-press-i00-privileged: the same instance and success check (Press the handle downward.), served as a robot service (images/metaworld/standard/server_mw.py, protocol eai-standard/2.1, tool module mw_tool). The agent sees camera RGB-D, the robot''s own state and the target point; no object poses, no reset; one episode.'
  oracle: full
  base_image: ghcr.io/mll-lab-nu/eai-metaworld:0.1.0
  agent_budget: 3600 s of wall clock per mode
  task_dirs: metaworldplus-handle-press-i00-privileged, metaworldplus-handle-press-i00-standard
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/metaworldplus.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- The demo is the verifier's replay of our reference solution on this
     task's frozen instance (privileged mode). Say here if it looks wrong. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

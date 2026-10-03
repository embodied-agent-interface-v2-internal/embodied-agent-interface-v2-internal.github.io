---
title: Manipulation · insert_flower
task_id: insert_flower
benchmark: vlabench

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://github.com/OpenMOSS/VLABench @ cf588fe, as defined in our task definitions @ 8c5594a43
  synced: '2026-10-02'
  instruction: Insert the rose into the vase_seen.
  family: vlabench/insert_flower
  robot: Franka Panda (7-DoF arm, two-finger gripper)
  scene_model: vlabench_table
  category: Manipulation
  instance: seed 4
  success_criteria:
    - VLABench's own success check for insert_flower (the task's termination condition).
      The episode ends the moment it holds.
    - 'unlimited (privileged): both fresh-process replays of the handed-in trajectory
      end in the same state, and the check holds on it'
    - 'limited (standard): the one episode (no reset) is recorded by the service and replays
      to the same state; the check holds on it live and in the replay'
  reference_solution: '158 control steps on this instance (solution/oracle.npy), replayed by solution/solve.sh. Source: PR #4''s first-author reference: VLABench''s general skills driven by VLABench''s expert sequence or by a skill sequence the PR #4 author wrote, recorded as control steps during PR #4''s authoring; only the recorded steps were committed (PR #4 @ ad3c510, refs/pull/4/head). VLABench''s experts are removed from the image. Re-verified by scripts/vlabench/freeze.sh: the replay ends with the task''s success at its last step.'
  limited_mode: 'VLABench''s insert_flower as a robot service: a Franka Panda arm at a table, instructed "Insert the rose into the vase_seen." (a direct command), on the same frozen instance as vlabench-insert-flower-i00-privileged. The simulator runs in the sim sidecar (environment/sim/server.py on main''s rcb_service.py); the agent only has the client: four cameras (RGB 320×320, depth on request, calibrated), the robot''s own state, and joint-position chunks. One episode, no reset, no object poses; nothing to hand in.'
  oracle: full
  base_image: ghcr.io/mll-lab-nu/eai-vlabench:0.1.0
  agent_budget: 3600 s of wall clock per mode
  task_dirs: vlabench-insert-flower-i00-privileged, vlabench-insert-flower-i00-standard
---

## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/vlabench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- The demo is the verifier's replay of our reference solution on this
     task's frozen instance (privileged mode). Say here if it looks wrong. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->

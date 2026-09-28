---
title: Turning On Radio
task_id: turning_on_radio
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Turn on the radio receiver that's on the table in the living room.
  scene_model: house_double_floor_lower
  rooms: [living_room]
  demo_duration_s: 72
  oracle_video: https://player.vimeo.com/video/1109198872
  oracle_thumbnail: https://vumbnail.com/1109198872.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 5.7
  demo_eef_m: [3.26, 4.07]
  demo_episodes: 200
  demo_mean_s: 72
  demo_mean_steps: 2149.6
  goal_categories: [radio_receiver.n.01]
  goal_clauses: 1
  goal_predicates: [toggled_on]
  object_categories: 4
  objects: 4
  rooms_loaded: [corridor_0, garden_0, kitchen_0, living_room_0]
  scene_model: house_double_floor_lower
  test_instance_ids: [301, 320]
  test_instances: 20
---

## Why this task is interesting

The simplest task in the suite — 72 seconds, one room, one object, one state
change — which is exactly what makes it valuable. It is the natural smoke test
for the evaluation harness: if this does not run end to end, nothing will, and
the failure will be in the plumbing rather than in the policy. Keep it for that
reason even though it discriminates poorly between strong agents.

Note that the goal is a *state change* (`toggled_on`), not a pose. There is no
rearrangement to score, so partial credit is close to binary here.

## Capability notes

- `mob.room-scale-nav` — the radio is on a table in the living room; the base
  must be positioned before the arm can reach. Single room only, so not
  `mob.multi-room-nav`.
- `mp.toggle-press` — the actual goal: actuate the receiver's control.
- `per.small-object` — a power control on a radio is a few centimetres across,
  and must be located in the head camera at working distance. This is the part
  most likely to fail in practice.

Deliberately **not** tagged:

- `mp.pick-place` — nothing is transported. The radio stays where it is.
- `rea.long-horizon` — two steps.
- `per.occluded-search` — the instruction states the location outright.

## Oracle demo review

**Not yet watched by anyone on the team.** The tagging above was derived from
the published instruction text alone. Watching the demo is the remaining work
on this page — in particular, check whether the control is reachable without
torso actuation, which would add `mob.height-variation`.


## Discussion

- Suggested as the harness smoke test because it is the shortest demo in the
  suite and needs no manipulation of transported objects.

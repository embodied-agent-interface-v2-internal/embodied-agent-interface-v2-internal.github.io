---
title: Can Meat
task_id: can_meat
benchmark: behavior-1k

# --- upstream: mirrored from the benchmark's own published metadata by scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Open the kitchen cabinet, take out the two hinged jars, open them, place exactly two cooked bratwursts from the chopping board on the countertop into each jar, then close both jars, put them back inside the cabinet, and close the cabinet.
  scene_model: house_single_floor
  rooms: [kitchen]
  demo_duration_s: 395
  oracle_video: https://player.vimeo.com/video/1114054618
  oracle_thumbnail: https://vumbnail.com/1114054618.jpg

# --- verified: read first-hand from the stack we run, by scripts/import_<benchmark>_verified.py. Do not hand-edit. ---
verified:
  source: BDDL activity definitions + 2026-challenge-task-instances (licensed download)
  stack: BEHAVIOR-1K v3.9.2 / OmniGibson 3.9.2 / Isaac Sim 5.1
  checked: '2026-09-21'
  demo_distance_m: 31.66
  demo_eef_m: [26.06, 28.46]
  demo_episodes: 200
  demo_mean_s: 395
  demo_mean_steps: 11847.1
  goal_categories: [bratwurst.n.01, cabinet.n.01, hinged_jar.n.01]
  goal_clauses: 4
  goal_counts: [2]
  goal_predicates: [inside, open]
  goal_quantifiers: [forall, forn]
  object_categories: 7
  objects: 11
  rooms_loaded:
    - corridor_0
    - dining_room_0
    - entryway_0
    - garden_0
    - kitchen_0
    - living_room_0
    - living_room_1
  scene_model: house_single_floor
  test_instance_ids: [301, 320]
  test_instances: 20
---

## Why this task is interesting

One of the densest goals in the suite. The instruction stacks four distinct
kinds of constraint into a single 395-second episode:

1. **A strict order** — the cabinet must open before the jars come out, the
   jars before they are filled, and both must be closed and returned at the end.
2. **An exact count with a distribution** — "exactly two … into **each** jar"
   is not "four bratwursts among the jars". Three in one and one in the other
   fails, and an agent that cannot represent per-container counts will produce
   exactly that error.
3. **Low-clearance insertion** — a bratwurst into a jar mouth leaves little room.
4. **A terminal tidiness condition** — closing the cabinet is part of the goal,
   and is the step most likely to be dropped by an agent that stops once the
   salient objects are placed.

Because BDDL awards partial credit over a conjunction of predicates, this task
produces a genuinely informative score rather than a near-certain zero: an
agent can demonstrably get most of the way and be measured doing it. That is
the property that earns it a slot.

## Capability notes

- `mp.articulated` — three articulated interactions of two kinds: the cabinet
  door, and two hinged jar lids.
- `mp.pick-place` — jars out and back, bratwursts from board to jars.
- `mp.insert-fit` — the jar mouth is the tight clearance in this task.
- `rea.ordering` — open → extract → open → fill → close → replace → close. The
  order is not incidental; several predicates are unsatisfiable out of sequence.
- `rea.quantifier-grounding` — "exactly two … into each jar". A per-container
  count, which is strictly harder than a global count.
- `per.state-recognition` — *cooked* bratwursts specifically, so the agent must
  read a non-geometric object state, not just find sausage-shaped geometry.
- `per.container-interior` — must perceive inside the cabinet, and inside each
  jar to verify its contents.

Deliberately **not** tagged:

- `phy.thermal` — the bratwursts are already cooked when the episode starts.
  Nothing cooks during the episode, so no thermal transition is required. This
  one is worth flagging because "cooked" in the instruction invites the tag.
- `mob.multi-room-nav` — kitchen only.
- `mp.bimanual` — plausible but unverified. An agent may well need one hand to
  steady a jar while inserting; confirm against the demo before adding it.

## Oracle demo review

**Not yet watched by anyone on the team.** Tagging above is derived from the
published instruction text. When reviewing, the two open questions are whether
the demo uses both arms for the jar (see above) and whether the teleoperator
closes the cabinet, since that terminal predicate is easy to miss.


## Discussion

- The `phy.thermal` exclusion is the kind of call that should be contested if
  anyone disagrees — the instruction says "cooked", but no state transition
  occurs during the episode.

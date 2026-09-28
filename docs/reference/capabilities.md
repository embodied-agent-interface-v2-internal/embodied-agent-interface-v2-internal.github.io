---
title: Labels
---

# Task labels

The shared vocabulary for the `capabilities:` field on a task page.

!!! warning "Where these came from, and how settled they are"

    BEHAVIOR publishes a **31-primitive skill vocabulary**, annotated on all
    20,000 demonstrations. That list is theirs and is ground truth.

    The labels on this page are **ours**. The *Skills* group is a coarse
    roll-up of those official primitives — each label lists which ones it
    covers, so you can check the derivation. The *Task structure* group is
    our own addition for things no single primitive captures.

    Treat this as a **starting point to argue with**, not a settled
    standard. It is deliberately coarse: an earlier draft had 34
    fine-grained entries and was too detailed to apply consistently.

**14 labels in 2 groups.**

## Skills

Coarse roll-ups of BEHAVIOR's own 31 annotated action primitives. Descriptive: what the demonstration physically does.

### Pick and place { #cap-pick-place }

`pick-place`

Grasp an object and put it somewhere — the base transport skill.

*Rolls up BEHAVIOR skills:* `pick up from`, `place in`, `place on`, `place under`, `place in next to`, `place on next to`, `hold`, `release`, `hand over`

*Not yet tagged on any task.*

### Open and close { #cap-articulated }

`articulated`

Doors, drawers and lids, where the object constrains the motion.

*Rolls up BEHAVIOR skills:* `open door`, `open drawer`, `open lid`, `close door`, `close drawer`, `close lid`

*Not yet tagged on any task.*

### Operate a device { #cap-actuate }

`actuate`

Switches, buttons, knobs, igniters — small precise actuation.

*Rolls up BEHAVIOR skills:* `press`, `turn on switch`, `turn off switch`, `turn to`, `ignite`

*Not yet tagged on any task.*

### Navigate { #cap-navigate }

`navigate`

Move the base to reach somewhere, or push something across the floor.

*Rolls up BEHAVIOR skills:* `move to`, `push to`

*Not yet tagged on any task.*

### Insert, attach, hang { #cap-insert-attach }

`insert-attach`

Low-clearance or constrained placement — a jar mouth, a hook, a fitting.

*Rolls up BEHAVIOR skills:* `insert`, `attach`, `hang`

*Not yet tagged on any task.*

### Pour and tip { #cap-pour }

`pour`

Transfer contents by tilting, including fluids and granular material.

*Rolls up BEHAVIOR skills:* `pour`, `tip over`

*Not yet tagged on any task.*

### Clean a surface { #cap-clean }

`clean`

Wiping, sweeping and spraying — sustained contact to change a surface state.

*Rolls up BEHAVIOR skills:* `wipe hard`, `sweep surface`, `spray`

*Not yet tagged on any task.*

### Cut { #cap-cut }

`cut`

Tool-mediated, irreversible division of an object.

*Rolls up BEHAVIOR skills:* `chop`

*Not yet tagged on any task.*

## Task structure

Properties of the task as a whole. Normative: what an agent must handle to succeed, which no single action primitive captures.

### Long horizon { #cap-long-horizon }

`long-horizon`

Many dependent subgoals in a required order; errors compound.

*Not yet tagged on any task.*

### Multi-room { #cap-multi-room }

`multi-room`

The goal spans more than one room, so the agent must traverse the house.

*Not yet tagged on any task.*

### Counting and quantifiers { #cap-counting }

`counting`

The goal says "exactly two", "all three", "the same cabinet" or "any shelf". Miscounting or failing to commit consistently fails outright.

*Not yet tagged on any task.*

### Object state change { #cap-object-state }

`object-state`

Success depends on a semantic state — cooked, frozen, soaked, sliced, toggled on — not just where things are.

*Not yet tagged on any task.*

### Bimanual { #cap-bimanual }

`bimanual`

Both arms must cooperate on the same object or motion.

*Not yet tagged on any task.*

### Search { #cap-search }

`search`

The target is not visible from the start pose and must be found.

*Not yet tagged on any task.*

---
title: Benchmark landscape
---

# What the field is actually benchmarking

A label vocabulary written against one benchmark describes that benchmark. This
page is the survey the [label taxonomy](capabilities.md) was written against:
fourteen suites the lab has integrated, is integrating, or has on its list,
read for **what each one is actually trying to measure** rather than for how
many tasks it ships.

The short version: these fourteen do not disagree about labels, they disagree
about *what a task is*. A LIBERO task is a language-conditioned trajectory on a
fixed tabletop. A HumanoidBench task is a reward function over a 61-dimensional
action space with no language at all. A RoboCasa365 task is a fifteen-step
kitchen activity for a mobile base. Any vocabulary that spans them has to say
something true about all three, which is why the taxonomy is organised as
independent facets rather than one list of skills.

## The fourteen

| Benchmark | Simulator | Embodiment | Scale | What it is really testing |
| --- | --- | --- | --- | --- |
| [BEHAVIOR-1K](https://behavior.stanford.edu/) | OmniGibson / Isaac Sim | R1 Pro, mobile bimanual | 100 challenge tasks, 50 scenes | Long-horizon household activity with real state change (cook, cut, clean) |
| [RoboCasa](https://robocasa.ai/) | MuJoCo | Panda + Omron mobile base | 100 tasks (25 atomic, 75 composite), 120 kitchens | Skills composed into kitchen activities, at scene scale |
| [RoboCasa365](https://arxiv.org/abs/2603.04356) | MuJoCo | mobile manipulators, humanoids, quadrupeds with arms | 365 tasks (65 atomic, 300 composite), 2,500 kitchens | The same, pushed to foundation-model scale and lifelong-learning splits |
| [RoboCasa-GR1](https://github.com/robocasa/robocasa-gr1-tabletop-tasks) | MuJoCo | Fourier GR1 humanoid | 24 tabletop tasks (18 pick-place, 6 articulated) | Whether humanoid upper-body policies transfer; GR00T N1's eval suite |
| [LIBERO](https://libero-project.github.io/) | MuJoCo | Franka Panda | 130 tasks, 4 suites × 10 + 90 | **Which kind of shift** breaks a policy: spatial, object, goal, or long |
| [LIBERO-PRO](https://arxiv.org/abs/2510.03827) | MuJoCo | Franka Panda | LIBERO, perturbed | That 90%+ on LIBERO can be memorisation — it collapses to 0.0% under perturbation |
| [Meta-World+](https://arxiv.org/abs/2505.11289) | MuJoCo | Sawyer | 50 tasks, MT10/MT25/MT50, ML10/ML45 | Multi-task and meta-RL transfer, with versioning finally pinned down |
| [VLABench](https://arxiv.org/abs/2412.18194) | MuJoCo | Franka, plus dual-arm, humanoid, quadruped | 100 categories (60 primitive, 40 composite), 2,000+ objects | Knowledge, not motion: common sense, implicit intent, physical law |
| [RoboTwin 2.0](https://arxiv.org/abs/2506.18088) | SAPIEN + CuRobo | Aloha-AgileX, ARX-X5, Piper, Franka, UR5 | 50 dual-arm tasks × 5 embodiments | Bimanual coordination **under domain randomisation**, across bodies |
| [RoboWits](https://arxiv.org/abs/2605.30326) | Genesis | Marvin, bimanual | 30 seed + 208 mutated | Creative problem solving: the obvious motion is designed to fail |
| [RoboLab](https://research.nvidia.com/labs/srl/projects/robolab/) | Isaac Lab / Isaac Sim | Franka + Robotiq | 120 tasks | Language grounding on a tabletop: colour, size, count, spatial, vague |
| [HumanoidBench](https://humanoid-bench.github.io/) | MuJoCo | Unitree H1 + two 21-DoF Shadow hands | 27 tasks (12 locomotion, 15 whole-body manipulation) | Whole-body control at 101 DoF; no language, reward only |
| [MuJoCo Playground](https://playground.mujoco.org/) | MJX | Go1, Spot, Barkour, G1, H1, T1, Apollo, Op3, Berkeley Humanoid; Panda, Aloha, Leap | ~19 locomotion + 10 manipulation envs | GPU-scale RL and sim-to-real: gaits, getting up, in-hand reorientation |
| [DexToolBench](https://arxiv.org/html/2602.16863v1) | Isaac Gym (+ real) | dexterous hand | 24 tool-use tasks, 6 tool categories | Tool use as a *hand* problem: grasp it, then rotate it in-hand to work |

One note on the table: **DexToolBench** appears in the literature as a
real-world benchmark with digital twins rather than a pure simulator, so "Isaac
Gym" describes its evaluation path, not its home.

## Six things they are collectively doing

**1. Composition, at two different scales.** RoboCasa, RoboCasa365, VLABench and
BEHAVIOR all build long tasks out of short ones, and all four publish the short
list: RoboCasa365's ten foundational skills (pick and place, open/close doors,
open/close drawers, twist knobs, turn levers, press buttons, insertion,
navigation, sliding racks, open/close lids) and VLABench's ten (pick & place,
open/close door, open/close drawer, hang, tool use, press button, insert, pour,
twist, explore) are nearly the same list, and both overlap BEHAVIOR's 31
primitives. **This is the closest thing the field has to a consensus vocabulary,
and it is a vocabulary of contact types.** It says nothing about bodies, language
or robustness.

**2. Robustness as a first-class axis.** LIBERO-PRO, RoboTwin 2.0, THE COLOSSEUM
and VLABench's tracks are all variations on one experiment: hold the task fixed,
vary something else, watch the policy fall over. The numbers are severe —
LIBERO-PRO reports 90%+ collapsing to 0.0%; THE COLOSSEUM measures 30–50% drops
from a single factor and >75% from several, with distractor count, target colour
and lighting the worst offenders. **A task that never varies its initial state is
not testing much**, and that is a property of the task we had no way to record.

**3. Language as the object of study, not the interface.** LIBERO varies the
goal wording deliberately; RoboLab ships three wordings per task; VLABench uses
non-template instructions carrying implicit intent; RoboTwin randomises language
as one of its five axes. Meanwhile HumanoidBench and Playground have no language
at all. Any "instruction following" label has to be about *what the wording
demands*, not about whether there is an instruction.

**4. Bodies other than an arm on a table.** HumanoidBench's 12 locomotion tasks,
Playground's joystick suites across eight robots, RoboCasa365's humanoids and
quadrupeds, and DexToolBench's in-hand rotations are all outside the reach of a
manipulation-shaped vocabulary. HumanoidBench in particular splits its own tasks
into locomotion, static manipulation and dynamic manipulation — a distinction
(does the object leave contact? does timing decide?) no manipulation benchmark
makes.

**5. Knowledge that is not in the scene.** VLABench is the clearest case: tasks
that need the rules of poker, which fruit has vitamin C, or what a latte is.
BEHAVIOR's BDDL goals are formal and self-contained by comparison. This is a
capability axis, not a perception axis, and only one of the fourteen tests it.

**6. Cross-embodiment as an experiment.** RoboTwin 2.0 runs the same 50 tasks on
five robots; Playground runs joystick tracking on eight; VLABench claims arms,
dual arms, humanoids and quadrupeds. The interesting property is not *which*
robot but whether the task is posed on more than one.

## What each benchmark exercises

Facets from the [taxonomy](capabilities.md). ● = central to the suite, ○ = present.

| | Embodiment | Interaction | Object state | Goal & language | Perception | Scene | Variation |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| BEHAVIOR-1K | ○ | ● | ● | ● | ● | ● | ○ |
| RoboCasa / 365 | ● | ● | ● | ● | ○ | ● | ● |
| RoboCasa-GR1 | ○ | ● | | ○ | | | ○ |
| LIBERO | | ○ | | ● | ○ | | ● |
| LIBERO-PRO | | ○ | | ○ | ○ | | ● |
| Meta-World+ | | ● | ○ | | | | ○ |
| VLABench | ○ | ● | ○ | ● | ● | ○ | ● |
| RoboTwin 2.0 | ● | ● | ○ | ○ | ○ | | ● |
| RoboWits | ○ | ● | | ● | ○ | | ○ |
| RoboLab | | ○ | | ● | ○ | | |
| HumanoidBench | ● | ● | | | | ○ | |
| MuJoCo Playground | ● | ○ | | | | ○ | ○ |
| DexToolBench | ● | ● | ○ | | | | ○ |

Read down a column: **Interaction** is the only facet every suite touches, which
is why a contact-type vocabulary looks universal until you try to use it.
**Embodiment** and **Variation** are each central to five suites and absent from
five others — they are not niche, they are simply invisible to any single
benchmark. **Object state** is nearly the private property of the household
suites. **Goal & language** and **Perception** are where the tabletop language
suites live, and where the legged suites have nothing to say.

## What this made the taxonomy look like

The [vocabulary](capabilities.md) was fitted to this survey and to a per-task
digest of the 250 tasks we hold (`scripts/task_skill_digest.py`), under one rule:
**a label earns its place only if knowing it changes what you predict about the
task.** Three consequences are worth stating, because they are what keeps the
list from being a pile of small capabilities.

**Three facets are ladders, not flag collections.** Scale (tabletop → room →
building → outdoor), horizon (atomic → composite → activity) and generalisation
(nothing varies → layout → appearance → objects → scenes → robots) are ordinal.
A task takes the highest rung, so "activity-scale task with appearance
randomisation" is two labels carrying what would otherwise be eight flags. The
generalisation ladder is the direct product of this survey: LIBERO-PRO, THE
COLOSSEUM, RoboTwin 2.0 and VLABench's tracks are all measuring rungs on it, and
the first rung — *nothing varies* — is a real finding about a suite, not an
absence of information. RoboLab sits there.

**Redundant labels were removed even though each sounded reasonable.**
`multi-room` implied `navigate`; `judge a state` implied whichever state label
was already present; `tell instances apart` implied `attribute reference`. Each
was dropped rather than counted twice. What replaced the last one is
`active-perception` — *you must act to find out* — which is not implied by
anything and which almost nothing in the field tests: RoboWits'
`differentiate_cubes`, where wood and metal look identical and the robot has to
float them, is the clearest instance in 1,150 tasks.

**Labels no suite in this table can reach were cut.** Two axes that sounded
important — another agent in the scene, a world that changes on its own — are
named here and left out of the vocabulary, because a label nothing can carry is
decoration. The thirteen labels currently unreachable by *our three integrated
suites* were kept, because HumanoidBench, Playground, DexToolBench, RoboTwin,
VLABench or RoboCasa each reach them: adding one of those suites must not mean
rewriting the vocabulary.

Two further notes on what was deliberately not done. **Nothing in the taxonomy is
a skill primitive.** The consensus ten-skill list is a good description of
contact and a poor description of difficulty; the Contact facet covers it without
mirroring it. And **no label names a robot** — `bimanual` means the task cannot
be done one-handed, `in-hand` means a parallel jaw could not do it. Which robot a
benchmark runs is a fact about the benchmark, recorded in
`data/benchmarks/<id>.yml`.

## Sources

Every claim above is from the linked paper, project page or repository, read on
2026-09-22. Numbers that a source did not state are omitted rather than guessed.

---
title: About RoboTwin 2.0
---

# About RoboTwin 2.0

Fifty **bimanual tabletop** tasks on a dual-arm **ALOHA-AgileX** in **SAPIEN 3** (PhysX physics,
Vulkan rendering) with **CuRobo** motion planning, from the RoboTwin 2.0 paper (ICML 2026). The
benchmark's purpose upstream is data: every task ships a scripted expert (`play_once`), and RoboTwin's
100k-episode dataset is that expert run on sequential seeds, kept only where it succeeded. Success is
the task's own `check_success()`, all-or-nothing.

[All 50 tasks](index.md){ .md-button .md-button--primary }
[Capability coverage](coverage.md){ .md-button }

## Why we are looking at it

1. **It is bimanual by construction.** Handover, simultaneous two-arm motion and arm selection are
   the norm, not the exception: 20 of the 50 tasks need both arms, 2 are explicit handovers.
2. **The whole suite is one code path.** A task is `load_actors` + `check_success` + `play_once` in
   one file, on one table, with one embodiment config. Integrating a task into our harness is a
   seed and a task name; five are integrated and validated, one of them in both evaluation modes.
3. **The expert is honest about difficulty.** Because upstream publishes the expert's success rate per
   task and embodiment (the *data-generation success rate*), and because we can run the same expert on
   our own seeds, every row carries a measured fragility rather than a guess.

What it is *not*: a perception or navigation benchmark. Fixed base, one table, clean scene by default;
ground-truth object poses, contact points and functional points are available to the expert and to a
privileged agent. And with RoboTwin's grasp/place primitives exposed, the easy half of the suite is
trivial for a frontier coding agent (see the model runs below).

## The unit of a row

A row is one of the **50 task classes** in `envs/`. Domain randomisation (cluttered table, textures,
lighting, table height) is a configuration switch, not a task, and is off in everything we show. Each
page carries:

| Block on the page | What it is | Read from |
| --- | --- | --- |
| `instruction`, `objects`, `average_steps`, `data_gen_success`, `embodiments` | What RoboTwin publishes about the task | its documentation page, one per task |
| `success_check`, `asset_models`, `expert_planned_motions`, `expert_methods` | The task's own predicate, verbatim, and the shape of its expert | `envs/<task>.py`, read with `ast` at the pinned commit |
| `eval_step_limit` | RoboTwin's policy-evaluation budget for the task | `env_cfg/task_config/_eval_step_limit.yml` |
| `oracle_video`, `oracle_video_world` | The official ALOHA head- and world-camera clips | the documentation site (static MP4s) |
| `verified:` | What our own run of the expert saw: seed, attempts, physics steps, pass rate over seeds | our render sweep in the `rcb-robotwin` image |

## The embodiment

| | |
| --- | --- |
| Robot | ALOHA-AgileX: two 6-DoF arms with parallel grippers, fixed base at y = −0.65 m facing the table; four other embodiments supported upstream (Piper, Franka Panda, ARX-X5, UR5-WSG) |
| Native actions | `qpos` (14-D joint targets + grippers, time-optimal interpolation) or `ee` (16-D end-effector pose + grippers, CuRobo plans against the table only) — RoboTwin's `take_action(action, action_type)` |
| Our trajectory | the per-physics-step drive targets of the 16 driven joints, 34 floats per row at 250 Hz, captured by hooking `scene.step()` |
| Cameras | head (static, above the table), front (static, facing the robot), left and right wrist; plus an observer and a diagonal world camera RoboTwin adds to every scene |
| Privileged state | object poses, contact-point grasps and functional points from the simulator; the expert uses all three |
| Episode budget | 400–1700 policy actions depending on the task (`_eval_step_limit.yml`) |
| Scenes | one tabletop |

## How a task defines success

`check_success()` in the task file, quoted verbatim on every page. Across the suite it is a mix of
pose tolerances on functional points (stacking, placing), joint-angle thresholds on articulated
objects (microwave door ≥ 60 % of range, laptop lid, switch), contact checks between named actors
(hammer on block, can inside basket and not on the table), gripper-open conditions, and a few
geometric ones (the scanner's axis pointing at the box). No partial credit, except `put_bottles_dustbin`
which also defines a `stage_reward` upstream.

## The success numbers, and how to read them

- **Data-generation success (official).** RoboTwin's collection script walks seeds 0, 1, 2, … and runs
  the scripted expert; a seed succeeds only if the scene settles, every plan succeeds, the planned
  joints stay legal and `check_success()` holds. The published rate is successes / seeds tried until 50
  demos were collected, per embodiment. It is the success rate of *their scripted expert on random
  layouts*, not of a policy — and the best single indicator of how fragile a task's grasps are.
- **Our expert run (`verified:`).** The same expert executed through our recorder in the `rcb-robotwin`
  image on uncommon seeds (60417, 28831, 91573, …), up to three to six attempts, because CuRobo planning
  is not deterministic across runs. The clip on the row is the successful attempt.
- **Expert pass rate.** For 13 candidates we ran one attempt on each of six uncommon seeds and required
  completion **and** a bit-exact replay.

Two tasks never pass: `pick_diverse_bottles` (the scene does not settle; `UnStableError` on every seed)
and `put_object_cabinet` (every plan fails). `click_alarmclock` passes live but fails our replay check.
All three are marked `drop` with the reason.

## What we run it on

Pinned to **`RoboTwin-Platform/RoboTwin @ 6dde571`** (main, 2026-09-14) and the Hugging Face asset
revision `981c92a`. Measured in `robot_coding_bench`:

| | |
| --- | --- |
| Image | `nvidia/cuda` 12.4 devel + SAPIEN 3.0.0b1 + mplib + CuRobo 0.7.8 + embodiments and objects, 21.6 GB — `rcb-robotwin:0.1.1` |
| GPU | required at runtime (CuRobo on CUDA, SAPIEN on Vulkan); the task's compose file reserves one |
| Determinism | PhysX on the CPU replays a recorded trajectory bit-exactly across processes (verifier: two fresh replays, hashes must agree). Planning is **not** deterministic: the same seed can fail on one run and pass on the next, so the oracle runner retries |
| Instance | `(task, seed)` rebuilt from the seed on every reset, with an initial-state hash check; ~19 s for the first build, 0.1 s after |
| Oracle scrub | every expert method is removed from the agent image (57 methods in 50 files, plus `code_gen/`); only `load_actors` and `check_success` remain readable |
| Integrated | 5 tasks in unlimited mode (agent has resets, privileged state and the primitives) and `stack_blocks_two` additionally in **limited mode** — the simulator runs in a sidecar the agent cannot open, the agent gets a client with `observe()` / `step()` only (RGB + proprioception, no reset), and the verifier grades the sidecar's own record |

### Model runs so far

Codex with GPT-6 Astra (ChatGPT subscription), one attempt, 3600 s budget, on `stack_blocks_two`
(seed 60417, red block right, green block left):

| Mode | Result | Agent time | Actions | Tokens in / out |
| --- | --- | --- | --- | --- |
| unlimited (resets, object poses, primitives) | **1** | 145 s | 20 tool steps | 359 k / 2 k |
| limited (RGB + proprioception, no reset, `ee` actions via the service) | **1** | 261 s | 17 actions, 3 820 physics steps | 724 k / 5 k |

Both runs converged on the same strategy: the left arm cannot reach the red block, so the right arm
moves it to the centre first and the left arm stacks the green block. In limited mode the agent
recovered block positions from the head camera using the calibration RoboTwin includes in every
observation. Losing resets, privileged state and the primitives roughly doubled time and tokens but did
not stop the model — which is why the four *core* rows below are the ones that matter.

## What this means for our suite — a proposal

**5 kept, 3 dropped, 42 pending.** The keeps are the tasks integrated and validated in the bench; the
four hard ones were chosen one per type, where RoboTwin's own expert still passes on some seed:

| Type | Task | Why it earns the slot | Difficulty |
| --- | --- | --- | --- |
| Handover / long horizon | `put_bottles_dustbin` — *core* | three bottles, right-side ones need an in-air handover to the left arm, then a drop into a bin only the left arm reaches; 8.8 k physics steps | hard |
| Articulated | `open_microwave` — *core* | the expert re-grasps along the door in a loop and still fails half the seeds; joint-angle predicate | hard |
| Multi-object + contact | `place_can_basket` — *core* | can into basket, then lift the basket with the other arm; contact-based predicate | hard |
| Bimanual tool use | `scan_object` — *core* | simultaneous grasps, then aim the scanner at the held box; orientation predicate, both grippers stay closed | hard |
| Calibration | `stack_blocks_two` | solved by GPT-6 in minutes in both modes; keeps the unlimited-vs-limited comparison honest | easy |

Candidates for a second round, from the sweep: `hanging_mug` (regrasp + hang, 5/6), `handover_block`
(6/6), `place_bread_basket` (bimanual when two breads, 6/6), `dump_bin_bigbin` (the only pour). The 42
pending rows are labelled and rated from their code and our runs, not triaged.

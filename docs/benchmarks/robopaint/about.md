---
title: About RoboPaint
---

# About RoboPaint

A benchmark we built for coding agents: a **Franka Panda holding a brush** paints the picture
it is given onto a sheet of paper. **ManiSkill 3.0.1** (SAPIEN 3.0.3, PhysX on the CPU)
simulates the robot; **Spline-FRIDA's learned stroke model** (CMU's FRIDA robot painter) turns
the path the brush tip actually took into paint. Every task runs in both modes.

[All tasks](index.md){ .md-button .md-button--primary }
[Runs](../../runs/robopaint.md){ .md-button }

## What the agent gets

- **A picture, never a vector.** The target is an RGB image, `target.png`, at the paper's true
  size and place. The drawing's geometry stays with the graders.
- **Thin primitives**: straight-line tip moves on per-step IK, joint moves, hold. Everything
  between the picture and a trajectory is the agent's.
- **The palette rule.** The brush starts dry and leaves no mark until it is dipped. Dipping into
  one of the five wells (black, red, blue, yellow, green) loads that paint and replaces the old
  one: no mixing, no cleaning, no running out. A stroke keeps the paint it had when it touched
  the paper, strokes cannot be undone, and pressure sets the line width (about 2.2 mm at a light
  touch, 7.5 mm pressed hard).

## Scoring

The final canvas is scored against the picture, in both fresh-process replays; each task page
lists its thresholds. Every brush family first aligns the sheet with the picture (the best
single shift, at most 5 mm along each axis), so a well-formed work placed a little off still
counts; oil scores only the central area, 8 mm in from the sheet's edges.
**Calligraphy and lettering**: IoU, boundary F within 1 mm, how much of each stroke is covered,
stray ink and a stroke limit; the IoU is the continuous score (`final_reward`). **Acrylic and
oil**, at a 1 mm scale: CIELAB ΔE (mean and p90), SSIM of L\*, edge correlation, paint IoU and a
stroke limit; 1 − mean ΔE / 20 is the continuous score. **Line drawings** (excluded): precision
and recall within 1 mm, colour by colour; F1 is the continuous score. The graders' other numbers
show on the [Runs page](../../runs/robopaint.md).

In the unlimited mode `s.score()` gives this feedback without giving the target away. A
**scoring sidecar**, a separate container with the graders' copy of the instance, replays the
agent's actions since its last reset and returns only the metrics. The agent's container holds
nothing derived from the target but the picture. The limited mode has no score: cameras and
proprioception only, and no reset.

## Families and tiers

| Family | What is painted | Tier |
| --- | --- | --- |
| Lettering | lettered words | medium to hard |
| Kaishu | regular-script brush calligraphy | hard; multi-character works extreme |
| Xingshu | running-script brush calligraphy (16 targets) | hard; four-character works extreme |
| Acrylic | painted areas, acrylic | hard |
| Oil | painted areas, oil | extreme |
| Line | coloured line drawings (9 targets): **excluded from the final benchmark**, too easy; kept on the site with their runs | easy |

A new family's pages come from our task definitions (`scripts/import_robopaint_tasks.py`), each
task with its difficulty as defined there.

## What we run it on

| | |
| --- | --- |
| Image | our RoboPaint image, 2.5 GB (ManiSkill + FRIDA); torch on the CPU |
| Physics | PhysX on the CPU; the GPU (Vulkan) only renders the cameras |
| Determinism | Bit-exact: the live run equals two fresh-process replays |

!!! note "FRIDA is GPL-3.0"

    FRIDA's code and brush weights are shipped unmodified inside the locally built image.
    That is fine for our runs; publishing the image would need FRIDA's licence notice alongside it.

## Upstream links

- [ManiSkill](https://github.com/haosulab/ManiSkill): the robot simulator (its `DrawSVG-v1` task is where the scene comes from)
- [FRIDA / Spline-FRIDA](https://github.com/cmubig/Frida/tree/spline-frida-z-master-resolved): the stroke model, pinned at commit 1652973
- [Spline-FRIDA paper](https://arxiv.org/abs/2412.00597)

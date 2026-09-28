---
title: Adding a benchmark
---

# Adding a benchmark

The registry is data. Nothing in the site's structure is specific to any one
suite — adding a benchmark means adding files, not changing code. RoboWits and
RoboLab were added this way; the only code that changed was to stop assuming
there was one benchmark (media folders, the skill-vocabulary check).

## 1. Register the benchmark

`data/benchmarks/<benchmark-id>.yml`. Copy `behavior-1k.yml` and adapt. The
fields the tooling actually reads:

| Field | Used for |
| --- | --- |
| `id`, `name` | page titles, cross-links |
| `simulator` | shown in the benchmark table |
| `status` | the benchmark table on the home page |
| `skill_vocabulary` | validating `skills:` on task pages |
| `scenes` | warning when a task names an unlisted scene |

Everything else is documentation for humans and is free-form.

## 2. Get the tasks in

`docs/benchmarks/<benchmark-id>/tasks/<task_id>.md`, one file each, with the
frontmatter from the [task page guide](task-page-guide.md).

For more than a handful, write an importer rather than hand-writing files.
Copy the closest of the three — `import_behavior_tasks.py` (a published gallery),
`import_robowits_tasks.py` or `import_robolab_tasks.py` (the benchmark's own
source tree, read with `ast`). The structure they share is worth keeping:

- fetch from a **machine-readable upstream source**, not scraped prose;
- write only into the `upstream:` block on pages that already exist;
- scaffold new pages from a template;
- **never delete**; report disappearances and let a human decide;
- be idempotent — re-running with no upstream change writes nothing;
- cache what you fetched under `data/benchmarks/<id>.tasks.upstream.json`, so
  rebuilding the pages never needs the upstream, a checkout or a network.

That last pair is what makes it safe to run in CI or on a schedule.

### Pin the version

Record the exact commit or tag you read, in every `upstream.source`. A task page
that does not say which version it describes is not reviewable: RoboLab v0.3.1
moved the canonical ground plane, so a demo recorded against v0.2.x no longer
reproduces. Pin the version the simulator image builds from, not `main`.

### Finding the videos

The site is built around watching demos, so look for them before concluding
there are none. Neither RoboWits nor RoboLab publishes a gallery, but both have a
project page serving static MP4s, one per task. Both importers read that page and
record the URL in `upstream.oracle_video`, which is all `make demos` needs.

**Check the mapping, do not trust it.** RoboWits names its clips by task number,
so the importer also reads the caption next to each clip and compares it to the
task title. RoboLab names its clips after the instruction, so the importer matches
on instruction text — and requires every content word of the file name to appear
in that task's own wordings, because pure string similarity attached "Take all
the bananas out of the grey bin" to the *keyboard* task at 0.83. Attaching the
wrong video to a task is worse than leaving it without one.

### If a task has no video

Say so rather than showing a grey box. RoboLab ships a preview image per scene;
the importer copies them to `docs/assets/<id>/scenes/` and records
`upstream.scene_image`, and the row falls back to that still, labelled "no oracle
video upstream". A still is not a demonstration, and the page never implies it is.

## 2b. Where the media goes

`docs/assets/<benchmark-id>/demos/<task_id>.mp4`, its `.jpg` poster beside it,
and a `manifest.json` per benchmark written by `scripts/fetch_demos.py`
(`--benchmark <id>`). Nothing is shared between benchmarks, so two suites may use
the same task id and a new one only adds a folder. Scene stills, if you have
them, go in `docs/assets/<benchmark-id>/scenes/`.

If a clip is **ours** rather than upstream's — a reference solution we recorded —
add `"source": "..."` to its manifest entry. It renders as a credit under the
player, so nobody mistakes it for the benchmark's own demo.

## 2c. Optional: a `verified:` block

If we run the benchmark ourselves, the facts we read from the copy we run belong
in a second machine-owned zone, `verified:`, written by
`scripts/import_<id>_verified.py` and kept apart from `upstream:` so an upstream
re-sync cannot drop it. `import_behavior_verified.py` is the worked example: it
reads the BDDL goal the evaluator scores and the dataset's own per-task
statistics from the licensed download, caches them, and writes the block.

Render is automatic — `scripts/hooks.py` has a field table for the keys it knows
and falls back to a humanised key for the rest.

## 3. Write the two hand-written pages

- `docs/benchmarks/<id>/index.md` — the landing page. Keep it to a sentence or
  two, then drop in the two placeholders; the task list is what people came for:

    ```markdown
    <!-- gen:benchmark-stats benchmark=my-benchmark -->
    <!-- gen:tasks benchmark=my-benchmark -->
    ```

- `docs/benchmarks/<id>/about.md` — scope, embodiment, evaluation protocol and
  upstream links. Anything long-form goes here, not on the landing page.

## 4. Wire up the nav

In `mkdocs.yml`, under `Benchmarks`, mirroring the BEHAVIOR-1K block:

```yaml
- My Benchmark:
    - Tasks: benchmarks/my-benchmark/index.md
    - Capability coverage: benchmarks/my-benchmark/coverage.md
    - About the benchmark: benchmarks/my-benchmark/about.md
```

`coverage.md` does not exist on disk — `scripts/gen_pages.py`
creates them for every benchmark in the registry. You only list them.

The benchmark's page under **Runs** needs no line at all: `scripts/hooks.py`
appends one per registered benchmark after the Runs overview, in the order of
this Benchmarks section.

## 5. Check

```bash
make check
```

The home page table, the capability reference's usage lists, all three
generated pages and the Runs section pick up the new benchmark with no further
work.

## 6. Optional: register your agent runs

If you run coding agents on the benchmark, it takes part in runs through a file
of its own, `state/runs/<benchmark-id>.yml`. The file names the Harbor batches
and the task scope of each run. Your machines go in a local, gitignored
`data/runs/hosts.<you>.local.yml`. `make runs` then collects the trials into
`data/runs/<benchmark-id>/`. It never touches another benchmark's files.
[Registering runs](registering-runs.md) has the formats and a complete example.

## On the capability taxonomy

Resist forking it per benchmark. A shared vocabulary across benchmarks is what
makes statements like "we have three tasks requiring bimanual coordination
outside the kitchen" possible at all. If your benchmark needs a capability that
does not exist, add it to `state/taxonomy.yml` for everyone — with the task
evidence that motivated it, in the description. RoboWits and RoboLab added five
that way (`tool-use`, `stack-balance`, `deformable`, `spatial-reference`,
`attribute-reference`), each naming the tasks that forced it.

`skill_vocabulary` in the registry is the other half: it is the benchmark's *own*
annotation vocabulary, and the only thing `skills:` on a task page is validated
against. BEHAVIOR publishes 31 skill primitives; RoboLab tags every task from an
11-term attribute list; RoboWits publishes neither, so its registry declares an
empty list and `skills:` there is unchecked.

# Benchmark Task Reference

Documentation site for the robotic benchmarks we are curating. For every task:
what it asks for, its **oracle demonstration playing inline**, the capabilities
it requires, and whether we are keeping it.

**Public site:** <https://embodied-agent-interface-v2-internal.github.io/>. It is
published from `main` by GitHub Actions; see [HANDOFF.md](HANDOFF.md#publishing).

Seven benchmarks, 557 tasks, each synced from its own upstream:

| Benchmark | Simulator | Tasks | Demos | Synced from |
| --- | --- | --- | --- | --- |
| **BEHAVIOR-1K** (2026 Challenge) | OmniGibson / Isaac Sim 5.1 | 100 | 98 | the official demo gallery, plus the licensed dataset we run |
| **RoboWits** | Genesis 0.4.7 | 30 | 23 | the task source at the pinned commit, plus the project page |
| **RoboLab** v0.3.1 | Isaac Lab 2.3 / Isaac Sim 5.1 | 120 | 13 + 107 scene stills | the task source at the pinned tag, plus the project page |
| **RoboTwin 2.0** | SAPIEN 3 / PhysX + CuRobo | 50 | 48 expert clips we recorded (six-camera grid) + 50 scene stills; official ALOHA clips linked | the task source at the pinned commit, plus the documentation site |
| **RoboPaint** (ours) | ManiSkill 3.0.1 + brush models (Spline-FRIDA, a virtual Chinese brush, MyPaint) | 91 (82 + 9 excluded) | 91 replays of our reference solution | our benchmark repository, at a pinned commit |
| **VLABench** | MuJoCo 3.2.2 / dm_control 1.0.22 | 96 | 39 replays of our validated reference solutions + 44 first-frame stills; none for the 13 tasks that cannot be built | our frozen instances (robot_coding_bench) of the task source at the pinned commit |
| **MetaWorld+** | MuJoCo 3.3.0 (Meta-World 3.1.1) | 70 (50 environments) | 70 replays of the upstream scripted policy's controls, rendered by us | our frozen instances (robot_coding_bench) of the task source at the pinned commit |

Each is pinned to the exact version our images build from, so what you review
here is what we run.

## Getting the repository

```bash
git clone git@github.com:embodied-agent-interface-v2-internal/embodied-agent-interface-v2-internal.github.io.git
cd embodied-agent-interface-v2-internal.github.io

make install     # creates .venv, installs the pinned toolchain
make edit        # start the site WITH editing enabled
```

Open the URL it prints. That is the whole setup — no simulator, no GPU and no
extra tooling. The 134 oracle demo videos (~1.2 GB) are committed, so they are
already there after a clone and the task list works immediately.

> **`make edit`, not `make serve`, if you intend to change anything.**
> Both serve the same site. Only `make edit` also starts the local daemon
> (`scripts/editd.py`, port 8009) that can write to `state/` — a browser page
> cannot write files by itself. Under `make serve` the Edit buttons are
> visible but tell you to run `make edit` instead of silently failing. A
> deployed copy is always read-only.

<details>
<summary>Just want to read the docs, without the 1.1 GB of video?</summary>

```bash
git clone --filter=blob:none git@github.com:embodied-agent-interface-v2-internal/embodied-agent-interface-v2-internal.github.io.git
```

A partial clone fetches file contents lazily. The task list will show
"demo not downloaded" placeholders until the blobs arrive, so prefer a normal
clone if you intend to review tasks at all.
</details>

## Working with the demo videos

They are committed, so a normal clone already has them. You only need these
commands to change what is stored.

| Situation | Command |
| --- | --- |
| Re-download from upstream (repair, or a new task) | `make demos` — all three benchmarks |
| One benchmark only | `.venv/bin/python scripts/fetch_demos.py --benchmark robowits` |
| Get sharper copies (720p, ~3–4× the size) | `.venv/bin/python scripts/fetch_demos.py --height 720` |
| Re-remux and re-probe local files | `.venv/bin/python scripts/fetch_demos.py --repair` |

Each benchmark keeps its media in its own folder,
`docs/assets/<benchmark>/demos/`, with its own `manifest.json`. Nothing is
shared between benchmarks, so two of them may use the same task id and adding a
fourth means adding a folder.

`scripts/fetch_demos.py` downloads each clip — with `yt-dlp` where it sits
behind YouTube or Vimeo, directly where a project page serves the file — remuxes
with `-movflags +faststart` (without it a browser cannot report duration or seek
until the whole file downloads), extracts a poster frame, and records real
duration and pixel dimensions in `docs/assets/<benchmark>/demos/manifest.json`.
Those probed durations are what the site displays, because a published duration
does not always describe the posted video (see
[About BEHAVIOR-1K](docs/benchmarks/behavior-1k/about.md)).

If you change the videos, commit them like anything else.

> **Think before re-downloading at a higher resolution.** Git keeps every
> version of a binary forever, so swapping all 98 BEHAVIOR videos for 720p
> copies would add their full size to the repository permanently, on top of what
> is already there. Fetch a sharper copy for one task if you need it; do not
> re-fetch the whole set casually.

> **116 tasks have no upstream video.** Two BEHAVIOR tasks
> (`putting_shoes_on_rack`, `wash_a_baseball_cap`) are behind a Vimeo login;
> seven RoboWits tasks — every one that simulates dough, sand or water — have no
> clip on the project page; and RoboLab publishes 13. RoboLab rows without a clip
> show the scene the task starts from instead, and say so. Preserving what we
> *do* have is a large part of why the videos are committed rather than
> re-fetched.

### Why the videos are committed

They were originally fetched per contributor with `make demos`, which made a
clone depend on YouTube and Vimeo still serving the files — two of them
already 401 and cannot be downloaded at all any more. Committing them means a
clone is reproducible and nobody needs `yt-dlp`.

They are stored as ordinary Git objects, not Git LFS. Each file is ~12 MB,
well under GitHub's 100 MB per-file limit, and plain Git has **no bandwidth
metering and no storage quota** — so clones are unlimited and free, and
contributors need no extra tooling. The trade-off is that the ~1.1 GB is
permanent: Git keeps every version of a binary, so replacing the set would add
to the repository rather than replace it.

## Day-to-day

```bash
make edit                  # review and label tasks
git add state/ && git commit -m "triage: <what you decided>"
git push
```

Your whole session is a diff of `state/` — that is the entire review surface.
Run `make check` before pushing; CI runs the same thing.

## Commands

| Command | What it does |
| --- | --- |
| `make serve` | Preview, **read-only** (`PORT=9000` to pin the port) |
| `make edit` | Preview **plus** the edit daemon — the only way to change labels or status from the page |
| `make demos` | Re-download demo videos for all three benchmarks (normally unnecessary — they are committed) |
| `make build` | Build into `site/`, failing on broken links |
| `make validate` | Check every task page against the schema |
| `make links` | Resolve every internal link in `site/` (catches raw-HTML hrefs) |
| `make check` | What CI runs: validate + strict build + links |
| `make public` | The public site as deployed (read-only, runs from the published snapshot), links and size checked |
| `make publish-runs` | Snapshot the agent runs for the public site (`data/published_runs/`: filtered, secret-scanned; `BENCHMARK=<id>`: only its part) |
| `make upload-run-media` | Export, compress and upload the runs' replays and images to the Hugging Face dataset (`BENCHMARK=<id>`, your own `hf auth login`) |
| `make sync` | Re-sync every benchmark's task pages from its upstream |

## Layout

```
state/                             EVERYTHING A HUMAN EDITS LIVES HERE
  taxonomy.yml                     two-tier label vocabulary
  tasks/<bench>.yml                per-task status, difficulty, labels, owner
data/
  benchmarks/<id>.yml              benchmark facts + its own annotation vocabulary
  benchmarks/<id>.tasks.*.json     importer caches, so a rebuild needs no upstream
docs/
  benchmarks/<bench>/index.md      landing page = the task list
  benchmarks/<bench>/tasks/*.md    upstream metadata + prose, one per task
  assets/<bench>/demos/*.mp4       oracle demos, committed (~1.2 GB over three)
  assets/<bench>/demos/*.jpg       poster frames, committed
  assets/<bench>/demos/manifest.json  real duration and dimensions per file
  assets/robolab/scenes/*.jpg      scene stills for rows with no upstream clip
  assets/robotwin-2/scenes/*.jpg   initial scenes rendered in our image; demos/ holds our six-view expert clips
scripts/
  taskdb.py                        registries + task pages, one view
  gallery.py                       the task list (rows + inline video)
  hooks.py                         task-page header, <!-- gen:... --> expansion
  gen_pages.py                     triage / coverage / capability reference
  validate.py                      the CI guardrail
  import_behavior_tasks.py         idempotent sync from the BEHAVIOR demo gallery
  import_behavior_verified.py      BDDL goals + dataset statistics from the licensed copy
  import_robowits_tasks.py         idempotent sync from the RoboWits source + project page
  import_robolab_tasks.py          idempotent sync from the RoboLab source + project page
  import_robotwin_tasks.py         idempotent sync from the RoboTwin 2.0 source (ast) + documentation site + our media
  fetch_demos.py                   downloads demos, remuxes, extracts posters
  statedb.py                       atomic read/write of state/
  editd.py                         localhost API that writes edits back to disk
  migrate_state.py                 one-off: frontmatter -> state/
```

## The label taxonomy

Two tiers, in `state/taxonomy.yml`:

```yaml
capabilities:                 # tier 1 — the broad property
  - id: manipulation
    name: Manipulation
    subcapabilities:          # tier 2 — what a task is tagged with
      - id: pick-place
        name: Pick and place
        description: Grasp an object and put it somewhere.
        from_skills: [pick up from, place in, place on, ...]
```

Tasks are tagged with **tier-2 ids** only; tier 1 is derived, so coverage reads
at either level without anyone maintaining two lists.

**Provenance matters here.** BEHAVIOR publishes a 31-primitive skill vocabulary
annotated across all 20,000 demonstrations — that list is *theirs* and is
ground truth. A sub-capability with `from_skills` is a roll-up of those
primitives, which is what lets the editor suggest labels from a task's
annotated skills. Everything else is *ours*.

Current shape: **8 facets, 45 labels**, fitted to fifteen benchmarks rather than
the three we have integrated (see `docs/reference/benchmark-landscape.md`) and to
a per-task digest of all 250 tasks we hold (`scripts/task_skill_digest.py`).
A facet is one question about a task: how far the robot must go, what the body
must do, what the contact must do, what must change about an object, what makes
the goal hard to read, how much has to go right, what must be perceived, and what
varies between episodes.

Three facets are **ladders** — scale, horizon and generalisation are ordinal, and
a task takes the highest rung rather than several flags. That is where the
information density comes from: a typical task carries four to six labels even
though 45 exist. A label was only kept if knowing it changes what you predict
about the task, so redundant ones were cut (`multi-room` implied `navigate`) and
so were ones no surveyed benchmark could reach.

Every label carries its derivation: `from_skills` for BEHAVIOR's own primitives,
`derived_from` for the official annotation of any benchmark that implies it, and
`evidence` naming the tasks that motivated it. Running
`python scripts/suggest_labels.py` applies those rules to all 250 tasks and
reports what the vocabulary reaches — today that is every BEHAVIOR and RoboWits
task and 117 of 120 RoboLab tasks, at 2–5 labels each.

Thirteen labels are reached by nothing in the three suites we have integrated —
the body facet, world knowledge, and most of the generalisation ladder. That is
deliberate: HumanoidBench, MuJoCo Playground, DexToolBench, VLABench, RoboTwin
and RoboCasa each reach them, and the point of a shared vocabulary is that adding
one of those does not mean rewriting it. Still a **first draft, not a standard**.

To revise it: edit `state/taxonomy.yml`, or use the **Label taxonomy** page in
the site (`make edit`), which writes the same file. Deleting a label that tasks
still use is refused, and the offending labels are named.

## Four rules

**1. All mutable state is in `state/`.** Curation used to live in the
frontmatter of 100 task pages; reviewing a colleague's work meant reading 100
diffs. Now `git diff state/` is the whole review. Task pages keep only upstream
metadata and prose, so an upstream re-sync can never clobber a decision.

**2. Aggregate views are generated, never committed.** The task list, triage
board, coverage matrix and capability reference are built from per-task
frontmatter at build time. One contributor edits one task file that nobody
else is touching, and every shared view updates itself. To change a view,
change the generator — not a page.

**3. Videos are local files, never embeds.** `<video>` is what gives playback
speed control, and nobody will review 100 six-minute demos at 1×. The MP4s are
gitignored; each contributor runs `make demos`.

**4. The list stays cheap no matter how long it gets.** Rows paint in chunks of
12 as you scroll, and a row shows a poster image until it nears the viewport,
only then becoming a real `<video preload="none">`. A handful of media elements
are alive at a time instead of a hundred.

## Status

Framework complete and building. **Content is mostly un-triaged** — 300 task
pages with upstream metadata and demos, 2 of them worked examples. Populating
the rest is the work. See [`HANDOFF.md`](HANDOFF.md).

---

Internal working document. Not affiliated with or endorsed by the BEHAVIOR team.

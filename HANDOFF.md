# Delivery handoff

**Scope:** a documentation site for reviewing benchmark tasks — what each task
is, its oracle demo, the capabilities it needs, and whether we keep it. Three
benchmarks: the 2026 BEHAVIOR Challenge (100 tasks), RoboWits (30) and
RoboLab (120).

## What you have

| | |
| --- | --- |
| Site | Material for MkDocs, builds clean under `--strict` |
| Pages | 12 hand-written, 3 generated per benchmark, 250 task pages |
| Demos | 134/250 local (1.2 GB) + poster frames, playable inline at 1–4× |
| Scene stills | 107 RoboLab rows with no upstream clip show their scene instead |
| Editing | In-browser status/label editing via a localhost daemon (`make edit`) |
| Labels | 8 facets, 45 labels, fitted to 15 benchmarks; 3 facets are ordinal ladders |
| Curated state | One folder, `state/` — the whole review surface |
| Triaged | 2 of 250 (worked examples), plus 2 tasks we have run end to end |

```bash
make install && make demos && make edit
```

**Tell people `make edit`, not `make serve`.** Both serve the identical site,
but only `make edit` starts `scripts/editd.py` (port 8009), which is the only
thing that can write to `state/`. A browser page cannot write files. Under
`make serve` the Edit buttons appear but tell the user to run `make edit`
instead of silently failing — that visible failure is deliberate, because the
obvious guess is `make serve` and the wall is otherwise confusing. A deployed
build has no daemon and is read-only by design.

## Three design decisions

**0. All human-editable state lives in `state/`.**
`state/taxonomy.yml` plus `state/tasks/<benchmark>.yml`. Task pages under
`docs/` carry only upstream metadata and prose. Reviewing a day of triage is
`git diff state/` instead of a hundred file diffs, and two people on different
branches touch one file each. Writes are atomic (temp file + replace) and
sorted, so the diff stays readable. `scripts/migrate_state.py` performed the
one-off move and is idempotent.

**1. One Markdown file per task; every aggregate view is generated.**
The task list, triage board and coverage matrix do not exist as files — they
are built from task frontmatter during `mkdocs build`. A contributor edits one
file nobody else touches, and the shared views update themselves. The usual
failure mode of fifty people editing one index is structurally impossible.

**2. Local MP4 in a `<video>`, never an embed.**
Only a real `<video>` element exposes `playbackRate`. Demos average 5.9
minutes; at 1× nobody reviews 100 of them. Speed is a global 1/2/3/4× control,
defaulting to 2× and remembered across pages. Videos are gitignored and
fetched with `make demos`.

**3. The list is resource-bounded.**
Rows paint 12 at a time as a sentinel scrolls into view, and each row is a
poster image until it nears the viewport, only then becoming a real
`<video preload="none">`. Without this, 100 rows meant 100 media elements and
a slow first paint. First paint now costs ~0.3 MB of posters instead of
instantiating a hundred players.

**4. Three frontmatter zones.**
`upstream:` is mirrored from what the benchmark publishes and owned by
`scripts/import_<benchmark>_tasks.py`. `verified:` is read first-hand from the
distribution we actually run — the BDDL goal, the dataset's own statistics —
and owned by `scripts/import_<benchmark>_verified.py`. Everything else is
human-owned. Each importer rewrites one zone, is idempotent, and never deletes,
so you can track a moving upstream without losing curation work.

**5. Media is namespaced per benchmark.**
`docs/assets/<benchmark>/demos/<task_id>.mp4` with a manifest per benchmark,
and `docs/assets/<benchmark>/scenes/` for scene stills. Nothing is shared, so
two suites can use the same task id and adding a third means adding a folder.

## Verified

- `make check`: 0 errors, no broken links, 117 pages.
- Importer is idempotent (second run: `unchanged: 100`).
- Video paths resolve from both the list page and task pages (they sit at
  different URL depths, which is easy to get wrong).
- Task list JS run against the real payload: rows render, filters and sort
  work, URL reflects filters, speed persists to `localStorage`, starting one
  video pauses the others.
- Default ordering: `keep`, then `drop`, then `needs-review`, then `pending`;
  alphabetical inside each group. The decision drives the order, not whether
  anyone has applied labels.
- Edit daemon round-tripped end to end: a POST rewrote a task's status,
  difficulty and capabilities on disk while leaving the prose and the
  `upstream:` block byte-identical; a custom capability was appended to
  `data/taxonomy.yml` and validation still passed. Both test edits reverted.
- Every page checked in a real browser (headless Chrome screenshots), which is
  how the faststart, duration and aspect-ratio bugs below were found.

## Not verified

- **Nothing has been opened in a browser.** Row proportions, dark mode, and
  how the 22rem player feels at real width are all unchecked. Run
  `make serve` first.
- **No demo has been watched.** The two worked examples were tagged from the
  published instruction text, and both say so on the page. Not reviewed.

## Three bugs that all looked like "the page is stale"

These wasted real time during development because they present identically —
you change something, nothing happens, a forced reload sometimes fixes it.
Each has a different cause and all three are fixed:

1. **Custom CSS/JS was not cache-busted.** MkDocs fingerprints the theme's
   bundled assets but leaves `extra_css` / `extra_javascript` as bare
   filenames, so browsers cached them indefinitely. An edit to `tasklist.js`
   did nothing until a hard reload. `on_config` in `scripts/hooks.py` now
   appends a content digest (`tasklist.js?h=0754864c`).

2. **`mkdocs serve` was not watching the files the site is built from.** It
   watches `docs/` and `mkdocs.yml` by default; most of this site comes from
   `state/` and `scripts/`. Added a `watch:` list. Without it, the Edit button
   wrote to disk and the server never noticed.

3. **`functools.lru_cache` survived rebuilds.** `mkdocs serve` rebuilds inside
   one long-lived process, so even a correctly-triggered rebuild re-emitted
   cached task data. `taskdb.reset_caches()` now runs at the start of every
   build. This was the one that made the Edit button look broken end to end.

Verified together: with a live server running, a `POST` to the edit daemon now
changes the rendered page within seconds, no manual refresh and no restart.

## A raw-HTML link bug that `--strict` cannot catch

`mkdocs build --strict` validates links written in Markdown. Links emitted as
raw HTML by our hooks ship **verbatim**, so `href=".../index.md"` reached the
site and 404'd on the home page's benchmark card and on every capability chip.

Fixed with `doc_url()` in `scripts/hooks.py`, which converts a docs-relative
`.md` path into a finished URL at the page's *output* depth — note that raw
HTML must be relative to `page.url`, not `page.file.src_uri`; the two differ.

`scripts/check_links.py` now resolves every internal link in `site/` against
the filesystem and runs as part of `make check` and CI, so this cannot recur.

## Bugs found by looking at the rendered page

Worth recording, because none were visible from the source:

- **Players reported `0:06` for a six-minute demo.** yt-dlp's merged MP4s put
  the `moov` atom last, so the browser cannot know the duration or seek until
  the whole file arrives. All files are now remuxed with `+faststart`.
- **Upstream durations mean different things in the two cohorts.** `can_meat`
  is published as 395 s while its video runs 267 s. Since resolved against the
  licensed dataset (`scripts/import_behavior_verified.py`): for the 50 Vimeo
  tasks the published number is the *mean episode length* over 200 teleoperated
  episodes, exact to the second, and the posted video is an edited 42–100% of
  it; for the 50 YouTube tasks it is the *video's* length. Nothing upstream is
  wrong — they publish different quantities. Rows are still labelled with the
  probed video duration, so the label cannot contradict the player beside it,
  and the episode mean now sits on the task page under `verified:`.
- **Every demo was pillarboxed.** These videos are square (the R1 Pro head
  camera is 720×720), not 16:9. Real dimensions are stored in the manifest and
  applied per row.

## The label taxonomy, and how to change it

`state/taxonomy.yml`, two tiers — a facet holding the labels a task is tagged with:

```yaml
version: 5
capabilities:
  - id: interaction           # tier 1: a facet, i.e. one question about a task
    name: Interaction
    description: What the contact has to do — the physics of the manipulation itself.
    subcapabilities:
      - id: articulated       # tier 2: what a task is tagged with
        name: Open and close
        description: A hinge, drawer or lid constrains the motion, so the path is
          set by the object rather than chosen by the planner.
        from_skills: [open door, open drawer, open lid, ...]   # BEHAVIOR's own primitives
        derived_from:                                          # which official annotation implies it
          behavior-1k: {goal_predicates: [open], object_abilities: [openable]}
        evidence: 22 BEHAVIOR goals require something open or closed.
```

Eight facets: **Scale** (4, ladder), **Body** (6), **Contact** (10),
**Object state** (4), **Goal** (6), **Structure** (5, ladder + 2 flags),
**Perception** (3), **Generalisation** (7, ladder + 1 flag). Tasks carry tier-2
ids in `state/tasks/<benchmark>.yml`; tier 1 is computed, so nobody maintains
both. A facet with `graded: true` is a ladder — `scripts/suggest_labels.py` keeps
only the highest matching rung, and labels marked `flag: true` sit in a graded
facet without being rungs.

The facets were fitted to fifteen benchmarks, not our three —
`docs/reference/benchmark-landscape.md` is that survey, and
`scripts/task_skill_digest.py` prints what all 250 tasks we hold actually demand,
which is the evidence the vocabulary had to fit.

`derived_from` is what makes the vocabulary checkable rather than aspirational:
`python scripts/suggest_labels.py` applies every rule to all 250 tasks and reports
the coverage into `tmp/`. It caught two rules that named a field no extract has
and so could never fire — plus three that fired on 30–84 tasks by tagging every
container and every knife, which is the difference between what an object *can*
do and what the task *needs*.

Three ways to revise it, all writing the same file:

1. The **Label taxonomy** page with `make edit` — rename, add, delete, save.
2. `state/taxonomy.yml` in an editor.
3. **Add & tag** on a task row, for when a gap shows up mid-triage; the new
   label is parked under a `custom` capability for later placement.

Two guard rails: the save path refuses to remove a label that tasks still
reference (and names them), and `make validate` rejects any task state
pointing at an id that does not exist.

## The label vocabulary is explicitly provisional

Worth being blunt in the handoff, because it is the part most likely to be
wrong: **each benchmark's own vocabulary is official; our 45 labels are not.**

Eight of the fourteen are a coarse roll-up of those primitives, each recording
which ones it covers (`from_skills` in `state/taxonomy.yml`), so the derivation
is inspectable and the editor can suggest labels from a task's annotated
skills. The other six describe task structure — long horizon, multi-room,
counting, object state, bimanual, search.

An earlier draft had 34 fine-grained labels that I invented without evidence
or discussion. It was too detailed to apply consistently and too speculative
to defend, so it was cut to this. Treat the current set as a **starting point
for the group to argue with**, not a standard. The "Add & tag" box appends new
labels to a `custom` group so proposals accumulate as evidence rather than
being lost.

## Known gaps

- **2 demos could not be downloaded** (`putting_shoes_on_rack`,
  `wash_a_baseball_cap`). Vimeo returns 401 for those two specifically; they
  require a login. Their rows show a "demo not downloaded" placeholder. Worth
  a retry later in case it is temporary.
- **50 of 100 tasks have no instruction text upstream** — the 2025 carryover
  cohort. We store an empty string rather than inventing a goal.
  Reconstructing them from the demos is tracked on the triage board, and
  `docs/contributing/task-page-guide.md` has the procedure.
- **The 1.1 GB of video is committed as ordinary Git objects**, not Git LFS.
  Plain Git has no bandwidth metering or storage quota, so clones are free and
  unlimited and contributors need no extra tooling; LFS would have metered
  every clone against the repository owner's account. The trade-off is that
  the size is permanent — Git keeps every version of a binary, so re-fetching
  all 98 at 720p would add ~3 GB rather than replace what is there. Fetch a
  sharper copy per task if needed.
- **The public site does not carry every video.** With all demos the site is
  about 1.4 GB, over GitHub Pages' 1 GB limit, so the public build links the
  BEHAVIOR-1K demos to the official videos instead (see "Publishing" below).
- **Demos are 360×360** (a few 480×480). The `height<=480` cap picked the
  360p rendition for most tasks. Fine at the list's 11 rem preview, soft on the
  task page. `python scripts/fetch_demos.py --height 720` re-fetches sharper at
  roughly 3–4× the disk cost.
- **The edit daemon has no auth, locking or conflict handling.** That is a
  deliberate fit to how this is used — one person, one machine — but it means
  it must never be exposed on a network.
- Every dependency is pinned; MkDocs is mid-way through a contested v2
  transition, so bump deliberately.

## Publishing

The site is public at <https://embodied-agent-interface-v2-internal.github.io/>.
It is built from `main` of
`github.com/embodied-agent-interface-v2-internal/embodied-agent-interface-v2-internal.github.io`
by `.github/workflows/deploy.yml`. Because this is an `<org>.github.io`
repository, the site sits at the root of the domain.

### How a change reaches the public site

1. **Locally**, make the change:
   - triage with `make edit` (writes `state/`);
   - re-sync a benchmark with `make sync-<benchmark>` (the importers run on your
     machine, because most of them read checkouts or private repositories);
   - or edit prose or code.
2. Run `make check`, the same check CI runs.
3. Run `make public`. It is the deployed build: read-only, with its links and
   size checked. To look at it, run `python -m http.server -d site`.
4. Commit, then push to `main` or open a pull request. CI runs `make check` and
   `make public` on every push and pull request.
5. **Deploy** runs on every push to `main`. It builds `make public` and publishes
   it within a few minutes. Watch it under *Actions → Deploy*; the
   `github-pages` environment shows the URL. It can also be started by hand
   (*Run workflow*).

### What the public build shows, and what it leaves out

The public build is set by `RB_PUBLIC=1`; `scripts/sitemode.py` has the rules and `data/public.yml` the settings.

- **No edit controls:** no Edit button, no taxonomy editor, no "edit this page".
- **Agent runs, from the published snapshot.** The public site never reads the local run data (`data/runs/`,
  `docs/assets/*/runs/`), even on a machine that has it. It reads `data/published_runs/`, which is committed:
  - each run's trials (state, grade, metrics, progress, agent time, requests, tokens, cost);
  - each trial's full text log (the model's words, its tool calls and their output, robot calls, token counts).
- **No machines.** The snapshot names no machine, path, job or host. Notes in `state/runs/` that name a machine
  read "one of our machines" on the public site; a local build shows them as written.
- **Run media on Hugging Face.** Replays and images are not on Pages. They live in the public dataset
  <https://huggingface.co/datasets/eai-v2-internal/agent-runs>, laid out as `<benchmark>/<run>/<task>/<slot>/`. The
  log pages play them inline from `run_media_base` in `data/public.yml`. `make guard`, part of `make check` and CI,
  fails if run media are ever committed here.
- **Run ids** are `<harness>-<model>-<effort>[-<tag>]` (e.g. `codex-gpt6_luna-xhigh`), the same on the site, in the
  Hugging Face dataset and in the runner's results folders (`SLUG`). `docs/contributing/registering-runs.md` has the
  rule. A renamed run lists its old ids under `formerly:` in `data/agents/`; its old log-page addresses redirect, and
  `?run=<old id>` still picks it. The first rename (2026-09-28): `codex-0.157-gpt6luna-xhigh-cgpt` became
  `codex-gpt6_luna-xhigh`, with the Hugging Face folders copied server-side (no re-upload).
- **Runs marked `hidden: true`** are not shown. Runs kept out of git (`state/runs/<b>.local.yml`,
  `data/agents/<run>.local.yml`) are not even in the repository.
- **Trials we stopped ourselves** (`stopped:` in `state/runs/`) show with their reason and count in no statistic.
- **Some demos.** The benchmarks in `link_demos` (`data/public.yml`, today `behavior-1k`) link to the official
  video instead of our copy. `make public` fails above 1 GB.

### Publishing agent runs

**In one command: `make publish`.** One gated, idempotent run. Run it once a whole batch has finished, never on a
loop: the owners want few, meaningful commits in the public repository (2026-09-28). If a publish needs a fix, amend
it before pushing. It logs to `.cache/publish.log`, and on any failure its last line says why and it exits non-zero
without pushing. It runs these steps:

1. A full import.
2. The snapshot, with finished trials only. Its secret and privacy scan must be clean.
3. If nothing changed, it stops here with exit 0.
4. The new media are exported, compressed (4 videos and 8 images at a time) and uploaded.
5. `make check` and `make public` must pass.
6. It commits `data/published_runs/` only, with the counts in the message, and pushes to main as a fast-forward.

It never forces a push, and it stops if origin has commits this checkout lacks.

**By hand**, the same steps:

1. `make runs`: collect the runs from our machines (local only, as always).
2. `make publish-runs`: write the filtered snapshot to `data/published_runs/`. It drops machines, paths, jobs and
   log checks, and redacts credentials, e-mail addresses and private IPs. It then scans what it wrote; if anything is
   left, it stops and leaves the published snapshot unchanged. The snapshot it replaces is kept in
   `.cache/published_runs.prev/`.
3. Review: `git diff --stat data/published_runs/`, and `make public` to look at it.
4. Commit and push. Deploy publishes it.

**Media**, after each `make publish-runs`:

1. Log in with `hf auth login`, using your own account; it must be a member of `eai-v2-internal`.
2. Run `make upload-run-media BENCHMARK=<id>`. With no `BENCHMARK`, it does every benchmark. It runs three steps:
   - `make export-run-media` collects the files the published logs name (hard links, in `.cache/run-media-export/`);
   - `make compress-run-media` converts them into `.cache/run-media-hf/`: videos to H.264 CRF 28 with the index
     first, at most 720p, no audio (each one checked for duration and a clean decode; where that is not smaller, a
     faststart remux of the original), and PNG to WebP;
   - `hf upload-large-folder` uploads only that benchmark's folder, plus the dataset card (`data/run-media-card.md`).
     It is resumable: run it again after an interruption.
3. The snapshot names the images as published (`run_media_images: webp` in `data/public.yml`), so nothing else
   changes on the site.

**A replay that arrives later** follows the same path. An example is a re-rendered video for a page that now says
"truncated at the source" (the four BEHAVIOR re-renders of 2026-09-28):
1. Put the verified video in the local run data (`data/runs/<id>/`, gitignored). Then edit the trial's entry in
   `data/runs/<id>/<run>.backfill.yml`: `video:` is the file's path, `note:` says how it was made, and any
   `video_problem:` goes. `make runs` then rebuilds the log page with that video, and the log checks count it.
2. `make publish-runs BENCHMARK=<id>` names the video in the snapshot. Only that benchmark's part changes, so
   another benchmark's unfinished batch stays out.
3. `make upload-run-media BENCHMARK=<id>` uploads only what is new or changed.
4. Commit the snapshot and push.

**A new benchmark, from a collaborator:**
1. Register its runs (`state/runs/<id>.yml`, `data/agents/`) and collect them with `make runs`.
2. Open a pull request with `make publish-runs BENCHMARK=<id>`; its snapshot is text only. Without `BENCHMARK`,
   a checkout that lacks the other benchmarks' run data would drop them from the snapshot.
3. Run `make upload-run-media BENCHMARK=<id>` with your own login.
4. Once the pull request is merged, Deploy publishes the pages and they play the media from the dataset.

### Rollback

- **Revert and push:** `git revert <commit>`, then push. Deploy republishes the
  content as it was.
- **Re-run an earlier deploy:** *Actions → Deploy → an earlier successful run
  → Re-run all jobs*. This republishes that run's commit until the next push.
- **Stop publishing:** *Actions → Deploy → … → Disable workflow* stops new
  deploys. *Settings → Pages → Unpublish site* takes the site down.

### Who needs which permission

- **An organisation owner, once:**
  - repository visibility (Pages from a private repository needs a paid plan);
  - *Settings → Pages → Build and deployment → Source: GitHub Actions*;
  - the organisation's settings must allow Actions and public Pages.
- **Maintainers:** write access to the repository, to push to `main` or merge
  pull requests. No secret or personal token is needed: the workflows use the
  built-in `GITHUB_TOKEN`, with only the permissions each job needs.
- **Contributors:** a branch or a fork, and a pull request.

### Still open

- `.github/CODEOWNERS`: its rules are commented out until the organisation's
  teams exist.
- Optional: enable Discussions and fill `extra.giscus` in `mkdocs.yml` to get a
  comment thread on each task. The site builds fine without it.

## What I would do next

1. `make serve` and look at it. The visual layer is the only large unverified
   surface left.
2. Calibrate capability tagging as a group on ten tasks before opening it up —
   that is where people will silently disagree.
3. Settle where the BEHAVIOR-1K demo copies live publicly (see "Publishing").

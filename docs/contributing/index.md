---
title: Contributing
---

# Contributing

## Setup

```bash
git clone <this-repo> && cd <this-repo>

make install     # one-time: .venv + the pinned toolchain
make demos       # one-time: 98 oracle demos + posters, ~1.2 GB
make edit        # start the site WITH editing enabled
```

The port is chosen automatically and printed, so two people on one machine do
not collide. Pin it with `make edit PORT=9000`.

`make demos` is optional but strongly recommended — without local video files
the task list shows placeholders. We use a `<video>` element rather than an
embedded YouTube/Vimeo player precisely so playback speed works, and that
needs local files.

### `make serve` versus `make edit`

!!! danger "If you intend to change anything, you need `make edit`"

    | | `make serve` | `make edit` |
    | --- | --- | --- |
    | The site | yes | yes |
    | **Edit** button on a task row | visible, but will not save | **saves to `state/`** |
    | Label taxonomy page | read-only | **editable** |
    | Extra process | none | `scripts/editd.py` on port 8009 |

    Both commands serve the *same site*. The difference is the daemon: a web
    page cannot write to your filesystem, so every save goes through a small
    local HTTP API. `make edit` starts it and stops it with the server.

    Under `make serve`, clicking **Edit** replaces the button text with
    ``run `make edit` `` rather than doing nothing, so the failure is visible
    instead of mysterious. If your changes are not sticking, that is why.

    The daemon is localhost-only, unauthenticated and single-user — everyone
    runs their own copy, so there is no locking and no conflict handling. Do
    not expose it on a network. A deployed build has no daemon and is
    therefore always read-only.

## Everything you change lives in `state/`

All curation — every status, label, owner and note, plus the taxonomy itself —
is in one folder:

```
state/
  taxonomy.yml           the label vocabulary: 6 facets, 35 labels
  display_tags.yml       what pages show: Capability and Task Domain tags
  tasks/behavior-1k.yml  per-task status, difficulty, labels, display tags, owner, notes
```

Task pages under `docs/` hold only upstream metadata and prose. So reviewing a
colleague's triage is:

```bash
git diff state/
```

rather than opening a hundred files. Two people on different branches touch
one file each instead of a hundred each.

## Editing from the page

With `make edit`, every task row has an **Edit** button. It opens in place, so
you decide while watching the demo — which is when the judgement actually
happens. You can set:

- **status** — keep, drop, needs-review, pending
- **difficulty** — for a coding agent driving this robot, not a human
- **display tags** — as toggle buttons, under their group: Capability, then
  Task Domain; a save needs at least one from each. Tags implied by the task's
  annotated BEHAVIOR skills are marked with a `·`, so usually you are
  confirming a suggestion rather than reading the whole vocabulary.

Saving writes `state/tasks/<benchmark>.yml` and nothing else — task pages are
never touched. **Add & tag** creates a new tag, in the group you pick, when the
existing vocabulary does not fit. The detailed labels (`labels:`) are not on the
page: set them in the state file by hand.

The [Label taxonomy](../reference/capabilities.md) page has the same treatment
for the display tags themselves: rename groups, add or remove tags, save back to
`state/display_tags.yml`. It refuses to delete a tag that tasks still use, and
names them, so the vocabulary cannot silently break your task state.

## Your first contribution: triage one task

1. Open the [task list](../benchmarks/behavior-1k/index.md). The default order
   puts already-labelled work first, so scroll past it — or filter **Status**
   to `pending`.
2. Set the playback **speed** to 2× or 3× once; it is remembered everywhere.
3. Click **Edit** on a task, set `owner` to your GitHub handle, and Save.
   Now nobody duplicates your work.
4. Watch the demo in the row. Then set status, difficulty and labels, and Save.
5. Optionally open the task page and write down *why* — see the
   [task page guide](task-page-guide.md). The prose is what a reviewer reads.
6. `make check`, then commit. Your whole session is a diff of `state/`.

**One task per pull request.** A one-file PR merges in minutes; a thirty-file
PR sits for a week. Exempt: taxonomy changes, tooling, and upstream re-syncs.

## What goes where

| You want to… | Edit |
| --- | --- |
| Triage a task, set tags | `state/tasks/<bench>.yml` — or the **Edit** button |
| Leave a task out of the final benchmark, keeping it on the site | `excluded: "<why>"` in `state/tasks/<bench>.yml` — see [the task page guide](task-page-guide.md#excluded-out-of-the-final-benchmark-still-on-the-site) |
| Add or reword a display tag | `state/display_tags.yml` — or the **Labels** page |
| Add or reword a detailed label | `state/taxonomy.yml` |
| Write prose about a task | `docs/benchmarks/<bench>/tasks/<task_id>.md` |
| Record benchmark-level facts | `data/benchmarks/<bench>.yml` |
| Register an agent run, or your benchmark's part in one | `data/agents/<run>.yml`, `state/runs/<bench>.yml` — see [Registering runs](registering-runs.md) |
| Change the task list / rows | `scripts/gallery.py`, `docs/javascripts/tasklist.js` |
| Change a generated page | `scripts/gen_pages.py` (the Runs pages: `scripts/runpages.py`) |
| Change the task-page header | `scripts/hooks.py` |

!!! danger "Never hand-edit an aggregate page"

    The task list, coverage matrix and capability reference are
    **generated at build time and not committed**. Wanting to edit one means
    the change belongs in the generator or in task frontmatter. This is the
    single rule that keeps many contributors from colliding.

## Review

CI runs `make check`: `scripts/validate.py` (schema, taxonomy, registries)
plus `mkdocs build --strict` (no broken links). Errors block a merge;
warnings — an incomplete task page — do not. It then runs `make public`, the
read-only build that is published.

## Publishing

Every push to `main` publishes the site at
<https://embodied-agent-interface-v2-internal.github.io/>, through the Deploy
workflow in GitHub Actions. There is nothing to run by hand.

- Before you push, run `make check`, then `make public` to see the public site
  as it will be deployed.
- The public site is read-only. It shows no Edit buttons. Its agent runs come
  from the committed snapshot that `make publish-runs` writes, without machine
  names or paths. Runs marked `hidden` are not shown.
- To take a change back, revert the commit and push.

HANDOFF.md, section "Publishing", has the details: the steps, rollback, and who
needs which permission.

A human reviewer checks the things CI cannot:

- Do the capability tags pass [the necessity test](capability-tagging.md#the-test-to-apply)?
- Is every `drop` reason falsifiable? "Too hard" is not; "the goal is
  satisfiable without touching the target object" is.
- Are reconstructed goals labelled as reconstructions?
- Did anyone write into an `upstream:` block?

Approving does not mean agreeing with every call — it means the call is stated
clearly enough to disagree with later.

### When two people disagree

Set `status: needs-review`, put **both** positions in `status_reason`, and
settle it on the task page's comment thread. Whoever closes it updates the
page. Never silently overwrite someone else's triage decision.

## Conventions

- **English only**, in pages and commit messages.
- **Sign your judgements** with your handle.
- `status: needs-review` with a real question beats silence.
- **Never edit `upstream:`** — it is overwritten on the next sync.

## Re-syncing upstream

```bash
make sync-dry    # preview
make sync        # write
```

Only `upstream:` blocks should change. Open it as its own PR. If prose changed,
stop and investigate. Tasks that vanish upstream are reported, never deleted.

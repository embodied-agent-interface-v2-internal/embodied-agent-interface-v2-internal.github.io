---
title: Home
---

# Benchmark task reference

Documentation for the benchmarks behind our robotic coding-agent work. For
every task: what it asks for, its oracle demonstration, the capabilities it
requires, and whether we are keeping it; and how our coding agents do on it.

## Benchmarks

<!-- gen:benchmark-cards -->

## Agent runs

<!-- gen:runs-home -->

## How to contribute

Everything you would change lives in **one folder**, `state/`. Task pages under
`docs/` hold only upstream metadata and prose, so reviewing a day of someone's
triage is `git diff state/` — not a hundred file diffs.

| I want to… | Edit this | Or use |
| --- | --- | --- |
| Triage a task, set its tags | `state/tasks/<benchmark>.yml` | the **Edit** button on any task row |
| Add or reword a display tag | `state/display_tags.yml` | the [Label taxonomy](reference/capabilities.md) page |
| Add or reword a detailed label | `state/taxonomy.yml` | — |
| Write up why a task is interesting | `docs/benchmarks/<benchmark>/tasks/<task_id>.md` | — |
| Record benchmark-level facts | `data/benchmarks/<benchmark>.yml` | — |
| Change how the task list looks | `scripts/gallery.py`, `docs/javascripts/tasklist.js` | — |
| Add a whole new benchmark | [walkthrough](contributing/adding-a-benchmark.md) | — |

### Start here

```bash
git clone <this-repo> && cd <this-repo>

make install     # one-time: creates .venv, installs the pinned toolchain
make demos       # one-time: downloads 134 oracle demos + posters (~1.2 GB)
make edit        # start the site WITH editing enabled
```

`make edit` prints the URL it picked (the port is chosen automatically, so a
colleague's copy never collides with yours). Open it, and you are on the task
list.

Then:

1. **Set the speed** to 2× or 3× once — it is remembered across pages.
2. **Filter Status to `pending`** and pick a short task.
3. **Click Edit** on that row, set `owner` to your handle, Save. Now nobody
   duplicates your work.
4. **Watch the demo** in the row, then set status, difficulty and labels.
5. Optionally open the task page and write down *why* — that prose is the part
   a reviewer actually reads.
6. `make check`, then commit. Your whole session is a diff of `state/`.

!!! danger "Editing only works under `make edit` — not `make serve`"

    | Command | Site | Edit buttons | Label taxonomy page |
    | --- | --- | --- | --- |
    | `make serve` | yes | **no** | read-only |
    | `make edit` | yes | **yes** | editable |

    The two commands serve the identical site. The difference is that
    `make edit` also starts a small local daemon (`scripts/editd.py`, port
    8009) that is the only thing able to write to `state/`. A browser page
    cannot write files on its own.

    Under `make serve` the **Edit** buttons are still visible — clicking one
    tells you to run `make edit` rather than silently doing nothing. If your
    edits are not saving, this is why: stop the server and run `make edit`.

    A deployed copy of this site is always read-only, by design.

<div class="grid cards" markdown>

- :material-play-box-outline: **Triage a task**

    The main job. Watch the demo, decide keep or drop, apply labels.
    [How to do it →](contributing/index.md#your-first-contribution-triage-one-task)

- :material-tag-multiple-outline: **Argue with the labels**

    The vocabulary is a first draft, not a standard: tasks show display
    tags in two groups, Capability and Task Domain, and keep their detailed
    labels for analysis. [Label taxonomy →](reference/capabilities.md)

- :material-text-search: **Reconstruct a missing goal**

    50 of the 100 tasks ship no instruction text upstream. Watching the demo
    and writing the goal down is high-value.
    [How →](contributing/task-page-guide.md#reconstructing-a-missing-instruction)

- :material-source-branch: **Add a benchmark**

    A YAML file plus task pages; every view picks it up automatically.
    [Walkthrough →](contributing/adding-a-benchmark.md)

</div>

!!! warning "Scope"

    Working document, compiled in part from public BEHAVIOR Challenge
    material. Not affiliated with or endorsed by the BEHAVIOR team.

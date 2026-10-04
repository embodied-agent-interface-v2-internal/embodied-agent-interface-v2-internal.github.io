# Local state

**Everything a human edits lives in this folder.** Nothing else in the
repository changes as you curate.

| File | Holds |
| --- | --- |
| `taxonomy.yml` | The two-tier label vocabulary: the detailed labels (`labels:`), not shown on task pages |
| `display_tags.yml` | What the site shows: the display tags (`display_tags:`), two groups, Capability and Task Domain |
| `tasks/<benchmark>.yml` | Per-task status, difficulty, labels, display tags, owner, notes, and `excluded` (below) |
| `runs/<benchmark>.yml` | The benchmark's agent runs: batches, which tasks each run covers, why the others are out ([registering runs](../docs/contributing/registering-runs.md)) |

## Why it is separated

Curated state used to live in the frontmatter of 100 individual task pages.
Reviewing a colleague's work meant opening 100 diffs, and two people on
different branches touched 100 files each. Now a full afternoon of triage is a
diff of one file:

```bash
git diff state/
```

Task pages under `docs/benchmarks/*/tasks/` keep only the upstream metadata
(synced, never hand-edited) and your prose. The site merges the two at build
time.

## Leaving a task out of the final benchmark: `excluded`

```yaml
line_city:
  difficulty: easy
  excluded: "too easy for the final benchmark (line drawings; kept for the record, results in Runs)"
```

Optional, per task, the benchmark owner's call: the task is not part of the final
benchmark, and the text says why. It is not a review decision (`status: drop`
stays what it is, for the benchmarks that use it). An excluded task keeps its
page, its demo and its agent runs; the task list shows it greyed with its own
label and puts it last; the benchmark's counts leave it out ("82 tasks + 9
excluded"); its page opens on a banner with the reason; on the Runs pages its
trials stay, last in a run's table, and the numbers count the benchmark's own
tasks unless you switch *Count* to include the excluded ones. Set it by hand (the
Edit button leaves it alone). Delete the line to bring the task back.

Notes about a decision (who, when, a quote) go in the comment block under the
file's header: the Edit button rewrites the records and keeps that block, but not
comments between records.

## Writing to it

Three ways, all equivalent:

- The **Edit** button on any row of the task list (`make edit`).
- The **Labels** page, for the taxonomy itself.
- A text editor. It is plain YAML, sorted by key, one task per block.

The site reads these files at build time, so `mkdocs serve` picks up an
external edit immediately.

---
title: Task page guide
---

# Task page guide

A task has two halves, kept in different places on purpose.

| | Where | Who writes it |
| --- | --- | --- |
| **Upstream metadata** | frontmatter of `docs/benchmarks/<bench>/tasks/<id>.md` | the importer, never you |
| **Prose** | body of that same file | you |
| **Curated state** | `state/tasks/<bench>.yml` | you, or the Edit button |

The split means a full afternoon of triage is one file's diff, and a re-sync
from upstream can never clobber a decision you made.

## The task page

```yaml
---
title: Can Meat
task_id: can_meat
benchmark: behavior-1k

# --- upstream: synced by scripts/import_behavior_tasks.py. Do not hand-edit. ---
upstream:
  source: https://behavior.stanford.edu/challenge/tasks/index.html
  synced: '2026-09-20'
  cohort: 2026-new
  instruction: Open the kitchen cabinet, take out the two hinged jars, ...
  scene_model: house_single_floor
  rooms: [kitchen]
  demo_duration_s: 395
  oracle_video: https://player.vimeo.com/video/1114054618
  oracle_thumbnail: https://vumbnail.com/1114054618.jpg
---
```

**Anything you write in `upstream:` is destroyed on the next sync.** If upstream
is wrong, say so in the prose and attribute the correction to us. `cohort` is
derived by the importer from the demo's video host, because the 2025 carryover
tasks use YouTube and the 2026 ones use Vimeo.

Below the frontmatter, four prose headings. Delete the HTML comments as you
fill them in; leave `_Not yet written._` where you have nothing, so the gaps
stay visible.

| Section | What belongs there |
| --- | --- |
| **Why this task is interesting** | One paragraph. Why it earns a slot — or why it does not. |
| **Capability notes** | Justify each label. One bullet each is plenty. |
| **Oracle demo review** | Does the demo satisfy the goal? Is it clean? Would it mislead an imitation learner? |
| **Discussion** | Conclusions from the comment thread. Sign your points. |

Do not restate the instruction, scene, rooms or duration in prose — all of it
renders automatically at the top of the page, and a copy would go stale.

## The curated state

`state/tasks/<benchmark>.yml`, one block per task:

```yaml
can_meat:
  status: keep
  difficulty: hard
  labels: [articulated, pick-place, insert-attach, long-horizon, counting,
           object-state, search]
  display_tags: [perception-understanding, planning-reasoning, control-coordination,
                 feedback-adaptation, mobile-whole-body-manipulation]
  owner: alice
  note: Dense multi-constraint goal; high discriminative value per episode.
  skills: [open door, open lid, pick up from, place in, close lid, close door]
```

| Field | Values |
| --- | --- |
| `status` | `keep` · `drop` · `needs-review` · `pending` |
| `difficulty` | `unrated` · `easy` · `medium` · `hard` · `extreme` — for a coding agent driving this robot, not a human teleoperator |
| `labels` | tier-2 ids from [the taxonomy](../reference/capabilities.md#detailed-labels), the detailed labels, not shown on the page; unknown ids fail validation |
| `display_tags` | what the page and the task list show: ids from [the display tags](../reference/capabilities.md), at least one Capability and one Task Domain tag; unknown ids, or tags from one group only, fail validation |
| `owner` | bare GitHub handle, no `@` |
| `note` | free text; optional |
| `excluded` | optional: why the task is not part of the final benchmark — see below |
| `skills` | BEHAVIOR's own primitives observed in the demo; must match their vocabulary exactly |
| `media` | extra screenshots or clips — see below |

Defaults are omitted from the file, so a block only ever contains decisions
someone actually made.

!!! tip "Use the Edit button"

    With `make edit`, every row of the task list has an **Edit** button that
    writes this file for you, while you are watching the demo. That is when
    the judgement actually happens.

### `excluded`: out of the final benchmark, still on the site

```yaml
line_city:
  difficulty: easy
  excluded: "too easy for the final benchmark (line drawings; kept for the record, results in Runs)"
```

The benchmark owner's call, per benchmark, and separate from `status` (a benchmark
that drops tasks in review keeps doing so, and looks the same). The task keeps its
page, demo and agent runs; lists show it greyed, labelled *excluded*, at the
bottom; the benchmark's counts and its Runs numbers leave it out, with the
excluded ones shown beside them; the task page opens on a banner with the reason.
The value must say why. Set it in the file by hand; the Edit button leaves it
alone.

### `labels` versus `skills`

`skills` is **descriptive** — what the demo does, in BEHAVIOR's own vocabulary.
`labels` is **normative** — what an agent must handle. They come apart often:
a teleoperator may open a drawer the goal never required. See
[Labelling tasks](capability-tagging.md).

### `media`

!!! danger "Never commit media files"

    Host them elsewhere and reference by URL — drag into a GitHub issue comment
    for a permanent CDN link, or use a HuggingFace dataset repo for anything
    systematic. `kind` is `image`, `video` or `link`; `url` must be absolute.

    The caption is the value: "fails at 2:10, drops the jar while turning"
    tells a reader whether to click; "rollout 3" does not.

```yaml
can_meat:
  media:
    - kind: image
      url: https://user-images.githubusercontent.com/12345/grasp-failure.png
      caption: Gripper clips through the jar rim on approach
      credit: "@handle"
```

## Reconstructing a missing instruction

The 50 `2025-carryover` tasks ship no instruction upstream. We leave it empty —
inventing one would launder a guess into a field that reads as official.

Put your reconstruction in *Why this task is interesting*, clearly marked, and
set `status: needs-review` with a `note` saying the goal is reconstructed:

```markdown
!!! note "Reconstructed goal — not official"

    Upstream publishes no instruction for this task. From the demo, the goal
    appears to be: move both frozen fruit packages from the countertop into the
    freezer and close it. Unverified against the BDDL definition. (@handle)
```

## Before you push

```bash
make check
```

Warnings are fine — an untriaged task is all warnings. Errors are not.

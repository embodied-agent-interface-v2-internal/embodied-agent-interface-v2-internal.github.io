---
title: Registering runs
---

# Registering your runs

A **run** is one agent configuration: a harness, a model and its settings, for
example *Codex CLI 0.157.0 + GPT-6 Luna, reasoning xhigh (ChatGPT login)*. Each
task of a benchmark that takes part in the run is tried once per mode. The
**Runs** tab shows an overview across benchmarks, plus a page per benchmark that
shows one run at a time. The task lists and task pages show each task's pills
for a chosen run, the benchmark's default run first.

As with tasks, registering a run means adding files, not editing code. Every
benchmark owner edits only their own files, and one owner's import never
rewrites another's data.

## Who owns what

| File | Holds | Owned by | In git |
| --- | --- | --- | --- |
| `data/agents/<run>.yml` | What the run is: harness, model, settings, billing, price key | Whoever registers it first. Every benchmark that runs this configuration reuses it | yes |
| `state/runs/<benchmark>.yml` | The benchmark's part in each run: its default run, batches, task scope, removals, follow-ups | The benchmark's owner | yes |
| `data/prices.yml` | List prices per model, behind the cost estimate | Shared: add a model once, with its source | yes |
| `data/runs/hosts.local.yml`, `data/runs/hosts.<name>.local.yml` | Which machine keeps which Harbor jobs | You, on your own machine | no |
| `data/runs/<benchmark>/<run>.json` | What `make runs` collected | The importer | no |
| `data/runs/status.json` | Every benchmark's default run, in the one-sweep shape, for scripts that poll it | The importer | no |
| `docs/assets/<benchmark>/runs/<run>/` | The log pages' data | The importer | no |

Why this split:

- **A run's definition is separate from any benchmark.** The same configuration
  usually runs on several benchmarks, and the overview adds them up by run id.
- **A benchmark's scope is curation**, like its task labels. It lives in
  `state/`, one file per benchmark, so triaging a run is a diff of one file that
  only that benchmark's owner touches.
- **Hosts stay local.** Machine aliases and paths never reach GitHub. Several
  people on one checkout each add a `hosts.<name>.local.yml` of their own.
- **Collected data is per benchmark and run.** Each output file has one writer,
  and nothing is ever merged into a shared file (`status.json` is derived).
- **Prices sit apart from the data**, so that every cost on the site can say
  where its numbers come from.

## 1. Describe the run once: `data/agents/<run>.yml`

The file name is the run id. Build it from the harness and version, the model,
the settings and the login, for example `codex-0.157-gpt6luna-xhigh-cgpt`. If the
same configuration is already registered, reuse its id instead of adding a file.

```yaml
label: Codex CLI 0.157.0 + GPT-6 Luna, reasoning xhigh (ChatGPT login)   # the run's name everywhere
short: Codex CLI 0.157 · GPT-6 Luna · xhigh · ChatGPT login   # the run picker: harness · model · effort · access
harness: Codex CLI 0.157.0 as harbor_agents.codex_chatgpt:CodexChatGPT
model: chatgpt/openai/gpt-6-luna
settings: {reasoning_effort: xhigh, version: 0.157.0}
billing: subscription        # subscription | openrouter | api | none
price: openai/gpt-6-luna     # a key of data/prices.yml
modes: [unlimited, limited]
```

The tooling reads `label`, `short`, `billing`, `price` and `modes`; `harness`,
`model` and `settings` are shown on the run's page. Write `short` as four parts
joined by ` · `: harness and version, model, reasoning effort, access. The run
picker shows it and highlights the parts in which a benchmark's runs differ. Anything else, such as
`since`, `notes` or the exact `harbor` command line, is for people.

## 2. Take part with your benchmark: `state/runs/<benchmark>.yml`

An excerpt of RoboLab's file:

```yaml
default: codex-0.157-gpt6luna-xhigh-cgpt   # shown first: task list, task pages, status.json
task_dir: "robolab-{task_dashed}-i00"      # the task's directory in the harness repo
runs:
  codex-0.157-gpt6luna-xhigh-cgpt:
    batch: robolab-lunacx-0925-2038
    followups:
    - {task: clean_up_toys, mode: unlimited, trial: robolab-clean-up-toys-i00__3b6KY3P, note: "regrade queued on gpu1: ..."}
    tasks:
    - animals_in_bin
    - apple_and_yogurt_in_bowl
    # ...
    removed:
      banana_on_plate: 'one-step pick-and-place: 1 object(s) onto plate_large'
      # ...
```

| Field | Meaning |
| --- | --- |
| `default` | The run the task list, the task pages and `data/runs/status.json` show first. Without it, the first run listed. |
| `task_dir` | The task's directory in the harness repo: Harbor names a job `<batch>-<mode>-<task dir>`. `{task}` is the task id, `{task_dashed}` the same with dashes. The default is `{benchmark}-{task_dashed}-i00`. |
| `progress` | Which reward key holds the partial credit beside success. The default is `final_reward`; BEHAVIOR uses `q_score`, the 2026 challenge's score. A success always counts as progress 1.0. |
| `metrics` | Optional. Continuous scores the grader writes to `reward.json`, beside success: a list of `{key, label, format, unit, better, summary, help}`. Each gets a column and a sort in the task table, and a run figure (the mean of the graded trials, or the median with `summary: median`). `format` is a Python format spec (default `.2f`); `better: lower` marks a distance; `help` is the column's and the figure's tooltip. A benchmark that declares none looks as before. |
| `per_family` | Optional, `{key, label}`: a `reward.json` key whose metric depends on the task's family (RoboPaint's `final_reward`: F1, IoU or 1 − mean ΔE / 20). The Runs page shows success and the key's plain mean per family and mode, naming each family's metric from its tasks' upstream `continuous_score`. The home table shows its plain mean as *mean* `label`, with a note that the metric depends on the family. |
| `runs.<id>.batch` | The Harbor batch, as named for `robot_coding_bench/scripts/run_agent_batch.sh`. |
| `rerun_batches` | Later batches. For each task and mode, the last batch that has the job wins. The earlier result stays as history: in the pill's tooltip, and on a log page named `<mode>-prev`. |
| `rerun_all` | `true`: the last rerun batch reruns every task and mode. Until it starts a job, that job reads *rerun queued*, and the earlier result stays as history. |
| `tasks` | The task ids in the run. Each runs once per mode. |
| `removed` | Task id → why it is not in the run. These rows show grey. |
| `others` | Why every task in neither list is not in it. These rows keep their colour: the task was simply not built for the run. |
| `followups` | `{task, mode, trial, note}`: what is already arranged for one trial (a regrade, a rerun). The pill gets ↻. The note disappears by itself once another trial replaces that one. |
| `notes` | `{task, mode, trial, note}`: a note on one trial that is graded as it is, with nothing arranged (e.g. the agent ended itself). The pill gets ⓘ; the note shows under *ⓘ Notes* on the Runs page and on the trial's log page, never among the follow-ups. Like a follow-up, it is tied to that trial. |
| `closed` | Why the run is over. Its jobs that never started read *not run* instead of *queued*. |
| `harness` | Optional: how this benchmark's pages word the run's harness, in place of the `harness` of `data/agents/<run>.yml`. |
| `stopped` | `{task, mode, note}`: a trial we stopped ourselves before it finished, or kept from starting. It reads *stopped by us* with the note, keeps its log page, and counts in no statistic (no rate, mean, time, token or cost total). What the importer recorded stays as it was in `data/runs/`. |
| `hidden` | `true` keeps the run in the registry but off the site: no picker option, overview card, task pills or log pages, and `make runs` stops collecting it. Its entry, its `data/agents/` file and what was collected stay. The default run cannot be hidden. |
| `modes` | Only when this benchmark runs fewer modes than the run defines. |

RoboPaint (`state/runs/robopaint.yml`) declares its continuous scores this way:

```yaml
metrics:
- {key: final_reward, label: F1, format: ".3f"}
- {key: iou, label: IoU, format: ".3f"}
- {key: chamfer_paint_to_target_mm, label: "Chamfer paint→target", format: ".2f", unit: mm, better: lower, summary: median}
```

A task its benchmark's owner excluded from the final benchmark (`excluded:` in
`state/tasks/<benchmark>.yml`) stays in the run as registered here: its trials
are collected, its log pages built, and the run's table lists it last, under
*Excluded from the benchmark*. The numbers above the table count the benchmark's
own tasks; a *Count* switch adds the excluded ones. Nothing changes in
`data/runs/status.json`.

Both layouts of the runner are understood without configuration. `SEQ=1` makes
one Harbor job per task and mode (`<batch>-<mode>-<task dir>/`). `SEQ=0` makes one
job per mode with a trial per task (`<batch>-<mode>/`); there, each trial's task
is read from its `config.json`.

## 3. Say where your jobs are: `data/runs/hosts.<name>.local.yml`

```yaml
local:  {jobs: ../robot_coding_bench/jobs/agents}                # local: a path
gpu1:   {ssh: gpu1, jobs: /data/me/rcb_jobs/agents}              # remote: an ssh alias
gpu2:   {ssh: gpu2, jobs: /scratch/me/rcb/jobs/agents, benchmarks: [behavior-1k]}
```

The importer reads every `data/runs/hosts*.local.yml` file. These files are
gitignored. To limit what a host is searched for, add `benchmarks:` or `runs:`
to its entry. Every host runs the same read-only probe (see the docstring of
`scripts/import_runs.py`). The probe never opens a credential. The only thing it
writes is its own offset cache, in `~/.cache/` on that host.

A run appears on this machine only after one of its batches has left a trace (a
batch log or a job directory) on a host that answered. A colleague's run whose
machines you cannot see shows *no data here*, never all *queued*.

## 4. Collect, then look

```bash
make runs                              # once: every run; also brings every log page up to date
make runs-watch                        # every 3 minutes, writing only what changed
make runs RUNS="--benchmark robolab"   # only your benchmark (--run <id> works too)
.venv/bin/python scripts/import_runs.py --once --no-sync   # quick: states only, no rsync
```

A running `make serve` or `make edit` rebuilds when the collected data changes.

## A new benchmark and a second run: the whole change

Suppose *My Bench* is already registered as a benchmark. It runs an existing
configuration, and also a new one, Claude Code with Opus. The change adds three
files and edits no shared file. The one exception: to estimate the new model's
cost, add its list price to `data/prices.yml` once.

```yaml
# data/agents/claude-code-2.1-opus55-sub.yml
label: Claude Code 2.1 + Claude Opus 5.5 (subscription)
short: Claude Code 2.1 · Claude Opus 5.5 · adaptive · subscription
harness: Claude Code 2.1 (Harbor's claude-code agent)
model: anthropic/claude-opus-5-5
billing: subscription
price: anthropic/claude-opus-5-5     # only if data/prices.yml has it, else leave price out
modes: [unlimited]
```

```yaml
# state/runs/my-bench.yml
default: codex-0.157-gpt6luna-xhigh-cgpt
task_dir: "my-bench-{task_dashed}-i00"
runs:
  codex-0.157-gpt6luna-xhigh-cgpt:
    batch: mybench-lunaxh-1001
    tasks: [pick_cube, open_drawer]
    others: not built for the harness yet
  claude-code-2.1-opus55-sub:
    batch: mybench-cc-opus-1002
    tasks: [pick_cube]
    others: first try on one task
```

```yaml
# data/runs/hosts.me.local.yml (not committed)
mybox: {ssh: mybox, jobs: /data/me/jobs/agents, benchmarks: [my-bench]}
```

`make runs`, then `make check`. *Runs → My Bench* shows both runs behind its
picker. The overview gains the new run's row, and a *My Bench* row in the
benchmarks table. The task list gets a Run menu.

## Cost: estimates and bills are never one number

- **Tokens** come from the model gateway's log of every request: input
  including its cached part, output including its reasoning part. A harness
  without the gateway falls back to Harbor's own count, which has no reasoning
  split.
- **Est. cost** is those tokens at the list prices in `data/prices.yml`:
  (input − cached) × input + cached × cached input + output × output. It is an
  estimate. It is labelled so everywhere, and on a subscription login it is the
  only cost there is.
- **Billed** is what a provider says it charged. OpenRouter includes its charge
  in every response, and the probe sums it from the gateway log. Claude Code over
  OpenRouter (our adapter) keeps its per-generation charges in
  `agent/openrouter_costs.json`. A bill sits in its own column and is never added
  to an estimate.
- The site uses neither Harbor's `agent_result.cost_usd` nor the grader's
  `agent_cost_self_reported`. The first is a LiteLLM list-price estimate; the
  second is not in dollars.

## Publishing: `make publish-runs`

The public site shows the runs from a committed snapshot, `data/published_runs/`, never from the local data.
`make publish-runs` writes it by hand. It drops the machine, the job, the paths and the log checks of every trial,
redacts anything shaped like a credential, e-mail addresses and private IPs, and scans what it wrote before
switching it in. Hidden runs are left out. `make publish-runs BENCHMARK=<id>` rewrites only that benchmark's part and
keeps the others as they are; use it in a checkout that has only your benchmark's runs.

Replays and images live on the Hugging Face dataset `eai-v2-internal/agent-runs`, one folder per benchmark. To add
yours:

1. Log in with `hf auth login`, using your own account; it must be a member of the organisation.
2. Run `make upload-run-media BENCHMARK=<your benchmark>`. It exports, compresses and uploads only that folder.

The site repository never holds run media: `make guard`, part of `make check` and CI, fails if any are committed.
HANDOFF.md, "Publishing", has the whole flow.

## For scripts that poll: `data/runs/status.json`

This file keeps the shape it had when the site tracked a single sweep:
`benchmarks.<benchmark>.tasks.<task>.<mode>` holds a record with `state`, `host`,
`trial`, `reward` and `exception`, and `hosts.<host>` holds `ok`, `at` and
`error`. It holds every benchmark's **default** run and nothing else, so adding
an old or a colleague's run never changes what a watcher sees. Two keys are new,
`runs` (benchmark → default run) and `benchmarks.<benchmark>.run`. The
per-benchmark files carry the same records for every run.

## What `make check` checks

- Every run a benchmark names is registered in `data/agents/`.
- Its default is one of its runs.
- Every task named in a run exists, and none is both in the run and removed.
- Follow-ups and notes name a task in the run and a mode it has; a note also names its trial.
- Prices are numbers, and every `price:` key exists in `data/prices.yml`.
- `task_dir` fills in only `{benchmark}`, `{task}` and `{task_dashed}`.
- The build creates a Runs page for every benchmark in the registry, even one
  with no runs yet. It needs no collected data, so CI builds it as well.

"""How an agent run reads on the site: state names, the log checklist, times, tokens and cost.

Shared by the task list (scripts/gallery.py), the task pages (scripts/hooks.py) and the Runs pages
(scripts/gen_pages.py), so they always agree on what "done", "logs complete" or "cost" means. The
records come from scripts/import_runs.py (data/runs/<benchmark>/<run>.json), the runs from scripts/runsdb.py.
"""

from __future__ import annotations

import datetime as dt

import runsdb
import sitemode

# Order = how urgently a row wants attention; also the "Run state" sort order.
STATES = ["stalled", "error", "running", "grading", "setup", "failed", "success", "queued", "notrun", "stopped", "nodata"]
STATE_LABEL = {
    "stalled": "stalled", "error": "error", "running": "running", "grading": "grading",
    "setup": "setting up", "failed": "failed", "success": "success", "queued": "queued", "notrun": "not run",
    "stopped": "stopped by us",
    "nodata": "no data",
}
STATE_HELP = {
    "queued": "not started yet",
    "notrun": "not run: the run was closed before this job started",
    "stopped": "stopped by us before it finished, or kept from starting (state/runs/ `stopped:`): counted in no statistic",
    "nodata": "nothing collected for this run on this machine (its owner collects it: make runs)",
    "setup": "Harbor is building the trial's containers",
    "running": "the agent is working",
    "grading": "the agent is done; the collect hook and the separate verifier are replaying its trajectory",
    "success": "graded: success",
    "failed": "graded: no success",
    "error": "the trial ended without a grade (see the exception)",
    "stalled": "no harbor process is running this unfinished job any more",
}
ACTIVE = {"setup", "running", "grading"}
DONE = {"success", "failed", "error"}
MODE_SHORT = {"unlimited": "U", "limited": "L"}


def log_dir(benchmark: str, run: str, task: str, slot: str):
    """docs/assets/<benchmark>/runs/<run>/<task>/<slot>/: the log page's data (scripts/runlog.py)."""
    from taskdb import DOCS
    return DOCS / "assets" / benchmark / "runs" / run / task / slot


def has_log(benchmark: str, run: str, task: str, slot: str) -> bool:
    """Whether a trial has log page data: locally docs/assets/<b>/runs/<run>/<task>/<slot>/log.json; on the public
    site (scripts/sitemode.py) only the published snapshot counts, data/published_runs/<b>/<run>/<task>/<slot>.json,
    even on a machine that has the local data."""
    if sitemode.PUBLIC:
        return (runsdb.PUBLISHED / benchmark / run / task / f"{slot}.json").is_file()
    return (log_dir(benchmark, run, task, slot) / "log.json").is_file()


def log_page(benchmark: str, run: str, task: str, slot: str) -> str:
    """The log page's source path, docs-relative: runs/<benchmark>/<run>/<task>/<slot>.md."""
    return f"runs/{benchmark}/{run}/{task}/{slot}.md"


def runs_page(benchmark: str) -> str:
    """The benchmark's Runs page, docs-relative (?run=<id> picks a run on it)."""
    return f"runs/{benchmark}.md"


def parse(ts: str | None) -> dt.datetime | None:
    if not ts:
        return None
    try:
        return dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def local(ts: str | None) -> str:
    t = parse(ts)
    return t.astimezone().strftime("%m-%d %H:%M") if t else "—"


def minutes(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    m = round(seconds / 60)
    return f"{m // 60}h {m % 60:02d}m" if m >= 60 else f"{m}m"


def elapsed(rec: dict, now: dt.datetime | None = None) -> float | None:
    t = parse(rec.get("started"))
    if not t:
        return None
    return ((now or dt.datetime.now(dt.timezone.utc)) - t).total_seconds()


def tok(n) -> str:
    """12345678 -> 12.3M, 201106 -> 201k."""
    if n is None:
        return "—"
    n = float(n)
    return f"{n / 1e9:.2f}B" if n >= 1e9 else f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}k" if n >= 1e3 else f"{n:.0f}"


def usd(x: float | None) -> str:
    if x is None:
        return "—"
    return f"${x:,.2f}" if x >= 1 else f"${x:.3f}" if x >= 0.01 else f"${x:.4f}"


def progress_of(rec: dict) -> float | None:
    """A trial's progress in [0, 1], the partial credit beside success: 1.0 whenever its verdict is success, else the
    grader's own value (the benchmark's `progress:` key), if it wrote one.

    Every benchmark, one rule: a partial-credit key can say less than a success (RoboLab's final_reward is the
    fraction of scored subtasks, 0 for a task without any, e.g. mustard_above_raisin's regrade: success 1,
    final_reward 0.0; RoboPaint's F1 can stop at 0.9997). BEHAVIOR's q_score is 1 on success anyway.
    The collected records keep the grader's raw value; only what is shown and averaged follows this."""
    if rec.get("state") == "success":
        return 1.0
    p = rec.get("progress")
    return float(p) if isinstance(p, (int, float)) else None


def metric_value(rec: dict, m: dict) -> float | None:
    """One declared metric of a trial (runsdb.BenchRun.metrics), as the grader wrote it, or None."""
    v = (rec.get("metrics") or {}).get(m["key"])
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def metric_text(v: float | None, m: dict) -> str:
    if v is None:
        return "—"
    try:
        text = format(v, m.get("format") or ".2f")
    except (ValueError, TypeError):
        text = f"{v:.2f}"
    return text + (f" {m['unit']}" if m.get("unit") else "")


def metric_summary(values: list[float], m: dict) -> float | None:
    """The run's figure for a metric: the mean of its graded trials, or the median where the benchmark says so."""
    if not values:
        return None
    if m.get("summary") == "median":
        xs = sorted(values)
        mid = len(xs) // 2
        return xs[mid] if len(xs) % 2 else (xs[mid - 1] + xs[mid]) / 2
    return sum(values) / len(values)


def estimate(rec: dict, br: runsdb.BenchRun | None) -> float | None:
    """List-price estimate of one trial (runsdb.estimate_usd with the run's price); never a bill."""
    return runsdb.estimate_usd(rec.get("tokens"), br.price if br else None)


def log_checks(rec: dict, mode: str) -> list[tuple[str, bool | None, str]]:
    """(item, ok, detail) for every record this trial should have kept by now. ok None = not due yet.

    File sizes come from the probe: None means the file is absent, 0 an empty file (a grader's stderr log is
    usually empty). None on the public site (scripts/sitemode.py): the published records carry no log checks."""
    if sitemode.PUBLIC:
        return []
    state = rec.get("state", "queued")
    if state in ("queued", "notrun", "nodata"):
        return []
    lg = rec.get("logs") or {}
    n = lambda k: lg.get(k) or 0
    done = state in DONE
    started = state != "setup"           # the agent has not been launched while Harbor builds the trial
    out = [
        ("agent stream (codex.txt)", (n("codex") > 0) if started else None, f"{n('codex') / 1e3:.0f} kB"),
        ("model exchanges (gateway.jsonl)", (n("gateway") > 0) if started else None,
         f"{rec.get('calls') or 0} requests, {rec.get('calls_failed') or 0} failed"),
    ]
    behind = [k for k in ("codex", "gateway") if n(f"mirror_{k}") < n(k)]
    have = n("mirror_codex") > 0 and n("mirror_gateway") > 0
    if done:
        out.append(("append-only mirror", have and not behind, "in step" if not behind else "behind: " + ", ".join(behind)))
    elif started:
        out.append(("append-only mirror", have or None, "copying (5 s lag)" if behind else "in step"))
    if not done:
        return out
    rw = rec.get("reward") or {}
    # The agent never moved the robot (the grader counted 0 actions): there is nothing to log or replay.
    idle = rw.get("n_actions") == 0
    # Codex keeps its session inside the container; Harbor copies it out when the agent ends.
    out.append(("Codex session", n("sessions") > 0, f"{n('sessions')} file(s)"))
    out.append(("trajectory.json (ATIF)", n("trajectory") > 0, ""))
    if mode == "limited":
        if idle and not n("episode"):
            out.append(("robot call log (episode.jsonl)", None, "the agent sent no robot action"))
        else:
            out.append(("robot call log (episode.jsonl)", n("episode") > 0, ""))
    out.append(("grade (reward.json + grade.log)", n("reward") > 0 and lg.get("grade_log") is not None, ""))
    if rw.get("missing_trajectory"):
        out.append(("replay video", None, "no trajectory handed in"))
    elif idle and not n("video"):
        out.append(("replay video", None, "no robot action to replay"))
    elif lg.get("episode_end") == "error" and not n("video"):
        out.append(("replay video", None, "the live episode ended with a simulator error: nothing to replay"))
    elif n("video") and lg.get("video_ok") is False:
        out.append(("replay video", False, f"truncated at the source ({n('video') / 1e6:.1f} MB, no MP4 index): cannot play"))
    else:
        out.append(("replay video", n("video") > 0, f"{n('video') / 1e6:.1f} MB"))
    scan = rec.get("scan")
    out.append(("key scan", None if scan is None else True,
                "pending" if scan is None else ("clean" if scan == 0 else f"{scan} file(s) redacted")))
    return out


def logs_state(rec: dict, mode: str) -> tuple[str, list[str]]:
    """'ok' | 'missing' | 'n/a', and the items that are missing."""
    checks = log_checks(rec, mode)
    if not checks:
        return "n/a", []
    missing = [name for name, ok, _ in checks if ok is False]
    return ("missing" if missing else "ok"), missing


def result_label(rec: dict) -> str:
    """A few characters for a pill: ✓ 15m, ✗ 1h 02m, running 23m, queued, rerun queued; ↻ = a follow-up is arranged."""
    state = rec.get("state", "queued")
    mark = " ↻" if rec.get("followup") else ""
    if state == "success":
        return "✓ " + minutes(rec.get("agent_wall_s")) + mark
    if state == "failed":
        pr = progress_of(rec)
        return "✗ " + minutes(rec.get("agent_wall_s")) + (f" {round(100 * pr)}%" if isinstance(pr, (int, float)) else "") + mark
    if state == "queued" and rec.get("rerun"):
        return "rerun queued"
    return STATE_LABEL.get(state, state) + mark


def title(rec: dict, mode: str, br: runsdb.BenchRun | None = None) -> str:
    """Tooltip text for a run pill."""
    state = rec.get("state", "queued")
    help_ = "rerun queued: this batch reruns every job" if state == "queued" and rec.get("rerun") else STATE_HELP.get(state, state)
    bits = [(f"{br.short} · " if br else "") + f"{mode}: {help_}"]
    if rec.get("host"):
        bits.append(f"host {rec['host']}, started {local(rec.get('started'))}")
    if rec.get("calls") is not None:
        bits.append(f"{rec['calls']} model requests ({rec.get('calls_failed') or 0} failed), last {local(rec.get('last_call'))}")
    t = rec.get("tokens") or {}
    if t.get("input") is not None:
        est = estimate(rec, br)
        bits.append(f"tokens {tok(t['input'])} in ({tok(t.get('cached'))} cached), {tok(t.get('output'))} out"
                    + (f"; est. {usd(est)} at list price" if est is not None else "")
                    + (f"; billed {usd(rec['billed_usd'])}" if rec.get("billed_usd") is not None else ""))
    rw = rec.get("reward") or {}
    if br is not None and br.metrics and rec.get("metrics"):
        bits.append(", ".join(f"{m['label']} {metric_text(metric_value(rec, m), m)}" for m in br.metrics
                              if metric_value(rec, m) is not None))
    prog = progress_of(rec)
    if prog is not None:
        raw = rec.get("progress")
        why = (f"a success counts as full progress; the grader's own value was {raw:.2f}" if state == "success"
               and isinstance(raw, (int, float)) and raw != 1 else
               "a success counts as full progress" if state == "success" else
               "BEHAVIOR: the 2026 challenge's q_score, the share of the goal's conditions that hold at the end of the "
               "replay; elsewhere the grader's final_reward")
        bits.append(f"progress {prog:.2f} ({why})")
    if rw:
        bits.append(", ".join(f"{k}={v}" for k, v in rw.items()))
    if rec.get("exception"):
        bits.append(f"exception {rec['exception']}")
    if rec.get("stale"):
        bits.append("its machine did not answer: last known state")
    if rec.get("regraded"):
        bits.append("regraded: the verifier's first grading failed (GPU out of memory); the trajectory was replayed again")
    sup = rec.get("supersedes")
    if sup:  # a rerun batch (`rerun_batches`), e.g. the particle tasks on the GPU backend
        why = f", {sup['exception']}" if sup.get("exception") else ""
        # the published records (the public site) name no machine and no job, only the trial
        on = f" on {sup['host']}" if sup.get("host") else ""
        ref = sup.get("job") or sup.get("trial") or "an earlier batch"
        if state == "queued":
            bits.append(f"previous run: {sup.get('state')}{on}{why} ({ref}), kept as history")
        else:
            bits.append(f"rerun of {ref} ({sup.get('state')}{on}{why})")
    if rec.get("followup"):
        bits.append(f"follow-up: {rec['followup']}")
    if rec.get("stopped"):
        bits.append(f"stopped by us: {rec['stopped']} (counted in no statistic)")
    return " · ".join(bits)


OUT_LABEL = {"outside": "not in run", "removed": "removed"}


def run_group(view: dict | None) -> int:
    """Default row order: tasks in the run (or no run at all) first, then the ones not built for it, removed last."""
    if not view or view["in"]:
        return 0
    return 2 if view.get("removed") else 1


DIFFICULTY_ORDER = ["easy", "medium", "hard", "extreme", "unrated"]


def default_rank(view: dict | None, status: str, difficulty: str, excluded: bool = False) -> list[int]:
    """The default row order, key by key (user, 2026-09-25), for the run on show:
      0. tasks excluded from the benchmark (state `excluded:`, owner 2026-09-28: "放到展示的最下面") go last;
      1. whether it runs: in the run, then not built for it, then removed. A benchmark with no run uses its
         review decision the same way: keep, then undecided, then drop;
      2. how much of it has finished: more modes done first;
      3. whether it is running: more modes running first;
      4. difficulty, easy to extreme.
    Compared as a list; the title breaks ties."""
    if view is None:
        group = {"keep": 0, "drop": 2}.get(status, 1)
        done = active = 0
    elif not view["in"]:
        group, done, active = run_group(view), 0, 0
    else:
        states = [m.get("state", "queued") for m in view["modes"].values()]
        group = 0
        done = sum(s in DONE for s in states)
        active = sum(s in ACTIVE or s == "stalled" for s in states)
    diff = DIFFICULTY_ORDER.index(difficulty) if difficulty in DIFFICULTY_ORDER else len(DIFFICULTY_ORDER)
    return [int(bool(excluded)), group, -done, -active, diff]


def task_tags(view: dict | None) -> list[str]:
    """The Run state facet values a task matches: its modes' states, or 'outside' / 'removed'."""
    if not view:
        return []
    if not view["in"]:
        return ["removed" if view.get("removed") else "outside"]
    return sorted({m.get("state", "queued") for m in view["modes"].values()}, key=STATES.index)


def task_rank(view: dict | None) -> int:
    """Sort key for the "Run state" order: the most urgent mode first, removed tasks last."""
    tags = task_tags(view)
    if not tags:
        return len(STATES) + 2
    if tags in (["outside"], ["removed"]):
        return len(STATES) + (tags == ["removed"])
    return min(STATES.index(t) for t in tags)


def pill_html(mode: str, rec: dict, now: dt.datetime | None = None, href: str | None = None,
              br: runsdb.BenchRun | None = None) -> str:
    """The same pill the task list draws, rendered at build time (running minutes as of the build); a link to the
    run's log page when `href` is given."""
    import html
    state = rec.get("state", "queued")
    live = state in ACTIVE and rec.get("started")
    since = f' <span data-since>{minutes(elapsed(rec, now))}</span>' if live else ""
    logs, missing = logs_state(rec, mode)
    tail = "" if logs == "n/a" else (
        f'<i class="rpill__logs rpill__logs--{logs}" title="'
        + html.escape("logs saved so far: complete" if logs == "ok" else "missing: " + ", ".join(missing))
        + f'">{"logs ✓" if logs == "ok" else "logs !"}</i>')
    # Pipes would split the Markdown table cell this pill sits in.
    started = f' data-started="{html.escape(rec["started"])}"' if live else ""
    tag, link = ("a", f' href="{html.escape(href)}"') if href else ("span", "")
    return (f'<{tag} class="rpill rpill--{state}"{link}{started} title="{html.escape(title(rec, mode, br))}">'
            f'<b>{MODE_SHORT.get(mode, mode[:1].upper())}</b>{html.escape(result_label(rec))}{since}{tail}</{tag}>'
            ).replace("|", "&#124;")


# ------------------------------------------------------------------------------------------------ totals


def agent_seconds(rec: dict, now: dt.datetime | None = None) -> tuple[float, float]:
    """(finished, so far): a finished trial's agent time, or how long an active one has been going."""
    state = rec.get("state", "queued")
    if state in DONE and rec.get("agent_wall_s") is not None:
        return float(rec["agent_wall_s"]), 0.0
    if state in ACTIVE:
        return 0.0, max(0.0, elapsed(rec, now) or 0.0)
    return 0.0, 0.0


def totals(pairs: list[tuple[runsdb.BenchRun, dict]], now: dt.datetime | None = None) -> dict:
    """What a set of trials adds up to: counts per state and mode, success, progress, time, tokens, cost.

    `pairs` = (the benchmark's run, one mode's record) for every task in scope and mode. Trials of a run this machine
    has no data for ("nodata") are counted apart, never as queued. Estimates and bills are summed apart and never
    into one number; `est_n` / `billed_n` say how many trials each covers."""
    nodata = sum(1 for _, rec in pairs if rec.get("state") == "nodata")
    # trials we stopped ourselves (`stopped:`) count in no statistic: not in the trials, rates, means, time or cost
    stopped = sum(1 for _, rec in pairs if rec.get("state") == "stopped")
    pairs = [(br, rec) for br, rec in pairs if rec.get("state") not in ("nodata", "stopped")]
    out = {"trials": len(pairs), "nodata": nodata, "stopped": stopped, "states": {}, "modes": {}, "done": 0, "success": 0, "progress_sum": 0.0,
           "progress_n": 0, "agent_s": 0.0, "agent_s_live": 0.0, "calls": 0, "input": 0, "cached": 0, "output": 0,
           "reasoning": 0, "tokens_n": 0, "est": 0.0, "est_n": 0, "billed": 0.0, "billed_n": 0, "reruns": 0,
           "followups": 0, "stale": 0}
    for br, rec in pairs:
        state = rec.get("state", "queued")
        out["states"][state] = out["states"].get(state, 0) + 1
        m = out["modes"].setdefault(rec.get("_mode", ""), {"trials": 0, "done": 0, "success": 0})
        m["trials"] += 1
        if state in DONE:
            out["done"] += 1
            m["done"] += 1
            prog = progress_of(rec)
            if prog is not None:
                out["progress_sum"] += prog
                out["progress_n"] += 1
        if state == "success":
            out["success"] += 1
            m["success"] += 1
        if state == "queued" and rec.get("rerun"):
            out["reruns"] += 1
        if rec.get("followup"):
            out["followups"] += 1
        if rec.get("stale"):
            out["stale"] += 1
        fin, live = agent_seconds(rec, now)
        out["agent_s"] += fin
        out["agent_s_live"] += live
        out["calls"] += rec.get("calls") or 0
        t = rec.get("tokens") or {}
        if t.get("input") is not None:
            out["tokens_n"] += 1
            for k in ("input", "cached", "output", "reasoning"):
                out[k] += t.get(k) or 0
        est = estimate(rec, br)
        if est is not None:
            out["est"] += est
            out["est_n"] += 1
        if rec.get("billed_usd") is not None:
            out["billed"] += rec["billed_usd"]
            out["billed_n"] += 1
    return out


def mode_records(br: runsdb.BenchRun, task: str) -> list[tuple[str, dict]]:
    """(mode, record) of one task in one run, [] when the task is not in it; each record carries `_mode`."""
    view = br.view(task)
    if not view["in"]:
        return []
    return [(m, {**r, "_mode": m}) for m, r in view["modes"].items()]

"""The Runs section: an overview across benchmarks, one page per benchmark, one log page per started trial.

Generated at build time by scripts/gen_pages.py for every benchmark in the registry, from the run registry
(scripts/runsdb.py: data/agents/, state/runs/) and what scripts/import_runs.py collected (data/runs/). Nothing here
is per benchmark: a benchmark that registers a run appears on every page below by itself.

    runs/overview.md                          every run, every benchmark: progress, time, tokens, cost, hosts
    runs/index.md                             a redirect to the overview (the one-sweep page lived at /runs/)
    runs/<benchmark>.md                       that benchmark's runs, one at a time (a picker, ?run=<id>)
    runs/<benchmark>/<run>/<task>/<slot>.md   a trial's log page (javascripts/runlog.js draws it)

Layout (owner, 2026-09-28: "粗粗看字太多了"): a page opens on a few numbers you can read at a glance, drawn rather
than written — one stacked bar per mode in the state pills' colours, mean progress, agent time, and one line of
tokens and cost. Everything else stays one click away: "How to read this page", "Run details", the full table.
Pages are HTML inside Markdown, so every link is a finished URL relative to the page's output URL; the picker, the
table's filters and its sort are javascripts/runs.js, the look stylesheets/runs.css.

Tasks a benchmark's owner excluded from the final benchmark (state `excluded:`, owner 2026-09-28: "我们仍然可以在 runs…
去展示它") keep their trials here: last in a run's table under "Excluded from the benchmark", and apart in the numbers,
which count the benchmark's own tasks; a "Count" switch adds the excluded ones (a run without any has no switch).
"""

from __future__ import annotations

import datetime as dt
import html
import json

import runsdb
import runview
import sitemode
import taskdb

E = html.escape
REG = "contributing/registering-runs.md"         # docs-relative; every runs/*.md page is two levels deep
# What a run without collected data says: locally, nothing was collected on this machine; on the public site, which
# carries no collected data (data/runs/ is local only; scripts/sitemode.py), its results are not published.
NO_DATA = "not published" if sitemode.PUBLIC else "no data here"

# The bars' segments, in order, with the pills' colours (stylesheets/runs.css .st-<key>): key, label, states.
SEGMENTS = [
    ("success", "success", {"success"}),
    ("failed", "failed", {"failed"}),
    ("error", "error / stalled", {"error", "stalled"}),
    ("running", "running", {"running", "setup"}),
    ("grading", "grading", {"grading"}),
    ("queued", "queued", {"queued"}),
    ("notrun", "not run", {"notrun"}),
]
SEGMENT_OF = {s: key for key, _, states in SEGMENTS for s in states}


def url(md_path: str, root: str) -> str:
    """A docs-relative .md path as a link from raw HTML on a page whose output URL is `root` deep."""
    if md_path.endswith("/index.md"):
        md_path = md_path[: -len("index.md")]
    elif md_path.endswith(".md"):
        md_path = md_path[: -len(".md")] + "/"
    return root + md_path


def _pct(a: int, b: int) -> str:
    return f"{100 * a / b:.0f}%" if b else "—"


def _hours(s: float) -> str:
    return f"{s / 3600:,.1f} h" if s else "—"


def _hosts(hosts: dict) -> str:
    """One chip per host: green when it answered, red with the error when it did not."""
    if not hosts:
        return ""
    return "".join(
        f'<span class="hchip hchip--{"ok" if st.get("ok") else "down"}" title="'
        + E(("answered " if st.get("ok") else "did not answer: " + (st.get("error") or "") + "; last answer ")
            + runview.local(st.get("at"))) + f'">{E(h)}</span>'
        for h, st in sorted(hosts.items()))


def _pairs(br: runsdb.BenchRun, bench: taskdb.Benchmark, scope: str = "bench") -> list[tuple[runsdb.BenchRun, dict]]:
    """(run, record) of every trial of the run's tasks in `scope`: "bench" the benchmark's own tasks, "excluded" the
    ones excluded from it (state `excluded:`), "all" both."""
    known = {t.task_id for t in bench.tasks}
    excl = {t.task_id for t in bench.excluded}
    return [(br, rec) for tid in br.tasks if tid in known and (scope == "all" or (tid in excl) == (scope == "excluded"))
            for _, rec in runview.mode_records(br, tid)]


def _split(br: runsdb.BenchRun, bench: taskdb.Benchmark) -> tuple[int, int]:
    """How many of the run's tasks are the benchmark's own, and how many are excluded from it."""
    known = {t.task_id for t in bench.tasks}
    excl = {t.task_id for t in bench.excluded}
    mine = [t for t in br.tasks if t in known]
    return len([t for t in mine if t not in excl]), len([t for t in mine if t in excl])


def _billed_text(br: runsdb.BenchRun, tot: dict) -> str:
    """The provider's charge, summed apart from the estimate; 'none' on a subscription login."""
    if tot["billed_n"]:
        return runview.usd(tot["billed"]) + (f" ({tot['billed_n']} of {tot['tokens_n']} trials)"
                                             if tot["billed_n"] < tot["tokens_n"] else "")
    return "none (subscription)" if br.billing == "subscription" else "—"


def _segments(recs: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in recs:
        key = SEGMENT_OF.get(r.get("state", "queued"))
        if key:
            out[key] = out.get(key, 0) + 1
    return out


# ------------------------------------------------------------------------------------------- drawn pieces


def sbar(counts: dict[str, int], small: bool = False) -> str:
    """A stacked bar: one segment per state group, as wide as its count, in the pills' colours."""
    total = sum(counts.values())
    if not total:
        return f'<div class="sbar{" sbar--sm" if small else ""} sbar--empty" role="img" aria-label="no trials"></div>'
    label = ", ".join(f"{counts[k]} {lab}" for k, lab, _ in SEGMENTS if counts.get(k))
    segs = "".join(f'<i class="st-{k}" style="flex-grow:{counts[k]}" title="{counts[k]} {lab}"></i>'
                   for k, lab, _ in SEGMENTS if counts.get(k))
    return f'<div class="sbar{" sbar--sm" if small else ""}" role="img" aria-label="{E(label)}">{segs}</div>'


def legend(counts: dict[str, int]) -> str:
    return '<span class="slegend">' + "".join(
        f'<span><i class="st-{k}"></i>{counts[k]} {lab}</span>' for k, lab, _ in SEGMENTS if counts.get(k)) + "</span>"


def kpis(pairs: list, modes: list[str], progress_note: str, now: dt.datetime, withdrawn: dict | None = None) -> str:
    """The glanceable numbers of a set of trials: a stacked bar per mode, mean progress, agent time. A mode whose
    results are withdrawn (`withdrawn:` in state/runs/) says so instead of numbers."""
    tot = runview.totals(pairs, now)
    out = []
    for mode in modes:
        if withdrawn and mode in withdrawn:
            w = withdrawn[mode]
            out.append(
                f'<div class="kpi kpi--mode kpi--withdrawn" title="{E(w["note"])}">'
                f'<div class="kpi__top"><span class="kpi__name">{E(mode.capitalize())}</span>'
                f'<span class="kpi__value kpi__value--off">withdrawn</span></div>'
                f'<div class="kpi__sub">{E(w["label"])}</div></div>')
            continue
        recs = [r for _, r in pairs if r.get("_mode") == mode and r.get("state") not in ("nodata",) + runview.UNCOUNTED]
        counts = _segments(recs)
        succ, done = counts.get("success", 0), sum(1 for r in recs if r.get("state") in runview.DONE)
        out.append(
            '<div class="kpi kpi--mode">'
            f'<div class="kpi__top"><span class="kpi__name">{E(mode.capitalize())}</span>'
            f'<span class="kpi__value">{succ}<span class="kpi__of"> / {len(recs)} success</span></span></div>'
            + sbar(counts) +
            f'<div class="kpi__sub">{legend(counts)}<span class="kpi__rate" title="success among graded trials">'
            f"{done} done · {_pct(succ, done)}</span></div></div>")
    mean = tot["progress_sum"] / tot["progress_n"] if tot["progress_n"] else None
    side = []
    side.append(
        '<div class="kpi kpi--num">'
        f'<div class="kpi__top"><span class="kpi__name">Mean progress</span>'
        f'<span class="kpi__value">{f"{mean:.2f}" if mean is not None else "—"}</span></div>'
        f'<div class="pbar" role="img" aria-label="mean progress {mean if mean is not None else 0:.2f} of 1">'
        f'<i style="width:{100 * (mean or 0):.1f}%"></i></div>'
        f'<div class="kpi__sub">{E(progress_note)} · {tot["progress_n"]} graded</div></div>')
    side.append(
        '<div class="kpi kpi--num">'
        f'<div class="kpi__top"><span class="kpi__name">Agent time</span><span class="kpi__value">{_hours(tot["agent_s"])}</span></div>'
        f'<div class="kpi__sub">finished trials{f" · + {_hours(tot["agent_s_live"])} running" if tot["agent_s_live"] else ""}</div></div>')
    # one column per mode, then the two numbers stacked in a narrower column
    return (f'<div class="kpis" style="--modes:{len(modes)}">' + "".join(out)
            + '<div class="kpi-side">' + "".join(side) + "</div></div>")


def cost_line(tot: dict, br: runsdb.BenchRun | None, price_note: str = "") -> str:
    """Requests, tokens, the list-price estimate and the bill, on one line; the two costs never added up."""
    if not tot["tokens_n"]:
        return '<p class="costline">no token counts yet</p>'
    reasoning = f" <small>({runview.tok(tot['reasoning'])} reasoning)</small>" if tot["reasoning"] else ""
    billed = _billed_text(br, tot) if br else (runview.usd(tot["billed"]) if tot["billed_n"] else "—")
    return (
        '<p class="costline">'
        f'<span title="model requests through the gateway">{tot["calls"]:,} requests</span>'
        f'<span>{runview.tok(tot["input"])} in <small>({_pct(tot["cached"], tot["input"])} cached)</small></span>'
        f'<span>{runview.tok(tot["output"])} out{reasoning}</span>'
        f'<span class="costline__est" title="{E("tokens at the list prices in data/prices.yml: an estimate, never a bill" + price_note)}">'
        f'≈ {runview.usd(tot["est"]) if tot["est_n"] else "—"} <small>at list price</small></span>'
        f'<span title="what the provider charged, where it says; never added to the estimate">billed: {E(billed)}</span>'
        "</p>")


def metric_strip(pairs: list, metrics: list[dict]) -> str:
    """The run's figure for each declared metric (state/runs/<b>.yml `metrics:`) over its graded trials; "" if none."""
    if not metrics:
        return ""
    graded = [r for _, r in pairs if r.get("state") in runview.DONE]
    cards = []
    for m in metrics:
        vals = [v for v in (runview.metric_value(r, m) for r in graded) if v is not None]
        main = runview.metric_summary(vals, m)
        other = runview.metric_summary(vals, {**m, "summary": "mean" if m["summary"] == "median" else "median"})
        per_mode = " · ".join(
            f"{mode} {runview.metric_text(runview.metric_summary(mv, m), m)}"
            for mode in dict.fromkeys(r.get("_mode") for r in graded)
            if (mv := [v for v in (runview.metric_value(r, m) for r in graded if r.get("_mode") == mode) if v is not None]))
        tip = (m["help"] + " · " if m["help"] else "") + per_mode
        cards.append(
            f'<div class="mcard" title="{E(tip)}{" · lower is better" if m["better"] == "lower" else ""}">'
            f'<span>{E(m["label"])}</span><b>{E(runview.metric_text(main, m))}</b>'
            f'<i>{m["summary"]}{f" · {"mean" if m["summary"] == "median" else "median"} {runview.metric_text(other, m)}" if vals else ""}'
            f' · {len(vals)} graded</i></div>')
    return '<div class="mstrip"><span class="mstrip__label">Grader metrics</span><div class="mcards">' + "".join(cards) + "</div></div>"


def family_scores(br: runsdb.BenchRun, bench: taskdb.Benchmark, scope: str = "bench") -> dict[str, dict]:
    """family -> {tasks, metric: [continuous_score, ...], excluded, modes: {mode: {done, success, values}}} for a
    benchmark whose score depends on the task family (`per_family:`); the family and its metric are the tasks' upstream
    `family` and `continuous_score`. Graded trials only; a trial we stopped counts in none of it."""
    pf = br.per_family
    excl = {t.task_id for t in bench.excluded}
    fams: dict[str, dict] = {}
    for t in bench.tasks:
        if not pf or t.task_id not in br.tasks:
            continue
        if scope != "all" and (t.task_id in excl) != (scope == "excluded"):
            continue
        f = fams.setdefault(str(t.upstream.get("family") or "other"),
                            {"tasks": 0, "metric": [], "excluded": t.task_id in excl, "modes": {}, "scene": t.scene})
        f["tasks"] += 1
        cs = str(t.upstream.get("continuous_score") or "")
        if cs and cs not in f["metric"]:
            f["metric"].append(cs)
        for mode, rec in runview.mode_records(br, t.task_id):
            md = f["modes"].setdefault(mode, {"done": 0, "success": 0, "values": []})
            if rec.get("state") not in runview.DONE:
                continue
            md["done"] += 1
            md["success"] += rec.get("state") == "success"
            v = runview.metric_value(rec, {"key": pf["key"]})
            if v is not None:
                md["values"].append(v)
    # the excluded families last; else in the order of the benchmark's scenes (data/benchmarks/<b>.yml; RoboPaint has
    # one per family), then by name
    scenes = list(bench.meta.get("scenes") or [])
    rank = lambda kv: (kv[1]["excluded"], scenes.index(kv[1]["scene"]) if kv[1]["scene"] in scenes else len(scenes), kv[0])
    return dict(sorted(fams.items(), key=rank))


def family_table(br: runsdb.BenchRun, bench: taskdb.Benchmark, scope: str) -> str:
    """Success and the plain mean of the family-specific score (`per_family:`), per task family and mode, with the
    metric that score is in each family. "" when the benchmark declares no such score."""
    pf = br.per_family
    fams = family_scores(br, bench, scope) if pf else {}
    if not fams:
        return ""
    rows = []
    for fam, f in fams.items():
        cells = [f"{E(fam.capitalize())}" + (' <span class="pill pill--excluded">excluded</span>' if f["excluded"] else ""),
                 str(f["tasks"]), E(" / ".join(f["metric"]) or "—")]
        for mode in br.modes:
            md = f["modes"].get(mode) or {}
            vals = md.get("values") or []
            cells.append(f'<b>{md["success"]}/{md["done"]}</b> <small>{_pct(md["success"], md["done"])}</small>'
                         if md.get("done") else "—")
            cells.append(f"{sum(vals) / len(vals):.3f}" if vals else "—")
        rows.append(cells)
    head = ["Family", "Tasks", f"Its {E(pf['label'])} is"] + [
        h for mode in br.modes for h in (f"{E(mode.capitalize())}: success", f"mean {E(pf['label'])}")]
    return ('<div class="mstrip"><span class="mstrip__label">By family</span></div>'
            f'<p class="rnote-lead">The grader\'s {E(pf["label"])} depends on the task family: the metric in the third '
            f"column. Each mean is the plain mean over the graded trials, a success at its own value.</p>"
            + _table(head, rows, "runs-sum runs-family"))


def issue_chips(tot: dict, pairs: list, hosts: dict, filterable: bool, followups: bool = True) -> str:
    """Only what needs a look, and only when there is some: a warning chip each; on a runs page it filters the table."""
    broken = tot["states"].get("error", 0) + tot["states"].get("stalled", 0)
    missing = sum(1 for _, r in pairs if r.get("state") not in ("stalled", "error", "nodata")
                  and runview.logs_state(r, r["_mode"])[0] == "missing")
    chips = []

    def chip(kind: str, text: str, f: str = "", title: str = "") -> None:
        tip = f' title="{E(title)}"' if title else ""
        if f and filterable:        # a button that filters the table below to these tasks
            chips.append(f'<button type="button" class="ichip ichip--{kind}" data-rt-filter="{f}"{tip}>{text}</button>')
        else:
            chips.append(f'<span class="ichip ichip--{kind}"{tip}>{text}</span>')

    if broken:
        chip("warn", f"⚠ {broken} ended without a grade", "error", "grading failed, or no harbor process is left for an unfinished job")
    if missing:
        chip("warn", f"⚠ {missing} with records missing", "logs", "a trial whose logs, mirror, replay or grade are not all kept")
    if tot["followups"] and followups:
        chip("info", f"↻ {tot['followups']} follow-up{'s' if tot['followups'] > 1 else ''} arranged", "followup")
    if tot["stale"]:
        chip("warn", f"⏸ {tot['stale']} last known (host silent)", "stale", "its host did not answer: the last state it reported")
    if tot["reruns"]:
        chip("info", f"{tot['reruns']} reruns queued", "queued")
    if tot.get("stopped"):
        chip("info", f"⏹ {tot['stopped']} stopped by us, not counted", "stopped",
             "trials we stopped before they finished, or kept from starting (state/runs/ `stopped:`): in no statistic")
    if tot.get("uncounted"):
        chip("info", f"⊘ {tot['uncounted']} not counted", "uncounted",
             "trials that ran but whose result does not count, each with its reason (state/runs/ `not_counted:`): "
             "in no statistic")
    for h, st in sorted((hosts or {}).items()):
        if not st.get("ok"):
            chip("down", f"✗ {E(h)} did not answer", "", st.get("error") or "")
    return f'<div class="ichips">{"".join(chips)}</div>' if chips else ""


# ------------------------------------------------------------------------------------------ the picker

PART_NAMES = ["harness", "model", "reasoning effort", "access"]     # the four parts of a run's `short` label


def _parts(label: str) -> list[str]:
    return [x.strip() for x in label.split("·") if x.strip()]


def picker(options: list[tuple[str, str, str, list[str]]], default: str, hint: str) -> str:
    """The "Agent run" selector: a labelled row of segmented buttons, one per run (id, text, full label, tags).

    A control, not a card: no numbers in it, the selected run in the primary colour. Each run's text names its
    setting part by part (harness · model · reasoning effort · access), and the parts in which the runs differ are
    emphasised. It is there even with a single run, so every page looks the same. javascripts/runs.js makes the
    buttons switch the run shown below (?run=<id>)."""
    parted = [_parts(text) for rid, text, _, _ in options if rid]
    differ = set()
    if len(parted) > 1 and len({len(x) for x in parted}) == 1:
        differ = {i for i in range(len(parted[0])) if len({x[i] for x in parted}) > 1}
    buttons = []
    for rid, text, full, tags in options:
        parts = _parts(text) if rid else [text]
        shown = " · ".join(f'<em>{E(x)}</em>' if i in differ else E(x) for i, x in enumerate(parts))
        badges = "".join(f'<span class="rpick__tag rpick__tag--{t}">{E(t)}</span>' for t in tags)
        on = " is-on" if rid == default else ""
        buttons.append(f'<a class="rpick__opt{on}" href="?run={E(rid)}" data-run="{E(rid)}" role="tab" title="{E(full)}">'
                       f'<span class="rpick__dot" aria-hidden="true"></span><span class="rpick__text">{shown}</span>{badges}</a>')
    single = " rpick--single" if len(options) == 1 else ""
    ids = {rid for rid, _, _, _ in options}
    known = {old: new for old, new in runsdb.aliases().items() if new in ids}
    alias = f" data-aliases='{E(json.dumps(known, separators=(',', ':')))}'" if known else ""
    return (f'<nav class="rpick{single}" data-runsel data-default="{E(default)}"{alias} aria-label="Agent run">'
            '<span class="rpick__label">Agent run</span>'
            f'<span class="rpick__seg" role="tablist">{"".join(buttons)}</span>'
            f'<span class="rpick__hint">{hint}</span></nav>')


def _differ_hint(runs: list[runsdb.BenchRun]) -> str:
    parted = [_parts(br.short) for br in runs]
    if len(runs) < 2:
        return ""
    names = []
    if len({len(x) for x in parted}) == 1 and len(parted[0]) == len(PART_NAMES):
        names = [PART_NAMES[i] for i in range(len(PART_NAMES)) if len({x[i] for x in parted}) > 1]
    return f"{len(runs)} runs with different settings" + (f": {', '.join(names)}" if names else "")


# ------------------------------------------------------------------------------- the "Count" switch


def scoped(blocks: dict[str, str], n_bench: int, n_excl: int, hint: str) -> str:
    """The numbers of a run (or a run's card) for the benchmark's own tasks, and, when some of the run's tasks are
    excluded from the benchmark, the same numbers including them behind a "Count" switch (javascripts/runs.js).

    `blocks` maps "bench" and "all" to their HTML. The benchmark's own tasks are counted by default; with no excluded
    task in the run there is no switch and the page reads as it always did."""
    if not n_excl:
        return blocks["bench"]
    opts = "".join(
        f'<button type="button" class="rscope__opt{" is-on" if key == "bench" else ""}" data-scope="{key}" '
        f'aria-pressed="{"true" if key == "bench" else "false"}" title="{E(tip)}">{text} <b>{n}</b></button>'
        for key, text, n, tip in (
            ("bench", "benchmark tasks", n_bench, "the benchmark's own tasks: what its numbers are"),
            ("all", "incl. excluded", n_bench + n_excl, "the tasks excluded from the benchmark too (state `excluded:`), "
                                                        "whose trials stay on the site for the record")))
    switch = (f'<div class="rscope" data-scope-switch><span class="rscope__label">Count</span>'
              f'<span class="rscope__seg">{opts}</span><span class="rscope__hint">{hint}</span></div>')
    return (switch + f'<div class="rscope-block" data-scope-block="bench">{blocks["bench"]}</div>'
            f'<div class="rscope-block" data-scope-block="all" hidden>{blocks["all"]}</div>')


def _only_excluded(n_excl: int) -> str:
    return (f'<div class="rempty">No task of the benchmark proper in this run yet: its {n_excl} task'
            f'{"s are" if n_excl > 1 else " is"} excluded from the benchmark. '
            '<button type="button" class="rempty__go" data-scope-go="all">Count them</button></div>')


# ----------------------------------------------------------------------------------- the benchmark page


def run_details(br: runsdb.BenchRun, bench: taskdb.Benchmark) -> str:
    """Everything about the run that is not a number: collapsed."""
    a = br.agent
    known = {t.task_id for t in bench.tasks}
    n_own, n_x = _split(br, bench)
    n_rm = len([t for t in br.removed if t in known])
    # a benchmark may word the harness its own way for its pages (`harness:` on its run in state/runs/<b>.yml)
    rows = [("Harness", E(str(br.spec.get("harness") or a.get("harness") or "—"))),
            ("Model", f"<code>{E(str(a.get('model') or '—'))}</code>")]
    if a.get("route"):      # the route or login: in the run's file, not in its id
        rows.append(("Route", E(str(a["route"]))))
    rows += [
            ("Settings", E(", ".join(f"{k} {v}" for k, v in (a.get("settings") or {}).items()) or "—")),
            ("Modes", E(", ".join(br.modes))),
            ("Batches", " ".join(f"<code>{E(b)}</code>" for b in br.batches) + (
                ("<br><small>The last batch reruns every task and mode; an earlier result stays as history, in its pill's "
                 "tooltip and on a <i>previous</i> log page.</small>" if br.rerun_all else
                 "<br><small>A later batch replaces an earlier one's run of the tasks it reruns; the earlier one stays "
                 "as history.</small>") if len(br.batches) > 1 else "")),
            ("Scope", f"{n_own} tasks in the run" + (f" + {n_x} excluded from the benchmark (last in the table)" if n_x else "")
                      + f" · {len(known) - n_own - n_x - n_rm} not in it · {n_rm} removed (lists at the end)"),
            ("Progress", E(("the 2026 challenge's q_score: the share of the goal's conditions that hold at the end of the "
                            "replay" if br.progress_key == "q_score" else f"the grader's {br.progress_key}, in [0, 1]")
                           + "; a success counts as 1.0")),
            ("Billing", E(f"{br.billing}: {runsdb.BILLING.get(br.billing, br.billing)}"))]
    price = br.price
    if price:
        rows.append(("List price", E(f"{a.get('price')}: ${price['input']} in / ${price.get('cached_input', price['input'])} "
                                     f"cached / ${price['output']} out per 1M tokens, as of {price.get('as_of', '?')}")))
    if br.closed:
        rows.append(("Closed", E(br.closed)))
    if a.get("notes"):
        rows.append(("Notes", E(str(a["notes"]))))
    formerly = [old for old, new in runsdb.aliases().items() if new == br.run]
    rows.append(("Run id", f"<code>{E(br.run)}</code> · <code>data/agents/{E(br.run)}.yml</code>, "
                           f"<code>state/runs/{E(bench.id)}.yml</code>"
                           + (" · formerly " + ", ".join(f"<code>{E(o)}</code>" for o in formerly) if formerly else "")))
    data = br.data
    if data and sitemode.PUBLIC:
        rows.append(("Results", f"as collected {runview.local(data.get('generated_at'))}, published with "
                                "<code>make publish-runs</code>"))
    elif data:
        rows.append(("Collected", f"{runview.local(data.get('generated_at'))} by <code>make runs</code> "
                                  f"{_hosts(data.get('hosts') or {})}"))
    return ('<details class="rdetails"><summary>Run details</summary><dl class="rdl">'
            + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows) + "</dl></details>")


def task_table(br: runsdb.BenchRun, bench: taskdb.Benchmark, now: dt.datetime, root: str) -> str:
    """Every task of the run, one row per mode, in the default order (in the run; modes finished; modes running;
    difficulty, easy first; A-Z), with filter chips and a sort (javascripts/runs.js). Tasks excluded from the
    benchmark (state `excluded:`) come last, under a heading of their own, whatever the sort."""
    inside = [t for t in bench.tasks if t.task_id in br.tasks]
    order = sorted(inside, key=lambda t: (runview.default_rank(br.view(t.task_id), t.status, t.difficulty,
                                                               bool(t.excluded)), t.title))
    n_x = sum(1 for t in order if t.excluded)
    recs_of = {t.task_id: runview.mode_records(br, t.task_id) for t in inside}
    billed = any(r.get("billed_usd") is not None for rs in recs_of.values() for _, r in rs)
    costs = [runview.estimate(r, br) or 0 for rs in recs_of.values() for _, r in rs]
    top = max(costs, default=0) or 1
    metrics = br.metrics
    head = ["Task", "Trial <small>(its log page)</small>", "Progress"] + \
           [(f'<span title="{E(m["help"])}">{E(m["label"])}</span>' if m["help"] else E(m["label"]))
            + (f' <small>({E(m["unit"])})</small>' if m["unit"] else "") for m in metrics] + \
           ["Agent time", "Requests", "Tokens in / out", "Est. cost"] + (["Billed"] if billed else []) + \
           ([] if sitemode.PUBLIC else ["Host"])         # the published records name no machine
    groups, chips = [], {}
    for i, t in enumerate(order):
        recs = recs_of[t.task_id]
        segs = {SEGMENT_OF.get(r.get("state", "queued"), "nodata") for _, r in recs if r.get("state") not in runview.UNCOUNTED}
        flags = {r.get("state") for _, r in recs if r.get("state") in runview.UNCOUNTED}
        rows = []
        for j, (mode, rec) in enumerate(recs):
            has = runview.has_log(bench.id, br.run, t.task_id, mode)
            # only a run this record says it replaced: a batch dropped from the run leaves its old page data behind
            prev = bool((rec.get("supersedes") or {}).get("trial")) and runview.has_log(bench.id, br.run, t.task_id, mode + "-prev")
            href = url(runview.log_page(bench.id, br.run, t.task_id, mode), root) if has else None
            tk = rec.get("tokens") or {}
            prog = runview.progress_of(rec)
            live = rec.get("state") in runview.ACTIVE
            if runview.logs_state(rec, mode)[0] == "missing" and rec.get("state") not in ("stalled", "error"):
                flags.add("logs")
            if rec.get("followup"):
                flags.add("followup")
            if rec.get("stale"):
                flags.add("stale")
            if t.excluded:
                flags.add("excluded")
            agent = runview.minutes(rec.get("agent_wall_s")) if rec.get("agent_wall_s") is not None else (
                f"{runview.minutes(runview.elapsed(rec, now))} <small>so far</small>" if live and rec.get("started") else "—")
            est = runview.estimate(rec, br)
            # The pill is the link to the trial's log page; a rerun keeps the run it replaced on a page of its own.
            prev_link = (f' <a class="rt-prev" href="{url(runview.log_page(bench.id, br.run, t.task_id, mode + "-prev"), root)}" '
                         f'title="the earlier run this rerun replaced, on a log page of its own">prev</a>') if prev else ""
            cells = [
                runview.pill_html(mode, rec, now, href=href, br=br) + prev_link,
                (f'<span class="pmini" title="progress {prog:.2f}"><i style="width:{100 * prog:.0f}%"></i></span>{prog:.2f}'
                 if isinstance(prog, (int, float)) else '<span class="rt-none">—</span>'),
            ] + [(runview.metric_text(runview.metric_value(rec, m), {**m, "unit": ""})
                  if runview.metric_value(rec, m) is not None else '<span class="rt-none">—</span>') for m in metrics] + [
                agent,
                f"{rec['calls']:,}" if rec.get("calls") is not None else "—",
                f"{runview.tok(tk.get('input'))} / {runview.tok(tk.get('output'))}" if tk.get("input") is not None else "—",
                (f'<i class="cbar" style="width:calc({100 * est / top:.0f}% - 0.3rem)"></i><span>{runview.usd(est)}</span>'
                 if est is not None else "—"),
            ]
            if billed:
                cells.append(runview.usd(rec.get("billed_usd")))
            if not sitemode.PUBLIC:
                cells += [E(rec.get("host") or "—")]
            task_cell = (f'<th rowspan="{len(recs)}" scope="rowgroup" class="rt-task">'
                         f'<a href="{url(f"benchmarks/{bench.id}/tasks/{t.task_id}.md", root)}">{E(t.title)}</a>'
                         + (f'<span class="pill pill--d-{t.difficulty}">{t.difficulty}</span>' if t.difficulty != "unrated" else "")
                         + "</th>") if j == 0 else ""
            classes = ["rt-cost" if k == 5 + len(metrics) else "rt-metric" if 2 <= k < 2 + len(metrics) else ""
                       for k in range(len(cells))]
            rows.append("<tr>" + task_cell + "".join(
                f'<td{f" class={chr(34)}{c}{chr(34)}" if c else ""}>{v}</td>' for c, v in zip(classes, cells)) + "</tr>")
        for key in segs | flags:
            chips[key] = chips.get(key, 0) + 1
        prog_vals = [p for p in (runview.progress_of(r) for _, r in recs) if p is not None]
        time_s = sum(sum(runview.agent_seconds(r, now)) for _, r in recs)
        cost_sum = sum(runview.estimate(r, br) or 0 for _, r in recs)
        mattrs = ""
        for k, m in enumerate(metrics):
            vals = [v for v in (runview.metric_value(r, m) for _, r in recs) if v is not None]
            if vals:
                mattrs += f' data-m{k}="{sum(vals) / len(vals):.6g}"'
        if t.excluded and t is next(x for x in order if x.excluded):
            # the heading of the excluded tasks, before the first of them (runs.js keeps it there on every sort)
            groups.append(
                f'<tbody class="rt-sep" data-rt-sep><tr><th colspan="{len(head)}" scope="rowgroup">'
                f'<span class="pill pill--excluded">excluded</span> Excluded from the benchmark '
                f'<small>· {n_x} task{"s" if n_x > 1 else ""}, kept for the record; the benchmark\'s numbers leave '
                f'{"them" if n_x > 1 else "it"} out</small></th></tr></tbody>')
        groups.append(
            f'<tbody class="rt-group{" rt-group--x" if t.excluded else ""}"{" data-x" if t.excluded else ""} data-i="{i}" '
            f'data-title="{E(t.title.lower())}" data-cost="{cost_sum:.6f}"{mattrs} '
            f'data-time="{time_s:.0f}" data-prog="{(sum(prog_vals) / len(prog_vals)) if prog_vals else -1:.4f}" '
            f'data-tags="{" ".join(sorted(segs | flags))}">' + "".join(rows) + "</tbody>")
    labels = [(k, lab) for k, lab, _ in SEGMENTS] + [("logs", "records missing"), ("followup", "follow-up"),
                                                     ("stale", "host silent"), ("stopped", "stopped by us"),
                                                     ("uncounted", "not counted"), ("withdrawn", "withdrawn"),
                                                     ("excluded", "excluded")]
    chip_html = f'<button type="button" data-f="" class="is-on">All <b>{len(order)}</b></button>' + "".join(
        f'<button type="button" data-f="{k}"><i class="st-{k}"></i>{lab} <b>{chips[k]}</b></button>'
        for k, lab in labels if chips.get(k))
    bar = ('<div class="rt-bar" data-rt-bar><span class="rt-chips" title="tasks with at least one trial in this state">'
           f"{chip_html}</span>"
           '<label class="rt-sort">Sort <select data-rt-sort>'
           '<option value="default">default order</option><option value="title">A–Z</option>'
           '<option value="cost">est. cost, highest first</option><option value="time">agent time, longest first</option>'
           '<option value="prog">progress, lowest first</option>'
           + "".join(f'<option value="m{k}" data-dir="{"asc" if m["better"] == "lower" else "desc"}">'
                     f'{E(m["label"])}, best first</option>' for k, m in enumerate(metrics))
           + '</select></label>'
           '<span class="rt-count" data-rt-count></span></div>')
    return (bar + '<div class="rt-wrap"><table class="rt"><thead><tr>' + "".join(f'<th scope="col">{h}</th>' for h in head)
            + "</tr></thead>" + "".join(groups) + "</table></div>")


def scope_list(br: runsdb.BenchRun, bench: taskdb.Benchmark, root: str) -> str:
    """The run's tasks as links, for a page without its results (the public site: scripts/sitemode.py)."""
    tasks = sorted((t for t in bench.tasks if t.task_id in br.tasks), key=lambda t: (bool(t.excluded), t.title))
    if not tasks:
        return ""
    items = "".join(f'<a class="rscope__task{" rscope__task--x" if t.excluded else ""}" '
                    f'href="{url(f"benchmarks/{bench.id}/tasks/{t.task_id}.md", root)}"'
                    f'{" title=" + chr(34) + "excluded from the benchmark" + chr(34) if t.excluded else ""}>{E(t.title)}</a>'
                    for t in tasks)
    return (f'<details class="rlist" open><summary>{len(tasks)} task{"s" if len(tasks) > 1 else ""} in this run, '
            f'{" and ".join(br.modes)}</summary><p class="rscope__tasks">{items}</p></details>')


def out_lists(br: runsdb.BenchRun, bench: taskdb.Benchmark, root: str) -> str:
    removed = [t for t in bench.tasks if t.task_id in br.removed]
    outside = [t for t in bench.tasks if t.task_id not in br.tasks and t.task_id not in br.removed]
    out = []
    for group, cls, what, why in ((removed, "runs-out", "removed from this run", lambda t: br.removed[t.task_id]),
                                  (outside, "", "not in this run", lambda t: br.others or "not in this run")):
        if not group:
            continue
        rows = "".join(f'<tr><td><a href="{url(f"benchmarks/{bench.id}/tasks/{t.task_id}.md", root)}">{E(t.title)}</a></td>'
                       f"<td>{E(why(t))}{' · excluded from the benchmark' if t.excluded else ''}</td></tr>"
                       for t in sorted(group, key=lambda t: (bool(t.excluded), t.title)))
        out.append(f'<details class="rlist {cls}"><summary>{len(group)} task(s) {what}</summary>'
                   f'<table><thead><tr><th>Task</th><th>Why</th></tr></thead><tbody>{rows}</tbody></table></details>')
    return "".join(out)


def _help(bench_page: bool) -> str:
    """The long explanation, folded: what a run is, what the colours and numbers mean."""
    colours = "".join(f'<span><i class="st-{k}"></i>{lab}</span>' for k, lab, _ in SEGMENTS)
    where = ("Pick a run above; the table lists every task of it, one row per mode, in the default order (finished "
             "first, then running, easier tasks first). A pill links to that trial's log page. Filter the table with "
             "the chips above it."
             if bench_page else
             "Each card is one run, added up over the benchmarks that take part in it; a benchmark's name opens its "
             "page for that run.")
    return (
        '<details class="rhelp"><summary>How to read this page</summary>'
        "<p>A <b>run</b> is one agent configuration, harness + model + settings; each task in it runs once per mode. "
        f"{where}</p>"
        f'<p class="slegend slegend--key">{colours}</p>'
        "<p><b>Bars</b> count trials, one per task and mode, by state. <b>Progress</b> is the partial credit beside "
        "success, in [0, 1]: BEHAVIOR's 2026 challenge q_score, elsewhere the grader's final_reward. <b>A success always "
        "counts as full progress, 1.0</b>, whatever that key says (RoboLab's final_reward is 0 for a task without scored "
        "subtasks); <b>mean progress</b> averages it over the graded trials. <b>Agent time</b> adds up finished trials; "
        "running ones are shown apart. A benchmark can also declare <b>grader metrics</b>, continuous scores its grader "
        "writes (IoU, F1, a distance): they get a column each, a sort, and a run figure, the mean or the median of the "
        "graded trials.</p>"
        "<p><b>Tokens</b> are the model gateway's count of every request (input includes the cached part, output the "
        "reasoning part). <b>≈ $</b> is those tokens at the list prices in <code>data/prices.yml</code>, an estimate "
        "and never a bill; <b>billed</b> is what a provider charged, where it says. The two are never added together.</p>"
        "<p>A benchmark's owner can <b>exclude</b> tasks from the final benchmark (<code>excluded:</code> in "
        "<code>state/tasks/&lt;benchmark&gt;.yml</code>). Their trials stay, last in a run's table under <i>Excluded from "
        "the benchmark</i>; the numbers count the benchmark's own tasks, and the <b>Count</b> switch adds the excluded "
        "ones.</p>"
        f'<p>Runs are registered per benchmark: <a href="{url(REG, "../../")}">how to register a run</a>.</p></details>')


def benchmark_page(bench: taskdb.Benchmark) -> str:
    """runs/<benchmark>.md: the benchmark's runs, one shown at a time."""
    now = dt.datetime.now(dt.timezone.utc)
    root = "../../"
    runs = runsdb.runs_of(bench.id)
    out = ["---", f"title: {bench.name} runs", "hide:", "  - toc", "---", "", f"# {bench.name} runs", "",
           f'<p class="rlead">Agent runs on the tasks of <a href="{url(f"benchmarks/{bench.id}/index.md", root)}">'
           f"{E(bench.name)}</a>, one run at a time.</p>", "", _help(True), ""]
    if not runs:
        out += ['<div class="rempty"><b>No runs registered yet.</b> The benchmark\'s owner adds one in '
                f'<code>state/runs/{E(bench.id)}.yml</code>: <a href="{url(REG, "../../")}">how to register a run</a>.</div>', ""]
        return "\n".join(out)
    options = [(br.run, br.short, br.label, [t for t, on in (("default", br.default), ("closed", bool(br.closed)),
                                                               (NO_DATA, not br.data)) if on]) for br in runs]
    hint = (_differ_hint(runs) if len(runs) > 1 else
            f'the only run registered so far · <a href="{url(REG, "../../")}">add one</a>')
    out += [picker(options, runs[0].run, hint), ""]
    for br in runs:
        data = br.data
        known = {t.task_id for t in bench.tasks}
        n_own, n_x = _split(br, bench)
        n_rm = len([t for t in br.removed if t in known])
        meta = ([f"{n_own + n_x} tasks × {len(br.modes)} modes"] + ([f"{n_x} of them excluded from the benchmark"] if n_x else [])
                + ([f"{n_rm} removed"] if n_rm else []))
        if data and sitemode.PUBLIC:
            meta.append(f"results as of {runview.local(data.get('generated_at'))}")
        elif data:
            hs = data.get("hosts") or {}
            down = [h for h, s in hs.items() if not s.get("ok")]
            meta.append(f"collected {runview.local(data.get('generated_at'))}")
            meta.append(f'<span title="{E(" · ".join(sorted(hs)))}">{len(hs) - len(down)}/{len(hs)} hosts answered</span>'
                        if hs else "no hosts")
        panel = [f'<section class="rpanel" data-run-panel="{E(br.run)}">',
                 '<div class="rhead"><h2 class="rhead__title">' + E(br.label)
                 + ('<span class="runtag runtag--default">default</span>' if br.default else "")
                 + (f'<span class="runtag runtag--closed" title="{E(br.closed)}">closed</span>' if br.closed else "")
                 + f'</h2><p class="rhead__meta">{" · ".join(meta)}</p></div>']
        if not data and sitemode.PUBLIC:
            panel.append('<div class="rempty"><b>Results not published.</b> This run\'s results stay on the machines '
                         "that ran it; this site shows its setting and the tasks in it.</div>")
        elif not data:
            panel.append('<div class="rempty"><b>Nothing collected on this machine.</b> Whoever runs it collects its '
                         "records with <code>make runs</code>, listing the machines that hold its jobs in "
                         "<code>data/runs/hosts*.local.yml</code>. The tasks in its scope are below.</div>")
        else:
            note = "q_score" if br.progress_key == "q_score" else br.progress_key
            price = br.price
            pnote = (f" ({br.agent.get('price')}: ${price['input']} / ${price.get('cached_input', price['input'])} cached / "
                     f"${price['output']} per 1M)") if price else ""

            def numbers(scope: str) -> str:
                pairs = _pairs(br, bench, scope)
                if scope == "bench" and not n_own:
                    return _only_excluded(n_x)
                tot = runview.totals(pairs, now)
                return "".join([kpis(pairs, br.modes, note, now, br.withdrawn), cost_line(tot, br, pnote),
                                metric_strip(pairs, br.metrics),
                                family_table(br, bench, scope),
                                issue_chips(tot, pairs, data.get("hosts") or {}, filterable=True, followups=False)])

            panel.append(scoped({"bench": numbers("bench"), "all": numbers("all") if n_x else ""}, n_own, n_x,
                                f"{n_x} of the run's tasks {'are' if n_x > 1 else 'is'} excluded from the benchmark: "
                                "last in the table"))
        panel.append(run_details(br, bench))
        follow = [(t, m, r["followup"]) for t in bench.tasks if t.task_id in br.tasks
                  for m, r in runview.mode_records(br, t.task_id) if r.get("followup")]
        if follow:
            panel.append('<div class="rfollow"><b>↻ Follow-ups arranged</b><ul>' + "".join(
                f'<li><a href="{url(f"benchmarks/{bench.id}/tasks/{t.task_id}.md", root)}">{E(t.title)}</a> '
                f'<span class="rfollow__mode">{E(m)}</span> {E(n)}</li>' for t, m, n in follow) + "</ul></div>")
        # notes on trials graded as they are (`notes:`): nothing is arranged for them
        noted = [(t, m, r["note"]) for t in bench.tasks if t.task_id in br.tasks
                 for m, r in runview.mode_records(br, t.task_id) if r.get("note")]
        if noted:
            panel.append('<div class="rfollow rnote"><b>ⓘ Notes</b><ul>' + "".join(
                f'<li><a href="{url(f"benchmarks/{bench.id}/tasks/{t.task_id}.md", root)}">{E(t.title)}</a> '
                f'<span class="rfollow__mode">{E(m)}</span> {E(n)}</li>' for t, m, n in noted) + "</ul></div>")
        # without results, the public site lists the run's tasks instead of a table of empty rows
        panel.append(scope_list(br, bench, root) if sitemode.PUBLIC and not data else task_table(br, bench, now, root))
        panel.append(out_lists(br, bench, root))
        panel.append("</section>")
        out += ["\n".join(panel), ""]
    return "\n".join(out)


# ------------------------------------------------------------------------------------------ the overview


def overview() -> str:
    """runs/overview.md: every run across the benchmarks, and which benchmark takes part in which run."""
    now = dt.datetime.now(dt.timezone.utc)
    root = "../../"
    benches = taskdb.benchmarks()
    parts = [br for br in runsdb.all_runs() if br.benchmark in benches]
    ids = list(dict.fromkeys(br.run for br in parts))
    out = ["---", "title: Runs overview", "hide:", "  - toc", "---", "", "# Runs", "",
           '<p class="rlead">Every agent run, added up over the benchmarks that take part in it.</p>', "", _help(False), ""]
    stamps = [br.data.get("generated_at") for br in parts if br.data.get("generated_at")]
    hosts = {}
    for br in parts:
        for h, st in (br.data.get("hosts") or {}).items():
            if h not in hosts or (st.get("at") or "") > (hosts[h].get("at") or ""):
                hosts[h] = st
    if stamps and sitemode.PUBLIC:
        out += [f'<p class="rstatus">Results as of {runview.local(max(stamps))}</p>', ""]
    elif stamps:
        out += [f'<p class="rstatus">Collected here {runview.local(max(stamps))} {_hosts(hosts)}</p>', ""]
    elif sitemode.PUBLIC:
        out += ['<div class="rempty"><b>Run results are not published on this site yet.</b> The runs below, their '
                "settings and the tasks in them come from the registry.</div>", ""]
    else:
        out += ['<div class="rempty"><b>No run data on this machine.</b> <code>make runs</code> (or <code>make runs-watch</code>) '
                "collects it from the machines in <code>data/runs/hosts*.local.yml</code>. The runs and their scopes below "
                "come from the registry.</div>", ""]
    if not ids:
        out += [f'<div class="rempty">No run is registered yet: <a href="{url(REG, "../../")}">how to register a run</a>.</div>', ""]
        return "\n".join(out)

    # 0. the same picker as on a benchmark's page, "All runs" first: picking a run shows its card alone
    firsts = {rid: next(br for br in parts if br.run == rid) for rid in ids}
    options = [("", "All runs", "every registered run", [])] + [
        (rid, firsts[rid].short, firsts[rid].label,
         ["closed"] if all(br.closed for br in parts if br.run == rid) else []) for rid in ids]
    out += [picker(options, "", f"{len(ids)} run{'s' if len(ids) > 1 else ''} registered, over "
                                f"{len({br.benchmark for br in parts})} benchmarks"), ""]

    # 1. one card per run: its numbers over every benchmark, then one bar per benchmark
    cards = []
    for rid in ids:
        mine = [br for br in parts if br.run == rid]
        a = mine[0]
        modes = list(dict.fromkeys(m for br in mine for m in br.modes))
        hs = {}
        for br in mine:
            hs.update(br.data.get("hosts") or {})
        split = {br.benchmark: _split(br, benches[br.benchmark]) for br in mine}
        n_own = sum(o for o, _ in split.values())
        n_x = sum(x for _, x in split.values())
        progress_note = "q_score / final_reward" if any(br.progress_key == "q_score" for br in mine) and \
            any(br.progress_key != "q_score" for br in mine) else ("q_score" if mine[0].progress_key == "q_score" else mine[0].progress_key)

        def numbers(scope: str) -> str:
            """The card's numbers over the benchmarks' own tasks ("bench") or with their excluded tasks ("all")."""
            pairs = [p for br in mine for p in _pairs(br, benches[br.benchmark], scope)]
            tot = runview.totals(pairs, now)
            rows = []
            for br in mine:
                own, x = split[br.benchmark]
                bp = _pairs(br, benches[br.benchmark], scope)
                bt = runview.totals(bp, now)
                counts = _segments([r for _, r in bp if r.get("state") != "nodata"])
                link = f'{url(runview.runs_page(br.benchmark), root)}?run={E(rid)}'
                extra = (f'<span class="rbench__x" title="tasks of this run excluded from the benchmark, not counted here">'
                         f"+ {x} excluded</span>" if x and scope == "bench" else "")
                extra += "".join(f'<span class="rbench__x" title="{E(w["note"])}">{E(m)} withdrawn: {E(w["label"])}</span>'
                                 for m, w in br.withdrawn.items())
                rows.append(
                    f'<a class="rbench" href="{link}"><span class="rbench__name">{E(benches[br.benchmark].name)}'
                    + ('<span class="runtag runtag--default">default</span>' if br.default else "") + "</span>"
                    + ((sbar(counts, small=True) + f'<span class="rbench__num">{bt["success"]} ✓ · {bt["done"]}/{bt["trials"]} done'
                        f"{extra}</span>" if own or scope == "all" else
                        f'<span class="rbench__none">only its {x} excluded task{"s" if x > 1 else ""} so far: not counted</span>')
                       if br.data else f'<span class="rbench__none">{NO_DATA}</span>') + "</a>")
            return ((kpis(pairs, modes, progress_note, now) + cost_line(tot, a) + issue_chips(tot, pairs, hs, filterable=False)
                     if tot["trials"] else '<div class="rempty">' + ("Results not published." if sitemode.PUBLIC else
                                                                        "No records of this run on this machine.") + "</div>")
                    + '<div class="rbenches">' + "".join(rows) + "</div>")

        cards.append(
            f'<section class="rcard2" data-run-panel="{E(rid)}">'
            f'<div class="rhead"><h2 class="rhead__title" title="{E(rid)}">{E(a.label)}'
            + ('<span class="runtag runtag--closed">closed</span>' if all(br.closed for br in mine) else "")
            + f'</h2><p class="rhead__meta">{len(mine)} benchmark{"s" if len(mine) > 1 else ""} · {n_own} tasks'
              + (f" + {n_x} excluded" if n_x else "") + f' · <code>{E(rid)}</code></p></div>'
            # no Count switch without results to count (the public site: scripts/sitemode.py)
            + (scoped({"bench": numbers("bench"), "all": numbers("all") if n_x else ""}, n_own, n_x,
                      " · ".join(f"{benches[b].name}: {x} excluded from the benchmark" for b, (_, x) in split.items() if x))
               if any(br.data for br in mine) else numbers("bench"))
            + "</section>")
    out += ["\n".join(cards), ""]

    # 2. which benchmark takes part in which run, benchmarks without a run included
    head = ["Benchmark"] + [f'<span title="{E(r)}">{E(next(br.short for br in parts if br.run == r))}</span>' for r in ids]
    rows = []
    for bid, bench in benches.items():
        mine = {br.run: br for br in runsdb.runs_of(bid)}
        row = [f'<a href="{url(runview.runs_page(bid), root)}">{E(bench.name)}</a>']
        for rid in ids:
            br = mine.get(rid)
            if not br:
                row.append('<span class="rt-none">—</span>')
                continue
            bp = _pairs(br, bench)
            bt = runview.totals(bp, now)
            counts = _segments([r for _, r in bp if r.get("state") != "nodata"])
            _, x = _split(br, bench)
            row.append(f'<a class="rcell" href="{url(runview.runs_page(bid), root)}?run={E(rid)}">'
                       + (sbar(counts, small=True) + f"<span>{bt['success']} ✓ · {bt['done']}/{bt['trials']}</span>"
                          if br.data else f"<span>{NO_DATA}</span>")
                       + (f'<span class="rcell__x" title="tasks of this run excluded from the benchmark, not counted">'
                          f"+ {x} excluded</span>" if x else "")
                       + "".join(f'<span class="rcell__x" title="{E(w["note"])}">{E(m)} withdrawn</span>'
                                 for m, w in br.withdrawn.items())
                       + ('<span class="runtag runtag--default">default</span>' if br.default else "")
                       + ('<span class="runtag runtag--closed">closed</span>' if br.closed else "") + "</a>")
        rows.append(row)
    out += ["## Runs by benchmark", "", _table(head, rows, "rmatrix"), ""]

    # 3. every number, for the record: folded
    head = ["Benchmark", "Run", "In run", "Not in / removed", "Excluded <small>(not counted)</small>"]
    modes = list(dict.fromkeys(m for br in parts for m in br.modes))
    head += [f"{m.capitalize()} done / success" for m in modes]
    head += ["Running", "Queued", "Failed grading / stalled", "Mean progress", "Grader metrics", "Agent-hours", "Requests",
             "Tokens in / cached", "Tokens out / reasoning", "Est. cost", "Billed",
             "Results as of" if sitemode.PUBLIC else "Collected"]
    rows = []
    for br in parts:
        bench = benches[br.benchmark]
        tot = runview.totals(_pairs(br, bench), now)
        st = tot["states"]
        known = {t.task_id for t in bench.tasks}
        n_in, n_x = _split(br, bench)
        n_rm = len([t for t in br.removed if t in known])
        xt = runview.totals(_pairs(br, bench, "excluded"), now)
        row = [f'<a href="{url(runview.runs_page(br.benchmark), root)}?run={E(br.run)}">{E(bench.name)}</a>',
               E(br.short) + (' <span class="runtag runtag--closed">closed</span>' if br.closed else ""),
               str(n_in), f"{len(known) - n_in - n_x - n_rm} / {n_rm}",
               (f"{n_x} tasks · {xt['done']}/{xt['trials']} done · {xt['success']} ✓ · "
                + (runview.usd(xt["est"]) if xt["est_n"] else "—") + " est." if n_x else "—")]
        for m in modes:
            md = tot["modes"].get(m)
            row.append("withdrawn" if m in br.withdrawn else
                       f"{md['done']}/{md['trials']} · {md['success']} ({_pct(md['success'], md['done'])})" if md else "—")
        graded = [r for _, r in _pairs(br, bench) if r.get("state") in runview.DONE]
        figures = []
        for m in br.metrics:
            vals = [v for v in (runview.metric_value(r, m) for r in graded) if v is not None]
            if vals:
                figures.append(f"{E(m['label'])} {E(runview.metric_text(runview.metric_summary(vals, m), m))}")
        row += [str(sum(st.get(s, 0) for s in runview.ACTIVE)),
                str(st.get("queued", 0) + st.get("notrun", 0)) + (f" ({tot['reruns']} reruns)" if tot["reruns"] else ""),
                str(st.get("error", 0) + st.get("stalled", 0)),
                f"{tot['progress_sum'] / tot['progress_n']:.2f}" if tot["progress_n"] else "—",
                " · ".join(figures) or "—",
                _hours(tot["agent_s"]), f"{tot['calls']:,}",
                f"{runview.tok(tot['input'])} / {runview.tok(tot['cached'])}",
                f"{runview.tok(tot['output'])} / {runview.tok(tot['reasoning'])}",
                runview.usd(tot["est"]) if tot["est_n"] else "—", _billed_text(br, tot),
                runview.local(br.data.get("generated_at")) if br.data else NO_DATA]
        rows.append(row)
    if stamps or not sitemode.PUBLIC:           # the public site without results has no numbers to list
        out += ['<details class="rlist"><summary>Every number: each benchmark in each run</summary>',
                _table(head, rows, "runs-sum"), "</details>", ""]
    return "\n".join(out)


def home_summary(root: str) -> str:
    """The home page's Agent runs section: each benchmark's default run in one row (its own tasks: the excluded ones
    and the trials we stopped count in none of these numbers), linking to its Runs page. "" without any run data."""
    now = dt.datetime.now(dt.timezone.utc)
    rows, runs, notes = [], [], []
    for bid, bench in taskdb.benchmarks().items():
        br = runsdb.default_run(bid)
        if br is None or not br.data:
            continue
        runs.append(br)
        tot = runview.totals(_pairs(br, bench, "bench"), now)
        link = f'<a href="{url(runview.runs_page(bid), root)}">{E(bench.name)}</a>'
        n_own, n_x = _split(br, bench)
        if not tot["trials"]:
            rows.append([link, f'<span class="rt-none">its {n_x} tasks in this run so far are excluded from the benchmark</span>',
                         "", "", "", "", ""])
            continue
        cells = [link, f"{n_own}" + (f' <small>+ {n_x} excluded</small>' if n_x else "")]
        for mode in ("unlimited", "limited"):
            md = tot["modes"].get(mode)
            w = br.withdrawn.get(mode)
            cells.append(f'<span class="rt-none" title="{E(w["note"])}">withdrawn: {E(w["label"])}</span>' if w else
                         f'<b>{_pct(md["success"], md["done"])}</b> <small>{md["success"]}/{md["done"]}</small>'
                         if md and md["done"] else "—")
        mean = tot["progress_sum"] / tot["progress_n"] if tot["progress_n"] else None
        key = "q_score" if br.progress_key == "q_score" else br.progress_key
        pf = br.per_family
        if pf:      # a score whose metric depends on the task family: its plain mean, explained under the table
            vals = [v for f in family_scores(br, bench).values() for md in f["modes"].values() for v in md["values"]]
            fams = {fam: f["metric"] for fam, f in family_scores(br, bench).items()}
            notes.append(f'<sup>*</sup> {E(bench.name)}: the plain mean of the grader\'s {E(pf["label"])} over the graded '
                         "trials, a success at its own value. Its metric depends on the task family: "
                         + "; ".join(f"{E(' / '.join(ms) or '—')} for {E(_and(fs))}" for ms, fs in _group(fams)) + ".")
            cells.append(f'{sum(vals) / len(vals):.2f} <small>mean {E(pf["label"])}<sup>*</sup></small>' if vals else "—")
        else:
            cells.append(f'{mean:.2f} <small>{E(key)}</small>' if mean is not None else "—")
        cells.append(runview.usd(tot["est"]) if tot["est_n"] else "—")
        cells.append(f'{runview.tok(tot["input"])} / {runview.tok(tot["output"])}' if tot["tokens_n"] else "—")
        rows.append(cells)
    if not rows:
        return ""
    agents = list(dict.fromkeys(br.label for br in runs))
    head = ["Benchmark", "Tasks run", "Success, unlimited", "Success, limited", "Mean score",
            "Est. cost <small>(list price)</small>", "Tokens in / out"]
    return (f'<p class="rlead">{E(" · ".join(agents))}, on every benchmark: success among graded trials, the mean '
            "score (partial credit, a success counts as 1.0), and what the model use would cost at list price. "
            f'<a href="{url("runs/overview.md", root)}">All runs, tasks and trial logs &rarr;</a></p>'
            + _table(head, rows, "runs-sum runs-home")
            + "".join(f'<p class="rnote-lead">{n}</p>' for n in notes))


def _and(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _group(fams: dict[str, list[str]]) -> list[tuple[list[str], list[str]]]:
    """(metric names, families) with the families that share their metric together, in first-seen order."""
    out: dict[tuple[str, ...], list[str]] = {}
    for fam, ms in fams.items():
        out.setdefault(tuple(ms), []).append(fam)
    return [(list(ms), fs) for ms, fs in out.items()]


def _table(head: list[str], rows: list[list[str]], cls: str) -> str:
    return (f'<div class="runs-scroll"><table class="{cls}"><thead><tr>' + "".join(f"<th>{h}</th>" for h in head)
            + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
            + "</tbody></table></div>")


def redirect() -> str:
    """runs/index.md: /runs/ held the one-sweep page until 2026-09-28; send it to the overview."""
    return "\n".join(["---", "template: redirect.html", "location: overview/", "---", ""])


def _runlog_div(root: str, benchmark: str, run: str, task: str, slot: str) -> str:
    """Where a log page's script (javascripts/runlog.js) finds the trial's data and media.

    Locally both are next to each other, docs/assets/<benchmark>/runs/<run>/<task>/<slot>/. On the public site
    (scripts/sitemode.py) the data is the published snapshot, served at runs-data/<benchmark>/<run>/<task>/<slot>/
    (scripts/gen_pages.py), and the replay and images load from data/public.yml's run_media_base; an empty
    data-media makes the page say "media not yet published"."""
    rel = f"{benchmark}/runs/{run}/{task}/{slot}/"
    if not sitemode.PUBLIC:
        return f'<div class="runlog" data-runlog="{root}assets/{rel}"></div>'
    media = f"{sitemode.RUN_MEDIA_BASE}{benchmark}/{run}/{task}/{slot}/" if sitemode.RUN_MEDIA_BASE else ""
    return (f'<div class="runlog" data-runlog="{root}runs-data/{benchmark}/{run}/{task}/{slot}/" '
            f'data-media="{E(media)}"></div>')


STUB = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved: {title}</title>'
        '<meta name="robots" content="noindex"><link rel="canonical" href="{to}">'
        '<meta http-equiv="refresh" content="0; url={to}">'
        '<script>location.replace("{to}" + location.search + location.hash);</script></head>'
        '<body><p>This log page moved: <a href="{to}">{title}</a>. The run was renamed from <code>{old}</code> '
        'to <code>{new}</code>.</p></body></html>\n')


WITHDRAWN_STUB = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Withdrawn: {title}</title>'
                  '<meta name="robots" content="noindex"><link rel="canonical" href="{to}">'
                  '<meta http-equiv="refresh" content="0; url={to}">'
                  '<script>location.replace("{to}");</script></head>'
                  '<body><p>This trial log was withdrawn: {label}. {note} See <a href="{to}">the task\'s page</a>.</p>'
                  '</body></html>\n')


def _sentence(text: str) -> str:
    """A note as a sentence: its first letter capitalised, without a final full stop (the caller adds one)."""
    text = str(text).strip().rstrip(".")
    return text[:1].upper() + text[1:]


def withdrawn_stubs(pages: list[str]) -> list[tuple[str, str]]:
    """(path, html) at the log-page addresses of a withdrawn mode (`withdrawn:` in state/runs/), under the run's id and
    its former ids, where this build has no log page (the public site): each leads to the task's page, which says
    "withdrawn". A local build keeps the pages themselves."""
    have = set(pages)
    formerly: dict[str, list[str]] = {}
    for old, new in runsdb.aliases().items():
        formerly.setdefault(new, []).append(old)
    out = []
    for bench in taskdb.benchmarks().values():
        for br in runsdb.runs_of(bench.id):
            for mode, w in br.withdrawn.items():
                for tid in br.tasks:
                    for slot in (mode, mode + "-prev"):
                        if f"runs/{bench.id}/{br.run}/{tid}/{slot}.md" in have:
                            continue
                        for rid in [br.run] + formerly.get(br.run, []):
                            out.append((f"runs/{bench.id}/{rid}/{tid}/{slot}/index.html", WITHDRAWN_STUB.format(
                                to=E(f"../../../../../benchmarks/{bench.id}/tasks/{tid}/"), title=E(f"{tid} · {slot}"),
                                label=E(w["label"]), note=E(_sentence(w["note"]) + ".") if w["note"] else "")))
    return out


def redirect_stubs(pages: list[str]) -> list[tuple[str, str]]:
    """(path, html) of a static redirect page at every former address of a log page: a run renamed (`formerly:` in
    data/agents/<run>.yml) keeps its old links working, runs/<b>/<former id>/<task>/<slot>/ -> runs/<b>/<id>/<task>/
    <slot>/. `pages` are the log pages' source paths, runs/<b>/<run>/<task>/<slot>.md."""
    formerly: dict[str, list[str]] = {}
    for old, new in runsdb.aliases().items():
        formerly.setdefault(new, []).append(old)
    out = []
    for page in pages:
        _, bench, run, task, slot = page[: -len(".md")].split("/")
        for old in formerly.get(run, []):
            out.append((f"runs/{bench}/{old}/{task}/{slot}/index.html",
                        STUB.format(to=E(f"../../../{run}/{task}/{slot}/"), title=E(f"{task} · {slot}"),
                                    old=E(old), new=E(run))))
    return out


def log_pages() -> list[tuple[str, str]]:
    """(path, text) of one page per trial that has log data: what the agent did, minute by minute."""
    out = []
    for bench in taskdb.benchmarks().values():
        for br in runsdb.runs_of(bench.id):
            known = {t.task_id: t for t in bench.tasks}
            for tid in br.tasks:
                t = known.get(tid)
                if t is None:
                    continue
                for mode in br.modes:
                    # <mode>-prev: the run a started rerun replaced (scripts/import_runs.py build_logs), kept as history,
                    # but only while the record still says so (a batch dropped from the run leaves its page data behind)
                    prev = mode + "-prev"
                    replaced = bool(((br.view(tid)["modes"].get(mode) or {}).get("supersedes") or {}).get("trial"))
                    for slot in (mode, prev):
                        if not runview.has_log(bench.id, br.run, tid, slot) or (slot == prev and not replaced):
                            continue
                        root = "../" * 5          # runs/<b>/<run>/<task>/<slot>/ -> the site root
                        links = (f"[← Task page](../../../../benchmarks/{bench.id}/tasks/{tid}.md) · "
                                 f'<a href="{root}runs/{bench.id}/?run={E(br.run)}">All {E(bench.name)} tasks in this run</a>')
                        if slot == mode and replaced and runview.has_log(bench.id, br.run, tid, prev):
                            links += f" · [Previous run, replaced by the rerun]({prev}.md)"
                        label = mode
                        if slot == prev:
                            links += f" · [Current run]({mode}.md)" if runview.has_log(bench.id, br.run, tid, mode) else ""
                            label = f"{mode} · previous run, replaced by the rerun"
                        rec = (br.view(tid)["modes"].get(mode) or {}) if slot == mode else \
                            ((br.view(tid)["modes"].get(mode) or {}).get("supersedes") or {})
                        est = runview.estimate(rec, br)
                        cost = ""
                        if slot == mode and (est is not None or rec.get("billed_usd") is not None):
                            cost = (f'<p class="runs-hosts">Model use: est. {runview.usd(est)} at list price'
                                    + (f" · billed {runview.usd(rec['billed_usd'])}" if rec.get("billed_usd") is not None else "")
                                    + "</p>")
                        # a trial we stopped ourselves says so first (state/runs/ `stopped:`)
                        stop = (f'<p class="runlog__stopped">&#9209; <b>Stopped by us:</b> {E(rec["stopped"])}. '
                                "This trial counts in no statistic.</p>") if slot == mode and rec.get("stopped") else ""
                        # a withdrawn mode (state/runs/ `withdrawn:`): only a local build still has these pages
                        w = br.withdrawn.get(mode)
                        if w:
                            stop += (f'<p class="runlog__stopped">⊘ <b>Withdrawn:</b> {E(w["label"])}'
                                     + (f". {E(_sentence(w['note']))}" if w["note"] else "")
                                     + ". This trial counts in no statistic and is not on the public site.</p>")
                        # a trial that ran but does not count (state/runs/ `not_counted:`): the reason first too
                        if slot == mode and rec.get("uncounted"):
                            stop += (f'<p class="runlog__stopped">⊘ <b>Not counted:</b> {E(str(rec["uncounted"]).rstrip("."))}. '
                                     "This trial counts in no statistic.</p>")
                        # a trial a rerun replaced: why (the follow-up that arranged the rerun, state/runs/ `followups:`)
                        if slot == prev and rec.get("followup"):
                            stop += (f'<p class="runlog__note">↻ <b>Replaced by a rerun:</b> '
                                     f'{E(str(rec["followup"]).rstrip("."))}.</p>')
                        # a note on this trial, graded as it is (state/runs/ `notes:`)
                        if slot == mode and rec.get("note"):
                            stop += f'<p class="runlog__note">ⓘ <b>Note:</b> {E(rec["note"].rstrip("."))}.</p>'
                        out.append((runview.log_page(bench.id, br.run, tid, slot), "\n".join([
                            "---", f"title: {t.title} · {label} run", "hide:", "  - toc", "---", "",
                            f"# {E(t.title)} <span class=\"runlog__mode\">{E(label)}</span>", "",
                            f'<p class="runlog__run">{E(br.label)}</p>', "",
                            links, "", stop, cost,
                            _runlog_div(root, bench.id, br.run, tid, slot), ""])))
    return out

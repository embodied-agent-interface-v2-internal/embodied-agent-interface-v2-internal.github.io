#!/usr/bin/env python3
"""Validates every task page against the schema and the registries.

This is the guardrail that lets many people edit in parallel without a
maintainer reading every diff. It runs in CI on every PR and is the same check
you can run locally with `make validate`.

Errors block the build. Warnings are incomplete-but-valid work — a brand new
task page is all warnings, which is fine and expected.

Exit codes: 0 clean (warnings allowed), 1 errors found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import runsdb  # noqa: E402
import taskdb  # noqa: E402

GITHUB_HANDLE_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
URL_RE = re.compile(r"^https?://", re.I)

REQUIRED_TOP = ["title", "task_id", "benchmark"]
MEDIA_KINDS = {"image", "video", "link"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


def check_registries(rep: Report) -> None:
    # Labels are flat ids now; a family prefix was noise nobody typed correctly.
    #
    # A label rolls up the primitives of whichever benchmark motivated it, so a
    # skill only has to exist in *some* registry: warning per benchmark would
    # fire ten times the moment a second suite with its own vocabulary appears.
    known = {s for b in taskdb.benchmarks().values() for s in b.skill_vocabulary}
    if known:
        for where, kind, index in (("state/taxonomy.yml", "label", taskdb.capability_index()),
                                   ("state/display_tags.yml", "tag", taskdb.tag_index())):
            for lid, label in index.items():
                unknown = [s for s in (label.get("from_skills") or []) if s not in known]
                if unknown:
                    rep.warn(where, f"{kind} {lid!r} maps skills no benchmark declares: {', '.join(unknown)}")
    groups = [g.get("id") for g in taskdb.tag_vocabulary().get("capabilities") or []]
    missing = [g for g in taskdb.TAG_GROUPS if g not in groups]
    if missing:
        rep.error("state/display_tags.yml", f"no group {', '.join(map(repr, missing))} (taskdb.TAG_GROUPS)")
    for bid, bench in taskdb.benchmarks().items():
        if not bench.skill_vocabulary:
            rep.warn(f"data/benchmarks/{bid}.yml", "no skill_vocabulary; `skills:` cannot be checked")


def check_task(task: taskdb.Task, bench: taskdb.Benchmark, rep: Report) -> None:
    where = task.src_uri
    meta = task.meta
    caps = taskdb.capability_index()

    for key in REQUIRED_TOP:
        if key not in meta:
            rep.error(where, f"missing required frontmatter key `{key}`")
    # Curated fields live in state/ now; leftovers here are silently ignored
    # by the site, so flag them rather than let them look effective.
    for stale in ("status", "difficulty", "capabilities", "owner", "skills"):
        if stale in meta:
            rep.error(where, f"`{stale}` belongs in state/ — run scripts/migrate_state.py")

    if task.task_id != task.path.stem:
        rep.error(where, f"task_id {task.task_id!r} does not match filename {task.path.stem!r}")
    if task.benchmark != bench.id:
        rep.error(where, f"benchmark {task.benchmark!r} does not match its directory {bench.id!r}")

    if task.status not in taskdb.STATUSES:
        rep.error(where, f"status {task.status!r} not one of {taskdb.STATUSES}")
    if task.difficulty not in taskdb.DIFFICULTIES:
        rep.error(where, f"difficulty {task.difficulty!r} not one of {taskdb.DIFFICULTIES}")

    # `status_reason` is optional. Keep or drop is the decision that matters;
    # anyone who wants to explain themselves can, in the prose or that field.

    # `excluded` leaves a task out of the final benchmark (kept on the site, greyed, last): the reason is the point.
    excluded = task.state.get("excluded")
    if excluded is not None and not (isinstance(excluded, str) and excluded.strip()):
        rep.error(f"state/tasks/{bench.id}.yml",
                  f"{task.task_id}: `excluded` must say why, in words (e.g. excluded: \"too easy for the final benchmark\")")

    for cid in task.capabilities:
        if cid not in caps:
            rep.error(f"state/tasks/{bench.id}.yml", f"{task.task_id}: unknown label {cid!r}")
    if len(set(task.capabilities)) != len(task.capabilities):
        rep.error(f"state/tasks/{bench.id}.yml", f"{task.task_id}: duplicate labels")

    # The display tags: untagged is unfinished work (a warning below); tagged is one tag or more from each group.
    tags = taskdb.tag_index()
    for tid in task.display_tags:
        if tid not in tags:
            rep.error(f"state/tasks/{bench.id}.yml", f"{task.task_id}: unknown display tag {tid!r}")
    if len(set(task.display_tags)) != len(task.display_tags):
        rep.error(f"state/tasks/{bench.id}.yml", f"{task.task_id}: duplicate display tags")
    if task.display_tags and task.missing_tag_groups:
        rep.error(f"state/tasks/{bench.id}.yml",
                  f"{task.task_id}: no {' or '.join(task.missing_tag_groups)} display tag — a tagged task takes at "
                  "least one from each group")

    if bench.skill_vocabulary:
        for skill in task.skills:
            if skill not in bench.skill_vocabulary:
                rep.error(
                    where,
                    f"skill {skill!r} is not in the {bench.id} skill_vocabulary",
                )

    if task.owner and not GITHUB_HANDLE_RE.match(task.owner):
        rep.error(where, f"owner {task.owner!r} is not a bare GitHub handle (no @, no URL)")

    media = task.state.get("media") or []
    if not isinstance(media, list):
        rep.error(where, "`media` must be a list")
    else:
        for i, item in enumerate(media):
            tag = f"media[{i}]"
            if not isinstance(item, dict):
                rep.error(where, f"{tag} must be a mapping with `kind` and `url`")
                continue
            if item.get("kind") not in MEDIA_KINDS:
                rep.error(where, f"{tag}.kind must be one of {sorted(MEDIA_KINDS)}")
            url = item.get("url", "")
            if not URL_RE.match(str(url)):
                rep.error(where, f"{tag}.url must be an absolute http(s) URL, got {url!r}")
            if not (item.get("caption") or "").strip():
                rep.warn(where, f"{tag} has no caption")

    up = task.upstream
    if not up:
        rep.error(where, "missing `upstream:` block; run scripts/import_behavior_tasks.py")
    else:
        if up.get("scene_model") not in (bench.meta.get("scenes") or [up.get("scene_model")]):
            rep.warn(where, f"scene {up.get('scene_model')!r} is not in the benchmark scene list")

    # Incomplete-but-valid: warnings, not errors.
    for gap in task.gaps():
        if gap != "instruction missing upstream":
            rep.warn(where, gap)

    if "_Not yet" in task.body and task.status == "keep":
        rep.warn(where, "marked `keep` but the page still has unwritten template sections")


def check_runs(rep: Report) -> None:
    """The run registry (scripts/runsdb.py): data/agents/<run>.yml, data/prices.yml, state/runs/<benchmark>.yml.

    A benchmark's runs file may only name real tasks, each either in a run or removed from it, never both, and only
    runs that are registered; see docs/contributing/registering-runs.md."""
    import string
    runsdb.agents(), runsdb.prices(), runsdb.plans()
    for path, err in runsdb.ERRORS:
        rep.error(path, f"cannot be read: {err}")
    for rid, agent in runsdb.agents().items():
        where = f"data/agents/{rid}.yml"
        if not agent.get("label"):
            rep.error(where, "no `label`")
        if agent.get("billing") and agent["billing"] not in runsdb.BILLING:
            rep.error(where, f"billing {agent['billing']!r} is not one of {sorted(runsdb.BILLING)}")
        if agent.get("price") and agent["price"] not in runsdb.prices():
            rep.error(where, f"price {agent['price']!r} is not a key of data/prices.yml")
        elif not agent.get("price"):
            rep.warn(where, "no `price`: its cost cannot be estimated")
        modes = agent.get("modes")
        if modes is not None and not (isinstance(modes, list) and all(isinstance(m, str) for m in modes)):
            rep.error(where, "`modes` must be a list of mode names")
        # the id is <harness>-<model>-<effort>[-<tag>], and the file's own fields spell it (registering-runs.md)
        if not runsdb.RUN_ID.match(rid):
            rep.error(where, "the run id must be <harness>-<model>-<effort>[-<tag>], each field [a-z0-9_]+")
        elif runsdb.id_of(agent) != rid:
            rep.error(where, f"the run id does not match its fields: `harness_id`, the model's `id` in data/prices.yml, "
                             f"settings.reasoning_effort and `tag` spell {runsdb.id_of(agent)!r}")
        for old in agent.get("formerly") or []:
            if str(old) in runsdb.agents():
                rep.error(where, f"formerly {old!r} is a registered run id itself")
    seen: dict[str, str] = {}
    for key, price in runsdb.prices().items():     # a model's `id`: its field in a run id, one model per id
        mid = price.get("id")
        if mid is None:
            continue
        if not re.fullmatch(r"[a-z0-9_]+", str(mid)):
            rep.error("data/prices.yml", f"{key}: `id` must be [a-z0-9_]+ (the model's field of a run id)")
        if mid in seen:
            rep.error("data/prices.yml", f"{key}: `id` {mid!r} is also {seen[mid]}'s")
        seen[mid] = key
    for key, price in runsdb.prices().items():
        for k in ("input", "output"):
            if not isinstance(price.get(k), (int, float)):
                rep.error("data/prices.yml", f"{key}: `{k}` must be a number (USD per 1M tokens)")
        if "cached_input" in price and not isinstance(price["cached_input"], (int, float)):
            rep.error("data/prices.yml", f"{key}: `cached_input` must be a number")
    benches = taskdb.benchmarks()
    for bid, plan in runsdb.plans().items():
        where = f"state/runs/{bid}.yml"
        if bid not in benches:
            rep.error(where, f"no benchmark {bid!r} in data/benchmarks/")
            continue
        runs = plan.get("runs")
        if not isinstance(runs, dict) or not runs:
            rep.warn(where, "no `runs:`")
            continue
        if plan.get("default") and plan["default"] not in runs:
            rep.error(where, f"default {plan['default']!r} is not one of its runs")
        for tpl in [plan.get("task_dir")] + [(spec or {}).get("task_dir") for spec in runs.values()]:
            if tpl:
                names = {f for _, f, _, _ in string.Formatter().parse(str(tpl)) if f is not None}
                if names - {"benchmark", "task", "task_dashed"}:
                    rep.error(where, f"task_dir {tpl!r}: only {{benchmark}}, {{task}} and {{task_dashed}} are filled in")
        for m in plan.get("metrics") or []:
            if not isinstance(m, dict) or not isinstance(m.get("key"), str):
                rep.error(where, f"metric {m!r}: needs at least `key`, a reward.json key")
                continue
            try:
                format(1.0, str(m.get("format") or ".2f"))
            except (ValueError, TypeError):
                rep.error(where, f"metric {m['key']}: format {m.get('format')!r} is not a Python format spec (e.g. .3f)")
            if m.get("better") not in (None, "higher", "lower"):
                rep.error(where, f"metric {m['key']}: better must be higher or lower")
            if m.get("summary") not in (None, "mean", "median"):
                rep.error(where, f"metric {m['key']}: summary must be mean or median")
        known = {t.task_id for t in benches[bid].tasks}
        for rid, spec in runs.items():
            here = f"{where} ({rid})"
            if rid not in runsdb.agents():
                rep.error(here, f"run {rid!r} is not registered: add data/agents/{rid}.yml")
            br = runsdb.get(bid, rid)
            spec = spec or {}
            if not spec.get("batch"):
                rep.error(here, "no `batch`")
            if "hidden" in spec and not isinstance(spec["hidden"], bool):
                rep.error(here, "`hidden` must be true or false")
            if spec.get("hidden") is True and plan.get("default") == rid:
                rep.error(here, "the default run cannot be hidden: make another run the default first")
            tasks, removed = list(spec.get("tasks") or []), dict(spec.get("removed") or {})
            for tid in [t for t in tasks if t not in known] + [t for t in removed if t not in known]:
                rep.error(here, f"unknown task {tid!r}")
            for tid in sorted(set(tasks) & set(removed)):
                rep.error(here, f"{tid!r} is both in the run and removed")
            if len(set(tasks)) != len(tasks):
                rep.error(here, "duplicate task ids")
            if not spec.get("others") and known - set(tasks) - set(removed):
                rep.warn(here, f"{len(known - set(tasks) - set(removed))} task(s) neither in the run nor removed, "
                               "and no `others` reason")
            for f in spec.get("stopped") or []:
                if not isinstance(f, dict) or not f.get("note") or f.get("task") not in tasks:
                    rep.error(here, f"stopped {f!r}: needs a task of the run, its mode and a note")
                elif br and f.get("mode") not in br.modes:
                    rep.error(here, f"stopped mode {f.get('mode')!r} is not one of {br.modes}")
            for f in spec.get("followups") or []:
                if not isinstance(f, dict) or not f.get("note"):
                    rep.error(here, f"follow-up {f!r} needs task, mode, trial and note")
                    continue
                if f.get("task") not in tasks:
                    rep.error(here, f"follow-up for {f.get('task')!r}, which is not in the run")
                if br and f.get("mode") not in br.modes:
                    rep.error(here, f"follow-up mode {f.get('mode')!r} is not one of {br.modes}")
                if not f.get("trial"):
                    rep.warn(here, f"follow-up for {f.get('task')} has no `trial`, so it never shows")
            wd = spec.get("withdrawn") or {}
            if not isinstance(wd, dict):
                rep.error(here, "`withdrawn` must map a mode to its reason")
            elif br:
                for m in wd:
                    if m not in br.modes:
                        rep.error(here, f"withdrawn mode {m!r} is not one of {br.modes}")
            for f in spec.get("not_counted") or []:
                if not isinstance(f, dict) or not f.get("note") or not f.get("trial") or f.get("task") not in tasks:
                    rep.error(here, f"not_counted {f!r}: needs a task of the run, its mode, the trial and a note")
                elif br and f.get("mode") not in br.modes:
                    rep.error(here, f"not_counted mode {f.get('mode')!r} is not one of {br.modes}")
            for f in spec.get("notes") or []:
                if not isinstance(f, dict) or not f.get("note") or not f.get("trial"):
                    rep.error(here, f"note {f!r} needs task, mode, trial and note")
                    continue
                if f.get("task") not in tasks:
                    rep.error(here, f"note on {f.get('task')!r}, which is not in the run")
                if br and f.get("mode") not in br.modes:
                    rep.error(here, f"note mode {f.get('mode')!r} is not one of {br.modes}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--quiet", action="store_true", help="only print the summary and errors")
    args = ap.parse_args()

    rep = Report()
    check_registries(rep)
    check_runs(rep)

    total = 0
    for bench in taskdb.benchmarks().values():
        for task in bench.tasks:
            total += 1
            check_task(task, bench, rep)

    if rep.errors:
        print(f"\n{len(rep.errors)} error(s):")
        for line in rep.errors:
            print(f"  ERROR  {line}")
    if rep.warnings and not args.quiet:
        print(f"\n{len(rep.warnings)} warning(s) — incomplete, not invalid:")
        for line in rep.warnings:
            print(f"  warn   {line}")

    print(f"\nchecked {total} task page(s): {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")

    if rep.errors:
        return 1
    if args.strict and rep.warnings:
        print("--strict: failing on warnings")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

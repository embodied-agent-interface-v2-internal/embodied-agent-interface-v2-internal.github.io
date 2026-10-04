"""Renders the task list: one row per task, demo playing in place.

Design constraints, learned the hard way:

  * A task name alone tells a reviewer nothing. The video is the primary
    content, so it gets real estate — a ~22rem player, not a thumbnail.
  * Local MP4 in a <video> element, never an embedded YouTube/Vimeo player,
    because only <video> exposes playbackRate. Reviewing 100 long-horizon
    demos at 1x is not something anyone will actually do; at 3x it is.
  * `preload="none"` plus a poster image: 100 rows cost 100 small images on
    load, and a video downloads only when someone presses play.
"""

from __future__ import annotations

import html
import json

import runsdb
import runview
import sitemode
import taskdb

# `capability` and `domain` are the display tags' two groups (state/display_tags.yml), one filter each.
FACETS = [("status", "Status"), ("runstate", "Run state"), ("scene", "Scene"), ("room", "Room"),
          ("capability", "Capability"), ("domain", "Task Domain"), ("difficulty", "Difficulty")]

SPEEDS = ["1", "2", "3", "4"]


def _payload(bench: taskdb.Benchmark, asset_root: str) -> list[dict]:
    tags = taskdb.tag_index()
    manifest = taskdb.demo_manifest(bench.id)
    media_base = f"{asset_root}{taskdb.demo_dir(bench.id)}"
    scene_base = f"{asset_root}{taskdb.scene_dir(bench.id)}"
    linked = sitemode.links_demos(bench.id)       # the public build links these demos to upstream (sitemode.py)
    out = []
    for t in sorted(bench.tasks, key=lambda t: t.title):
        runs = _shown_runs(t.runs)
        entry = manifest.get(t.task_id)
        # Prefer the locally extracted frame; fall back to the upstream
        # thumbnail so a contributor who has not run `make demos` still sees
        # something rather than a grey box.
        if entry and entry.get("poster"):
            poster = f"{media_base}{t.task_id}.jpg"
        elif t.scene_image:
            # No video for this task: the scene it starts from is what makes
            # the row worth looking at.
            poster = f"{scene_base}{t.scene_image}"
        else:
            poster = t.upstream.get("oracle_thumbnail", "")
        out.append({
            "id": t.task_id,
            "title": t.title,
            "url": f"tasks/{t.task_id}/",
            "instruction": t.instruction,
            "poster": poster,
            "aspect": (
                f"{entry['width']} / {entry['height']}"
                if entry and entry.get("width") and entry.get("height")
                else "1 / 1"
            ),
            "src": f"{media_base}{t.task_id}.mp4" if entry and not linked else "",
            "fallback": t.upstream.get("oracle_video", ""),
            # the upstream video to open instead, where this build does not carry our copy
            "watch": t.upstream.get("oracle_video", "") if linked else "",
            # Whether upstream publishes a demo at all. Without it, a row with
            # no video is "nothing to download", not "you have not downloaded".
            "published": bool(t.upstream.get("oracle_video")),
            "scene": t.scene,
            "rooms": t.rooms,
            "roomLabel": ", ".join(taskdb.humanize(r) for r in t.rooms),
            "duration": t.duration,
            "durationLabel": taskdb.fmt_duration(t.duration),
            "status": t.status,
            "difficulty": t.difficulty,
            # why the task is not part of the final benchmark (state `excluded:`), "" if it is: greyed, last
            "excluded": t.excluded,
            "owner": t.owner,
            # the display tags (`display_tags:`), Capability first, then Task Domain; the detailed labels are not sent
            "caps": [tags[c]["name"] if c in tags else c for c in t.display_tags],
            "capIds": t.display_tags,
            # each tag's group, which colours its chip
            "capGroups": [tags[c]["group_id"] if c in tags else "" for c in t.display_tags],
            "skills": t.skills,
            # One entry per run of the benchmark; the page shows the one picked in its Run menu (the default run
            # first). "" = the order without any run: the review decision.
            "runs": {br.run: _run(t, br, view, asset_root) for br, view in runs},
            "runTags": {br.run: runview.task_tags(view) for br, view in runs},
            "runRank": {br.run: runview.task_rank(view) for br, view in runs},
            "order": {"": runview.default_rank(None, t.status, t.difficulty, bool(t.excluded)),
                      **{br.run: runview.default_rank(view, t.status, t.difficulty, bool(t.excluded))
                         for br, view in runs}},
        })
    return out


def _run(t: taskdb.Task, br, view: dict, asset_root: str) -> dict:
    """One run's view of a row: why it is out, or one pill per mode (linking to its log page, if any)."""
    if not view["in"]:
        return {"in": False, "removed": view.get("removed", False), "reason": view["reason"]}
    modes = []
    for mode, rec in view["modes"].items():
        logs, missing = runview.logs_state(rec, mode)
        modes.append({
            "mode": mode,
            "short": runview.MODE_SHORT.get(mode, mode[:1].upper()),
            "state": rec.get("state", "queued"),
            "label": runview.result_label(rec),
            "active": rec.get("state") in runview.ACTIVE,
            "started": rec.get("started"),
            "title": runview.title(rec, mode, br),
            "logs": logs,
            "missing": missing,
            "log": (f"{asset_root}{runview.log_page(t.benchmark, br.run, t.task_id, mode)[:-3]}/"
                    if runview.has_log(t.benchmark, br.run, t.task_id, mode) else ""),
        })
    return {"in": True, "modes": modes}


def _shown_runs(pairs: list) -> list:
    """(run, view) pairs worth a pill: all of them locally; on the public site (scripts/sitemode.py), which carries
    no collected run data, only runs that have some."""
    return [(br, view) for br, view in pairs if br.data or not sitemode.PUBLIC]


def _runs_meta(bench: taskdb.Benchmark) -> list[dict]:
    """The benchmark's runs for the Run menu, default first, with each run's Run state facet values."""
    out = []
    for br in runsdb.runs_of(bench.id):
        if sitemode.PUBLIC and not br.data:
            continue
        values = [v for v in runview.STATES + ["outside", "removed"]
                  if any(v in runview.task_tags(br.view(t.task_id)) for t in bench.tasks)]
        out.append({"id": br.run, "label": br.label, "short": br.short, "default": br.default, "closed": bool(br.closed),
                    "values": [[v, runview.STATE_LABEL.get(v) or runview.OUT_LABEL[v]] for v in values]})
    return out


def render(bench: taskdb.Benchmark, asset_root: str = "") -> str:
    tasks = bench.tasks
    tags = taskdb.tag_index()
    payload = _payload(bench, asset_root)
    runs = _runs_meta(bench)

    values = {
        "scene": sorted({t.scene for t in tasks}),
        "room": sorted({r for t in tasks for r in t.rooms}),
        "status": [s for s in taskdb.STATUSES if any(t.status == s for t in tasks)],
        "difficulty": [d for d in taskdb.DIFFICULTIES if any(t.difficulty == d for t in tasks)],
        **{group: taskdb.ordered_tags({c for t in tasks for c in t.display_tags
                                        if tags.get(c, {}).get("group_id") == group})
           for group in taskdb.TAG_GROUPS},
        # the default run's states; the page swaps in another run's when its Run menu changes
        "runstate": [v for v, _ in (runs[0]["values"] if runs else [])],
    }
    labels = {c: tags[c]["name"] for group in taskdb.TAG_GROUPS for c in values[group]}
    labels.update({v: runview.STATE_LABEL.get(v) or runview.OUT_LABEL[v] for v in values["runstate"]})

    bar = ['<span class="tl__searchwrap">'
           '<input type="search" class="tl__search" data-role="search" '
           'placeholder="Search name or instruction…" aria-label="Search tasks">'
           '<button type="button" class="tl__searchgo" data-role="search-go" '
           'aria-label="Search">Search</button></span>']
    if runs:
        # Which run the pills, the Run state filter and the default order are about (the benchmark's default first).
        opts = "".join(f'<option value="{html.escape(r["id"])}" title="{html.escape(r["label"])}">'
                       f'{html.escape(r["short"])}{" · default" if r["default"] else ""}'
                       f'{" · closed" if r["closed"] else ""}</option>' for r in runs)
        bar.append(f'<select data-role="run" class="tl__run" aria-label="Run">{opts}</select>')
    for facet, label in FACETS:
        if not values[facet]:
            continue
        opts = "".join(
            f'<option value="{html.escape(v)}">'
            f'{html.escape(labels.get(v, taskdb.humanize(v)))}</option>'
            for v in values[facet])
        bar.append(f'<select data-facet="{facet}" aria-label="Filter by {label}">'
                   f'<option value="">{label}: any</option>{opts}</select>')
    bar.append('<select data-role="sort" aria-label="Sort">'
               '<option value="review">Default order</option>'
               '<option value="title">A\u2013Z</option>'
               '<option value="duration-asc">Shortest first</option>'
               '<option value="duration-desc">Longest first</option>'
               + ('<option value="run">Run state</option>' if runs else "")
               + "</select>")
    bar.append('<button type="button" data-role="reset" class="tl__reset">Reset</button>')

    speed = "".join(
        f'<button type="button" data-speed="{s}"'
        f'{" class=is-on" if s == "2" else ""}>{s}&times;</button>' for s in SPEEDS)

    return (
        '<div class="tl" data-tasklist>'
        f'<div class="tl__bar">{"".join(bar)}</div>'
        '<div class="tl__sub">'
        f'<span class="tl__speed">Speed <span class="tl__speedbtns">{speed}</span></span>'
        '<span class="tl__count" data-role="count"></span>'
        "</div>"
        '<div class="tl__rows" data-role="rows"></div>'
        '<p class="tl__empty" data-role="empty" hidden>No task matches these filters.</p>'
        "</div>\n"
        '<script type="application/json" id="tl-data">'
        + json.dumps(payload, ensure_ascii=False) + "</script>"
        '<script type="application/json" id="tl-runs">'
        + json.dumps(runs, ensure_ascii=False) + "</script>"
    )

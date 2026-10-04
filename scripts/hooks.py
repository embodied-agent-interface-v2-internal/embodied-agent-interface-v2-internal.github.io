"""MkDocs build hook.

Two jobs:
  1. Build the header of every task page from frontmatter — facts, instruction,
     local demo player, display tags. Contributors write prose only; no
     data is duplicated into the body, so an upstream re-sync updates every
     page at once.
  2. Expand `<!-- gen:... -->` placeholders so hand-written pages can embed the
     task list and live counts without anyone maintaining them.

Note on paths: markdown links are resolved by MkDocs relative to the *source*
file, but raw HTML `src=` attributes are not touched, so they must be relative
to the *output URL*. The two depths differ, and `page.url` gives the second.
"""

from __future__ import annotations

import hashlib
import html
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gallery  # noqa: E402
import runpages  # noqa: E402
import runview  # noqa: E402
import sitemode  # noqa: E402
import taskdb  # noqa: E402

PLACEHOLDER_RE = re.compile(r"^<!--\s*gen:(?P<kind>[\w.-]+)(?P<args>[^>]*?)-->\s*$", re.M)
SPEEDS = ["1", "2", "3", "4"]


def on_config(config):
    """Reset caches for this build, and content-hash our own CSS/JS.

    Cache-hashing: MkDocs fingerprints the theme's bundled assets but leaves
    `extra_css` / `extra_javascript` as bare filenames, which browsers cache
    hard — an edit to tasklist.js then silently does nothing until a forced
    reload, which looks exactly like the feature was never built.

    Appending a digest of the file contents makes the URL change whenever the
    file does, and stay put when it does not.
    """
    # `mkdocs serve` reuses this process across rebuilds, so memoised task and
    # taxonomy data would otherwise survive an edit and the page would never
    # update. on_config runs once per build, which is the right moment.
    taskdb.reset_caches()

    docs = Path(config["docs_dir"])

    def stamp(entry):
        # mkdocs 1.6 may hand back ExtraScriptValue rather than a plain str.
        path = getattr(entry, "path", entry)
        if not isinstance(path, str) or "://" in path or "?" in path:
            return entry
        target = docs / path
        if not target.is_file():
            return entry
        digest = hashlib.sha256(target.read_bytes()).hexdigest()[:8]
        stamped = f"{path}?h={digest}"
        if hasattr(entry, "path"):
            entry.path = stamped
            return entry
        return stamped

    config["extra_css"] = [stamp(x) for x in config.get("extra_css") or []]
    config["extra_javascript"] = [stamp(x) for x in config.get("extra_javascript") or []]
    config["nav"] = _runs_nav(config.get("nav"))
    if sitemode.PUBLIC:
        # The public site is read-only: no "edit this page" link (scripts/sitemode.py).
        features = config["theme"]["features"]
        if "content.action.edit" in features:
            features.remove("content.action.edit")
    return config


def on_files(files, config):
    """What the public build (scripts/sitemode.py) leaves out: the log pages' data, docs/assets/<benchmark>/runs/
    (local only; present on a machine that collects runs), and the MP4s of the benchmarks whose demos it links to
    upstream instead (RB_PUBLIC_LINK_DEMOS). Their posters and every other file stay."""
    if not sitemode.PUBLIC:
        return files
    drop = [f for f in files if re.match(r"assets/[^/]+/runs/", f.src_uri)
            or (f.src_uri.endswith(".mp4") and any(f.src_uri.startswith(taskdb.demo_dir(b)) for b in sitemode.LINK_DEMOS))]
    for f in drop:
        files.remove(f)
    return files


def _runs_nav(nav):
    """Append one Runs page per registered benchmark to the "Runs" section, after its Overview.

    The pages are generated for every benchmark in data/benchmarks/ (scripts/gen_pages.py), so a new benchmark
    appears here without anyone editing mkdocs.yml. Same order as the Benchmarks section; any benchmark not
    listed there follows, by id."""
    if not isinstance(nav, list):
        return nav
    order = []

    def walk(item):
        if isinstance(item, str):
            m = re.match(r"benchmarks/([^/]+)/index\.md$", item)
            if m and m.group(1) not in order:
                order.append(m.group(1))
        elif isinstance(item, dict):
            for v in item.values():
                walk(v)
        elif isinstance(item, list):
            for v in item:
                walk(v)

    walk(nav)
    benches = taskdb.benchmarks()
    ids = [b for b in order if b in benches] + sorted(b for b in benches if b not in order)
    for entry in nav:
        key = next((k for k in ("Agent runs", "Runs") if isinstance(entry, dict) and k in entry), None)
        if key:
            section = entry[key]
            section = section if isinstance(section, list) else [section]
            have = {v for x in section for v in (x.values() if isinstance(x, dict) else [x]) if isinstance(v, str)}
            section += [{benches[b].name: runview.runs_page(b)} for b in ids if runview.runs_page(b) not in have]
            entry[key] = section
    return nav


def doc_url(md_path: str, url_root: str) -> str:
    """Turn a docs-relative .md path into a link usable from raw HTML.

    MkDocs rewrites `.md` links written in Markdown, but leaves `href`
    attributes inside raw HTML completely alone — they ship verbatim and 404.
    Anything emitted as HTML must therefore be a finished URL, and must be
    relative to the page's OUTPUT url (page.url), not its source path.
    """
    if md_path.endswith("/index.md"):
        md_path = md_path[: -len("index.md")]
    elif md_path.endswith(".md"):
        md_path = md_path[: -len(".md")] + "/"
    return url_root + md_path


def _speed_buttons() -> str:
    btns = "".join(
        f'<button type="button" data-speed="{s}"'
        f'{" class=is-on" if s == "2" else ""}>{s}&times;</button>'
        for s in SPEEDS
    )
    return f'<div class="demo__speed">Playback speed <span class="btns">{btns}</span></div>'


def _demo(task: taskdb.Task, asset_root: str) -> str:
    """The oracle demo as a local <video>.

    A local file rather than a YouTube/Vimeo embed: only a real <video>
    element exposes playbackRate, and these demos average nearly six minutes.
    Media is per benchmark: docs/assets/<benchmark>/demos/<task_id>.mp4.
    """
    demos = taskdb.demo_dir(task.benchmark)
    watch = task.upstream.get("oracle_video", "")
    if sitemode.links_demos(task.benchmark) and watch:
        # The public build links this benchmark's demos to upstream instead of carrying our copies
        # (scripts/sitemode.py): the poster we extracted, and the official video one click away.
        entry = taskdb.demo_manifest(task.benchmark).get(task.task_id) or {}
        poster = (f"{asset_root}{demos}{task.task_id}.jpg" if entry.get("poster")
                  else task.upstream.get("oracle_thumbnail", ""))
        host = re.sub(r"^(?:www|player)\.", "", re.sub(r"^https?://([^/]+).*$", r"\1", watch))
        img = (f'<img class="demo__scene" src="{html.escape(poster)}" alt="{html.escape(task.title)}: demo poster" '
               'loading="lazy">' if poster else "")
        return (f'<div class="demo demo--linked">{img}<p class="demo__watch"><a href="{html.escape(watch)}" '
                f'target="_blank" rel="noopener">Watch the official demo on {html.escape(host)} &#8599;</a></p></div>')
    if not task.has_demo:
        # No demo published for this task. A scene preview is not a
        # demonstration, but it is the difference between reviewing the row and
        # guessing at it, so show it and say what it is.
        if task.scene_image:
            src = f"{asset_root}{taskdb.scene_dir(task.benchmark)}{task.scene_image}"
            return (
                f'<div class="demo"><img class="demo__scene" src="{html.escape(src)}"'
                f' alt="{html.escape(task.scene)} scene" loading="lazy">'
                '<div class="demo__none demo__none--tight"><span>No oracle video published upstream'
                " — this is the scene it starts from.</span></div></div>"
            )
        return (
            '<div class="demo"><div class="demo__none">'
            "<span>No oracle demo for this task.</span>"
            "<span>Run <code>make demos</code> to fetch the ones published upstream.</span>"
            "</div></div>"
        )
    entry = taskdb.demo_manifest(task.benchmark).get(task.task_id) or {}
    poster = (
        f"{asset_root}{demos}{task.task_id}.jpg"
        if entry.get("poster")
        else task.upstream.get("oracle_thumbnail", "")
    )
    # These demos are square (the head camera is 720x720). A hardcoded 16:9
    # frame pillarboxes every one of them.
    aspect = (
        f"{entry['width']} / {entry['height']}"
        if entry.get("width") and entry.get("height")
        else "1 / 1"
    )
    video = (
        f'<video data-demo controls playsinline preload="metadata" style="aspect-ratio:{aspect}"'
        + (f' poster="{html.escape(poster)}"' if poster else "")
        + f' src="{asset_root}{demos}{task.task_id}.mp4"></video>'
    )
    # Where a clip came from, when it is not the benchmark's own published demo.
    credit = entry.get("source", "")
    note = f'<p class="demo__credit">{html.escape(credit)}</p>' if credit else ""
    return f'<div class="demo">{video}{_speed_buttons()}{note}</div>'


# What a benchmark states about a task beyond the instruction: the success
# criteria, what is in the scene, how long an episode may run. Keys already in
# the page header are folded out; anything unlisted still renders, after these.
UPSTREAM_ROWS: list[tuple[str, str]] = [
    ("success_criteria", "Success criteria"),
    ("success_predicate", "Success predicate"),
    ("success_params", "Predicate arguments"),
    ("subtasks", "Scored subtasks"),
    ("subtask_predicates", "Subtask predicates"),
    ("objects", "Objects"),
    ("object_materials", "Physics"),
    ("attributes", "Upstream attributes"),
    ("difficulty_label", "Upstream difficulty"),
    ("episode_length_s", "Episode budget"),
    ("episode_steps_default", "Episode budget"),
    ("control_mode_default", "Default control mode"),
    ("eval_scenes", "Evaluation scenes"),
    ("mutations", "Published mutations"),
    ("blenderkit_assets", "BlenderKit assets"),
    ("instruction_variants", "Other wordings"),
    ("registry_id", "Registry id"),
    ("env_class", "Environment class"),
    ("task_name", "Upstream name"),
    ("source_file", "Defined in"),
    # RoboTwin 2.0
    ("asset_models", "Asset models"),
    ("embodiments", "Embodiments"),
    ("data_gen_success", "Data-generation success (scripted expert, per embodiment)"),
    ("average_steps", "Average demo length"),
    ("eval_step_limit", "Episode budget"),
    ("expert_planned_motions", "Expert: planned motions"),
    ("expert_methods", "Expert methods (scrubbed from our agent image)"),
    ("success_check", "Success check (verbatim)"),
    ("doc_url", "Task documentation"),
    ("oracle_video_world", "Official world-view clip"),
]

UPSTREAM_FOLDED = {"source", "synced", "cohort", "instruction", "scene_model", "rooms",
                   "demo_duration_s", "oracle_video", "oracle_thumbnail", "scene_image",
                   "scene_usda", "oracle_video_source", "oracle_video_instruction",
                   "oracle_video_matched", "task_number", "average_steps_note", "videos"}


def _upstream_value(key: str, value, block: dict) -> str:
    if key == "success_criteria" and isinstance(value, list):
        return "<br>".join(f"{i}. {html.escape(str(v))}" for i, v in enumerate(value, 1))
    if key == "instruction_variants" and isinstance(value, dict):
        return "<br>".join(f"*{html.escape(k)}* — {html.escape(str(v))}" for k, v in value.items())
    if key == "success_params" and isinstance(value, dict):
        return " · ".join(f"`{k}`: {v}" for k, v in value.items())
    if key in ("episode_length_s",):
        return f"{value} s"
    if key in ("episode_steps_default",):
        return f"{value} control steps"
    if key == "blenderkit_assets":
        return f"{value} (not redistributable — mounted from the host)"
    if key == "source_file":
        return f"`{value}`"
    if key == "eval_step_limit":
        return f"{value} policy actions (RoboTwin's evaluation budget)"
    if key == "average_steps":
        return f"{value} recorded steps at save_freq=15 (ALOHA-AgileX), about {int(value) * 15:,} physics steps"
    if key == "success_check":
        # Multi-line code inside a one-line Markdown table row: escape, then <br> per line, keeping indentation.
        lines = [html.escape(l).replace(" ", "&nbsp;") for l in str(value).splitlines()]
        return '<code style="white-space:pre;display:block">' + "<br>".join(lines) + "</code>"
    if key in ("doc_url", "oracle_video_world"):
        return f'<a href="{html.escape(str(value))}">{html.escape(str(value))}</a>'
    if isinstance(value, dict):
        def _v(v):
            return ", ".join(f"`{x}`" for x in v) if isinstance(v, list) else html.escape(str(v))
        return "<br>".join(f"*{html.escape(str(k))}* — {_v(v)}" for k, v in value.items())
    if isinstance(value, list):
        return " ".join(f"`{v}`" for v in value) if value else "—"
    return str(value)


def _upstream_facts(task: taskdb.Task) -> str:
    """The benchmark's own description of the task, past the instruction.

    BEHAVIOR publishes little more than the instruction, so this is empty there.
    RoboWits states its success criteria in the environment's docstring and
    RoboLab declares predicate, subtasks and attributes in the task class — all
    of it worth reading before deciding whether to keep a task.
    """
    block = task.upstream or {}
    rows = []
    for key, label in UPSTREAM_ROWS:
        if key in block and block[key] not in (None, [], {}, ""):
            rows.append(f"    | {label} | {_upstream_value(key, block[key], block)} |")
    extra = [k for k in block if k not in UPSTREAM_FOLDED
             and k not in {key for key, _ in UPSTREAM_ROWS} and block[k] not in (None, [], {}, "")]
    for key in extra:
        rows.append(f"    | {taskdb.humanize(key)} | {_upstream_value(key, block[key], block)} |")
    if not rows:
        return ""
    bench = taskdb.benchmarks().get(task.benchmark)
    name = bench.name if bench else task.benchmark
    out = [f'\n??? note "What {name} states about this task"', "",
           "    | | |", "    | --- | --- |", *rows]
    source = block.get("source", "")
    if source:
        out += ["", f"    From {source}."]
    return "\n".join(out) + "\n"


# The `verified:` frontmatter zone, rendered in a fixed order with the units
# spelled out. Anything not listed here still renders, after these, with a
# humanised key — a new benchmark can add facts without touching this table.
VERIFIED_ROWS: list[tuple[str, str]] = [
    ("goal_predicates", "Goal predicates"),
    ("goal_quantifiers", "Quantifiers"),
    ("goal_counts", "Counted quantities"),
    ("goal_clauses", "Goal clauses"),
    ("goal_categories", "Objects named in the goal"),
    ("objects", "Objects in the problem"),
    ("rooms_loaded", "Rooms loaded"),
    ("demo_episodes", "Demonstrations"),
    ("demo_mean_s", "Mean episode"),
    ("demo_distance_m", "Base travel, mean"),
    ("demo_eef_m", "Gripper travel, mean"),
    ("test_instances", "Evaluation instances"),
    ("action_dim", "Action vector"),
    ("control_hz", "Control rate"),
    ("episode_steps", "Episode budget"),
    ("physics", "Physics"),
    ("assets", "Assets required"),
    ("eval_scenes", "Evaluation scenes"),
    ("success_check", "Success check"),
    ("harness", "In our harness"),
]

# Keys folded into another row, or already shown in the page header.
VERIFIED_FOLDED = {"source", "stack", "checked", "scene_model", "demo_mean_steps",
                   "object_categories", "test_instance_ids"}


def _chips(values: list) -> str:
    return " ".join(f"`{v}`" for v in values)


def _verified_value(key: str, value, block: dict) -> str:
    """One row's value, with the units and any companion field folded in."""
    if key == "objects":
        cats = block.get("object_categories")
        return f"{value} in {cats} categories" if cats else str(value)
    if key == "demo_episodes":
        return f"{value} teleoperated episodes"
    if key == "demo_mean_s":
        steps = block.get("demo_mean_steps")
        out = taskdb.fmt_duration(int(value))
        return f"{out} ({steps:,.0f} control steps at 30 Hz)" if steps else out
    if key == "demo_distance_m":
        return f"{value} m"
    if key == "demo_eef_m" and isinstance(value, list) and len(value) == 2:
        return f"left {value[0]} m · right {value[1]} m"
    if key == "test_instances":
        ids = block.get("test_instance_ids")
        return f"{value} public test instances" + (f" (ids {ids[0]}–{ids[-1]})" if ids else "")
    if key == "control_hz":
        return f"{value} Hz"
    if key == "episode_steps":
        return f"{value:,} control steps"
    if isinstance(value, list):
        return _chips(value) if value else "—"
    return str(value)


def _verified(task: taskdb.Task) -> str:
    """Facts read first-hand from the stack we run, as a collapsible table.

    Collapsed by default: it is reference material you open when a number
    matters, not something to scroll past on every page.
    """
    block = task.meta.get("verified") or {}
    if not block:
        return ""
    rows = []
    for key, label in VERIFIED_ROWS:
        if key in block and block[key] not in (None, [], ""):
            rows.append(f"    | {label} | {_verified_value(key, block[key], block)} |")
    extra = [k for k in block if k not in VERIFIED_FOLDED
             and k not in {key for key, _ in VERIFIED_ROWS} and block[k] not in (None, [], "")]
    for key in extra:
        rows.append(f"    | {taskdb.humanize(key)} | {_verified_value(key, block[key], block)} |")
    if not rows:
        return ""

    stack = block.get("stack", "")
    checked = block.get("checked", "")
    summary = "Measured on the stack we run" + (f" — {stack}" if stack else "")
    out = [f'\n??? abstract "{summary}"', ""]
    out.append("    | | |")
    out.append("    | --- | --- |")
    out.extend(rows)
    source = block.get("source", "")
    if source or checked:
        out.append("")
        out.append(f"    Read from {source}" + (f", {checked}." if checked else "."))
    return "\n".join(out) + "\n"


def _display_tags(task: taskdb.Task, link_root: str, url_root: str) -> str:
    tags = taskdb.tag_index()
    if not task.display_tags:
        return (
            "\n## Tags\n\n"
            '!!! danger "Not tagged yet"\n\n'
            "    No tags on this task yet. Applying them is the most useful\n"
            f"    contribution you can make here — see the\n"
            f"    [label taxonomy]({link_root}reference/capabilities.md).\n"
        )
    # One row per group, Capability before Task Domain (state/display_tags.yml's order), each in its group's colour.
    # The detailed labels (`labels:`) are not shown.
    rows = []
    for group, ids in task.tag_groups:
        chips = "".join(f'<a class="chip chip--{group["id"]}" href="{doc_url("reference/capabilities.md", url_root)}'
                        f'#{tags[tid]["anchor"]}">{html.escape(tags[tid]["name"])}</a>' for tid in ids)
        chips = chips or '<span class="chip chip--gap">none yet</span>'
        rows.append(f'<div class="row__labels"><span class="row__group">{html.escape(group["name"])}</span>'
                    f"{chips}</div>")
    unknown = [tid for tid in task.display_tags if tid not in tags]
    if unknown:
        rows.append('<div class="row__labels"><span class="row__group">Unknown</span>'
                    + "".join(f'<span class="chip chip--gap">{html.escape(tid)}</span>' for tid in unknown)
                    + "</div>")
    out = f'\n## Tags\n\n{"".join(rows)}\n'
    if task.skills:
        skills = "".join(f'<span class="chip">{html.escape(s)}</span>' for s in task.skills)
        out += f'\n**Skill primitives in the demo:** <span class="row__labels">{skills}</span>\n'
    return out


def _extra_media(media: list, asset_root: str) -> str:
    cards = []
    for item in media or []:
        if not isinstance(item, dict):
            continue
        kind, url = item.get("kind", "link"), item.get("url", "")
        caption, credit = item.get("caption", url), item.get("credit", "")
        if kind == "image":
            inner = f'<img src="{html.escape(url)}" alt="{html.escape(caption)}" loading="lazy">'
        elif kind == "video":
            inner = f'<video controls playsinline preload="none" src="{html.escape(url)}"></video>'
        else:
            inner = f'<a href="{html.escape(url)}">{html.escape(caption)}</a>'
        meta = f"<figcaption>{html.escape(caption)}"
        meta += f" — {html.escape(credit)}" if credit else ""
        cards.append(f'<figure class="media-card">{inner}{meta}</figcaption></figure>')
    if not cards:
        return ""
    return f'\n\n## Contributed media\n\n<div class="media-grid">{"".join(cards)}</div>\n'


def _task_header(task: taskdb.Task, link_root: str, asset_root: str) -> str:
    # One scannable line. The things worth dwelling on are the instruction and
    # the video, so those get the space instead of a grid of labelled boxes.
    bits = [
        f'<span class="pill pill--{task.status}">{task.status}</span>',
        f'<span><code>{html.escape(task.scene)}</code></span>',
        f'<span>{", ".join(taskdb.humanize(r) for r in task.rooms) or "—"}</span>',
        f"<span>{taskdb.fmt_duration(task.duration)}</span>",
    ]
    if task.difficulty != "unrated":
        bits.insert(1, f'<span class="pill pill--d-{task.difficulty}">{task.difficulty}</span>')
    if task.excluded:
        bits.insert(0, '<span class="pill pill--excluded">excluded</span>')
    bits.append(
        f"<span>@{html.escape(task.owner)}</span>" if task.owner
        else '<span class="missing">unowned</span>'
    )

    out = ['<div class="meta">' + "".join(bits) + "</div>"]
    if task.excluded:
        # The owner's call (state `excluded:`), apart from the review status: said first, in their words.
        out.append(
            '\n<div class="admonition excluded"><p class="admonition-title">Excluded from the benchmark</p>'
            f"<p>{html.escape(task.excluded)}</p>"
            '<p class="runs-hosts">Greyed and last in the task list, left out of the benchmark\'s numbers; its demo and '
            f"agent runs stay (<code>excluded:</code> in <code>state/tasks/{html.escape(task.benchmark)}.yml</code>).</p></div>\n")
    out.append(_run_block(task, link_root, asset_root))

    if task.instruction:
        out.append('\n!!! quote "Task instruction (upstream)"\n\n    '
                   + task.instruction.replace("\n", "\n    ") + "\n")
    else:
        hint = (
            "    The 2025 carryover tasks ship without instruction text. Watch the\n"
            if task.benchmark == "behavior-1k"
            else "    This task ships no instruction text upstream. Watch the\n"
        )
        out.append(
            '\n!!! warning "No instruction published upstream"\n\n'
            + hint
            + "    demo and write the goal in your own words below, clearly marked as\n"
            "    a reconstruction rather than the official goal.\n"
        )

    out.append("\n" + _demo(task, asset_root))
    out.append(_upstream_facts(task))
    out.append(_verified(task))
    out.append(_display_tags(task, link_root, asset_root))
    out.append(_extra_media(task.state.get("media") or [], asset_root))
    return "\n".join(out)


def _run_block(task: taskdb.Task, link_root: str, url_root: str) -> str:
    """Where this task stands in each of its benchmark's runs (the default run first), and whether every record of
    its trials was kept."""
    # the public build carries no collected run data (data/runs/ is local only): runs without any are left out
    runs = [(br, view) for br, view in task.runs if br.data or not sitemode.PUBLIC]
    if not runs:
        return ""
    page = doc_url(runview.runs_page(task.benchmark), url_root)
    parts = []
    for br, view in runs:
        billed = view["in"] and any(r.get("billed_usd") is not None for r in view["modes"].values())
        tags = "".join(f'<span class="runtag runtag--{k}">{v}</span>' for k, v in
                       (("default", "default run"), ("closed", "closed")) if (k == "default" and br.default)
                       or (k == "closed" and br.closed))
        head = (f'<p class="runblock__head"><a href="{page}?run={html.escape(br.run)}">{html.escape(br.label)}</a>'
                f"{tags}</p>")
        if not view["in"]:
            what = "Removed from this run" if view.get("removed") else "Not in this run"
            parts.append(f'<div class="runblock runblock--out">{head}<p>{what}: {html.escape(view["reason"])}</p></div>')
            continue
        rows, checks = [], []
        for mode, rec in view["modes"].items():
            rw = rec.get("reward") or {}
            href = (doc_url(runview.log_page(task.benchmark, br.run, task.task_id, mode), url_root)
                    if runview.has_log(task.benchmark, br.run, task.task_id, mode) else None)
            t = rec.get("tokens") or {}
            est = runview.estimate(rec, br)
            rows.append(
                "<tr>"
                f"<td>{runview.pill_html(mode, rec, href=href, br=br)}</td>"
                + ("" if sitemode.PUBLIC else f"<td>{html.escape(rec.get('host') or '—')}</td>") +
                f"<td>{runview.local(rec.get('started'))}</td>"
                f"<td>{runview.minutes(rec.get('agent_wall_s'))}</td>"
                f"<td>{rec.get('calls') if rec.get('calls') is not None else '—'}</td>"
                f"<td>{runview.tok(t.get('input'))} / {runview.tok(t.get('output'))}</td>"
                f"<td>{runview.usd(est)}</td>"
                + (f"<td>{runview.usd(rec.get('billed_usd'))}</td>" if billed else "")
                + f"<td>{html.escape(', '.join(f'{k} {v}' for k, v in rw.items() if k != 'success') or (rec.get('exception') or '—'))}</td>"
                "</tr>")
            items = runview.log_checks(rec, mode)
            if items:
                mark = {True: "✓", False: "✗", None: "…"}
                lis = "".join(f"<li>{mark[ok]} {html.escape(name)}"
                              + (f" <span class='runs-hosts'>{html.escape(d)}</span>" if d else "") + "</li>"
                              for name, ok, d in items)
                where = html.escape(f"{rec.get('host')}: {rec.get('job')}/{rec.get('trial') or ''}")
                checks.append(f"<details><summary>{html.escape(mode)} records</summary>"
                              f"<p class='runs-hosts'><code>{where}</code></p><ul>{lis}</ul></details>")
        parts.append(
            f'<div class="runblock">{head}'
            '<table><thead><tr><th>Trial</th>' + ("" if sitemode.PUBLIC else "<th>Host</th>") + '<th>Started</th><th>Agent time</th>'
            '<th>Model requests</th><th>Tokens in / out</th><th>Est. cost</th>'
            + ("<th>Billed</th>" if billed else "") + '<th>Grade</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table>" + "".join(checks) + "</div>")
    # The default run leads; the others fold away, so a task with many runs still opens on its video.
    if len(parts) > 1:
        parts = [parts[0], f'<details class="runblock-more"><summary>{len(parts) - 1} other run(s) of '
                           f"{html.escape(taskdb.benchmarks()[task.benchmark].name)}</summary>" + "".join(parts[1:]) + "</details>"]
    return (
        '\n<div class="admonition info runs-task"><p class="admonition-title">Agent runs</p>'
        f'<p>Each mode of this task runs once per run. Est. cost is tokens at list price (data/prices.yml), '
        f'never a bill; see the <a href="{page}">{html.escape(taskdb.benchmarks()[task.benchmark].name)} runs</a> '
        "for every task of a run.</p>"
        + "".join(parts) + "</div>\n"
    )


# ─────────────────────────────────────────────────────────────── placeholders


def _stats(bench_id: str) -> str:
    bench = taskdb.benchmarks().get(bench_id)
    if not bench:
        return f"<!-- unknown benchmark: {bench_id} -->"
    # The benchmark's own tasks; the ones excluded from it (state `excluded:`) are counted apart, beside them.
    tasks, excluded = bench.included, bench.excluded
    by = {s: sum(1 for t in tasks if t.status == s) for s in taskdb.STATUSES}
    cards = [
        ("Tasks", str(len(tasks)), ""),
        *([("Excluded", f"+ {len(excluded)}", "stat--excluded")] if excluded else []),
        ("Keep", str(by["keep"]), ""),
        ("Drop", str(by["drop"]), ""),
        ("Untriaged", str(by["pending"]), ""),
        ("Tagged", f"{sum(1 for t in tasks if t.tagged)}/{len(tasks)}", ""),
        # the public build links some benchmarks' demos to the official videos instead (scripts/sitemode.py)
        (("Demos (official, linked)", f"{sum(1 for t in tasks if t.upstream.get('oracle_video'))}/{len(tasks)}", "")
         if sitemode.links_demos(bench_id) else
         ("Demos local", f"{len(taskdb.local_demos(bench_id) & {t.task_id for t in tasks})}/{len(tasks)}", "")),
    ]
    tip = (f"{len(tasks)} tasks in the benchmark + {len(excluded)} excluded from it (state `excluded:`): kept on the "
           "site, greyed at the bottom of the list, left out of the other counts")
    inner = "".join(f"<div class='stat{' ' + c if c else ''}'" + (f" title='{html.escape(tip, quote=True)}'" if c else "")
                    + f"><b>{v}</b><span>{k}</span></div>" for k, v, c in cards)
    return f'<div class="stats">{inner}</div>'


def _benchmark_table(link_root: str) -> str:
    lines = ["| Benchmark | Simulator | Tasks | Triaged |", "| --- | --- | --- | --- |"]
    for bench in taskdb.benchmarks().values():
        tasks, excluded = bench.included, bench.excluded
        triaged = sum(1 for t in tasks if t.status != "pending")
        lines.append(
            f"| [{bench.name}]({link_root}benchmarks/{bench.id}/index.md) "
            f"| {bench.simulator} | {len(tasks)}{f' + {len(excluded)} excluded' if excluded else ''} "
            f"| {triaged}/{len(tasks)} |"
        )
    return "\n".join(lines)


def _benchmark_cards(url_root: str) -> str:
    """A card per benchmark: the counts that decide what to work on next."""
    cards = []
    for bench in taskdb.benchmarks().values():
        tasks, excluded = bench.included, bench.excluded
        pending = sum(1 for t in tasks if t.status == "pending")
        untagged = sum(1 for t in tasks if not t.tagged)
        href = doc_url(f"benchmarks/{bench.id}/index.md", url_root)
        cards.append(
            f'<a class="bcard" href="{href}">'
            f'<span class="bcard__name">{html.escape(bench.name)}</span>'
            f'<span class="bcard__sim">{html.escape(bench.simulator)}</span>'
            f'<span class="bcard__nums">'
            f"<b>{len(tasks)}</b> tasks{f' + {len(excluded)} excluded' if excluded else ''} &middot; "
            f"<b>{pending}</b> untriaged &middot; "
            f"<b>{untagged}</b> untagged</span>"
            f'<span class="bcard__go">Open the task list &rarr;</span>'
            "</a>"
        )
    return f'<div class="bcards">{"".join(cards)}</div>'


def _status_legend() -> str:
    lines = ["| Status | Meaning |", "| --- | --- |"]
    for s in taskdb.STATUSES:
        lines.append(f"| `{s}` | {taskdb.STATUS_HELP[s]} |")
    return "\n".join(lines)


def on_page_markdown(markdown: str, page, config, files):
    # Depth for markdown links (relative to the source file)…
    link_root = "../" * page.file.src_uri.count("/")
    # …and for raw HTML asset paths (relative to the output URL).
    asset_root = "../" * page.url.count("/")

    def sub(match: re.Match) -> str:
        kind = match.group("kind")
        args = dict(re.findall(r"(\w+)=([\w.-]+)", match.group("args") or ""))
        if kind == "tasks":
            bench = taskdb.benchmarks().get(args.get("benchmark", ""))
            if not bench:
                return f"<!-- unknown benchmark: {args.get('benchmark')} -->"
            return gallery.render(bench, asset_root=asset_root)
        if kind == "benchmark-stats":
            return _stats(args.get("benchmark", ""))
        if kind == "benchmark-table":
            return _benchmark_table(link_root)
        if kind == "benchmark-cards":
            return _benchmark_cards(asset_root)
        if kind == "runs-home":
            return runpages.home_summary(asset_root)
        if kind == "status-legend":
            return _status_legend()
        if kind == "taxonomy-editor":
            # Filled in by the browser once the local edit daemon answers; a local build without it shows the
            # hint, and the public site shows nothing (scripts/sitemode.py).
            if sitemode.PUBLIC:
                return ""
            return (
                '<div class="tax" data-taxonomy-editor>'
                '<p class="tax__hint">Run <code>make edit</code> to change the display tags '
                "from this page. Without the local edit daemon the site is read-only.</p>"
                "</div>"
            )
        return f"<!-- unknown generator: {kind} -->"

    markdown = PLACEHOLDER_RE.sub(sub, markdown)

    meta = page.meta or {}
    if not (meta.get("task_id") and meta.get("benchmark")):
        return markdown

    bench = taskdb.benchmarks().get(meta["benchmark"])
    task = next((t for t in bench.tasks if t.task_id == meta["task_id"]), None) if bench else None
    if task is None:
        return markdown

    header = _task_header(task, link_root, asset_root)
    lines = markdown.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("# "):
            return "\n".join(lines[: i + 1]) + "\n\n" + header + "\n" + "\n".join(lines[i + 1:])
    return f"# {task.title}\n\n{header}\n{markdown}"


def on_post_page(output: str, page, config):
    """Tell the page where editing lives, when there is a front door.

    `make edit` runs mkdocs on an internal port behind a front door that serves
    /api/* on the same address as the site. A browser that lands on the internal
    port directly — an old tab, a bookmark — gets a site that is silently
    read-only, and cannot tell that from a published build. It cannot learn the
    right address from `site_url` either: `mkdocs serve` overwrites that with its
    own dev address. So the Makefile passes it in, and the page carries it.

    Absent outside `make edit`, so a published build gains nothing.
    """
    if "</head>" not in output:
        return output
    if sitemode.PUBLIC:
        # The public site: the task list shows no edit controls and never probes for the edit daemon.
        output = output.replace("</head>", '<meta name="rb-public" content="1"></head>', 1)
    front = os.environ.get("RB_FRONT_URL", "").strip()
    if not front:
        return output
    tag = f'<meta name="rb-front" content="{html.escape(front, quote=True)}">'
    return output.replace("</head>", tag + "</head>", 1)

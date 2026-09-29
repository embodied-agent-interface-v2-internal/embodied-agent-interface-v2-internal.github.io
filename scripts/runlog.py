"""Turn one trial's raw records into the data of its log page: docs/assets/<benchmark>/runs/<run>/<task>/<mode>/.

Reads only what every trial keeps, never a credential (the model gateway never logs one):
- agent/gateway.jsonl: every model request. Its arrival time `t` and duration `latency_s`; the response (what the model decided: its words,
  its tool calls); and the request's tail (the previous tool call and its output, with any image the model was shown);
- artifacts/data/episode.jsonl (limited): every robot call of the episode, with the note the agent gave it;
- verifier/replay.mp4 and replay.last.png: the graded replay, shown only when the MP4 is complete (a render cut off
  or crashed mid-write leaves a file without its index, which no player opens: the page then says so);
- artifacts/app/output/ (only when there is no replay: the agent handed in no trajectory): the newest images the
  agent saved there and its gen.py, the closest thing to its last attempt.

The gateway log is complete while the trial runs (Codex writes its own session only at the end), so a running trial
gets a live page too. A trial with no gateway log (a harness without our model gateway, e.g. HumanoidBench's runs) gets
the same page from the harness's own session log once the agent has ended: Codex's rollout (agent/sessions/**/*.jsonl)
or Claude Code's (agent/sessions/projects/**/*.jsonl), which log each response and tool output but no request latency.
Writes log.json, img/<n>.<ext> (the images the model saw) and replay.mp4 / replay.png.
Called by scripts/import_runs.py, with `extra` from the run's local-only data/runs/<benchmark>/<run>.backfill.yml:
`note` (a line shown on the page), `episode` (a robot call log recovered elsewhere, used when the trial kept none),
`video` (a replay rendered again later from the recorded trajectory, shown in place of the graded replay's own video
where that one is truncated or missing; `note` says how it was made), `video_problem` (the page shows no replay video,
and this reason).
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

CMD = re.compile(r'\bcmd\s*:\s*("(?:[^"\\]|\\.)*")')
SSE = re.compile(r"^data:\s*(\{.*\})\s*$", re.M)
WALL = re.compile(r"Wall time ([\d.]+) seconds")
HEAD, TAIL = 1800, 700            # characters of a tool output kept on the page (head + tail)
VERSION = 4                       # bump to rebuild every page after a change here
SNAPSHOTS = 12                    # newest agent images shown when a run has no replay


def _sse(text: str) -> tuple[list[dict], dict]:
    """(output items, usage) of one streamed response."""
    items, usage = [], {}
    for m in SSE.finditer(text or ""):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            continue
        if d.get("type") == "response.output_item.done" and isinstance(d.get("item"), dict):
            items.append(d["item"])
        elif d.get("type") == "response.completed":
            usage = (d.get("response") or {}).get("usage") or {}
    return items, usage


def _script(inp: str) -> dict:
    """The shell command of a code-mode `exec` call, when it is one plain exec_command; else the whole script."""
    cmds = []
    for m in CMD.finditer(inp or ""):
        try:
            cmds.append(json.loads(m.group(1)))
        except ValueError:
            pass
    if len(cmds) == 1 and (inp or "").count("await tools.") == 1:
        return {"cmd": cmds[0]}
    return {"code": inp or ""}


def _clip(text: str) -> tuple[str, int]:
    n = len(text)
    if n <= HEAD + TAIL + 200:
        return text, n
    return text[:HEAD] + f"\n\n… {n - HEAD - TAIL:,} characters not shown …\n\n" + text[-TAIL:], n


def _save_image(url: str, out: Path, seen: dict) -> str | None:
    m = re.match(r"data:image/(\w+);base64,(.*)", url or "", re.S)
    if not m:
        return None
    data = base64.b64decode(m.group(2))
    key = hashlib.sha1(data).hexdigest()[:16]
    if key not in seen:
        name = f"img/{len(seen) + 1:03d}.{'jpg' if m.group(1) == 'jpeg' else m.group(1)}"
        (out / "img").mkdir(parents=True, exist_ok=True)
        (out / name).write_bytes(data)
        seen[key] = name
    return seen[key]


def _fill(step: dict, o, te: float, out: Path, images: dict) -> None:
    """A tool call's output (a string, or content parts with any image the model was shown) into its step."""
    texts, imgs = [], []
    for part in ([{"type": "input_text", "text": o}] if isinstance(o, str) else (o or [])):
        if part.get("type") in ("input_text", "output_text"):
            texts.append(part.get("text") or "")
        elif part.get("type") == "input_image":
            name = _save_image(part.get("image_url"), out, images)
            if name:
                imgs.append(name)
    text = "".join(texts)
    head = text.split("\n", 1)[0]
    step["status"] = ("failed" if head.startswith("Script failed") else
                      "background" if head.startswith("Script running") else "ok")
    wall = WALL.search(text[:200])
    step["wall"] = float(wall.group(1)) if wall else None
    body = re.sub(r"^Script [^\n]*\n(Wall time [^\n]*\n)?(Output:\n)?", "", text, count=1)
    step["out"], step["n"] = _clip(body)
    step["te"] = te
    if imgs:
        step["img"] = imgs


def _sessions(src: Path, out: Path, images: dict) -> tuple[float | None, list, list]:
    """(t0, calls, steps) from the harness's own session log, for a trial with no gateway log. A request is taken to
    run from the output it answers (or the previous response) to its response: the session logs no latency."""
    ev = []
    for f in sorted((src / "agent" / "sessions").rglob("*.jsonl")):
        for line in f.open(errors="replace"):
            try:
                e = json.loads(line)
                ev.append((datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")).timestamp(), e))
            except (ValueError, KeyError, TypeError, AttributeError):
                continue
    if not ev:
        return None, [], []
    ev.sort(key=lambda x: x[0])
    t0 = ev[0][0]
    rel = lambda t: round(t - t0, 1)
    calls, steps, pending, seen, last = [], [], {}, set(), t0
    for t, e in ev:
        p, kind = e.get("payload") or {}, e.get("type")
        m = e.get("message") if isinstance(e.get("message"), dict) else {}
        if kind == "token_usage_record":                                  # Codex: one per model response
            u = p.get("usage") or {}
            calls.append([rel(last), rel(t), 200, u.get("input_tokens"), u.get("cached_input_tokens"),
                          u.get("output_tokens"), u.get("reasoning_output_tokens")])
            last = t
        elif kind == "response_item" and p.get("type") == "message" and p.get("role") == "assistant":
            text = "".join(c.get("text") or "" for c in p.get("content") or [] if c.get("type") == "output_text")
            if text.strip():
                steps.append({"k": "say", "t": rel(t), "text": text.strip()})
        elif kind == "response_item" and p.get("type") in ("custom_tool_call", "function_call"):
            step = {"k": "run", "t": rel(t), "tool": p.get("name") or "tool"}
            step.update(_script(p.get("input") if p.get("type") == "custom_tool_call" else p.get("arguments")))
            steps.append(step)
            pending[p.get("call_id")] = step
        elif kind == "response_item" and p.get("type") in ("custom_tool_call_output", "function_call_output"):
            if (step := pending.pop(p.get("call_id"), None)) is not None:
                _fill(step, p.get("output"), rel(t), out, images)
                last = t
        elif kind == "assistant" and isinstance(m.get("content"), list):     # Claude Code
            if m.get("id") and m["id"] not in seen:         # the log repeats a message once per content block
                seen.add(m["id"])
                u = m.get("usage") or {}
                cached, write = u.get("cache_read_input_tokens") or 0, u.get("cache_creation_input_tokens") or 0
                calls.append([rel(last), rel(t), 200, (u.get("input_tokens") or 0) + cached + write, cached,
                              u.get("output_tokens"), None])
                last = t
            for c in m["content"]:
                if c.get("type") == "text" and (c.get("text") or "").strip():
                    steps.append({"k": "say", "t": rel(t), "text": c["text"].strip()})
                elif c.get("type") == "tool_use":
                    inp = c.get("input") or {}
                    step = {"k": "run", "t": rel(t), "tool": c.get("name") or "tool",
                            **({"cmd": inp["command"]} if isinstance(inp.get("command"), str)
                               else {"code": json.dumps(inp, ensure_ascii=False, indent=1)})}
                    steps.append(step)
                    pending[c.get("id")] = step
        elif kind == "user" and isinstance(m.get("content"), list):
            for c in m["content"]:
                if c.get("type") != "tool_result" or (step := pending.pop(c.get("tool_use_id"), None)) is None:
                    continue
                body = c.get("content")
                image = lambda s: f"data:{s.get('media_type')};base64,{s.get('data')}"
                parts = [{"type": "input_text", "text": body}] if isinstance(body, str) else [
                    {"type": "input_image", "image_url": image(x["source"])}
                    if x.get("type") == "image" and isinstance(x.get("source"), dict) else
                    {"type": "input_text", "text": x.get("text") or ""} for x in body or [] if isinstance(x, dict)]
                _fill(step, parts, rel(t), out, images)
                if c.get("is_error"):
                    step["status"] = "failed"
                last = t
    return t0, calls, steps


def mp4_complete(path: Path) -> bool:
    """Whether an MP4's top-level boxes span the whole file and include its index (moov). A render that was cut off or
    crashed mid-write leaves the frames (mdat) without the moov, and no player can open the file."""
    try:
        size = path.stat().st_size
        with path.open("rb") as fh:
            off, moov = 0, False
            while off + 8 <= size:
                fh.seek(off)
                head = fh.read(16)
                n, kind = int.from_bytes(head[:4], "big"), head[4:8]
                if n == 1:
                    n = int.from_bytes(head[8:16], "big")
                elif n == 0:
                    n = size - off
                if n < 8:
                    return False
                moov = moov or kind == b"moov"
                off += n
            return moov and off == size
    except OSError:
        return False


def build(src: Path, out: Path, meta: dict, extra: dict | None = None) -> dict:
    """Rebuild out/ from the trial dir src. meta: the page header (task, mode, state, reward, records, ...); extra: the
    trial's local-only backfill entry (see the module docstring)."""
    extra = extra or {}
    out.mkdir(parents=True, exist_ok=True)
    recs = []
    gw = src / "agent" / "gateway.jsonl"
    if gw.is_file():
        with gw.open("rb") as fh:
            for line in fh:
                try:
                    x = json.loads(line)
                except ValueError:
                    continue
                if x.get("method") == "POST" and isinstance(x.get("t"), (int, float)):
                    recs.append(x)
    t0 = min((x["t"] for x in recs), default=None)       # the gateway stamps a request when it arrives
    calls, steps, pending, images = [], [], {}, {}
    rel = lambda t: round(t - t0, 1)
    for x in recs:
        start, end = rel(x["t"]), rel(x["t"] + (x.get("latency_s") or 0))
        # The request carries the output of the previous tool call(s): what the model saw next.
        for it in x.get("tail") or []:
            if it.get("type") not in ("custom_tool_call_output", "function_call_output"):
                continue
            step = pending.pop(it.get("call_id"), None)
            if step is None:
                continue
            _fill(step, it.get("output"), start, out, images)
        items, usage = _sse(x.get("response") or "")
        det = usage.get("output_tokens_details") or {}
        cached = (usage.get("input_tokens_details") or {}).get("cached_tokens")
        calls.append([start, end, x.get("status"), usage.get("input_tokens"), cached,
                      usage.get("output_tokens"), det.get("reasoning_tokens")])
        for it in items:
            if it.get("type") == "message" and it.get("role", "assistant") == "assistant":
                text = "".join(c.get("text") or "" for c in it.get("content") or [] if c.get("type") == "output_text")
                if text.strip():
                    steps.append({"k": "say", "t": end, "text": text.strip()})
            elif it.get("type") in ("custom_tool_call", "function_call"):
                step = {"k": "run", "t": end, "tool": it.get("name") or "tool"}
                step.update(_script(it.get("input") if it.get("type") == "custom_tool_call" else it.get("arguments")))
                steps.append(step)
                pending[it.get("call_id")] = step

    if t0 is None:          # no gateway log: the harness's own session log (see the module docstring)
        t0, calls, steps = _sessions(src, out, images)

    robot = []
    # the sim service writes /data, or /out where /data is a licensed dataset mount (BEHAVIOR)
    ep = next((p for p in (src / "artifacts" / "data" / "episode.jsonl", src / "artifacts" / "out" / "episode.jsonl")
               if p.is_file()), src / "artifacts" / "data" / "episode.jsonl")
    if not ep.is_file() and extra.get("episode") and Path(extra["episode"]).is_file():
        ep = Path(extra["episode"])       # recovered elsewhere (e.g. from a stopped sim container); `note` says where
    ended = {}                            # how the live episode ended: its `end` reason and the first simulator error
    if t0 is not None and ep.is_file():
        for line in ep.open(errors="replace"):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("ev") == "end" and e.get("reason"):
                ended["reason"] = e["reason"]
            if e.get("error") and "error" not in ended:
                ended["error"] = str(e["error"])[:300]
            if isinstance(e.get("ts"), (int, float)):
                robot.append({k: v for k, v in {
                    "t": rel(e["ts"]), "ev": e.get("ev"), "call": e.get("call"), "type": e.get("type"),
                    # an error event carries no note of its own: its message is what the row should say
                    "note": e.get("note") or (str(e["error"])[:300] if e.get("error") else None),
                    "steps": e.get("control_steps"), "clip": e.get("n_clipped"),
                    "success": e.get("success")}.items() if v is not None})

    media = {}
    video = src / "verifier_regrade" / "replay.mp4"   # a regrade (after a failed grading) is the verdict
    if not video.is_file():
        video = src / "verifier" / "replay.mp4"
    again = Path(extra["video"]) if extra.get("video") else None     # rendered again later (see the docstring)
    if extra.get("video_problem"):
        media["problem"] = str(extra["video_problem"])
    elif again is not None and mp4_complete(again):
        dst = out / "replay.mp4"
        if not dst.is_file() or dst.stat().st_size != again.stat().st_size:
            shutil.copyfile(again, dst)
        media.update(video="replay.mp4", rerendered=True)
    elif video.is_file() and not mp4_complete(video):
        media["problem"] = ("The replay video is truncated at the source: its render was cut off or crashed before the "
                            "file was finished, so it has no index and cannot be played.")
    else:
        for src_name, dst_name, key in (("replay.mp4", "replay.mp4", "video"), ("replay.last.png", "replay.png", "last")):
            f = src / "verifier_regrade" / src_name
            if not f.is_file():
                f = src / "verifier" / src_name
            if f.is_file():
                dst = out / dst_name
                if not dst.is_file() or dst.stat().st_size != f.stat().st_size:
                    shutil.copyfile(f, dst)
                media[key] = dst_name

    snaps, gen = [], None
    output = src / "artifacts" / "app" / "output"
    if "video" not in media and output.is_dir():
        pics = sorted((f for f in output.rglob("*") if f.suffix.lower() in (".png", ".jpg", ".jpeg") and f.is_file()),
                      key=lambda f: f.stat().st_mtime)[-SNAPSHOTS:]
        if pics:
            (out / "snap").mkdir(exist_ok=True)
        for n, f in enumerate(pics, 1):
            name = f"snap/{n:02d}{f.suffix.lower()}"
            shutil.copyfile(f, out / name)
            snaps.append({"src": name, "name": str(f.relative_to(output)),
                          "t": round(f.stat().st_mtime - t0, 1) if t0 else None})
        if (output / "gen.py").is_file():
            gen = (output / "gen.py").read_text(errors="replace")
            gen = gen if len(gen) <= 40000 else gen[:40000] + f"\n\n… {len(gen) - 40000:,} more characters …"

    sum_of = lambda i: sum(c[i] or 0 for c in calls)
    data = {
        "v": 1, **meta, "built": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "start": t0, "span": max([c[1] for c in calls] + [s.get("te") or 0 for s in steps] + [r["t"] for r in robot], default=0),
        "totals": {"calls": len(calls), "failed": sum(1 for c in calls if c[2] != 200), "output": sum_of(5),
                   "reasoning": sum_of(6), "input": sum_of(3), "cached": sum_of(4),
                   "runs": sum(1 for s in steps if s["k"] == "run"), "said": sum(1 for s in steps if s["k"] == "say"),
                   "images": len(images), "robot": sum(1 for r in robot if r.get("call"))},
        "calls": calls, "steps": steps, "robot": robot, "media": media, "snapshots": snaps, "gen": gen,
        "ended": ended, "note": extra.get("note"),
    }
    tmp = out / "log.json.tmp"
    tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    tmp.replace(out / "log.json")
    return data

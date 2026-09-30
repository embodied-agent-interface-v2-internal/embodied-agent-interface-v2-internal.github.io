"""Turn one trial's raw records into the data of its log page: docs/assets/<benchmark>/runs/<run>/<task>/<mode>/.

Reads only what every trial keeps, never a credential (the model gateway never logs one):
- agent/gateway.jsonl: every model request. Its arrival time `t` and duration `latency_s`; the response (what the model decided: its words,
  its tool calls); and the request's tail (the previous tool call and its output, with any image the model was shown);
- agent/trajectory.json, only for a trial that ran without our gateway (no request in gateway.jsonl): Harbor's ATIF
  trajectory, written when the agent ends. Each agent step is one answered model request: its words, tool calls,
  token counts and the tool outputs (with any image the model was shown). It keeps no request's start or duration and
  no failed request, so a request is drawn from when its input was complete (the prompt, or the last tool output: the
  step's time plus the tool's reported wall time, or the wait a Terminus keystroke asked for) to the step's time. A
  readable reasoning summary (Terminus over OpenRouter; Codex keeps its reasoning encrypted) is kept as the step's
  `think`, which the page does not show;
- artifacts/data/episode.jsonl (limited): every robot call of the episode, with the note the agent gave it; where a
  trial has none, its trusted recording (artifacts/trusted-recording/events.jsonl: every observation and control);
- verifier/replay.mp4 and replay.last.png: the graded replay, shown only when the MP4 is complete (a render cut off
  or crashed mid-write leaves a file without its index, which no player opens: the page then says so);
- artifacts/app/output/ (only when there is no replay: the agent handed in no trajectory): the newest images the
  agent saved there and its gen.py, the closest thing to its last attempt.

The gateway log is complete while the trial runs (Codex writes its own session only at the end), so a running trial
gets a live page too (a trial without the gateway gets its page once the agent ends). Writes log.json, img/<n>.<ext> (the images the model saw) and replay.mp4 / replay.png.
Called by scripts/import_runs.py, with `extra` from the run's local-only data/runs/<benchmark>/<run>.backfill.yml:
`note` (a line shown on the page), `episode` (a robot call log recovered elsewhere, used when the trial kept none),
`video` (a replay rendered again later from the recorded trajectory, shown in place of the graded replay's own video
where that one is truncated or missing; `note` says how it was made), `video_problem` (the page shows no replay video,
and this reason).
"""

from __future__ import annotations

import ast
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
VERSION = 5                       # bump to rebuild every page after a change here
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


def _output(step: dict, parts: list, out: Path, seen: dict) -> None:
    """Fill a tool run step with its output: response-style parts (text, and images the model was shown)."""
    texts, imgs = [], []
    for part in parts:
        if part.get("type") in ("input_text", "output_text", "text"):
            texts.append(part.get("text") or "")
        elif part.get("type") == "input_image":
            name = _save_image(part.get("image_url"), out, seen)
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
    if imgs:
        step["img"] = imgs


def _when(stamp) -> float | None:
    try:
        return datetime.fromisoformat(str(stamp).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _parts(content) -> list[dict]:
    """An ATIF message or tool output as response-style parts. Codex's tool outputs arrive as the repr of its list."""
    if isinstance(content, str) and content.startswith("[{"):
        try:
            content = ast.literal_eval(content)
        except (ValueError, SyntaxError, MemoryError, RecursionError):
            pass
    if isinstance(content, str):
        return [{"type": "input_text", "text": content}]
    return [p for p in content or [] if isinstance(p, dict)] if isinstance(content, list) else []


def _atif(src: Path, out: Path, seen: dict) -> tuple[float | None, list, list]:
    """(t0, calls, steps) from Harbor's ATIF trajectory (see the module docstring)."""
    try:
        traj = json.loads((src / "agent" / "trajectory.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, [], []
    rows = [(_when(s.get("timestamp")), s) for s in traj.get("steps") or [] if isinstance(s, dict)]
    rows = [(t, s) for t, s in rows if t is not None]
    if not rows:
        return None, [], []
    t0 = min(t for t, _ in rows)
    calls, steps, ready, running = [], [], 0.0, []
    for t, s in rows:
        t = round(t - t0, 1)
        for step in running:            # a tool's output is in before the model's next answer
            step["te"] = min(step["te"], t)
        running = []
        if s.get("source") != "agent":
            ready = t
            continue
        m = s.get("metrics") or {}
        calls.append([min(ready, t), t, 200, m.get("prompt_tokens"), m.get("cached_tokens"), m.get("completion_tokens"),
                      (m.get("extra") or {}).get("reasoning_output_tokens")])
        ready, first = t, len(steps)
        text = "".join(p.get("text") or "" for p in _parts(s.get("message")) if p.get("type") in ("input_text", "text"))
        if text.strip():
            steps.append({"k": "say", "t": t, "text": text.strip()})
        results = {r.get("source_call_id"): r for r in (s.get("observation") or {}).get("results") or []
                   if isinstance(r, dict)}
        for tc in s.get("tool_calls") or []:
            args = tc.get("arguments") if isinstance(tc.get("arguments"), dict) else {}
            step = {"k": "run", "t": t, "tool": tc.get("function_name") or "tool"}
            if isinstance(args.get("input"), str):              # Codex code mode: the script it ran
                step.update(_script(args["input"]))
            elif isinstance(args.get("keystrokes"), str):       # Terminus: the keys it typed into its terminal
                step["cmd"] = args["keystrokes"] or f"(no keys: waits {args.get('duration', 0)} s for output)"
            elif args:
                step["code"] = json.dumps(args, ensure_ascii=False, indent=1)
            r = results.get(tc.get("tool_call_id"))
            if r is not None:
                _output(step, _parts(r.get("content")), out, seen)
                wait = step["wall"] if step["wall"] is not None else args.get("duration")
                step["te"] = round(t + (wait if isinstance(wait, (int, float)) else 0), 1)
                ready = max(ready, step["te"])
                running.append(step)
            steps.append(step)
        if s.get("reasoning_content") and len(steps) > first:
            steps[first]["think"] = str(s["reasoning_content"]).strip()
    return t0, calls, steps


def _jsonl(path: Path):
    for line in path.open(errors="replace"):
        try:
            yield json.loads(line)
        except ValueError:
            continue


def _recording(path: Path):
    """A trusted recording's events (artifacts/trusted-recording/events.jsonl, robot_coding_bench's limited tasks) in
    episode.jsonl's shape: every observation and every control is one robot call (a control is one action, which the
    agent sends one at a time or in batches)."""
    call = 0
    for e in _jsonl(path):
        kind, ts = e.get("kind"), _when(e.get("at"))
        if kind == "agent_start":
            yield {"ev": "start", "ts": ts}
        elif kind == "observation":
            call += 1
            yield {"ev": "observe", "ts": ts, "call": call, "type": None if e.get("camera") is None else f"camera {e['camera']}"}
        elif kind == "action_end":
            call += 1
            yield {"ev": "step", "ts": ts, "call": call, "control_steps": 1}
        elif kind == "request_rejected":
            call += 1
            yield {"ev": "rejected", "ts": ts, "call": call}
        elif kind == "episode_end":
            yield {"ev": "end", "ts": ts, "reason": e.get("reason"), "success": e.get("online_success"), "error": e.get("error")}


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
            o = it.get("output")
            _output(step, [{"type": "input_text", "text": o}] if isinstance(o, str) else (o or []), out, images)
            step["te"] = start
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
    if not recs:                          # ran without our gateway: Harbor's trajectory, once the agent has ended
        t0, calls, steps = _atif(src, out, images)

    robot = []
    # the sim service writes /data, or /out where /data is a licensed dataset mount (BEHAVIOR)
    ep = next((p for p in (src / "artifacts" / "data" / "episode.jsonl", src / "artifacts" / "out" / "episode.jsonl")
               if p.is_file()), src / "artifacts" / "data" / "episode.jsonl")
    if not ep.is_file() and extra.get("episode") and Path(extra["episode"]).is_file():
        ep = Path(extra["episode"])       # recovered elsewhere (e.g. from a stopped sim container); `note` says where
    ended = {}                            # how the live episode ended: its `end` reason and the first simulator error
    recording = src / "artifacts" / "trusted-recording" / "events.jsonl"
    events = _jsonl(ep) if ep.is_file() else _recording(recording) if recording.is_file() else []
    if t0 is not None:
        for e in events:
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

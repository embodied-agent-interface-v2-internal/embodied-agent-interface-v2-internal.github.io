#!/usr/bin/env python3
"""Sync RoboTwin 2.0 task pages from the benchmark's own files.

RoboTwin 2.0 defines each of its 50 bimanual tasks as one Python class in
`envs/<task>.py`: `load_actors` builds the scene, `check_success` is the success
predicate, and `play_once` is the scripted expert used to collect the public
dataset. The class is read with `ast` (no simulator needed), so the page records
the predicate verbatim, the objects the scene creates, and how many planned
motions the expert takes — all machine-read, nothing scraped from prose.

What RoboTwin publishes *about* a task lives on its documentation site, one page
per task (`https://robotwin-platform.github.io/doc/tasks/<task>.html`): the
one-line description, the objects, the average demo length, the per-embodiment
data-generation success rate, and per-embodiment head/world-camera videos served
as static MP4s. Those pages are fetched once into a cache outside the repository
(`--fetch-docs`) and read as HTML; the fields are well delimited (`<b>Field</b>:`
and one table), so this is closer to a feed than to scraping.

`--media DIR` points at our own render of the suite (robot_os_world_all/
robotwin2_tasks, made in the rcb-robotwin image): per task an `initial.png` of
the scene we start from, and — where RoboTwin's expert succeeded on one of the
uncommon seeds we use — a six-camera-grid `expert.mp4` of that run. The still
becomes `docs/assets/robotwin-2/scenes/<task>.jpg`; the clip becomes the row's
demo under `docs/assets/robotwin-2/demos/` with a manifest entry crediting us,
because it is our recording of *their* expert, not an upstream demo. The
official ALOHA head-camera clip is recorded in `upstream.oracle_video` so
`scripts/fetch_demos.py --benchmark robotwin-2` can fetch it instead. What the
render run observed (seed, attempts, physics steps) goes into the `verified:`
zone; `--sweep JSON` adds the expert pass rate over seeds where we measured it.

Re-running is safe and expected:
  * new upstream task    -> a fresh page is scaffolded from the template
  * existing task        -> only the `upstream:` (and `verified:`) blocks are rewritten
  * task pulled upstream -> reported, never deleted (a human decides)

Usage:
  python scripts/import_robotwin_tasks.py --source ../robot_coding_bench/third_party/RoboTwin --fetch-docs \
      --media ../robotwin2_tasks --sweep ../robot_coding_bench/exps/robotwin_expert_sweep_2026-09-21.json
  python scripts/import_robotwin_tasks.py            # from the cache
  python scripts/import_robotwin_tasks.py --dry-run
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import html as htmlmod
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = "robotwin-2"
CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.upstream.json"
TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"
SCENE_DIR = ROOT / "docs" / "assets" / BENCHMARK / "scenes"
DEMO_DIR = ROOT / "docs" / "assets" / BENCHMARK / "demos"

REPO_URL = "https://github.com/RoboTwin-Platform/RoboTwin"
DOCS_URL = "https://robotwin-platform.github.io/doc/tasks/"
DOCS_CACHE = Path.home() / ".cache" / "rcb-docs" / "robotwin-2-docs"
EMBODIMENT = "aloha-agilex"          # the embodiment our image runs; its clips are the ones we link
KEEP_METHODS = {"setup_demo", "load_actors", "check_success"}

BODY_TEMPLATE = """
## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/robotwin-2.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- The row plays OUR recording of RoboTwin's scripted expert (play_once) on
     an uncommon seed, as a six-camera grid; the official ALOHA clip is linked
     from the facts table. Does the expert satisfy the goal cleanly? What does
     it rely on (contact-point grasps, functional points, a planner)? -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->
"""


# ─────────────────────────────────────────────────────────── source reading

def title_of(task_id: str) -> str:
    words = task_id.split("_")
    fixed = {"rgb": "RGB", "qrcode": "QR code", "a2b": "A to B", "bigbin": "big bin", "mic": "microphone",
             "playingcard": "playing card", "pillbottle": "pill bottle", "plasticbox": "plastic box",
             "alarmclock": "alarm clock"}
    words = [fixed.get(w, w) for w in words]
    return " ".join(words).capitalize().replace("Rgb", "RGB").replace("qr code", "QR code")


def read_source(source: Path) -> list[dict]:
    """One dict per task class in envs/<task>.py, read with ast."""
    limits = yaml.safe_load((source / "env_cfg/task_config/_eval_step_limit.yml").read_text())
    tasks = []
    for path in sorted((source / "envs").glob("*.py")):
        if path.name.startswith("_"):
            continue
        src = path.read_text()
        tree = ast.parse(src)
        classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
        if not classes:
            continue
        cls = classes[0]
        fns = {f.name: f for f in cls.body if isinstance(f, ast.FunctionDef)}
        if "check_success" not in fns or "load_actors" not in fns:
            continue
        expert = [f for n, f in fns.items() if n not in KEEP_METHODS]
        expert_src = "\n".join(ast.get_source_segment(src, f) for f in expert)
        check = ast.get_source_segment(src, fns["check_success"])
        check = re.sub(r"\n\s*#.*", "", check)                      # drop comment-only lines
        load = ast.get_source_segment(src, fns["load_actors"])
        models = sorted(set(re.findall(r'modelname\s*=\s*"([^"]+)"', load)) | set(re.findall(r'"(\d{3}_[a-z\-]+)"', load)))
        tasks.append({
            "id": path.stem,
            "title": title_of(path.stem),
            "source_file": f"envs/{path.name}",
            "eval_step_limit": limits.get(path.stem),
            "expert_planned_motions": len(re.findall(r"self\.move\(", expert_src)),
            "expert_methods": [f.name for f in expert],
            "success_check": check,
            "asset_models": models,
            "articulated": "urdf" in load.lower(),
            "uses_both_arms": bool(re.search(r"self\.move\(\s*self\.\w+\([^)]*\)\s*,\s*self\.", expert_src, re.S)) or "opposite" in expert_src,
        })
    return tasks


# ─────────────────────────────────────────────────────────── docs reading

def fetch_docs(cache: Path, task_ids: list[str]) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    for tid in task_ids:
        dest = cache / f"{tid}.html"
        if dest.is_file() and dest.stat().st_size > 0:
            continue
        with urllib.request.urlopen(f"{DOCS_URL}{tid}.html", timeout=60) as r:
            dest.write_bytes(r.read())


def read_docs(cache: Path, tasks: list[dict]) -> int:
    n = 0
    for task in tasks:
        path = cache / f"{task['id']}.html"
        if not path.is_file():
            continue
        s = path.read_text(errors="ignore")
        def field(name: str) -> str:
            m = re.search(rf"<b>{name}</b>:\s*(.*?)<br>", s, re.S)
            return htmlmod.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""
        task["instruction"] = field("Description")
        objects = field("Objects")
        task["objects"] = [o.strip() for o in objects.split(",") if o.strip()]
        avg = field("Average Steps")
        m = re.match(r"(\d+)", avg)
        task["average_steps"] = int(m.group(1)) if m else None
        task["average_steps_note"] = avg
        ths = [re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<th[^>]*>(.*?)</th>", s)]
        tds = [re.sub(r"<[^>]+>", "", x) for x in re.findall(r"<td[^>]*>(.*?)</td>", s)]
        if ths and tds and tds[0].startswith("Data Generation"):
            task["data_gen_success"] = dict(zip(ths[1:], tds[1:]))
            task["embodiments"] = ths[1:]
        vids = sorted(set(re.findall(r'src=(\./task_video_clean/[^ >"]+)', s)))
        task["videos"] = {Path(v).stem: DOCS_URL + v[2:] for v in vids}
        task["oracle_video"] = task["videos"].get(f"{EMBODIMENT}_head", "")
        task["oracle_video_world"] = task["videos"].get(f"{EMBODIMENT}_world", "")
        task["doc_url"] = f"{DOCS_URL}{task['id']}.html"
        n += 1
    return n


# ─────────────────────────────────────────────────────────── our media

def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, check=False).stdout.strip()


def probe(path: Path) -> tuple[int, int, int]:
    dims = _run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                 "-of", "csv=p=0", str(path)])
    dur = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    w, h = (int(x) for x in dims.split(",")[:2]) if dims else (0, 0)
    return w, h, int(round(float(dur))) if dur else 0


def attach_media(media: Path, tasks: list[dict], synced: str, sweep: dict) -> tuple[int, int]:
    """Copy our scene stills and expert clips in; write the demo manifest with a credit; fill `verified`."""
    SCENE_DIR.mkdir(parents=True, exist_ok=True); DEMO_DIR.mkdir(parents=True, exist_ok=True)
    meta_all = json.loads((media / "render_meta.json").read_text()) if (media / "render_meta.json").is_file() else {}
    manifest_path = DEMO_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
    n_scene = n_demo = 0
    for task in tasks:
        tid = task["id"]; d = media / "media" / tid; r = meta_all.get(tid, {})
        still = d / "initial.png"
        if still.is_file():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(still), "-q:v", "3", str(SCENE_DIR / f"{tid}.jpg")], check=True)
            task["scene_image"] = f"{tid}.jpg"; n_scene += 1
        clip = d / "expert.mp4"
        if clip.is_file() and r.get("expert_ok"):
            dest = DEMO_DIR / f"{tid}.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-c", "copy", "-movflags", "+faststart", str(dest)], check=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", str(dest), "-frames:v", "1", "-q:v", "3", str(DEMO_DIR / f"{tid}.jpg")], check=True)
            w, h, sec = probe(dest)
            manifest[tid] = {"bytes": dest.stat().st_size, "height": h, "width": w, "seconds": sec, "poster": True,
                             "source": (f"Recorded by us: RoboTwin's scripted expert (play_once) run in our rcb-robotwin image on seed "
                                        f"{r.get('seed')}, six-camera grid — world / observer / head // front / left wrist / right wrist. "
                                        f"The official ALOHA clip is linked in the facts table.")}
            n_demo += 1
        tries = r.get("tries", [])
        if r:
            attempt = next((i + 1 for i, x in enumerate(tries) if x.get("success")), None)
            reasons = sorted({(x.get("error") or ("plan failed" if (x.get("exec") or {}).get("ok") is False else "check_success false")).split("(")[0][:60] for x in tries if not x.get("success")})
            v = {"source": "rendered and run in our rcb-robotwin image (robot_coding_bench images/robotwin)",
                 "stack": "RoboTwin 2.0 @ 6dde571, SAPIEN 3.0.0b1 (PhysX), CuRobo 0.7.8, ALOHA-AgileX, clean scene",
                 "checked": synced,
                 "expert_run": (f"succeeded on seed {r.get('seed')}, attempt {attempt} of {len(tries)}" if r.get("expert_ok")
                                else f"failed on all {len(tries)} attempts ({'; '.join(reasons)})"),
                 "physics_steps": r.get("n_actions"),
                 "scene_image": "initial scene, head camera, 640x480, before any motion"}
            sw = sweep.get(tid)
            if sw:
                ok = sum(1 for x in sw.values() if x.get("live_success") and x.get("replay_success") and x.get("deterministic"))
                v["expert_pass_rate"] = f"{ok}/{len(sw)} uncommon seeds, one attempt each, replay bit-exact required"
            task["_verified"] = {k: val for k, val in v.items() if val not in (None, "", [])}
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return n_scene, n_demo


# ─────────────────────────────────────────────────────────── page writing

UPSTREAM_KEYS = ["instruction", "objects", "asset_models", "embodiments", "data_gen_success", "average_steps",
                 "eval_step_limit", "expert_planned_motions", "expert_methods", "success_check", "source_file",
                 "doc_url", "oracle_video", "oracle_video_world", "scene_image"]


def upstream_block(task: dict, synced: str, ref: str) -> dict:
    block = {"source": f"{REPO_URL} @ {ref}" if ref else REPO_URL, "synced": synced, "scene_model": "tabletop"}
    for key in UPSTREAM_KEYS:
        value = task.get(key)
        if value not in (None, [], {}, ""):
            block[key] = value
    return block


def scaffold(task: dict, synced: str, ref: str) -> dict:
    meta = {"title": task["title"], "task_id": task["id"], "benchmark": BENCHMARK,
            "upstream": upstream_block(task, synced, ref)}
    if task.get("_verified"):
        meta["verified"] = task["_verified"]
    return meta


def git_ref(source: Path) -> str:
    out = subprocess.run(["git", "-C", str(source), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=None, help="a RoboTwin 2.0 checkout (robot_coding_bench/third_party/RoboTwin); omit to use the cache")
    ap.add_argument("--fetch-docs", action="store_true", help=f"fetch the per-task documentation pages into {DOCS_CACHE}")
    ap.add_argument("--docs-cache", default=str(DOCS_CACHE), help="directory of <task>.html pages (pre-populated or fetched)")
    ap.add_argument("--media", default=None, help="our catalog dir (robotwin2_tasks): media/<task>/{initial.png,expert.mp4}, render_meta.json")
    ap.add_argument("--sweep", default=None, help="expert seed-sweep results JSON from robot_coding_bench")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rewrite pages even when upstream is unchanged")
    args = ap.parse_args()
    synced = dt.date.today().isoformat()

    if args.source:
        source = Path(args.source).expanduser()
        tasks = read_source(source)
        ids = [t["id"] for t in tasks]
        cache = Path(args.docs_cache).expanduser()
        if args.fetch_docs:
            fetch_docs(cache, ids)
        n_docs = read_docs(cache, tasks)
        sweep = json.loads(Path(args.sweep).read_text()) if args.sweep else {}
        n_scene, n_demo = attach_media(Path(args.media).expanduser(), tasks, synced, sweep) if args.media else (0, 0)
        ref = git_ref(source)
        payload = {"source": REPO_URL, "ref": ref, "docs": DOCS_URL, "read": synced, "tasks": tasks}
        CACHE.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"read {len(tasks)} task(s) from {source} -> {CACHE.name} ({n_docs} doc pages, {n_scene} stills, {n_demo} clips)")
    else:
        if not CACHE.is_file():
            sys.exit(f"no cache at {CACHE}; run once with --source <RoboTwin checkout>")
        payload = json.loads(CACHE.read_text()); tasks = payload["tasks"]

    ref = payload.get("ref", "")
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    created = updated = unchanged = 0; seen = set()
    for task in tasks:
        seen.add(task["id"]); path = TASK_DIR / f"{task['id']}.md"
        fresh = upstream_block(task, synced, ref); verified = task.get("_verified")
        if path.is_file():
            meta, body = read_page(path)
            current = dict(meta.get("upstream") or {})
            comparable = dict(fresh, synced=current.get("synced", synced))
            same_verified = not verified or dict(meta.get("verified") or {}, checked=verified["checked"]) == verified
            if current == comparable and same_verified and not args.force:
                unchanged += 1; continue
            meta["upstream"] = dict(fresh, synced=synced)
            if verified:
                meta["verified"] = verified
            if not args.dry_run:
                write_page(path, meta, body)
            updated += 1
        else:
            if not args.dry_run:
                write_page(path, scaffold(task, synced, ref), BODY_TEMPLATE)
            created += 1
    orphans = sorted(p.stem for p in TASK_DIR.glob("*.md") if p.stem not in seen and p.stem != "index")
    print(f"upstream tasks : {len(tasks)}\ncreated        : {created}{' (dry run)' if args.dry_run else ''}\n"
          f"updated        : {updated}\nunchanged      : {unchanged}")
    if orphans:
        print(f"no longer upstream (left in place, decide by hand): {', '.join(orphans)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

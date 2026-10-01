#!/usr/bin/env python3
"""Sync DexToolBench task pages from SimToolReal's own files.

DexToolBench (SimToolReal, github.com/tylerlum/simtoolreal, MIT) is 6 tool categories x 2 objects x 2 tasks. Each task
is one JSON file, `dextoolbench/trajectories/<category>/<object>/<task>.json`: the tool's start pose and the sequence
of goal poses extracted from a human RGB-D demo. The benchmark's score is task progress: a goal counts when all 8
corners of the tool's grasp box are within the tolerance of the goal pose, then the next goal becomes current. The
tool meshes are `assets/urdf/dextoolbench/<category>/<object>/`, the per-category tables `assets/urdf/table_narrow_*.urdf`.

We run the suite in plain MuJoCo (robot_coding_bench tasks dextoolbench_<category>_<object>_<task>, image
rcb-mujoco): SimToolReal's own sim2sim scene rebuilt, plus each category's table props. `--harness DIR` points at
that repository: for every task it has built, the page's `verified:` zone records what the pretrained policy (the
task's oracle) reached in that scene, and `--oracle-jobs DIR` supplies the oracle's replay video (four views), which
becomes the row's demo under docs/assets/dextoolbench/demos/ with a manifest entry crediting us.

Re-running is safe: only the `upstream:` / `verified:` blocks are rewritten; a task gone upstream is reported, never
deleted. The upstream read is cached in data/benchmarks/dextoolbench.tasks.upstream.json.

Usage:
  python scripts/import_dextoolbench_tasks.py --source <simtoolreal checkout or rcb_mj/simtoolreal> \\
      --harness ../robot_coding_bench --oracle-jobs ../robot_coding_bench/exps/jobs/mj-oracle-all
  python scripts/import_dextoolbench_tasks.py            # from the cache
"""
from __future__ import annotations

import argparse, datetime as dt, json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = "dextoolbench"
CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.upstream.json"
TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"
DEMO_DIR = ROOT / "docs" / "assets" / BENCHMARK / "demos"
REPO_URL = "https://github.com/tylerlum/simtoolreal"
REF = "313d5ae"
TABLES = {"hammer": "table_narrow_nail.urdf (one nail)", "eraser": "table_narrow_whiteboard.urdf (a whiteboard at the table's edge)",
          "marker": "table_narrow_whiteboard.urdf (a whiteboard at the table's edge)", "spatula": "table_narrow_bowl_plate.urdf (a bowl and a plate)",
          "brush": "table_narrow.urdf (plain)", "screwdriver": "table_narrow.urdf (plain)"}
MOTION = {"swing_down": "a downward hammer swing", "swing_side": "a sideways hammer swing", "draw_smile": "drawing a smiley face",
          "write_c": "writing the letter C", "wipe_smile": "wiping a smiley face", "wipe_c": "wiping the letter C",
          "sweep_forward": "a forward sweep", "sweep_right": "a sweep to the right", "serve_plate": "serving onto a plate",
          "flip_over": "flipping something over", "spin_vertical": "spinning it about a vertical axis", "spin_horizontal": "spinning it about a horizontal axis"}

BODY_TEMPLATE = """
## Why this task is interesting

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/dextoolbench.yml. -->

_Not yet written._

## Oracle demo review

<!-- The row plays OUR replay of SimToolReal's pretrained policy in our MuJoCo port (four views: front, side, top,
     oblique). The policy is the benchmark's own method, not a scripted expert; how far it gets here is the facts
     table's `oracle` line. -->

_Not yet reviewed._

## Discussion
"""


def read_source(src: Path) -> list[dict]:
    tasks = []
    for f in sorted((src / "dextoolbench" / "trajectories").glob("*/*/*.json")):
        cat, obj, task = f.parts[-3], f.parts[-2], f.stem
        d = json.loads(f.read_text())
        tasks.append({"id": f"{cat}_{obj}_{task}", "title": f"{obj.replace('_', ' ').capitalize()} · {task.replace('_', ' ')}",
                      "category": cat, "object": obj, "task": task, "n_goals": len(d["goals"]),
                      "instruction": f"Pick up the {obj.replace('_', ' ')} and move it through the demonstrated motion ({MOTION.get(task, task)}): bring it to each of the {len(d['goals'])} goal poses in order.",
                      "source_file": f"dextoolbench/trajectories/{cat}/{obj}/{task}.json",
                      "tool_model": f"assets/urdf/dextoolbench/{cat}/{obj}/{obj}.urdf", "table": TABLES.get(cat, "")})
    return tasks


def _run(cmd): return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()


def probe(p: Path):
    dims = _run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(p)])
    dur = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)])
    w, h = (int(x) for x in dims.split(",")[:2]) if dims else (0, 0)
    return w, h, int(round(float(dur))) if dur else 0


def attach(tasks, harness: Path | None, jobs: Path | None, synced: str) -> int:
    DEMO_DIR.mkdir(parents=True, exist_ok=True); mf = DEMO_DIR / "manifest.json"
    manifest = json.loads(mf.read_text()) if mf.is_file() else {}; n = 0
    oracle = {}
    if jobs and jobs.is_dir():
        for tr in jobs.glob("*__*"):
            try:
                name = json.loads((tr / "result.json").read_text())["task_name"].split("/")[-1]
                oracle[name] = (tr, json.loads((tr / "verifier/reward.json").read_text()))
            except Exception: continue
    for t in tasks:
        name = f"dextoolbench_{t['id']}"; built = harness is not None and (harness / "tasks" / name).is_dir()
        v = {"source": "run in our MuJoCo port (robot_coding_bench tasks/" + name + ", image rcb-mujoco 0.1.1)",
             "stack": "MuJoCo 3.3.7 (CPU, bit-exact replay), KUKA iiwa 14 (MuJoCo Menagerie 1b86ece) + Sharpa HA4, 600 Hz physics, 60 Hz control",
             "checked": synced, "harness_task": name if built else "not built"}
        if name in oracle:
            tr, rw = oracle[name]
            v["oracle"] = f"SimToolReal's pretrained policy, recorded in this scene and replayed: {rw.get('goals_reached')}/{rw.get('n_goals')} goals"
            clip = tr / "verifier" / "replay.mp4"
            if clip.is_file():
                dest = DEMO_DIR / f"{t['id']}.mp4"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-c", "copy", "-movflags", "+faststart", str(dest)], check=True)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", str(dest), "-frames:v", "1", "-q:v", "3", str(DEMO_DIR / f"{t['id']}.jpg")], check=True)
                w, h, sec = probe(dest)
                manifest[t["id"]] = {"bytes": dest.stat().st_size, "height": h, "width": w, "seconds": sec, "poster": True,
                                     "source": ("Recorded by us: SimToolReal's pretrained RL policy replayed in our MuJoCo port of the task, "
                                                f"four views (front, side / top, oblique); it reaches {rw.get('goals_reached')} of {rw.get('n_goals')} goals here. "
                                                "The green ghost tool is the current goal.")}
                n += 1
        elif not built:
            v["oracle"] = "the pretrained policy reaches no goal in our MuJoCo port, so the task is not built until a solution is verified"
        t["_verified"] = v
    mf.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n"); return n


UPSTREAM_KEYS = ["category", "object", "task", "instruction", "n_goals", "source_file", "tool_model", "table"]


def upstream_block(t, synced):
    b = {"source": f"{REPO_URL} @ {REF}", "synced": synced, "scene_model": "tabletop"}
    b.update({k: t[k] for k in UPSTREAM_KEYS if t.get(k) not in (None, "", [])})
    b["metric"] = "task progress: goals reached / goals (8 grasp-box keypoints within 1.5 cm; 10 s per goal)"
    return b


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source"); ap.add_argument("--harness"); ap.add_argument("--oracle-jobs"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(); synced = dt.date.today().isoformat()
    if a.source:
        tasks = read_source(Path(a.source).expanduser())
        if not a.dry_run: CACHE.write_text(json.dumps({"source": REPO_URL, "ref": REF, "read": synced, "tasks": tasks}, indent=1) + "\n")
    else:
        tasks = json.loads(CACHE.read_text())["tasks"]
    n_demo = attach(tasks, Path(a.harness).expanduser() if a.harness else None, Path(a.oracle_jobs).expanduser() if a.oracle_jobs else None, synced) if not a.dry_run else 0
    TASK_DIR.mkdir(parents=True, exist_ok=True); new = upd = 0
    for t in tasks:
        path = TASK_DIR / f"{t['id']}.md"
        if path.exists():
            meta, body = read_page(path); meta["upstream"] = upstream_block(t, synced)
            if t.get("_verified"): meta["verified"] = t["_verified"]
            if not a.dry_run: write_page(path, meta, body)
            upd += 1
        else:
            meta = {"title": t["title"], "task_id": t["id"], "benchmark": BENCHMARK, "upstream": upstream_block(t, synced)}
            if t.get("_verified"): meta["verified"] = t["_verified"]
            if not a.dry_run: write_page(path, meta, BODY_TEMPLATE)
            new += 1
    gone = sorted({p.stem for p in TASK_DIR.glob("*.md")} - {t["id"] for t in tasks})
    print(f"dextoolbench: {len(tasks)} tasks, {new} new, {upd} updated, {n_demo} demos" + (f"; gone upstream (kept): {gone}" if gone else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

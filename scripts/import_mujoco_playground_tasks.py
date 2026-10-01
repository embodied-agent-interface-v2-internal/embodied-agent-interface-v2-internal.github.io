#!/usr/bin/env python3
"""Sync MuJoCo Playground task pages (manipulation suite) from Playground's own registry.

MuJoCo Playground (github.com/google-deepmind/mujoco_playground, Apache-2.0) registers its manipulation environments in
`mujoco_playground/_src/manipulation/__init__.py` (`_envs`); each is a class with a `default_config()` (control and
physics timestep, episode length) and an MJX scene XML. Playground defines rewards for RL, not success tests, so the
success test on each page is ours (the robot_coding_bench task's `check()`), stated as such.

`--source DIR` is a Playground checkout: the registry and each env's config are read from it. `--harness DIR` points at
robot_coding_bench: for every env it has built (tasks/mujoco_playground_<snake>), the page's `verified:` zone records the
scripted oracle's result, and `--oracle-jobs DIR` supplies the oracle's replay video as the row's demo, credited to us.

Re-running is safe: only the `upstream:` / `verified:` blocks are rewritten; an env gone upstream is reported, never
deleted. The upstream read is cached in data/benchmarks/mujoco-playground.tasks.upstream.json.

Usage:
  python scripts/import_mujoco_playground_tasks.py --source <playground checkout @ 4057c14> \\
      --harness ../robot_coding_bench --oracle-jobs ../robot_coding_bench/exps/jobs/mj-oracle-all
  python scripts/import_mujoco_playground_tasks.py            # from the cache
"""
from __future__ import annotations

import argparse, datetime as dt, json, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = "mujoco-playground"
CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.upstream.json"
TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"
DEMO_DIR = ROOT / "docs" / "assets" / BENCHMARK / "demos"
REPO_URL = "https://github.com/google-deepmind/mujoco_playground"
REF = "4057c14"
REG = "mujoco_playground/_src/manipulation/__init__.py"

# One line per env, written by us from the env's source (its docstring, reward terms and scene).
ABOUT = {
    "AlohaHandOver": ("ALOHA 2 (two ViperX 300s arms)", "Pick up the box with the left arm, hand it over to the right arm, and hold it at the target."),
    "AlohaSinglePegInsertion": ("ALOHA 2 (two ViperX 300s arms)", "Pick up the socket with one arm and the peg with the other, lift both, and insert the peg into the socket."),
    "PandaPickCube": ("Franka Panda", "Pick up the box and bring it to the target position."),
    "PandaPickCubeOrientation": ("Franka Panda", "Pick up the box and hold it at the target position, in the target orientation."),
    "PandaPickCubeCartesian": ("Franka Panda (Cartesian controller)", "Pick up the box and lift it to a fixed location, with a Cartesian end-effector controller; built for pixel observations and sim2real."),
    "PandaOpenCabinet": ("Franka Panda", "Grasp the handle and pull it along its slide to the target."),
    "PandaRobotiqPushCube": ("Franka Panda + Robotiq 2F-85", "Push the cube across the table to the target."),
    "LeapCubeReorient": ("LEAP hand", "Reorient the cube in the hand to match a goal orientation."),
    "LeapCubeRotateZAxis": ("LEAP hand", "Rotate the cube about the vertical axis as fast as possible without dropping it."),
    "AeroCubeRotateZAxis": ("TetherIA Aero Hand Open", "Rotate the cube about the vertical axis as fast as possible without dropping it."),
}
SUCCESS = {  # our success tests (robot_coding_bench `check()`), for the envs we built
    "AlohaHandOver": "box centre within 3 cm of the target, touching the right gripper and nothing of the left arm, off the table (z >= 0.05 m), at the end of the trajectory",
    "AlohaSinglePegInsertion": "peg tip within 5 mm of the socket's axis and at least 25 % of the socket's depth inside it, at the end of the trajectory",
    "PandaPickCubeOrientation": "box centre within 2 cm of the target and orientation within 15 degrees, at the end of the trajectory",
    "PandaOpenCabinet": "handle within 1.5 cm of the target along its slide, at the end of the trajectory",
}


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()   # AlohaHandOver -> aloha_hand_over


def read_source(src: Path) -> list[dict]:
    reg = (src / REG).read_text()
    mods = {alias: f"{pkg}/{mod}" for pkg, mod, alias in
            re.findall(r"from mujoco_playground\._src\.manipulation\.(\S+) import (\S+) as (\S+)", reg)}
    block = reg.split("_envs = {", 1)[1].split("}", 1)[0]
    tasks = []
    for name, alias in re.findall(r'"(\w+)":\s*(\w+)\.', block):
        f = f"mujoco_playground/_src/manipulation/{mods[alias]}.py"; code = (src / f).read_text()
        cfg = {k: float(v) for k, v in re.findall(r"(ctrl_dt|sim_dt|episode_length|action_repeat)=([\d.]+)", code)}
        robot, what = ABOUT.get(name, ("", ""))
        t = {"id": snake(name), "title": re.sub(r"(?<!^)(?=[A-Z])", " ", name), "env": name, "robot": robot,
             "instruction": what, "source_file": f}
        if cfg.get("ctrl_dt"): t["control_hz"] = round(1 / cfg["ctrl_dt"])
        if cfg.get("ctrl_dt") and cfg.get("episode_length"): t["episode_s"] = round(cfg["ctrl_dt"] * cfg["episode_length"], 2)
        tasks.append(t)
    return tasks


def _run(cmd): return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()


def probe(p: Path):
    dims = _run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(p)])
    dur = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)])
    w, h = (int(x) for x in dims.split(",")[:2]) if dims else (0, 0)
    return w, h, int(round(float(dur))) if dur else 0


def attach(tasks, harness: Path | None, jobs: Path | None, synced: str) -> int:
    DEMO_DIR.mkdir(parents=True, exist_ok=True); mf = DEMO_DIR / "manifest.json"
    manifest = json.loads(mf.read_text()) if mf.is_file() else {}; n = 0; oracle = {}
    if jobs and jobs.is_dir():
        for tr in jobs.glob("*__*"):
            try:
                name = json.loads((tr / "result.json").read_text())["task_name"].split("/")[-1]
                oracle[name] = (tr, json.loads((tr / "verifier/reward.json").read_text()))
            except Exception: continue
    for t in tasks:
        name = f"mujoco_playground_{t['id']}"; built = harness is not None and (harness / "tasks" / name).is_dir()
        if not built: t["_verified"] = {"harness_task": "not built", "checked": synced}; continue
        v = {"source": f"run in plain MuJoCo (robot_coding_bench tasks/{name}, image rcb-mujoco 0.1.1)",
             "stack": "MuJoCo 3.3.7 (CPU, bit-exact replay), Playground's scene XML @ 4057c14 + MuJoCo Menagerie 1b86ece, 50 Hz control",
             "checked": synced, "harness_task": name, "success_test": "ours: " + SUCCESS.get(t["env"], "")}
        if name in oracle:
            tr, rw = oracle[name]
            v["oracle"] = f"scripted IK oracle (privileged state), replayed in the verifier: success {rw.get('success')}, deterministic {rw.get('deterministic')}"
            clip = tr / "verifier" / "replay.mp4"
            if clip.is_file():
                dest = DEMO_DIR / f"{t['id']}.mp4"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-c", "copy", "-movflags", "+faststart", str(dest)], check=True)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", str(dest), "-frames:v", "1", "-q:v", "3", str(DEMO_DIR / f"{t['id']}.jpg")], check=True)
                w, h, sec = probe(dest)
                manifest[t["id"]] = {"bytes": dest.stat().st_size, "height": h, "width": w, "seconds": sec, "poster": True,
                                     "source": ("Recorded by us: our scripted IK oracle (it reads object and target poses from the "
                                                "simulator) replayed from the task's frozen start in plain MuJoCo. Playground ships "
                                                "no demonstrations; its reference solutions are trained RL policies.")}
                n += 1
        t["_verified"] = v
    mf.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n"); return n


UPSTREAM_KEYS = ["env", "robot", "instruction", "control_hz", "episode_s", "source_file"]

BODY_TEMPLATE = """
## Why this task is interesting

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/mujoco-playground.yml. -->

_Not yet written._

## Oracle demo review

<!-- The row plays OUR scripted oracle's replay (built tasks only); Playground ships no demos. -->

_Not yet reviewed._

## Discussion
"""


def upstream_block(t, synced):
    b = {"source": f"{REPO_URL} @ {REF}", "synced": synced, "scene_model": "tabletop"}
    b.update({k: t[k] for k in UPSTREAM_KEYS if t.get(k) not in (None, "", [])})
    b["metric"] = "Playground: dense RL reward, no success test"
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
    n_demo = 0 if a.dry_run else attach(tasks, Path(a.harness).expanduser() if a.harness else None,
                                        Path(a.oracle_jobs).expanduser() if a.oracle_jobs else None, synced)
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
    print(f"{BENCHMARK}: {len(tasks)} tasks, {new} new, {upd} updated, {n_demo} demos" + (f"; gone upstream (kept): {gone}" if gone else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

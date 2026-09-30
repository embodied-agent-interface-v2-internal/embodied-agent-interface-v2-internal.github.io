#!/usr/bin/env python3
"""Sync VLABench's task pages from robot_coding_bench, where our frozen instances of it are defined.

VLABench (OpenMOSS/VLABench @ cf588fe, assets @ 08d7a44) registers 96 tasks with `register.add_task` at that commit;
robot_coding_bench maps each to one task directory (`suites/coverage.json`): an accepted one under `tasks/`, or a
candidate under `staging/`. A task's frozen instance is its `tests/instance.json` (the full construction and initial
state; 13 tasks could not be frozen). The sensor-only twins of eight tasks are not part of the site (owner,
2026-09-29). The site's task id is the native task name (`select_fruit`); a run's job is
`<batch>-<mode>-vlabench-<name with dashes>-i00`
(`task_dir: "vlabench-{task_dashed}-i00"` in state/runs/vlabench.yml).

What it reads, from a robot_coding_bench checkout:
  suites/coverage.json, suites/coverage-catalog.json   the task -> directory map; the task's group and where upstream
                                                        registers it (file, line, SHA256)
  <dir>/task.toml, instruction.md, tests/instance.json  seed, the native instruction, the control contract
  <dir>/validation/status.json                          whether a reference solution was validated (candidates)
and, with --demos, our renders (jobs/site-media/vlabench/<dir>/): the validated reference solution replayed by the
trusted renderer (trajectory.mp4, last.jpg), or, for a frozen task without one, its initial scene (scene.png).

Writes docs/benchmarks/vlabench/tasks/<id>.md (only the `upstream:` block of an existing page; a new task gets a page
from the template), data/benchmarks/vlabench.tasks.upstream.json (the cache), docs/assets/vlabench/demos/<id>.mp4 +
.jpg + manifest.json and docs/assets/vlabench/scenes/<id>.jpg. Re-running is safe; nothing is ever deleted.

Usage:
  python scripts/import_vlabench_tasks.py --source ../robot_coding_bench --demos ../robot_coding_bench/jobs/site-media/vlabench
  python scripts/import_vlabench_tasks.py                  # from the cache
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = "vlabench"
UPSTREAM_REPO = "https://github.com/OpenMOSS/VLABench"
UPSTREAM_COMMIT = "cf588fe60c0c7282174fe979f5913170cfe69017"
ASSETS_COMMIT = "08d7a4479a55c8fbb89ac0fd6fcf06e53d65b4a4"
CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.upstream.json"
TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"
DEMOS = ROOT / "docs" / "assets" / BENCHMARK / "demos"
SCENES = ROOT / "docs" / "assets" / BENCHMARK / "scenes"

BODY_TEMPLATE = """
## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/vlabench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- Where there is a demo, it is the validated reference solution's controls for this frozen
     instance, replayed by our trusted renderer (camera 2, 10 fps = real time). Say whether
     the trajectory is clean and what it relies on. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->
"""


# ------------------------------------------------------------------------------------------------ source


def _json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.is_file() else {}


def _reference(d: Path, accepted: bool) -> tuple[str, str]:
    """(status, reason) of the task's reference solution: validated, failed, or no frozen instance."""
    status = _json(d / "validation" / "status.json")
    if status:
        return status.get("status", ""), status.get("reason", "")
    replay = _json(d / "validation" / "failure-replay" / "result.json")   # an early candidate's reference, replayed
    if replay and replay.get("success") is False:
        return "reference_failed", "our reference trajectory was replayed and does not meet the native condition"
    if accepted and (d / "solution" / "oracle.npz").is_file():
        return "reference_validated", "accepted task: its oracle scored 1 in Harbor acceptance"
    return "", ""


def read_source(root: Path) -> list[dict]:
    coverage = [t for t in _json(root / "suites" / "coverage.json")["tasks"] if t.get("benchmark") == BENCHMARK]
    catalog = {t["native_task"]: t for t in _json(root / "suites" / "coverage-catalog.json")["tasks"]
               if t.get("benchmark") == BENCHMARK}
    tasks = []
    for entry in coverage:
        name = entry["native_task"]
        d = root / entry["paths"][0]
        cat = catalog.get(name, {})
        meta = tomllib.loads((d / "task.toml").read_text()) if (d / "task.toml").is_file() else {}
        inst = _json(d / "tests" / "instance.json")
        status, reason = _reference(d, d.parent.name == "tasks")
        base = {
            "native_task": name,
            "group": cat.get("group", ""),
            "registered_at": (cat.get("source") or {}).get("url", ""),
            "source_file": (cat.get("source") or {}).get("path", ""),
            "seed": (meta.get("metadata") or {}).get("instance_seed", inst.get("seed")),
            "instruction": str(inst.get("instruction") or "").strip(),
            "frozen": bool(inst),
            "initial_state_sha256": inst.get("initial_state_sha256", ""),
            "control_dt": inst.get("control_dt"),
            "agent_budget_s": int((meta.get("agent") or {}).get("timeout_sec", 0)),
        }
        tasks.append({**base, "id": name, "title": name.replace("_", " ").title(), "tier": "privileged",
                      "task_dir": d.name, "path": str(d.relative_to(root)), "accepted": d.parent.name == "tasks",
                      "reference": status or ("no_frozen_instance" if not inst else ""),
                      "reference_reason": reason})
    return tasks


# ----------------------------------------------------------------------------------------------- pages

REFERENCE = {
    "reference_validated": "validated: our reference solution meets the native condition in two fresh-process replays",
    "reference_failed": "none validated: our reference replays exactly but does not meet the native condition",
    "no_frozen_instance": "none: the task could not be frozen at this commit",
    "freeze_failed": "none: the task could not be frozen at this commit",
}


def upstream_block(task: dict, synced: str) -> dict:
    block = {
        "source": f"{UPSTREAM_REPO} @ {UPSTREAM_COMMIT[:7]} (assets @ {ASSETS_COMMIT[:7]})",
        "synced": synced,
        "instruction": task["instruction"],
        "scene_model": f"vlabench_{task['group']}" if task["group"] else "vlabench",
        "native_task": task["native_task"],
        "group": task["group"],
        "tier": task["tier"],
        "seed": task["seed"],
        "registered_at": task["registered_at"],
        "source_file": task["source_file"],
        "robot": "Franka Panda: 9 absolute actuator targets (7 arm joints in radians, 2 finger slides in metres)",
        "control": f"{1 / task['control_dt']:g} Hz (each control held {task['control_dt']:g} s, 100 physics substeps); "
                   "at most 4000 controls" if task.get("control_dt") else "",
        "observation": "privileged state: object and robot poses, official skills, IK and planning",
        "success_criteria": [
            f"the native VLABench success condition of {task['native_task']}, when the trajectory ends "
            "(controls after native termination are rejected)",
            "both fresh-process replays of the trajectory meet it and end in the same exact state",
        ] if task["frozen"] else [],
        "frozen_instance": (f"our task directory {task['task_dir']} (initial state sha256 "
                            f"{task['initial_state_sha256'][:12]})" if task["frozen"] else
                            "not frozen: the native task could not be built at this commit"),
        "reference_solution": REFERENCE.get(task["reference"], task["reference"]),
        "reference_note": task["reference_reason"] if task["reference"] != "reference_validated" else "",
        "agent_budget": f"{task['agent_budget_s']} s of wall clock per mode" if task["agent_budget_s"] else "",
    }
    if task.get("scene_image"):
        block["scene_image"] = task["scene_image"]
    return {k: v for k, v in block.items() if v not in (None, "", [], {})}


def scaffold(task: dict, synced: str) -> dict:
    return {"title": task["title"], "task_id": task["id"], "benchmark": BENCHMARK, "upstream": upstream_block(task, synced)}


# ----------------------------------------------------------------------------------------------- media


def _probe(mp4: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", str(mp4)],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    st = (d.get("streams") or [{}])[0]
    return {"width": st.get("width"), "height": st.get("height"),
            "seconds": max(1, round(float((d.get("format") or {}).get("duration") or 0)))}


def install_media(tasks: list[dict], demos: Path, source: Path, dry: bool) -> int:
    """Reference replays (faststart) with their last frame as the poster; initial-scene stills for the rest."""
    manifest_path = DEMOS / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
    changed = 0
    for t in tasks:
        src = demos / t["task_dir"]
        scene_src = src / "scene.png"
        video, poster_src, credit = None, None, ""
        render = _json(src / "render.json")
        if render.get("complete") and (src / "trajectory.mp4").is_file():
            video, poster_src = src / "trajectory.mp4", src / "last.jpg"
            credit = (f"Recorded by us: our validated reference solution's {render.get('n_actions')} controls for this "
                      "frozen instance, replayed by our trusted renderer (camera 2; 10 fps = real time).")
        if video is not None:
            dst, poster = DEMOS / f"{t['id']}.mp4", DEMOS / f"{t['id']}.jpg"
            if dry:
                changed += int(t["id"] not in manifest)
                continue
            DEMOS.mkdir(parents=True, exist_ok=True)
            tmp = DEMOS / f".{t['id']}.tmp.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-c", "copy", "-movflags", "+faststart", str(tmp)],
                           check=True)
            if not dst.is_file() or dst.read_bytes() != tmp.read_bytes():
                tmp.replace(dst)
                changed += 1
            else:
                tmp.unlink()
            if poster_src is not None and poster_src.is_file():
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(poster_src), "-q:v", "3", str(poster)], check=True)
            else:
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.2", "-i", str(dst), "-frames:v", "1", "-q:v", "3",
                                str(poster)], check=True)
            manifest[t["id"]] = {**_probe(dst), "bytes": dst.stat().st_size, "poster": poster.is_file(), "source": credit}
        elif scene_src.is_file():
            t["scene_image"] = f"{t['id']}.jpg"
            if not dry:
                SCENES.mkdir(parents=True, exist_ok=True)
                dst, tmp = SCENES / t["scene_image"], SCENES / f".{t['scene_image']}.tmp.jpg"
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(scene_src), "-q:v", "3", str(tmp)], check=True)
                if not dst.is_file() or dst.read_bytes() != tmp.read_bytes():
                    tmp.replace(dst)
                    changed += 1
                else:
                    tmp.unlink()
    if not dry:
        text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        if not manifest_path.is_file() or manifest_path.read_text() != text:
            DEMOS.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(text)
    return changed


# ------------------------------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=None, help="a robot_coding_bench checkout")
    ap.add_argument("--demos", default=None, help="our renders: <dir>/<task dir>/")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rewrite pages even when upstream is unchanged")
    args = ap.parse_args()

    if args.source:
        source = Path(args.source).expanduser()
        tasks = read_source(source)
        if not tasks:
            sys.exit(f"no VLABench tasks in {source}/suites/coverage.json")
        media = install_media(tasks, Path(args.demos).expanduser(), source, args.dry_run) if args.demos else 0
        payload = {"upstream": f"{UPSTREAM_REPO} @ {UPSTREAM_COMMIT}", "tasks": tasks}
        old = json.loads(CACHE.read_text()) if CACHE.is_file() else {}
        if {k: old.get(k) for k in payload} != payload:
            payload["read"] = dt.date.today().isoformat()
            if not args.dry_run:
                CACHE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        print(f"read {len(tasks)} task(s) from {source} -> {CACHE.name}")
    else:
        if not CACHE.is_file():
            sys.exit(f"no cache at {CACHE}; run once with --source <robot_coding_bench checkout>")
        tasks, media = json.loads(CACHE.read_text())["tasks"], 0

    synced = dt.date.today().isoformat()
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    created = updated = unchanged = 0
    seen = set()
    for task in tasks:
        seen.add(task["id"])
        path = TASK_DIR / f"{task['id']}.md"
        fresh = upstream_block(task, synced)
        if path.is_file():
            meta, body = read_page(path)
            current = dict(meta.get("upstream") or {})
            if current == dict(fresh, synced=current.get("synced", synced)) and not args.force:
                unchanged += 1
                continue
            meta["upstream"] = dict(fresh, synced=synced)
            if not args.dry_run:
                write_page(path, meta, body)
            updated += 1
        else:
            if not args.dry_run:
                write_page(path, scaffold(task, synced), BODY_TEMPLATE)
            created += 1
    orphans = sorted(p.stem for p in TASK_DIR.glob("*.md") if p.stem not in seen and p.stem != "index")
    print(f"tasks     : {len(tasks)}")
    print(f"created   : {created}{' (dry run)' if args.dry_run else ''}")
    print(f"updated   : {updated}")
    print(f"unchanged : {unchanged}")
    print(f"media     : {media} file(s) changed" if args.demos else "media     : not asked (--demos dir)")
    if orphans:
        print(f"no longer in robot_coding_bench ({len(orphans)}): {', '.join(orphans)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

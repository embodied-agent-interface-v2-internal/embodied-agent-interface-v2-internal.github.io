#!/usr/bin/env python3
"""Sync MetaWorld+'s task pages from robot_coding_bench, where the frozen instances are defined.

MetaWorld+ is our suite over upstream Meta-World 3.1.1 (Farama-Foundation/Metaworld @ 59fc34d, the v3 environments with
reward v2): all 50 environments, 70 frozen instances. Every instance is a directory in robot_coding_bench,
`tasks/metaworldplus-<env>-privileged-iNN`, whose frozen NPZ holds the full MuJoCo state, model arrays, task caches and
RNG (never a seed-only restore). The site's task id is `<family>_iNN` (dashes become underscores), so
`metaworldplus-push-privileged-i00` is `push_i00`, and a run's job is `<batch>-<mode>-metaworldplus-<family>-iNN`
(`task_dir: "metaworldplus-{task_dashed}"` in state/runs/metaworldplus.yml).

What it reads:
  <source>/tasks/metaworldplus-*-privileged-iNN   task.toml ([metadata] environment_id, family, instance_seed,
                                                   budgets), instruction.md (the task sentence), README.md
  <inventory>  (optional) the experiment's frozen inventory (robot_coding_bench jobs/<experiment>/inventory/):
               inventory.json (instance SHA, source tree digest, limited-mode target observability) and
               limited-target-errata.json (audited corrections, applied here)
  <metaworld>  (optional) the upstream checkout at the pinned commit: env_dict.py (the environment's class and file)
               and the `success` line(s) of its evaluate_state
and, with --demos, our renders of each instance's trusted reference controls (the upstream scripted policy's,
replayed by the trusted renderer): <demos>/<task dir>/replay.mp4 + final.png + render.json.

Writes docs/benchmarks/metaworldplus/tasks/<id>.md (only the `upstream:` block of an existing page; a new task gets a
page from the template), data/benchmarks/metaworldplus.tasks.upstream.json (the cache: rebuilding the pages needs no
source), and docs/assets/metaworldplus/demos/<id>.mp4 + .jpg + manifest.json. Re-running is safe and expected: an
unchanged source writes nothing; a task that disappears is reported, never deleted.

Usage:
  python scripts/import_metaworldplus_tasks.py --source ../robot_coding_bench \\
      --inventory ../robot_coding_bench/jobs/metaworldplus-codex-luna-high-60min-20260928T1717Z/inventory \\
      --metaworld ../robot_coding_bench/.cache/robot24/metaworld --demos ../robot_coding_bench/jobs/site-media/metaworldplus
  python scripts/import_metaworldplus_tasks.py                  # from the cache
  python scripts/import_metaworldplus_tasks.py ... --dry-run
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = "metaworldplus"
UPSTREAM_REPO = "https://github.com/Farama-Foundation/Metaworld"
UPSTREAM_COMMIT = "59fc34d7768af9785e4688c3e1db671424f4a6c3"
CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.upstream.json"
TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"
DEMOS = ROOT / "docs" / "assets" / BENCHMARK / "demos"
DIR_RE = re.compile(r"metaworldplus-(.+)-privileged-i(\d+)")
TARGET_KIND = {
    "visible_marker": "a native goal marker that renders in the fixed cameras",
    "geometry_and_language": "set by visible object or mechanism geometry and the task sentence",
    "not_observable": "in privileged state only: no native marker renders and the task sentence does not name it",
}

BODY_TEMPLATE = """
## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/metaworldplus.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- The demo is the upstream scripted policy's controls for this frozen instance, replayed
     by our trusted renderer (corner and corner3 cameras, 80 fps = real time). Say whether
     the trajectory is clean and what it relies on. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->
"""


# ------------------------------------------------------------------------------------------------ source


def _task_sentence(instruction_md: str) -> str:
    """The bold task sentence of the first line: `Complete this fixed-instance robot task: **Push the block.**`."""
    m = re.search(r"\*\*(.+?)\*\*", instruction_md.splitlines()[0] if instruction_md else "")
    return m.group(1).strip() if m else ""


def _title(env_id: str, index: int) -> str:
    return f"{env_id.removesuffix('-v3').replace('-', ' ').title()} · i{index:02d}"


def _success_statements(path: Path) -> str:
    """The file's complete statements that set the native success flag: `success = ...` and the `"success": ...` entry
    of the info dict evaluate_state returns (ast source segments, so a multi-line expression stays whole)."""
    if not path.is_file():
        return ""
    src = path.read_text()
    found = []
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "success" for t in node.targets):
            found.append((node.lineno, ast.get_source_segment(src, node)))
        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == "success":
                    found.append((key.lineno, f'"success": {ast.get_source_segment(src, value)}'))
    return "\n".join(dict.fromkeys(s for _, s in sorted(found)))


def upstream_source(metaworld: Path | None) -> dict[str, dict]:
    """environment id -> {class, source_file, success_check} from the pinned upstream checkout (ast, never imported)."""
    if not metaworld:
        return {}
    head = subprocess.run(["git", "-C", str(metaworld), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head != UPSTREAM_COMMIT:
        sys.exit(f"{metaworld} is at {head or '?'}, not the pinned {UPSTREAM_COMMIT}")
    pkg = metaworld / "metaworld"
    # ENV_CLS_MAP = {"push-v3": envs.SawyerPushEnvV3, ...}; envs/__init__.py imports each class from its own file
    modules = {}
    for node in ast.walk(ast.parse((pkg / "envs" / "__init__.py").read_text())):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("metaworld.envs."):
            for a in node.names:
                modules[a.asname or a.name] = node.module
    out = {}
    for node in ast.walk(ast.parse((pkg / "env_dict.py").read_text())):
        if not (isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "ENV_CLS_MAP" for t in node.targets)
                and isinstance(node.value, ast.Dict)):
            continue
        for key, value in zip(node.value.keys, node.value.values):
            if not (isinstance(key, ast.Constant) and isinstance(value, ast.Attribute)):
                continue
            env_id, cls = key.value, value.attr
            module = modules.get(cls)
            if not module:
                continue
            rel = module.replace(".", "/") + ".py"
            path = metaworld / rel
            out[env_id] = {"class": cls, "source_file": rel, "success_check": _success_statements(path)}
    return out


def read_source(root: Path, inventory: Path | None, metaworld: Path | None) -> list[dict]:
    inv = json.loads((inventory / "inventory.json").read_text()) if inventory else {"rows": []}
    rows = {r["source_slug"]: r for r in inv.get("rows", [])}
    errata = {}
    if inventory and (inventory / "limited-target-errata.json").is_file():
        for c in json.loads((inventory / "limited-target-errata.json").read_text()).get("corrections", []):
            errata[c["environment_id"]] = c
    native = upstream_source(metaworld)
    tasks = []
    for d in sorted((root / "tasks").glob("metaworldplus-*-privileged-i*")):
        m = DIR_RE.fullmatch(d.name)
        if not m or not (d / "task.toml").is_file():
            continue
        meta = tomllib.loads((d / "task.toml").read_text())
        md = meta.get("metadata") or {}
        index = int(m.group(2))
        family = str(md.get("family", m.group(1))).replace("-", "_")
        env_id = md.get("environment_id", "")
        row = rows.get(d.name, {})
        target = dict(row.get("limited_target") or {})
        fix = errata.get(env_id) or {}
        if fix.get("corrected"):
            target.update(kind=fix["corrected"], rationale=fix.get("evidence", target.get("rationale", "")), audited=True)
        if fix.get("corrected_rationale"):
            target.update(rationale=fix["corrected_rationale"], audited=True)
        limited = (row.get("modes") or {}).get("limited") or {}
        up = native.get(env_id, {})
        tasks.append({
            "id": f"{family}_i{index:02d}",
            "title": _title(env_id, index),
            "family": family,
            "environment_id": env_id,
            "index": index,
            "seed": md.get("instance_seed"),
            "instruction": _task_sentence((d / "instruction.md").read_text()) if (d / "instruction.md").is_file() else "",
            "instance_sha": row.get("instance_sha", ""),
            "source_tree_sha256": row.get("source_tree_sha256", ""),
            "task_dir": d.name,
            "agent_budget_s": int((meta.get("agent") or {}).get("timeout_sec", 0)),
            "upstream_class": up.get("class", ""),
            "upstream_file": up.get("source_file", ""),
            "success_check": up.get("success_check", ""),
            "target_kind": target.get("kind", ""),
            "target_rationale": target.get("rationale", ""),
            "target_audited": bool(target.get("audited")),
            "limited_blocked": limited.get("blocked_reason") or "",
        })
    return tasks


# ----------------------------------------------------------------------------------------------- pages


def upstream_block(task: dict, synced: str) -> dict:
    """What upstream Meta-World defines about the task, and the facts of our frozen instance of it."""
    kind = task["target_kind"]
    block = {
        "source": f"{UPSTREAM_REPO} @ {UPSTREAM_COMMIT[:7]}",
        "synced": synced,
        "instruction": task["instruction"],
        "scene_model": task["environment_id"],
        "environment_id": task["environment_id"],
        "family": task["family"],
        "instance": task["index"],
        "seed": task["seed"],
        "instance_sha": task["instance_sha"],
        "robot": "Sawyer, fixed wrist, two-finger gripper; mocap XYZ control",
        "action": "[dx, dy, dz, grip] in [-1, 1]: 0.01 m per unit, grip +1 closes; 80 Hz (5 physics steps of 2.5 ms)",
        "horizon": "500 controls (6.25 s simulated)",
        "success_criteria": [
            "the native v3 / reward-v2 success flag, attained at any control of the trajectory",
            "both fresh-process replays of the trajectory meet this and end in the same exact state",
        ],
        "success_check": task["success_check"],
        "source_file": task["upstream_file"],
        "env_class": task["upstream_class"],
        "limited_target": (f"{TARGET_KIND.get(kind, kind)}{' (audited correction)' if task['target_audited'] else ''}: "
                           f"{task['target_rationale']}") if kind else "",
        "limited_mode": ("not evaluated: the goal is in privileged state only" if task["limited_blocked"]
                         else "evaluated: RGB-D, calibration and proprioception, one sealed episode"),
        "frozen_instance": (f"full MuJoCo state, model arrays, task caches and RNG; our task directory {task['task_dir']}"
                            + (f" (tree sha256 {task['source_tree_sha256'][:12]})" if task["source_tree_sha256"] else "")),
        "agent_budget": f"{task['agent_budget_s']} s of wall clock per mode" if task["agent_budget_s"] else "",
    }
    return {k: v for k, v in block.items() if v not in (None, "", [], {})}


def scaffold(task: dict, synced: str) -> dict:
    return {"title": task["title"], "task_id": task["id"], "benchmark": BENCHMARK, "upstream": upstream_block(task, synced)}


# ----------------------------------------------------------------------------------------------- demos


def _probe(mp4: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", str(mp4)],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    st = (d.get("streams") or [{}])[0]
    return {"width": st.get("width"), "height": st.get("height"),
            "seconds": max(1, round(float((d.get("format") or {}).get("duration") or 0)))}


def install_demos(tasks: list[dict], demos: Path, dry: bool) -> int:
    """Copy each instance's reference replay (remuxed with faststart) and its last frame as the poster."""
    manifest_path = DEMOS / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
    changed = 0
    for t in tasks:
        src = demos / t["task_dir"]
        info = json.loads((src / "render.json").read_text()) if (src / "render.json").is_file() else {}
        if not info.get("rendered") or not (src / "replay.mp4").is_file():
            continue
        dst, poster = DEMOS / f"{t['id']}.mp4", DEMOS / f"{t['id']}.jpg"
        if dry:
            changed += int(t["id"] not in manifest)
            continue
        DEMOS.mkdir(parents=True, exist_ok=True)
        tmp = DEMOS / f".{t['id']}.tmp.mp4"
        # faststart: without the index first a browser cannot show the duration or seek (as scripts/fetch_demos.py)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src / "replay.mp4"), "-c", "copy", "-movflags", "+faststart",
                        str(tmp)], check=True)
        if not dst.is_file() or dst.read_bytes() != tmp.read_bytes():
            tmp.replace(dst)
            changed += 1
        else:
            tmp.unlink()
        if (src / "final.png").is_file():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src / "final.png"), "-q:v", "3", str(poster)], check=True)
        entry = {**_probe(dst), "bytes": dst.stat().st_size, "poster": poster.is_file(),
                 "source": (f"Recorded by us: the upstream scripted policy's {info.get('n_actions')} controls for this frozen "
                            "instance, replayed by our trusted renderer (corner and corner3 cameras, shown rotated 180°; "
                            "80 fps = real time).")}
        manifest[t["id"]] = entry
    if not dry:
        text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        if not manifest_path.is_file() or manifest_path.read_text() != text:
            DEMOS.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(text)
    return changed


# ------------------------------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=None, help="a robot_coding_bench checkout holding tasks/metaworldplus-*")
    ap.add_argument("--inventory", default=None, help="the experiment's inventory/ directory (instance SHA, limited target)")
    ap.add_argument("--metaworld", default=None, help="the upstream Meta-World checkout at the pinned commit")
    ap.add_argument("--demos", default=None, help="our reference renders: <dir>/<task dir>/replay.mp4")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rewrite pages even when upstream is unchanged")
    args = ap.parse_args()

    if args.source:
        source = Path(args.source).expanduser()
        tasks = read_source(source, Path(args.inventory).expanduser() if args.inventory else None,
                            Path(args.metaworld).expanduser() if args.metaworld else None)
        if not tasks:
            sys.exit(f"no tasks/metaworldplus-*-privileged-i* under {source}")
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
        tasks = json.loads(CACHE.read_text())["tasks"]
    demo_files = install_demos(tasks, Path(args.demos).expanduser(), args.dry_run) if args.demos else 0

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
    print(f"environments : {len({t['environment_id'] for t in tasks})}")
    print(f"tasks        : {len(tasks)}")
    print(f"created      : {created}{' (dry run)' if args.dry_run else ''}")
    print(f"updated      : {updated}")
    print(f"unchanged    : {unchanged}")
    print(f"demos        : {demo_files} file(s) changed" if args.demos else "demos        : not asked (--demos dir)")
    if orphans:
        print(f"no longer in robot_coding_bench ({len(orphans)}): {', '.join(orphans)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Sync HumanoidBench's task pages from robot_coding_bench, where our selection of it is defined.

HumanoidBench (carlosferrazza/humanoid-bench, pinned in our image at cb11890) registers 32 tasks for a Unitree H1,
bare or with two Shadow hands. robot_coding_bench keeps 9 of them (23 until 2026-10-04) plus one fixture (sit_simple)
and defines each as a pair, `tasks/humanoidbench-<category>-<task>-i00-privileged` and its `-standard` twin (before
protocol v1.0: `tasks/humanoidbench-<category>-<task>-i00` and `-limited`), generated from
`scripts/humanoidbench/subset.toml` (what a human decided: which tasks, why, how to describe them) and `facts.json`
(what the simulator says: the success bar, the episode length, the action size, the all-zero-action floor). The site's
task id is `<category>_<task>`, so `humanoidbench-manip-bookshelf-simple-i00` is `manip_bookshelf_simple`, and a run's
job is `<batch>-<mode>-humanoidbench-<category>-<task>-i00` (`task_dir: "humanoidbench-{task_dashed}-i00"` in
state/runs/humanoidbench.yml).

What it reads, from a commit's export (`git archive <commit>`, never a checkout of anyone's working tree):
  scripts/humanoidbench/subset.toml   env id, robot, paper category, capability class, role, the scoring prose
  scripts/humanoidbench/facts.json    success bar, max steps, action size, all-zero-action return
  tasks/<dir>/instruction.md          the task sentence (its `**Task:**` paragraph)
  tasks/<dir>/task.toml               the agent's budget
and, with --scenes, the starting scene as the limited mode's room camera sees it at t = 0 (`gen_tasks.py
measure-limited --images DIR` writes <task>/t0_room_camera.png; a results site's assets/cameras/<task>/room_camera.png
is the same file): the task's scene image. HumanoidBench publishes no per-task demonstration, so a row shows that still.

Writes docs/benchmarks/humanoidbench/tasks/<id>.md (only the `upstream:` block of an existing page; a new task gets a
page from the template), data/benchmarks/humanoidbench.tasks.upstream.json (the cache: rebuilding the pages needs no
source), docs/assets/humanoidbench/scenes/<id>.png, and a NEW task's entry in state/tasks/humanoidbench.yml: `status:
keep` with its capability class as the note, and the fixture `excluded` (an entry that exists is never changed:
curation is the owner's). Re-running is safe: an unchanged source writes nothing; a task that disappears is reported,
never deleted.

Usage:
  python scripts/import_humanoidbench_tasks.py --source ../robot_coding_bench --commit origin/main \\
      --scenes ../robot_coding_bench/jobs/results/humanoidbench/assets/cameras
  python scripts/import_humanoidbench_tasks.py                  # from the cache
  python scripts/import_humanoidbench_tasks.py ... --dry-run
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = "humanoidbench"
UPSTREAM = "https://github.com/carlosferrazza/humanoid-bench @ cb11890"   # images/humanoidbench/Dockerfile HB_COMMIT
CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.upstream.json"
TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"
SCENES = ROOT / "docs" / "assets" / BENCHMARK / "scenes"
STATE = ROOT / "state" / "tasks" / f"{BENCHMARK}.yml"
CATEGORY_NAMES = {"loco": "Locomotion", "manip": "Manipulation"}
ROBOTS = {"h1": "Unitree H1 (19 actuators)", "h1hand": "Unitree H1 with two Shadow hands (61 actuators)"}

BODY_TEMPLATE = """
## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/humanoidbench.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- HumanoidBench publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->
"""


# ------------------------------------------------------------------------------------------------ source


def export(source: Path, commit: str, into: Path) -> tuple[Path, str]:
    """The HumanoidBench task dirs and sources of `commit` in the git repo `source`, unpacked under `into`; and the
    short commit."""
    git = ["git", "-C", str(source)]
    sha = subprocess.run(git + ["rev-parse", "--short", f"{commit}^{{commit}}"], capture_output=True, text=True, check=True).stdout.strip()
    names = subprocess.run(git + ["ls-tree", "--name-only", sha, "tasks/"], capture_output=True, text=True, check=True).stdout.split()
    dirs = [n for n in names if Path(n).name.startswith("humanoidbench-")]
    if not dirs:
        sys.exit(f"no tasks/humanoidbench-* at {commit} ({sha}) in {source}")
    into.mkdir(parents=True, exist_ok=True)
    tar = into / "tasks.tar"
    with tar.open("wb") as fh:
        subprocess.run(git + ["archive", "--format=tar", sha, "--", "scripts/humanoidbench/subset.toml",
                              "scripts/humanoidbench/facts.json", *dirs], stdout=fh, check=True)
    with tarfile.open(tar) as tf:
        tf.extractall(into, filter="data")
    tar.unlink()
    return into, sha


def _task_sentence(instruction_md: str) -> str:
    """The instruction's task paragraph, as plain text: from its `**Task:**` to the end of that paragraph."""
    lines = instruction_md.splitlines()
    start = next((i for i, l in enumerate(lines) if "**Task:**" in l), None)
    if start is None:
        return ""
    para = []
    for line in lines[start:]:
        if not line.strip():
            break
        para.append(line.strip())
    text = " ".join(para).split("**Task:**", 1)[1].strip()
    text = re.sub(r"`([^`]*)`", r"\1", text).replace("**", "")
    return text[:1].upper() + text[1:]


def _prose(text: str) -> str:
    """One line of plain text: subset.toml's prose wraps its lines and marks emphasis with *...*."""
    return re.sub(r"\*([^*]+)\*", r"\1", " ".join((text or "").split()))


def task_pair(base: Path) -> tuple[Path, Path | None]:
    """A task's privileged directory and its limited twin: `<base>-privileged` and `-standard` since protocol v1.0,
    `<base>` and `<base>-limited` before it (the twin is None when there is none)."""
    named = lambda suffix: base.with_name(base.name + suffix)  # noqa: E731
    priv = named("-privileged") if named("-privileged").is_dir() else base
    return priv, next((d for d in (named("-standard"), named("-limited")) if d.is_dir()), None)


def read_source(root: Path) -> list[dict]:
    subset = tomllib.loads((root / "scripts" / "humanoidbench" / "subset.toml").read_text())
    facts = json.loads((root / "scripts" / "humanoidbench" / "facts.json").read_text())
    tasks = []
    for t in subset.get("task") or []:
        family, cat = t["family"], t.get("paper_category", "")
        base = root / "tasks" / f"humanoidbench-{cat}-{family.replace('_', '-')}-i00"
        d, twin = task_pair(base)
        f = facts.get(family) or {}
        if not (d / "task.toml").is_file() or not f:
            continue
        meta = tomllib.loads((d / "task.toml").read_text())
        lim = t.get("standard") or t.get("limited") or {}
        flim = f.get("standard") or f.get("limited") or {}
        tasks.append({
            "id": f"{cat}_{family}",
            "title": f"{CATEGORY_NAMES.get(cat, cat.title())} · {family.replace('_', ' ').capitalize()}",
            "family": family,
            "category": cat,
            "env_id": t.get("env_id", ""),
            "robot": t.get("robot", ""),
            "capability_class": t.get("capability_class", ""),
            "role": t.get("role", ""),
            "instruction": _task_sentence((d / "instruction.md").read_text()) if (d / "instruction.md").is_file() else "",
            "scoring": _prose(t.get("scoring_note", "")),
            "ends": _prose(t.get("ends_note", "")),
            "limited_ends": _prose(lim.get("ends", "")),
            "limited_hidden": _prose(lim.get("hidden", "")),
            "bar": f.get("success_bar"),
            "max_steps": f.get("max_steps"),
            "nu": f.get("nu"),
            "nop_return": f.get("nop_return"),
            "control_hz": flim.get("control_hz"),
            "image_hw": flim.get("image_hw"),
            "agent_budget_s": int((meta.get("agent") or {}).get("timeout_sec", 0)),
            "limited_twin": twin is not None,
            "task_dir": base.name,
        })
    return tasks


# ----------------------------------------------------------------------------------------------- pages


def upstream_block(task: dict, synced: str, commit: str) -> dict:
    """What HumanoidBench and our task definitions state about the task (the agent's side and the grader's)."""
    bar, steps = task["bar"], task["max_steps"]
    criteria = [f"the summed per-step reward over one episode reaches {bar:g}, HumanoidBench's own success bar "
                f"(a total of rewards, not a number of steps; an episode is at most {steps} control steps)" if bar else "",
                "unlimited: both fresh-process replays of the handed-in trajectory reach it and end in the same state",
                "limited: the run passes the moment its one episode reaches it (no reset in our runs since 2026-10-04; "
                "the recorded episode replays to the same state)"]
    hw = task.get("image_hw") or []
    block = {
        "source": f"{UPSTREAM}, as defined in our task definitions @ {commit}" if commit else UPSTREAM,
        "synced": synced,
        "instruction": task["instruction"],
        "env_id": task["env_id"],
        "robot": ROBOTS.get(task["robot"], task["robot"]),
        "scene_model": f"humanoidbench_{task['category']}",
        "scene_image": f"{task['id']}.png",
        "category": CATEGORY_NAMES.get(task["category"], task["category"]),
        "capability_class": task["capability_class"],
        "role": task["role"],
        "success_criteria": [c for c in criteria if c],
        "scoring": task["scoring"],
        "ends_early": task["ends"],
        "zero_action_return": task["nop_return"],
        "action_dim": task["nu"],
        "control_rate_hz": task["control_hz"],
        "limited_mode": (f"head cameras (RGB {hw[0]}×{hw[1]}), joint angles and velocities; a pelvis IMU and a camera "
                         f"fixed in the room when the run turns them on. Not {task['limited_hidden']}, not the reward"
                         if task["limited_twin"] and hw else ""),
        "agent_budget": f"{task['agent_budget_s']} s of wall clock per mode" if task["agent_budget_s"] else "",
    }
    return {k: v for k, v in block.items() if v not in (None, "", [], {})}


def scaffold(task: dict, synced: str, commit: str) -> dict:
    return {"title": task["title"], "task_id": task["id"], "benchmark": BENCHMARK,
            "upstream": upstream_block(task, synced, commit)}


# ----------------------------------------------------------------------------------------------- state


def seed_state(tasks: list[dict], dry: bool) -> list[str]:
    """A new task's entry in state/tasks/humanoidbench.yml: kept (subset.toml selected it), its capability class as
    the note; the fixture excluded. Existing entries are untouched."""
    import yaml
    text = STATE.read_text() if STATE.is_file() else ""
    have = yaml.safe_load(text) or {} if text else {}
    new = [t for t in tasks if t["id"] not in have]
    if new and not dry:
        add = "".join(f"{t['id']}:\n  status: keep\n  note: {json.dumps(t['capability_class'], ensure_ascii=False)}\n"
                      + ("  excluded: \"a fixture, not scored: it checks the pipeline end to end (subset.toml role = fixture)\"\n"
                         if t["role"] == "fixture" else "") for t in new)
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(text + ("" if not text or text.endswith("\n") else "\n") + add)
    return [t["id"] for t in new]


# ------------------------------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=None, help="a robot_coding_bench git clone (with --commit) or an export of it")
    ap.add_argument("--commit", default="", help="the commit to read from the clone (git archive), e.g. origin/main")
    ap.add_argument("--scenes", default=None, help="a dir of <task>/room_camera.png or <task>/t0_room_camera.png")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rewrite pages even when upstream is unchanged")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="humanoidbench-") as tmpd:
        if args.source:
            source = Path(args.source).expanduser()
            if args.commit and (source / ".git").exists():
                root, commit = export(source, args.commit, Path(tmpd) / "export")
            else:
                root, commit = source, args.commit
            tasks = read_source(root)
            if not tasks:
                sys.exit(f"no HumanoidBench tasks under {source}")
            payload = {"commit": commit, "tasks": tasks}
            old = json.loads(CACHE.read_text()) if CACHE.is_file() else {}
            if {k: old.get(k) for k in payload} != payload:
                payload["read"] = dt.date.today().isoformat()
                if not args.dry_run:
                    CACHE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
            print(f"read {len(tasks)} task(s) at {commit or '(no commit)'} from {source} -> {CACHE.name}")
        else:
            if not CACHE.is_file():
                sys.exit(f"no cache at {CACHE}; run once with --source <robot_coding_bench clone> --commit <commit>")
            payload = json.loads(CACHE.read_text())
            tasks, commit = payload["tasks"], payload.get("commit", "")

    scenes = 0
    if args.scenes:
        for t in tasks:
            src = next((p for p in (Path(args.scenes) / t["family"] / "room_camera.png",
                                    Path(args.scenes) / t["family"] / "t0_room_camera.png") if p.is_file()), None)
            dst = SCENES / f"{t['id']}.png"
            if src and (not dst.is_file() or dst.read_bytes() != src.read_bytes()):
                scenes += 1
                if not args.dry_run:
                    SCENES.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src, dst)

    synced = dt.date.today().isoformat()
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    created = updated = unchanged = 0
    seen = set()
    for task in tasks:
        seen.add(task["id"])
        path = TASK_DIR / f"{task['id']}.md"
        fresh = upstream_block(task, synced, commit)
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
                write_page(path, scaffold(task, synced, commit), BODY_TEMPLATE)
            created += 1
    seeded = seed_state(tasks, args.dry_run)
    orphans = sorted(p.stem for p in TASK_DIR.glob("*.md") if p.stem not in seen and p.stem != "index")
    print(f"tasks     : {len(tasks)}")
    print(f"created   : {created}{' (dry run)' if args.dry_run else ''}")
    print(f"updated   : {updated}")
    print(f"unchanged : {unchanged}")
    print(f"scenes    : {scenes} file(s) changed" if args.scenes else "scenes    : not asked (--scenes DIR)")
    if seeded:
        print(f"state for {len(seeded)} new task(s) in {STATE.relative_to(ROOT)}")
    if orphans:
        print(f"no longer in robot_coding_bench ({len(orphans)}): {', '.join(orphans)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

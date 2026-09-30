#!/usr/bin/env python3
"""Sync KinDER's task pages from robot_coding_bench, where our selection of it is defined.

KinDER (Princeton-Robot-Planning-and-Learning/kindergarden, pinned in our image at 5b2dbac) has 31 task families of
physical reasoning for a TidyBot++ mobile manipulator: Dynamic3D in MuJoCo, Kinematic3D in PyBullet, and 2D ones in
Pymunk. robot_coding_bench keeps 11 of them, one variant each at seed 0, and defines each as a pair,
`tasks/kinder-<family>-i00` and its `-limited` twin, generated from `scripts/kinder/subset.toml` (what a human decided:
which environments, each goal's sentence) and `facts.json` (what the simulator says: the action space, the state
size, the camera images, the checks). The site's task id is the family with underscores, so `kinder-sweep-into-drawer-i00`
is `sweep_into_drawer`, and a run's job is `<batch>-<mode>-kinder-<family>-i00` (`task_dir: "kinder-{task_dashed}-i00"`
in state/runs/kinder.yml).

What it reads, from a commit's export (`git archive <commit>`, never a checkout of anyone's working tree):
  scripts/kinder/subset.toml          env id, the episode length (where a task sets its own), the goal sentences
  scripts/kinder/facts.json           the action space, the state vector's size, the limited mode's cameras
  tasks/<dir>/instruction.md          the task sentence (its `**Task:**` paragraph) and the scoring's step budget
  tasks/<dir>-limited/instruction.md  the limited twin's task sentence, where it differs
  tasks/<dir>/task.toml               the agent's budget
and, with --scenes, the starting scene as the limited mode's room camera sees it at t = 0 (a results site's
assets/cameras/<family>/room_camera.png, or `t0_room_camera.png`): the task's scene image, stored as JPEG (640×480 PNG
is ~300 KB each). KinDER publishes no per-task demonstration, so a row shows that still.

Writes docs/benchmarks/kinder/tasks/<id>.md (only the `upstream:` block of an existing page; a new task gets a page
from the template), data/benchmarks/kinder.tasks.upstream.json (the cache: rebuilding the pages needs no source),
docs/assets/kinder/scenes/<id>.jpg, and a NEW task's entry in state/tasks/kinder.yml: `status: keep` with its
category as the note (an entry that exists is never changed: curation is the owner's). Re-running is safe: an
unchanged source writes nothing; a task that disappears is reported, never deleted.

Usage:
  python scripts/import_kinder_tasks.py --source ../robot_coding_bench --commit dev/pingyue \\
      --scenes ../robot_coding_bench/jobs/results/kinder/assets/cameras
  python scripts/import_kinder_tasks.py                  # from the cache
  python scripts/import_kinder_tasks.py ... --dry-run
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = "kinder"
UPSTREAM = "https://github.com/Princeton-Robot-Planning-and-Learning/kindergarden @ 5b2dbac"   # images/kinder/Dockerfile
CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.upstream.json"
TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"
SCENES = ROOT / "docs" / "assets" / BENCHMARK / "scenes"
STATE = ROOT / "state" / "tasks" / f"{BENCHMARK}.yml"
# KinDER's own environment classes (facts.json entry_point: kinder.envs.<kind>.…), and the simulator each runs in.
KINDS = {"dynamic3d": ("Dynamic3D", "MuJoCo"), "kinematic3d": ("Kinematic3D", "PyBullet")}
ROBOTS = {"dynamic3d": "TidyBot++: holonomic base, Kinova Gen3 7-DoF arm, Robotiq 2F-85 gripper",
          "kinematic3d": "TidyBot++, kinematic: holonomic base, Kinova Gen3 7-DoF arm, gripper; a move that would "
                         "collide is not carried out"}

BODY_TEMPLATE = """
## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/kinder.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- KinDER publishes no per-task demonstration; the row shows the
     starting scene. Say here if a reference trajectory is ever recorded. -->

_No demo._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->
"""


# ------------------------------------------------------------------------------------------------ source


def export(source: Path, commit: str, into: Path) -> tuple[Path, str]:
    """The KinDER task dirs and sources of `commit` in the git repo `source`, unpacked under `into`; and the short
    commit."""
    git = ["git", "-C", str(source)]
    sha = subprocess.run(git + ["rev-parse", "--short", f"{commit}^{{commit}}"], capture_output=True, text=True, check=True).stdout.strip()
    names = subprocess.run(git + ["ls-tree", "--name-only", sha, "tasks/"], capture_output=True, text=True, check=True).stdout.split()
    dirs = [n for n in names if Path(n).name.startswith("kinder-")]
    if not dirs:
        sys.exit(f"no tasks/kinder-* at {commit} ({sha}) in {source}")
    into.mkdir(parents=True, exist_ok=True)
    tar = into / "tasks.tar"
    with tar.open("wb") as fh:
        subprocess.run(git + ["archive", "--format=tar", sha, "--", "scripts/kinder/subset.toml",
                              "scripts/kinder/facts.json", *dirs], stdout=fh, check=True)
    with tarfile.open(tar) as tf:
        tf.extractall(into, filter="data")
    tar.unlink()
    return into, sha


def _task_sentence(instruction_md: str) -> str:
    """The instruction's task sentence, as plain text: from its `**Task:**` to the end of that paragraph."""
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


def _step_budget(instruction_md: str) -> tuple[int | None, str]:
    """The scoring's step budget and, where the instruction gives one, its robot time: `**1000 control steps** (100 s
    at 10 Hz)` -> (1000, "100 s at 10 Hz")."""
    m = re.search(r"\*\*(\d+) control steps\*\*(?: \(([^)]*)\))?", instruction_md)
    return (int(m[1]), m[2] or "") if m else (None, "")


def _actions(doc: str) -> str:
    """KinDER's own summary of an action, from its action space's docstring: the sentence that starts `Actions`."""
    for line in doc.splitlines():
        if line.startswith("Actions"):
            return re.sub(r"^Actions(:| are)\s*", "", line.strip()).rstrip(".")
    return ""


def read_source(root: Path) -> list[dict]:
    subset = tomllib.loads((root / "scripts" / "kinder" / "subset.toml").read_text())
    facts = json.loads((root / "scripts" / "kinder" / "facts.json").read_text())
    tasks = []
    for t in subset.get("task") or []:
        family = t["family"]
        d = root / "tasks" / f"kinder-{family}-i00"
        f = facts.get(family) or {}
        if not (d / "task.toml").is_file() or not f:
            continue
        kind = next((k for k in KINDS if f".{k}." in f.get("entry_point", "")), "")
        meta = tomllib.loads((d / "task.toml").read_text())
        full_md = (d / "instruction.md").read_text() if (d / "instruction.md").is_file() else ""
        lim = d.parent / f"{d.name}-limited"
        lim_md = (lim / "instruction.md").read_text() if (lim / "instruction.md").is_file() else ""
        steps, robot_time = _step_budget(full_md)
        bounds = [abs(x) for x in (f.get("action_high") or [])[:10] if isinstance(x, (int, float))]
        tasks.append({
            "id": family.replace("-", "_"),
            "title": f"{KINDS.get(kind, (kind,))[0]} · {family.replace('-', ' ').capitalize().replace(' 3d', ' 3D')}",
            "family": family,
            "kind": kind,
            "env_id": t.get("env_id", ""),
            "instruction": _task_sentence(full_md),
            "limited_instruction": _task_sentence(lim_md) if "limited_statement" in t else "",
            "max_steps": steps,
            "robot_time": robot_time,
            "action_dim": f.get("action_dim"),
            "actions": _actions(f.get("action_doc", "")),
            "action_bound": max(bounds) if bounds else None,
            "state_dim": f.get("obs_dim"),
            "nop_success": f.get("nop_success"),
            "image_hw": (f.get("limited") or {}).get("image_hw"),
            "agent_budget_s": int((meta.get("agent") or {}).get("timeout_sec", 0)),
            "limited_twin": lim.is_dir(),
            "task_dir": d.name,
        })
    return tasks


# ----------------------------------------------------------------------------------------------- pages


def upstream_block(task: dict, synced: str, commit: str) -> dict:
    """What KinDER and our task definitions state about the task (the agent's side and the grader's)."""
    steps, time_ = task["max_steps"], task["robot_time"]
    criteria = [f"KinDER's own goal check (the environment's `terminated`) fires within the episode: at most {steps} "
                f"control steps{f' ({time_})' if time_ else ''}; no partial credit" if steps else "",
                "unlimited: both fresh-process replays of the handed-in trajectory reach it and end in the same state",
                "limited: the one episode reaches it (no reset in our runs); the service records the episode, and it "
                "replays to the same state"]
    hw = task.get("image_hw") or []
    kinematic = task["kind"] == "kinematic3d"
    name, sim = KINDS.get(task["kind"], (task["kind"], ""))
    block = {
        "source": f"{UPSTREAM}, as defined in our task definitions @ {commit}" if commit else UPSTREAM,
        "synced": synced,
        "instruction": task["instruction"],
        "limited_instruction": task["limited_instruction"],
        "env_id": task["env_id"],
        "robot": ROBOTS.get(task["kind"], ""),
        "scene_model": f"kinder_{task['kind']}",
        "scene_image": f"{task['id']}.jpg",
        "category": f"{name} ({sim})" if sim else name,
        "instance": "seed 0: the scene KinDER builds from it, pinned by its digest",
        "success_criteria": [c for c in criteria if c],
        "holding_still": "does not reach the goal (checked by running an episode of zero actions)"
                         if task["nop_success"] is False else "",
        "action_dim": task["action_dim"],
        "actions": (f"{task['actions']}; each base and joint delta at most {task['action_bound']:g} a step"
                    if task["actions"] and task["action_bound"] else task["actions"]),
        "state_dim": task["state_dim"],
        "limited_mode": (f"base RGB and wrist RGB-D cameras ({hw[0]}×{hw[1]}), base odometry, the arm's joint angles"
                         + ("" if kinematic else " and velocities") + ", the fingers' position"
                         + ("; a move that would collide comes back `blocked`" if kinematic else "")
                         + ". Not where any object or the goal region is, not the goal check before the episode ends"
                         if task["limited_twin"] and hw else ""),
        "agent_budget": f"{task['agent_budget_s']} s of wall clock per mode" if task["agent_budget_s"] else "",
    }
    return {k: v for k, v in block.items() if v not in (None, "", [], {})}


def scaffold(task: dict, synced: str, commit: str) -> dict:
    return {"title": task["title"], "task_id": task["id"], "benchmark": BENCHMARK,
            "upstream": upstream_block(task, synced, commit)}


# ---------------------------------------------------------------------------------------------- scenes


def copy_scenes(tasks: list[dict], scenes: Path, dry: bool) -> int:
    """Each task's t = 0 room-camera still, as JPEG (ffmpeg, as the RoboLab and RoboPaint importers use). A file is
    rewritten only when the conversion differs from what is there."""
    changed = 0
    with tempfile.TemporaryDirectory(prefix="kinder-scenes-") as tmpd:
        for t in tasks:
            src = next((p for p in (scenes / t["family"] / "room_camera.png", scenes / t["family"] / "t0_room_camera.png")
                        if p.is_file()), None)
            if not src:
                continue
            jpg = Path(tmpd) / f"{t['id']}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-q:v", "3", str(jpg)], check=True)
            dst = SCENES / jpg.name
            if dst.is_file() and dst.read_bytes() == jpg.read_bytes():
                continue
            changed += 1
            if not dry:
                SCENES.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(jpg.read_bytes())
    return changed


# ----------------------------------------------------------------------------------------------- state


def seed_state(tasks: list[dict], dry: bool) -> list[str]:
    """A new task's entry in state/tasks/kinder.yml: kept (subset.toml selected it), its category as the note.
    Existing entries are untouched."""
    import yaml
    text = STATE.read_text() if STATE.is_file() else ""
    have = yaml.safe_load(text) or {} if text else {}
    new = [t for t in tasks if t["id"] not in have]
    if new and not dry:
        add = "".join(f"{t['id']}:\n  status: keep\n  note: {json.dumps(KINDS.get(t['kind'], (t['kind'],))[0])}\n"
                      for t in new)
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(text + ("" if not text or text.endswith("\n") else "\n") + add)
    return [t["id"] for t in new]


# ------------------------------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=None, help="a robot_coding_bench git clone (with --commit) or an export of it")
    ap.add_argument("--commit", default="", help="the commit to read from the clone (git archive), e.g. dev/pingyue")
    ap.add_argument("--scenes", default=None, help="a dir of <family>/room_camera.png or <family>/t0_room_camera.png")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rewrite pages even when upstream is unchanged")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory(prefix="kinder-") as tmpd:
        if args.source:
            source = Path(args.source).expanduser()
            if args.commit and (source / ".git").exists():
                root, commit = export(source, args.commit, Path(tmpd) / "export")
            else:
                root, commit = source, args.commit
            tasks = read_source(root)
            if not tasks:
                sys.exit(f"no KinDER tasks under {source}")
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

    scenes = copy_scenes(tasks, Path(args.scenes), args.dry_run) if args.scenes else 0

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

#!/usr/bin/env python3
"""Shared importer for the benchmarks whose selection is defined in robot_coding_bench by its own generator: MetaWorld+,
VLABench, RoboCasa, RoboCasa365, RoboCasa-GR1 and MolmoSpaces (scripts/import_<benchmark>_tasks.py each give the
constants).

Each such benchmark is a set of task pairs in robot_coding_bench, `tasks/<prefix>-<task>-i00-privileged` and
`...-standard` (protocol v1.0.1), written by the benchmark's generator under `scripts/<benchmark>/`. The site's task id
is the task part with underscores (`metaworldplus-button-press-i00-*` is `button_press`), and a run's job is
`<batch>-<mode>-<prefix>-<task>-i00` (`task_dir` in state/runs/<benchmark>.yml).

What it reads, from a commit's export (`git archive <commit>`, never a checkout of anyone's working tree):
  tasks/<dir>-privileged/README.md         the key table (family, oracle, budget, image), Task, Reference solution,
                                           Details (source, instance, deliverable)
  tasks/<dir>-privileged/instruction.md    the task sentence (its `**Task: ...**`) and what the success check requires
  tasks/<dir>-privileged/task.toml         the agent's budget
  tasks/<dir>-standard/README.md           what the standard (limited) twin gives the agent
and, with --demos, the verifier's replay of our reference solution in the oracle's validation trials (Harbor trial dirs
under the given dirs, searched recursively, read only): <trial>/verifier/replay.mp4 with replay.last.png as its poster,
re-encoded (H.264, CRF 30, +faststart) and credited to us. A privileged trial wins over a standard one. A benchmark
without a reference solution shows a still instead: with --scenes, each task's starting scene (the file `scene` names
under the given dir, e.g. a results site's t = 0 camera images), stored as docs/assets/<id>/scenes/<task>.jpg and named
in the page's `scene_image`.

Writes docs/benchmarks/<id>/tasks/<task>.md (only the `upstream:` block of an existing page; a new task gets a page from
the template), data/benchmarks/<id>.tasks.upstream.json (the cache: rebuilding the pages needs no source),
docs/assets/<id>/demos/<task>.mp4 + .jpg + manifest.json, and a NEW task's entry in state/tasks/<id>.yml
(`status: keep`, its category as the note; an entry that exists is never changed). Re-running is safe: an unchanged
source writes nothing; a task that disappears is reported, never deleted.
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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Bench:
    id: str                    # the site's benchmark id
    name: str                  # its display name
    prefix: str                # task directory prefix in robot_coding_bench, e.g. "robocasa-"
    upstream: str              # the upstream project and the version our image pins
    robot: str
    scene_model: str
    category: Callable[[dict], str]          # a task record -> its category (the task list's grouping)
    title: Callable[[dict], str]             # a task record -> the page title
    excludes: tuple[str, ...] = ()           # prefixes of OTHER benchmarks that start with this prefix
    demo_note: str = "the scene camera"
    body: str = ""
    extra: Callable[[dict], dict] = field(default=lambda t: {})   # benchmark-specific upstream fields
    sources: tuple[str, ...] = ()            # more files to export beside the task dirs (e.g. the generator's data)
    enrich: Callable[[Path, dict], None] = field(default=lambda root, t: None)   # add fields to a task record
    scene: Callable[[dict], str] | None = None   # a task record -> its t = 0 still under --scenes (no demos of ours)


BODY_TEMPLATE = """
## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/{id}.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- The demo is the verifier's replay of our reference solution on this
     task's frozen instance (privileged mode). Say here if it looks wrong. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->
"""


# ------------------------------------------------------------------------------------------------ markdown


def clean(s: str) -> str:
    """Markdown to one line of plain text: links keep their text, code and emphasis marks go."""
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"`([^`]*)`", r"\1", s).replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", s).strip()


def section(md: str, heading: str) -> str:
    """The body of the first `## <heading...>` section (a regex on the heading text), up to the next `## `."""
    m = re.search(rf"^## {heading}[^\n]*\n(.*?)(?=^## |\Z)", md, re.M | re.S)
    return m.group(1).strip() if m else ""


def table(md: str) -> dict[str, str]:
    """The rows of the first `| key | value |` table in `md` (header and rule rows skipped)."""
    rows, started = {}, False
    for line in md.splitlines():
        if line.startswith("|"):
            started = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and not set(cells[0]) <= set("-: "):
                rows[cells[0].lower()] = "|".join(cells[1:]).strip()
        elif started:
            break
    return rows


def goal(instruction: str) -> str:
    m = re.search(r"\*\*Task:\s*(.+?)\*\*", instruction, re.S)
    text = clean(m.group(1)) if m else ""
    return text[:1].upper() + text[1:]


def requirements(instruction: str) -> list[str]:
    """What the success check requires, as the privileged instruction states it (its `## Success` section): the
    paragraph that says what the check requires (or what must hold), with its bullets where it introduces a list; else
    the section's opening sentences, plus the instruction's own note that the task sentence states the check exactly."""
    sec = section(instruction, "Success")
    paras = [p for p in re.split(r"\n\s*\n", sec) if p.strip()]
    for p in paras[1:]:
        lines = p.splitlines()
        if not re.search(r"\b(requires?|hold)\b", lines[0], re.I):
            continue
        if not lines[0].rstrip().endswith(":"):
            return [clean(p)]
        items, cur = [], ""
        for line in lines[1:]:
            if line.startswith("- "):
                if cur:
                    items.append(cur)
                cur = line[2:].strip()
            elif cur and line.strip():
                cur += " " + line.strip()
        if cur:
            items.append(cur)
        return [clean(i).rstrip(";") for i in items] or [clean(p)]
    out = []
    if paras:
        out.append(" ".join(re.split(r"(?<=\.)\s+", clean(paras[0]))[:2]))
    m = re.search(r"This states exactly what [^.;]*", instruction)
    if m:
        out.append(clean(m.group(0)) + ".")
    return [o for o in out if o]


# ------------------------------------------------------------------------------------------------ source


def export(source: Path, commit: str, bench: Bench, into: Path) -> tuple[Path, str]:
    git = ["git", "-C", str(source)]
    sha = subprocess.run(git + ["rev-parse", "--short=9", f"{commit}^{{commit}}"], capture_output=True, text=True,
                         check=True).stdout.strip()
    names = subprocess.run(git + ["ls-tree", "--name-only", sha, "tasks/"], capture_output=True, text=True,
                           check=True).stdout.split()
    dirs = [n for n in names if Path(n).name.startswith(bench.prefix)
            and not any(Path(n).name.startswith(x) for x in bench.excludes)]
    if not dirs:
        sys.exit(f"no tasks/{bench.prefix}* at {commit} ({sha}) in {source}")
    into.mkdir(parents=True, exist_ok=True)
    tar = into / "tasks.tar"
    with tar.open("wb") as fh:
        subprocess.run(git + ["archive", "--format=tar", sha, "--", *bench.sources, *dirs], stdout=fh, check=True)
    with tarfile.open(tar) as tf:
        tf.extractall(into, filter="data")
    tar.unlink()
    return into, sha


def read_source(root: Path, bench: Bench) -> list[dict]:
    tasks = []
    for priv in sorted((root / "tasks").glob(f"{bench.prefix}*-privileged")):
        if any(priv.name.startswith(x) for x in bench.excludes):
            continue
        base = priv.name[: -len("-privileged")]
        std = priv.parent / f"{base}-standard"
        readme = (priv / "README.md").read_text()
        instr = (priv / "instruction.md").read_text()
        meta = tomllib.loads((priv / "task.toml").read_text())
        keys, details = table(readme), table(section(readme, "Details"))
        std_readme = (std / "README.md").read_text() if (std / "README.md").is_file() else ""
        tid = base[len(bench.prefix):].removesuffix("-i00").replace("-", "_")
        md = meta.get("metadata") or {}
        tasks.append({
            "id": tid,
            "task_dir": base,
            "family": clean(keys.get("family / instance", "")).split(" / ")[0] or md.get("family", ""),
            "seed": md.get("instance_seed"),
            "instruction": goal(instr),
            "requirements": requirements(instr),
            "oracle": clean(keys.get("oracle", "")),
            "base_image": clean(keys.get("base image", "")),
            "source": clean(details.get("source", "")),
            "env_source": (re.search(r"\[environment source\]\(([^)]+)\)", details.get("source", "")) or [None, ""])[1],
            "instance": clean(details.get("instance", "")),
            "deliverable": clean(details.get("deliverable", "")),
            "reference": clean(section(readme, "Reference solution")),
            "limited": clean(section(std_readme, "Task")),
            "agent_budget_s": int((meta.get("agent") or {}).get("timeout_sec", 0)),
            "standard_twin": std.is_dir(),
        })
        bench.enrich(root, tasks[-1])
    return tasks


# ----------------------------------------------------------------------------------------------- pages


def upstream_block(bench: Bench, task: dict, synced: str, commit: str) -> dict:
    criteria = list(task["requirements"]) + [
        "unlimited (privileged): both fresh-process replays of the handed-in trajectory end in the same state, and the "
        "check holds on it",
        "limited (standard): the one episode (no reset) is recorded by the service and replays to the same state; the "
        "check holds on it live and in the replay",
    ]
    block = {
        "source": f"{bench.upstream}, as defined in our task definitions @ {commit}" if commit else bench.upstream,
        "synced": synced,
        "instruction": task["instruction"],
        "family": task["family"],
        "robot": bench.robot,
        "scene_model": bench.scene_model,
        "category": bench.category(task),
        "instance": task["instance"] or (f"seed {task['seed']}" if task.get("seed") is not None else ""),
        "success_criteria": criteria,
        "deliverable": task["deliverable"],
        "reference_solution": task["reference"],
        "limited_mode": task["limited"] if task["standard_twin"] else "",
        "oracle": task["oracle"],
        "base_image": task["base_image"],
        "agent_budget": f"{task['agent_budget_s']} s of wall clock per mode" if task["agent_budget_s"] else "",
        "environment_source": task.get("env_source", ""),
        "task_dirs": f"{task['task_dir']}-privileged, {task['task_dir']}-standard",
        "scene_image": f"{task['id']}.jpg" if (scene_dir(bench) / f"{task['id']}.jpg").is_file() else "",
        **bench.extra(task),
    }
    return {k: v for k, v in block.items() if v not in (None, "", [], {})}


# ----------------------------------------------------------------------------------------------- demos


def _probe(mp4: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", str(mp4)],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    st = (d.get("streams") or [{}])[0]
    return {"width": st.get("width"), "height": st.get("height"),
            "seconds": max(1, round(float((d.get("format") or {}).get("duration") or 0)))}


def find_demos(dirs: list[str], bench: Bench) -> dict[str, Path]:
    """task dir -> the trial dir holding the verifier's replay of a passing oracle run (privileged over standard;
    a later one over an earlier one)."""
    found: dict[str, tuple[int, str, Path]] = {}
    for d in dirs:
        for cfg in Path(d).expanduser().glob("**/*__*/config.json"):
            trial = cfg.parent
            try:
                result = json.loads((trial / "result.json").read_text())
                reward = json.loads((trial / "verifier" / "reward.json").read_text())
            except (OSError, ValueError):
                continue
            if (result.get("agent_info") or {}).get("name") != "oracle" or reward.get("success") != 1:
                continue
            if not (trial / "verifier" / "replay.mp4").is_file():
                continue
            name = (result.get("task_name") or "").split("/")[-1]
            base = re.sub(r"-(privileged|standard)$", "", name)
            if not base.startswith(bench.prefix) or any(base.startswith(x) for x in bench.excludes):
                continue
            rank = (0 if name.endswith("-standard") else 1, result.get("finished_at") or "", trial)
            if base not in found or rank[:2] > found[base][:2]:
                found[base] = rank
    return {k: v[2] for k, v in found.items()}


def install_demos(bench: Bench, tasks: list[dict], found: dict[str, Path], dry: bool) -> int:
    demos = ROOT / "docs" / "assets" / bench.id / "demos"
    manifest_path = demos / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
    changed = 0
    for t in tasks:
        trial = found.get(t["task_dir"])
        if not trial:
            continue
        src, png = trial / "verifier" / "replay.mp4", trial / "verifier" / "replay.last.png"
        dst, poster = demos / f"{t['id']}.mp4", demos / f"{t['id']}.jpg"
        old = manifest.get(t["id"]) or {}
        if dst.is_file() and poster.is_file() and old.get("bytes") == dst.stat().st_size:
            continue        # already installed: re-encoding is not byte-stable, so an installed demo is kept
        changed += 1
        if dry:
            continue
        demos.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-c:v", "libx264", "-preset", "slow", "-crf", "30",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(dst)], check=True)
        if png.is_file():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-q:v", "3", str(poster)], check=True)
        else:   # the replay's last frame
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", str(dst), "-frames:v", "1", "-q:v", "3",
                            str(poster)], check=True)
        manifest[t["id"]] = {**_probe(dst), "bytes": dst.stat().st_size, "poster": True,
                             "source": f"Recorded by us: our reference solution, replayed by the verifier ({bench.demo_note})."}
    if not dry and manifest:
        text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        if not manifest_path.is_file() or manifest_path.read_text() != text:
            manifest_path.write_text(text)
    return changed


def scene_dir(bench: Bench) -> Path:
    return ROOT / "docs" / "assets" / bench.id / "scenes"


def install_scenes(bench: Bench, tasks: list[dict], scenes: Path, dry: bool) -> int:
    """Each task's starting scene as a JPEG still (ffmpeg, as the KinDER importer does), rewritten only
    when the conversion differs from what is there."""
    changed = 0
    with tempfile.TemporaryDirectory(prefix=f"{bench.id}-scenes-") as tmpd:
        for t in tasks:
            src = scenes / bench.scene(t)
            if not src.is_file():
                continue
            jpg = Path(tmpd) / f"{t['id']}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-q:v", "3", str(jpg)], check=True)
            dst = scene_dir(bench) / jpg.name
            if dst.is_file() and dst.read_bytes() == jpg.read_bytes():
                continue
            changed += 1
            if not dry:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(jpg.read_bytes())
    return changed


# ----------------------------------------------------------------------------------------------- state


def seed_state(bench: Bench, tasks: list[dict], dry: bool) -> list[str]:
    import yaml
    state = ROOT / "state" / "tasks" / f"{bench.id}.yml"
    text = state.read_text() if state.is_file() else ""
    have = (yaml.safe_load(text) or {}) if text else {}
    new = [t for t in tasks if t["id"] not in have]
    if new and not dry:
        add = "".join(f"{t['id']}:\n  status: keep\n  note: {json.dumps(bench.category(t), ensure_ascii=False)}\n" for t in new)
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text(text + ("" if not text or text.endswith("\n") else "\n") + add)
    return [t["id"] for t in new]


# ------------------------------------------------------------------------------------------------- main


def main(bench: Bench, doc: str) -> int:
    ap = argparse.ArgumentParser(description=doc, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=None, help="a robot_coding_bench git clone (with --commit) or an export of it")
    ap.add_argument("--commit", default="", help="the commit to read from the clone (git archive), e.g. origin/main")
    ap.add_argument("--demos", action="append", default=[], help="a dir of the oracle's Harbor trials (repeatable)")
    ap.add_argument("--scenes", default=None, help="a dir of t = 0 stills (the benchmark's `scene` names each file)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rewrite pages even when upstream is unchanged")
    args = ap.parse_args()
    if args.scenes and not bench.scene:
        ap.error(f"--scenes: {bench.name} has no starting-scene stills (its pages show demos)")
    cache = ROOT / "data" / "benchmarks" / f"{bench.id}.tasks.upstream.json"
    pages = ROOT / "docs" / "benchmarks" / bench.id / "tasks"

    with tempfile.TemporaryDirectory(prefix=f"{bench.id}-") as tmpd:
        if args.source:
            source = Path(args.source).expanduser()
            if args.commit and (source / ".git").exists():
                root, commit = export(source, args.commit, bench, Path(tmpd) / "export")
            else:
                root, commit = source, args.commit
            tasks = read_source(root, bench)
            if not tasks:
                sys.exit(f"no {bench.name} tasks under {source}")
            payload = {"commit": commit, "tasks": tasks}
            old = json.loads(cache.read_text()) if cache.is_file() else {}
            if {k: old.get(k) for k in payload} != payload:
                payload["read"] = dt.date.today().isoformat()
                if not args.dry_run:
                    cache.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
            print(f"read {len(tasks)} task(s) at {commit or '(no commit)'} from {source} -> {cache.name}")
        else:
            if not cache.is_file():
                sys.exit(f"no cache at {cache}; run once with --source <robot_coding_bench clone> --commit <commit>")
            payload = json.loads(cache.read_text())
            tasks, commit = payload["tasks"], payload.get("commit", "")

    demo_files = install_demos(bench, tasks, find_demos(args.demos, bench), args.dry_run) if args.demos else 0
    scene_files = install_scenes(bench, tasks, Path(args.scenes), args.dry_run) if args.scenes else 0

    synced = dt.date.today().isoformat()
    pages.mkdir(parents=True, exist_ok=True)
    created = updated = unchanged = 0
    seen = set()
    for task in tasks:
        seen.add(task["id"])
        path = pages / f"{task['id']}.md"
        fresh = upstream_block(bench, task, synced, commit)
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
                write_page(path, {"title": bench.title(task), "task_id": task["id"], "benchmark": bench.id,
                                  "upstream": fresh}, (bench.body or BODY_TEMPLATE).replace("{id}", bench.id))
            created += 1
    seeded = seed_state(bench, tasks, args.dry_run)
    orphans = sorted(p.stem for p in pages.glob("*.md") if p.stem not in seen and p.stem != "index")
    print(f"tasks     : {len(tasks)}")
    print(f"created   : {created}{' (dry run)' if args.dry_run else ''}")
    print(f"updated   : {updated}")
    print(f"unchanged : {unchanged}")
    print(f"demos     : {demo_files} task(s) changed" if args.demos else "demos     : not asked (--demos DIR)")
    if args.scenes:
        print(f"scenes    : {scene_files} still(s) changed")
    if seeded:
        print(f"state for {len(seeded)} new task(s) in state/tasks/{bench.id}.yml")
    if orphans:
        print(f"no longer in robot_coding_bench ({len(orphans)}): {', '.join(orphans)}")
    return 0

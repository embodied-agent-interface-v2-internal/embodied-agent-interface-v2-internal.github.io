#!/usr/bin/env python3
"""Sync RoboPaint's task pages from robot_coding_bench, where the benchmark is defined.

RoboPaint is ours: a Franka Panda holding a brush (ManiSkill 3.0.1) paints a picture onto paper, and Spline-FRIDA's
learned stroke model turns the path the brush tip took into paint. Every task is a pair in robot_coding_bench,
`tasks/robopaint-<family>-<target>-i00-privileged` and its `-standard` twin (protocol v1.0 names). Since robot_coding_bench
PR #68 (2026-10-07) RoboPaint is what was RoboPaint-strict: the brush targets with process rules in the verifier (no
colouring in, a path budget, few sweeps); the earlier picture-only tasks (`robopaint-<family>-<target>-i00` + `-limited`)
are gone. The site's task id is `<family>_<target>` (dashes become underscores), so `robopaint-kaishu-ai-i00-*` is
`kaishu_ai`.

What it reads, from a commit's export (`git archive <commit>`, never a checkout of anyone's working tree):
  task.toml               the description (its "success iff ..." rule and continuous score), [metadata] difficulty /
                          tier / line_complexity, the budgets
  instruction.md          the task sentence
  tests/instance.json     the graders' copy: the rule's thresholds and the truth's scalar facts (never shown to the agent;
                          fine for reviewers)
  environment/target.png  the picture the agent paints: the task's scene image
and, with --demos, the verifier's replay of the reference solution in validation jobs (a host:dir read with rsync, or a
local dir; read only): <job>/<trial>/verifier/replay.mp4 with replay.last.png as its poster, credited to us.

Writes docs/benchmarks/robopaint/tasks/<id>.md (only the `upstream:` block of an existing page; a new task gets a page
from the template), data/benchmarks/robopaint.tasks.upstream.json (the cache: rebuilding the pages needs no source),
docs/assets/robopaint/scenes/<id>.png, docs/assets/robopaint/demos/<id>.mp4 + .jpg + manifest.json, and the difficulty
of a NEW task in state/tasks/robopaint.yml, from its task.toml (an entry that exists is never changed: curation is
the owner's). Re-running is safe and expected: an unchanged source writes nothing; a new family's tasks appear when
its commit is in the source; a task that disappears is reported, never deleted.

Usage:
  git -C ../robot_coding_bench fetch origin                  # the commit has to be in the clone
  python scripts/import_robopaint_tasks.py --source ../robot_coding_bench --commit origin/main \\
      --demos <host>:<jobs dir>/paint_jobs/<oracle validation job>
  python scripts/import_robopaint_tasks.py                  # from the cache
  python scripts/import_robopaint_tasks.py ... --dry-run
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
REPO_URL = "https://github.com/JamesKrW/robot_coding_bench"
# benchmark -> how its task dirs are named: the dirs read (one per task), the name pattern, its other mode's suffix
# (the robopaint-strict layout of 2026-10-06 is gone: PR #68 renamed those tasks to RoboPaint's)
LAYOUTS = {
    "robopaint": {"glob": "robopaint-*-i00-privileged", "dir_re": r"robopaint-([a-z0-9]+)-(.+)-i00-privileged",
                  "twin": "-standard", "base_re": r"-privileged$", "source": "our RoboPaint task definitions"},
}


def configure(benchmark: str) -> None:
    """Point the module's paths at one benchmark's pages, cache, media and state."""
    global BENCHMARK, LAYOUT, CACHE, TASK_DIR, SCENES, DEMOS, STATE, DIR_RE
    BENCHMARK, LAYOUT = benchmark, LAYOUTS[benchmark]
    CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.upstream.json"
    TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"
    SCENES = ROOT / "docs" / "assets" / BENCHMARK / "scenes"
    DEMOS = ROOT / "docs" / "assets" / BENCHMARK / "demos"
    STATE = ROOT / "state" / "tasks" / f"{BENCHMARK}.yml"
    DIR_RE = re.compile(LAYOUT["dir_re"])


configure("robopaint")
FAMILY_NAMES = {"line": "Line", "lettering": "Lettering", "kaishu": "Kaishu", "xingshu": "Xingshu", "acrylic": "Acrylic",
                "oil": "Oil"}

BODY_TEMPLATE = """
## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/{benchmark}.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- The demo is our reference solution, replayed by the verifier: canvas camera,
     scene camera, side camera and the exact canvas. Say whether
     the trajectory is clean and what it relies on. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->
"""


# ------------------------------------------------------------------------------------------------ source


def export(source: Path, commit: str, into: Path) -> tuple[Path, str]:
    """The robopaint task dirs of `commit` in the git repo `source`, unpacked under `into`; and the short commit."""
    git = ["git", "-C", str(source)]
    sha = subprocess.run(git + ["rev-parse", "--short", f"{commit}^{{commit}}"], capture_output=True, text=True, check=True).stdout.strip()
    names = subprocess.run(git + ["ls-tree", "--name-only", sha, "tasks/"], capture_output=True, text=True, check=True).stdout.split()
    dirs = [n for n in names if DIR_RE.fullmatch(Path(n).name) or
            (LAYOUT["twin"] == "-standard" and DIR_RE.fullmatch(Path(n).name.replace("-standard", "-privileged")))]
    if not dirs:
        sys.exit(f"no {BENCHMARK} tasks at {commit} ({sha}) in {source}")
    into.mkdir(parents=True, exist_ok=True)
    tar = into / "tasks.tar"
    with tar.open("wb") as fh:
        subprocess.run(git + ["archive", "--format=tar", sha, "--", *dirs], stdout=fh, check=True)
    with tarfile.open(tar) as tf:
        tf.extractall(into, filter="data")
    tar.unlink()
    return into, sha


def _task_sentence(instruction_md: str) -> str:
    """The instruction's task paragraph, as plain text: from its `**Task:**` (or `**Task (臨帖):**`, anywhere in a
    line: each family words its instruction its own way) to the end of that paragraph."""
    lines = instruction_md.splitlines()
    start = next((i for i, l in enumerate(lines) if re.search(r"\*\*Task\b[^*]*:\*\*", l)), None)
    if start is None:
        return ""
    para = []
    for line in lines[start:]:
        if not line.strip():
            break
        para.append(line.strip())
    text = re.split(r"\*\*Task\b[^*]*:\*\*", " ".join(para), maxsplit=1)[1].strip()
    text = re.sub(r"`([^`]*)`", r"\1", text).replace("**", "")
    return text[:1].upper() + text[1:]


def _scored_as(desc: str) -> str:
    """What the rule is applied to, as the description words it right before a parenthesised `success iff`: the
    sentence that leads into the parenthesis, and whatever stands inside it before `success iff`. Registered scoring
    (v2) aligns the sheet first: "Scored against the picture after the best single shift of the sheet within 5 mm
    (success iff ...", "Scored against the picture (after aligning the sheet ... up to 5 mm per axis: success iff ...".
    "" for a rule stated outside parentheses (the line drawings) and for a bare "Scored against the picture"."""
    i = desc.find("success iff")
    if i < 0:
        return ""
    head = desc[:i]
    op = head.rfind("(")
    if op < 0 or ")" in head[op:]:
        return ""
    stop = head.rfind(". ", 0, op)
    lead = head[stop + 2 if stop >= 0 else 0:op].strip()
    inner = head[op + 1:].strip().rstrip(":;,").strip()
    text = " ".join(x for x in (lead, inner) if x)
    if text.lower() in ("", "scored against the picture"):
        return ""
    return text[:1].lower() + text[1:]


def _success_items(text: str) -> list[str]:
    """`a >= 1, b (x, y) <= 2 and at most 3 strokes` -> its conditions (split outside parentheses)."""
    out, cur, depth, i = [], "", 0, 0
    while i < len(text):
        depth += {"(": 1, ")": -1}.get(text[i], 0)
        sep = next((x for x in (", ", " and ") if depth == 0 and text.startswith(x, i)), None)
        if sep:
            out.append(cur)
            cur, i = "", i + len(sep)
            continue
        cur += text[i]
        i += 1
    return [x.strip() for x in out + [cur] if x.strip()]


def _lift_scope(items: list[str]) -> tuple[list[str], list[str]]:
    """Split off a parenthesis that qualifies every condition, which a description may attach to the last metric:
    `paint IoU >= 0.96 (all after the best single shift of the sheet, ..., inside the central area 8 mm in from the
    sheet's edges)` -> the condition, and `all after ...` for the lead-in bullet."""
    kept, scope = [], []
    for item in items:
        m = re.search(r"\s*\((all [^()]*)\)$", item)
        if m:
            scope.append(m.group(1))
            item = item[:m.start()].rstrip()
        kept.append(item)
    return kept, scope


def _scalar(v):
    return isinstance(v, (int, float, str)) and not isinstance(v, bool) and len(str(v)) < 200


def read_source(root: Path) -> list[dict]:
    tasks = []
    for d in sorted((root / "tasks").glob(LAYOUT["glob"])):
        m = DIR_RE.fullmatch(d.name)
        if not m or not (d / "task.toml").is_file():
            continue
        family, target = m.group(1), m.group(2)
        meta = tomllib.loads((d / "task.toml").read_text())
        md = meta.get("metadata") or {}
        inst_path = d / "tests" / "instance.json"
        inst = json.loads(inst_path.read_text()) if inst_path.is_file() else {}
        rule, truth = inst.get("target") or {}, inst.get("truth") or {}
        desc = (meta.get("task") or {}).get("description", "")
        picture = re.search(r"picture target\.png \(([^)]*)\)", desc)
        # every family states its rule in words: "success iff <conditions>; <score> is the continuous score"
        iff = re.search(r"success iff (.+?); (?:the )?(.+?) is the continuous score", desc)
        # the process rules follow the picture rule, in words, with the task's numbers ("Process rules (RoboPaint-strict):"
        # before PR #68)
        process = re.search(r"Process rules(?: \(RoboPaint-strict\))?: (.+)$", desc.strip())
        items, scope = _lift_scope(_success_items(iff.group(1))) if iff else ([], [])
        lead = _scored_as(desc) or ("scored against the picture" if scope else "")
        tasks.append({
            "id": f"{family}_{target.replace('-', '_')}",
            "title": f"{FAMILY_NAMES.get(family, family.title())} · {target.replace('-', ' ').title()}",
            "family": family,
            "target": target,
            "instruction": _task_sentence((d / "instruction.md").read_text()) if (d / "instruction.md").is_file() else "",
            "picture": picture.group(1) if picture else "",
            "difficulty": md.get("difficulty", ""),
            "line_complexity": md.get("line_complexity", ""),
            "tier": md.get("tier", ""),
            "rule": {k: v for k, v in rule.items() if _scalar(v) and k != "image"},
            "success_items": items,
            "scored_as": ", ".join([lead] + scope) if lead else "",
            "continuous": iff.group(2) if iff else "",
            "truth": {k: v for k, v in truth.items() if k != "svg" and (_scalar(v) or isinstance(v, (list, dict)))},
            "scorer": (d / "environment" / "scorer").is_dir(),
            "agent_budget_s": int((meta.get("agent") or {}).get("timeout_sec", 0)),
            "process_rules": process.group(1).rstrip(".") if process else "",
            "limited_twin": (d.parent / (re.sub(LAYOUT.get("base_re", "$^"), "", d.name) + LAYOUT["twin"])).is_dir(),
            "task_dir": re.sub(LAYOUT.get("base_re", "$^"), "", d.name),
            "target_png": str(d / "environment" / "target.png"),
        })
    return tasks


# ----------------------------------------------------------------------------------------------- pages


def _criteria(rule: dict, truth: dict, items: list[str] = ()) -> list[str]:
    """The success rule, in words: from the graders' thresholds (success_<quantity>, the line drawings), else as the
    task's description states it (`items`, the other families)."""
    out = []
    tol = rule.get("tol_mm")
    for k, v in rule.items():
        if not k.startswith("success_"):
            continue
        what = k.removeprefix("success_")
        if what == "precision":
            out.append(f"precision >= {v:.2f}: painted pixels within {tol:g} mm of a line of their colour" if tol is not None
                       else f"precision >= {v:.2f}")
        elif what == "recall":
            out.append(f"recall >= {v:.2f}: the drawing's line length with paint of its colour within {tol:g} mm" if tol is not None
                       else f"recall >= {v:.2f}")
        elif what == "color_recall":
            out.append(f"every colour's own recall >= {v:.2f}")
        else:
            out.append(f"{what.replace('_', ' ')} >= {v}")
    if not out and items:
        out = list(items)
    if isinstance(truth.get("element_recall"), (int, float)):
        out.append(f"(reported) every element of the drawing counts as complete at recall >= {truth['element_recall']:.2f}")
    out.append("both fresh-process replays of the trajectory meet this and end in the same state")
    return out


def upstream_block(task: dict, synced: str, commit: str) -> dict:
    """What robot_coding_bench states about the task (agent-side and, for reviewers, grader-side)."""
    truth = task["truth"]
    known = {"line_width_mm", "length_mm", "colors", "length_mm_by_color", "element_recall"}
    block = {
        # the public pages name no repository and no commit (owner, 2026-09-28: "robopaint上不要写那个仓库")
        "source": LAYOUT["source"],
        "synced": synced,
        "instruction": task["instruction"],
        "scene_model": f"robopaint_{task['family']}",
        "scene_image": f"{task['id']}.png",
        "family": task["family"],
        "picture": task["picture"],
        "difficulty": task["difficulty"],
        "line_complexity": task["line_complexity"],
        "tier": task["tier"],
        "colours": truth.get("colors"),
        "line_width": f"{truth['line_width_mm']:g} mm" if isinstance(truth.get("line_width_mm"), (int, float)) else "",
        "line_length": f"{round(truth['length_mm'])} mm" if isinstance(truth.get("length_mm"), (int, float)) else "",
        "line_length_by_colour": {k: f"{round(v)} mm" for k, v in (truth.get("length_mm_by_color") or {}).items()},
        # first what the rule is applied to (v2 aligns the sheet with the picture first), then the rule
        "success_criteria": ([task["scored_as"]] if task.get("scored_as") else [])
                            + _criteria(task["rule"], truth, task.get("success_items")
                                        or _success_items(task.get("success_text", "")))
                            + ([f"process rules: {task['process_rules']}"] if task.get("process_rules") else []),
        # the reward.json final_reward: F1 for a line drawing, the IoU for calligraphy, 1 - mean ΔE / 20 for a painting
        "continuous_score": task.get("continuous", ""),
        # the grader-side facts of other families, as they come (never seen by the agent)
        "grader_facts": {k: v for k, v in truth.items() if k not in known and _scalar(v)},
        "scoring": ("s.score() is served by a separate scoring container: it replays the actions the agent executed "
                    "since its last reset on the graders' copy and returns the metrics, never images or target data"
                    if task["scorer"] else ""),
        "agent_budget": f"{task['agent_budget_s']} s of wall clock per mode" if task["agent_budget_s"] else "",
    }
    return {k: v for k, v in block.items() if v not in (None, "", [], {})}


def scaffold(task: dict, synced: str, commit: str) -> dict:
    return {"title": task["title"], "task_id": task["id"], "benchmark": BENCHMARK,
            "upstream": upstream_block(task, synced, commit)}


# ----------------------------------------------------------------------------------------------- demos


def fetch_demos(sources: list[str], tmp: Path) -> dict[str, tuple[Path, str]]:
    """task dir -> (the trial dir holding verifier/replay.mp4, the job's name), from validation jobs of the oracle.

    A later source wins over an earlier one for the same task; a trial counts only if its grade was a success."""
    found: dict[str, tuple[Path, str]] = {}
    for n, src in enumerate(sources):
        local = Path(src).expanduser()
        if not local.is_dir() and ":" in src:
            local = tmp / f"demos{n}"
            local.mkdir(parents=True, exist_ok=True)
            host, path = src.split(":", 1)
            subprocess.run(["rsync", "-a", "--prune-empty-dirs", "-e", "ssh -o BatchMode=yes -o ConnectTimeout=10",
                            "--include=*/", "--include=config.json", "--include=verifier/reward.json",
                            "--include=verifier/replay.mp4", "--include=verifier/replay.last.png", "--exclude=*",
                            f"{host}:{path.rstrip('/')}/", f"{local}/"], check=True, capture_output=True, timeout=900)
        job = Path(src.split(":", 1)[-1]).name
        for trial in sorted(local.glob("*__*")):
            try:
                cfg = json.loads((trial / "config.json").read_text())
                reward = json.loads((trial / "verifier" / "reward.json").read_text())
            except (OSError, ValueError):
                continue
            name = Path(((cfg.get("task") or {}).get("path") or "").rstrip("/")).name
            if name.endswith("-limited") or reward.get("success") != 1 or not (trial / "verifier" / "replay.mp4").is_file():
                continue
            found[name] = (trial, job)
    return found


def _probe(mp4: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height:format=duration", "-of", "json", str(mp4)],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    st = (d.get("streams") or [{}])[0]
    return {"width": st.get("width"), "height": st.get("height"), "seconds": round(float((d.get("format") or {}).get("duration") or 0))}


def install_demos(tasks: list[dict], found: dict[str, tuple[Path, str]], dry: bool) -> int:
    """Copy each task's replay and poster in, and record it in the manifest; returns how many files changed."""
    manifest_path = DEMOS / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
    changed = 0
    for t in tasks:
        hit = found.get(t["task_dir"])
        if not hit:
            continue
        trial, job = hit
        mp4, png = trial / "verifier" / "replay.mp4", trial / "verifier" / "replay.last.png"
        dst = DEMOS / f"{t['id']}.mp4"
        entry = {**_probe(mp4), "bytes": mp4.stat().st_size, "poster": png.is_file(),
                 "source": ("Recorded by us: our reference solution, replayed by the verifier (canvas camera, scene camera, side camera, "
                            "exact canvas).")}
        if dry:
            changed += int(manifest.get(t["id"]) != entry)
            continue
        DEMOS.mkdir(parents=True, exist_ok=True)
        if not dst.is_file() or dst.stat().st_size != mp4.stat().st_size:
            shutil.copyfile(mp4, dst)
            changed += 1
        poster = DEMOS / f"{t['id']}.jpg"
        if png.is_file() and (not poster.is_file() or manifest.get(t["id"], {}).get("bytes") != entry["bytes"]):
            # the replay's last frame is the poster: the finished painting (ffmpeg, as scripts/fetch_demos.py uses)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-q:v", "3", str(poster)], check=True)
            changed += 1
        manifest[t["id"]] = entry
    if not dry:
        text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        if not manifest_path.is_file() or manifest_path.read_text() != text:
            DEMOS.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(text)
    return changed


# ----------------------------------------------------------------------------------------------- state


def seed_state(tasks: list[dict], dry: bool) -> list[str]:
    """A new task's difficulty from its task.toml, appended to state/tasks/robopaint.yml; existing entries untouched."""
    import yaml
    text = STATE.read_text() if STATE.is_file() else ""
    have = yaml.safe_load(text) or {} if text else {}
    new = [t for t in tasks if t["difficulty"] and t["id"] not in have]
    if new and not dry:
        add = "".join(f"{t['id']}:\n  difficulty: {t['difficulty']}\n" for t in new)
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(text + ("" if not text or text.endswith("\n") else "\n") + add)
    for t in tasks:
        cur = (have.get(t["id"]) or {}).get("difficulty")
        if cur and t["difficulty"] and cur != t["difficulty"]:
            print(f"  note: {t['id']} is {cur} in state, {t['difficulty']} in task.toml (state kept)")
    return [t["id"] for t in new]


# ------------------------------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=None, help="a robot_coding_bench git clone (with --commit) or an export of it")
    ap.add_argument("--commit", default="", help="the commit to read from the clone (git archive), e.g. origin/dev/qineng")
    ap.add_argument("--demos", action="append", default=[], help="a validation job of the oracle, host:dir or a dir (repeatable)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rewrite pages even when upstream is unchanged")
    ap.add_argument("--benchmark", default="robopaint", choices=sorted(LAYOUTS), help="robopaint (the only one)")
    args = ap.parse_args()
    configure(args.benchmark)

    with tempfile.TemporaryDirectory(prefix="robopaint-") as tmpd:
        tmp = Path(tmpd)
        if args.source:
            source = Path(args.source).expanduser()
            if args.commit and (source / ".git").exists():
                root, commit = export(source, args.commit, tmp / "export")
            else:
                root, commit = source, args.commit
            tasks = read_source(root)
            if not tasks:
                sys.exit(f"no tasks/{LAYOUT['glob']} under {source}")
            if not args.dry_run:
                SCENES.mkdir(parents=True, exist_ok=True)
                for t in tasks:
                    dst = SCENES / f"{t['id']}.png"
                    if Path(t["target_png"]).is_file() and (not dst.is_file() or dst.read_bytes() != Path(t["target_png"]).read_bytes()):
                        shutil.copyfile(t["target_png"], dst)
            for t in tasks:
                t.pop("target_png")
            payload = {"tasks": tasks}      # no repository, no commit: the pages name neither
            old = json.loads(CACHE.read_text()) if CACHE.is_file() else {}
            if {k: old.get(k) for k in payload} != payload:
                payload["read"] = dt.date.today().isoformat()
                if not args.dry_run:
                    CACHE.write_text(json.dumps(payload, indent=2) + "\n")
            print(f"read {len(tasks)} task(s) at {commit or '(no commit)'} from {source} -> {CACHE.name}")
        else:
            if not CACHE.is_file():
                sys.exit(f"no cache at {CACHE}; run once with --source <robot_coding_bench clone> --commit <commit>")
            payload = json.loads(CACHE.read_text())
            tasks, commit = payload["tasks"], payload.get("commit", "")
        demo_files = install_demos(tasks, fetch_demos(args.demos, tmp), args.dry_run) if args.demos else 0

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
                write_page(path, scaffold(task, synced, commit), BODY_TEMPLATE.replace("{benchmark}", BENCHMARK))
            created += 1
    seeded = seed_state(tasks, args.dry_run)
    orphans = sorted(p.stem for p in TASK_DIR.glob("*.md") if p.stem not in seen and p.stem != "index")
    families = sorted({t["family"] for t in tasks})
    print(f"families  : {', '.join(families)}")
    print(f"tasks     : {len(tasks)}")
    print(f"created   : {created}{' (dry run)' if args.dry_run else ''}")
    print(f"updated   : {updated}")
    print(f"unchanged : {unchanged}")
    print(f"demos     : {demo_files} file(s) changed" if args.demos else "demos     : not asked (--demos host:dir)")
    if seeded:
        print(f"difficulty from task.toml for {len(seeded)} new task(s) in {STATE.relative_to(ROOT)}")
    if orphans:
        print(f"no longer in robot_coding_bench ({len(orphans)}): {', '.join(orphans)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Sync RoboLab task pages from the benchmark's own source tree.

Like RoboWits, RoboLab publishes its tasks as code rather than as a gallery —
but the code is unusually declarative: every task is a dataclass carrying the
instruction (in three wordings), the scene, the episode budget, the attribute
tags, the success predicate and the scored subtasks. We read all of it with
`ast`, so this runs without Isaac Sim, a GPU, or an install.

Two things worth knowing about what lands in `upstream:`

  * `difficulty_label` is **RoboLab's** difficulty, recomputed here with their
    own formula (`SKILL_WEIGHTS` over the task's attributes against
    `DIFFICULTY_THRESHOLDS`, both read from their `constants.py`). It is not
    our `difficulty` in state/, which asks a different question: how hard is
    this for a coding agent driving the robot?
  * `scene_image` is the scene preview RoboLab ships in `assets/scenes/_images`,
    converted to JPEG and copied into `docs/assets/robolab/scenes/`. These have no
    oracle video, so the scene picture is what makes a row reviewable at all.

Usage:
  python scripts/import_robolab_tasks.py --source ~/src/RoboLab   # read + write
  python scripts/import_robolab_tasks.py                          # from the cache
  python scripts/import_robolab_tasks.py --dry-run
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
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from taskio import read_page, write_page  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BENCHMARK = "robolab"
CACHE = ROOT / "data" / "benchmarks" / f"{BENCHMARK}.tasks.upstream.json"
TASK_DIR = ROOT / "docs" / "benchmarks" / BENCHMARK / "tasks"
SCENE_DIR = ROOT / "docs" / "assets" / BENCHMARK / "scenes"
REPO_URL = "https://github.com/NVlabs/RoboLab"
SITE_URL = "https://research.nvidia.com/labs/srl/projects/robolab/"

# Params of the success `DoneTerm` worth mirroring; the rest is plumbing.
SUCCESS_PARAMS = ["object", "container", "reference_object", "surface", "objects",
                  "order", "logical", "K", "require_gripper_detached", "require_contact_with"]

# ───────────────────────────────────────────────────── project-page videos

VIDEO_RE = re.compile(r'src="\./static/videos/((?:captioned/)?[^"]+)\.mp4"')
# `Put_the_onion_in_the_wood_bowl_0_viewport_3X` -> the instruction, an episode
# index and a speed-up suffix. The instruction is what identifies the task.
SUFFIX_RE = re.compile(r"_\d+(_viewport)?(_\d+X)?$", re.I)
# Below this, a paraphrase is a guess rather than a match.
FUZZY_MIN = 0.72
STOPWORDS = {"the", "a", "an", "of", "on", "in", "into", "out", "to", "and", "or", "it",
             "is", "are", "all", "up", "from", "with", "that", "so", "make", "sure",
             "put", "place", "pick", "take", "move", "each", "every", "please"}


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def site_videos(url: str = SITE_URL) -> list[dict]:
    """Every task clip on the project page, as {url, words}.

    RoboLab names each clip after the instruction it is demonstrating, which is
    the only key it shares with the task definitions — there is no task id in
    the file name, so matching is on the instruction text itself.
    """
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": "robobench-docs/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        page = resp.read().decode("utf-8", "replace")

    skip = {"scene_gen", "task_gen", "env_gen", "lighting", "shadows", "backgrounds",
            "textures", "object_pose", "camera_views", "robolab_dashboard"}
    out = []
    for name in dict.fromkeys(VIDEO_RE.findall(page)):
        stem = name.split("/")[-1]
        if stem in skip:
            continue
        phrase = SUFFIX_RE.sub("", stem).replace("_", " ")
        out.append({"url": urllib.parse.urljoin(url, f"static/videos/{name}.mp4"),
                    "words": words(phrase), "name": stem})
    return out


def attach_videos(tasks: list[dict], clips: list[dict]) -> None:
    """Match clips to tasks on instruction text, exactly or as a prefix.

    A clip may demonstrate the `vague` or `specific` wording rather than the
    default one, so all three are candidates; which one it was is recorded, as
    it changes what the video is evidence of.
    """
    used = set()
    for task in tasks:
        candidates = {"default": task["instruction"], **(task.get("instruction_variants") or {})}
        for variant, text in candidates.items():
            target = words(text)
            if not target:
                continue
            for clip in clips:
                if clip["url"] in used:
                    continue
                w = clip["words"]
                if w == target or (len(w) >= 4 and target[:len(w)] == w):
                    task["oracle_video"] = clip["url"]
                    task["oracle_video_instruction"] = variant
                    used.add(clip["url"])
                    break
            if task.get("oracle_video"):
                break

    # Anything left over is a clip whose file name paraphrases the instruction
    # ("the small yogurt" for "the small red yogurt"). String similarity alone
    # is not safe here — "Take all the bananas out of the grey bin and put it on
    # the table" scores 0.83 against the *keyboard* task, which is a different
    # task entirely. So require containment as well: every content word of the
    # clip has to appear somewhere in that task's own wordings, which is what
    # separates a paraphrase from a different task phrased alike.
    from difflib import SequenceMatcher

    for clip in clips:
        if clip["url"] in used:
            continue
        clip_content = {w for w in clip["words"] if w not in STOPWORDS}
        best, score = None, 0.0
        for task in tasks:
            if task.get("oracle_video"):
                continue
            wordings = {"default": task["instruction"], **(task.get("instruction_variants") or {})}
            vocabulary = {w for text in wordings.values() for w in words(text)}
            if not clip_content <= vocabulary:
                continue
            for variant, text in wordings.items():
                ratio = SequenceMatcher(None, " ".join(clip["words"]), " ".join(words(text))).ratio()
                if ratio > score:
                    best, score = (task, variant), ratio
        if best and score >= FUZZY_MIN:
            task, variant = best
            task["oracle_video"] = clip["url"]
            task["oracle_video_instruction"] = variant
            task["oracle_video_matched"] = f"paraphrase of the {variant} wording ({score:.2f})"
            used.add(clip["url"])
            print(f"  ~ {clip['name'][:52]:54s} -> {task['id']} ({score:.2f}, {variant})")

    unmatched = [c["name"] for c in clips if c["url"] not in used]
    print(f"project-page clips: {len(used)} matched to tasks, {len(unmatched)} unmatched")
    for name in unmatched:
        print(f"  ? {name}")


BODY_TEMPLATE = """
## Why this task is interesting

<!-- One paragraph. What makes this hard, or why it earns a slot in the suite?
     Delete this comment when you write it. -->

_Not yet written._

## Capability notes

<!-- Justify the labels in state/tasks/robolab.yml. One bullet per label is
     plenty; reviewers read this to sanity-check the tagging. -->

_Not yet written._

## Oracle demo review

<!-- RoboLab ships no per-task oracle video; the row shows its scene instead.
     If we have recorded a reference solution, say whether the trajectory is
     clean and what it relies on. -->

_Not yet reviewed._

## Discussion

<!-- Sign your points with your GitHub handle. Long threads belong in the
     linked GitHub Discussion; keep the conclusions here. -->
"""


def snake(name: str) -> str:
    name = re.sub(r"Task$", "", name)
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def titleize(name: str) -> str:
    """`BlockStackingSpecifiedOrderTask` -> `Block Stacking Specified Order`."""
    return snake(name).replace("_", " ").title()


# ────────────────────────────────────────────────────────── source reading

def _literal(node: ast.AST):
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError):
        return None


def _assigned(cls: ast.ClassDef, name: str) -> ast.AST | None:
    for item in cls.body:
        targets = []
        if isinstance(item, ast.Assign):
            targets = item.targets
        elif isinstance(item, ast.AnnAssign):
            targets = [item.target]
        else:
            continue
        for t in targets:
            if isinstance(t, ast.Name) and t.id == name:
                return item.value
    return None


def _success_term(module: ast.Module, terminations_name: str) -> dict:
    """The `success = DoneTerm(func=..., params={...})` of a terminations class."""
    for node in module.body:
        if not (isinstance(node, ast.ClassDef) and node.name == terminations_name):
            continue
        value = _assigned(node, "success")
        if not isinstance(value, ast.Call):
            continue
        out: dict = {}
        for kw in value.keywords:
            if kw.arg == "func":
                out["predicate"] = getattr(kw.value, "id", getattr(kw.value, "attr", ""))
            elif kw.arg == "params":
                params = _literal(kw.value) or {}
                kept = {k: v for k, v in params.items() if k in SUCCESS_PARAMS}
                if kept:
                    out["params"] = kept
        return out
    return {}


def _subtasks(cls: ast.ClassDef) -> dict:
    """How many scored subtasks, and which predicates they are built from."""
    value = _assigned(cls, "subtasks")
    if not isinstance(value, ast.List):
        return {}
    predicates = []
    for element in value.elts:
        if isinstance(element, ast.Call):
            fn = getattr(element.func, "id", getattr(element.func, "attr", ""))
            if fn == "Subtask":
                for kw in element.keywords:
                    if kw.arg == "conditions" and isinstance(kw.value, ast.Call):
                        inner = kw.value
                        if getattr(inner.func, "id", "") == "partial" and inner.args:
                            fn = getattr(inner.args[0], "id", getattr(inner.args[0], "attr", "")) or fn
                        else:
                            fn = getattr(inner.func, "id", getattr(inner.func, "attr", "")) or fn
            if fn:
                predicates.append(fn)
    return {"subtasks": len(value.elts), "subtask_predicates": sorted(set(predicates))}


def difficulty_rules(source: Path) -> tuple[dict, tuple]:
    """RoboLab's own attribute weights and difficulty thresholds."""
    text = (source / "robolab" / "constants.py").read_text(encoding="utf-8")
    tree = ast.parse(text)
    weights, thresholds = {}, (2, 4)
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else (
            [node.target] if isinstance(node, ast.AnnAssign) else [])
        for t in targets:
            if not isinstance(t, ast.Name):
                continue
            if t.id == "SKILL_WEIGHTS":
                weights = _literal(node.value) or {}
            elif t.id == "DIFFICULTY_THRESHOLDS":
                thresholds = tuple(_literal(node.value) or (2, 4))
    return weights, thresholds


def label_for(attributes: list[str], weights: dict, thresholds: tuple) -> str:
    score = sum(weights.get(a, 0) for a in attributes or [])
    simple, moderate = thresholds
    return "simple" if score <= simple else ("moderate" if score <= moderate else "complex")


def parse_task_module(path: Path, weights: dict, thresholds: tuple) -> dict | None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        bases = {getattr(b, "id", getattr(b, "attr", "")) for b in node.bases}
        if "Task" not in bases:
            continue

        scene_call = _assigned(node, "scene")
        scene_file = ""
        if isinstance(scene_call, ast.Call) and scene_call.args:
            scene_file = _literal(scene_call.args[0]) or ""

        instruction = _literal(_assigned(node, "instruction")) or {}
        if isinstance(instruction, str):
            instruction = {"default": instruction}
        attributes = _literal(_assigned(node, "attributes")) or []
        objects = _literal(_assigned(node, "contact_object_list")) or []
        episode = _literal(_assigned(node, "episode_length_s"))
        task_name = _literal(_assigned(node, "task_name")) or node.name

        terminations = _assigned(node, "terminations")
        success = _success_term(tree, getattr(terminations, "id", "")) if terminations else {}

        out = {
            "id": snake(node.name),
            "title": titleize(node.name),
            "env_class": node.name,
            "task_name": task_name,
            "source_file": f"robolab/tasks/benchmark/{path.name}",
            "scene_usda": scene_file,
            "scene_model": Path(scene_file).stem,
            "instruction": (instruction.get("default") or "").strip(),
            "instruction_variants": {k: v for k, v in instruction.items() if k != "default"},
            "episode_length_s": episode,
            "attributes": attributes,
            "difficulty_label": label_for(attributes, weights, thresholds),
            "objects": [o for o in objects if o != "table"],
            **success,
            **_subtasks(node),
        }
        return out
    return None


def copy_scene_images(source: Path, scenes: set[str], quality: int = 82) -> dict[str, str]:
    """Copy RoboLab's scene previews into docs/ as JPEG, and report the mapping.

    PNG at 640x480 is ~260 KB each and this repository already carries a
    gigabyte of video; JPEG keeps 75 previews under a couple of megabytes.
    """
    src_dir = source / "assets" / "scenes" / "_images"
    if not src_dir.is_dir():
        print(f"no scene images at {src_dir}; rows will have no poster")
        return {}
    SCENE_DIR.mkdir(parents=True, exist_ok=True)
    out: dict[str, str] = {}
    missing = []
    for scene in sorted(scenes):
        png = src_dir / f"{scene}.png"
        if not png.is_file():
            missing.append(scene)
            continue
        jpg = SCENE_DIR / f"{scene}.jpg"
        if not jpg.is_file():
            try:
                from PIL import Image  # type: ignore
                Image.open(png).convert("RGB").save(jpg, "JPEG", quality=quality, optimize=True)
            except ImportError:
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(png),
                                "-q:v", "4", str(jpg)], check=True)
        out[scene] = jpg.name
    if missing:
        print(f"no preview image for {len(missing)} scene(s): {', '.join(missing[:6])}")
    print(f"scene previews: {len(out)} in {SCENE_DIR.relative_to(ROOT)}")
    return out


def read_source(source: Path, with_images: bool) -> list[dict]:
    task_dir = source / "robolab" / "tasks" / "benchmark"
    if not task_dir.is_dir():
        sys.exit(f"{source} does not look like a RoboLab checkout (no {task_dir})")
    weights, thresholds = difficulty_rules(source)

    tasks = []
    for path in sorted(task_dir.glob("*.py")):
        if path.name.startswith("_"):
            continue
        parsed = parse_task_module(path, weights, thresholds)
        if parsed:
            tasks.append(parsed)

    images = copy_scene_images(source, {t["scene_model"] for t in tasks if t["scene_model"]}) if with_images else {}
    for task in tasks:
        if task["scene_model"] in images:
            task["scene_image"] = images[task["scene_model"]]
    return tasks


# ────────────────────────────────────────────────────────── page writing

UPSTREAM_KEYS = ["instruction", "scene_model", "scene_usda", "scene_image", "env_class",
                 "task_name", "source_file", "episode_length_s", "attributes",
                 "difficulty_label", "predicate", "params", "subtasks",
                 "subtask_predicates", "objects", "instruction_variants",
                 "oracle_video", "oracle_video_instruction", "oracle_video_matched"]


def upstream_block(task: dict, synced: str, ref: str) -> dict:
    block = {"source": f"{REPO_URL} @ {ref}" if ref else REPO_URL, "synced": synced}
    for key in UPSTREAM_KEYS:
        value = task.get(key)
        if value not in (None, [], {}, ""):
            block["success_predicate" if key == "predicate" else
                  ("success_params" if key == "params" else key)] = value
    return block


def scaffold(task: dict, synced: str, ref: str) -> dict:
    return {
        "title": task["title"],
        "task_id": task["id"],
        "benchmark": BENCHMARK,
        "upstream": upstream_block(task, synced, ref),
    }


def git_ref(source: Path) -> str:
    for cmd in (["git", "-C", str(source), "describe", "--tags", "--exact-match"],
                ["git", "-C", str(source), "rev-parse", "--short", "HEAD"]):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except Exception:  # noqa: BLE001
            pass
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default=None, help="a RoboLab checkout; omit to use the cache")
    ap.add_argument("--no-scene-images", action="store_true", help="skip copying scene previews")
    ap.add_argument("--no-videos", action="store_true",
                    help="skip the project page; keep whatever video URLs are cached")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="rewrite pages even when upstream is unchanged")
    args = ap.parse_args()

    if args.source:
        source = Path(args.source).expanduser()
        tasks = read_source(source, not args.no_scene_images)
        if not args.no_videos:
            try:
                attach_videos(tasks, site_videos())
            except Exception as exc:  # noqa: BLE001
                print(f"could not read the project page ({exc!r}); no video URLs recorded")
        payload = {"source": REPO_URL, "ref": git_ref(source), "site": SITE_URL,
                   "read": dt.date.today().isoformat(), "tasks": tasks}
        CACHE.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"read {len(tasks)} task(s) from {source} -> {CACHE.name}")
    else:
        if not CACHE.is_file():
            sys.exit(f"no cache at {CACHE}; run once with --source <RoboLab checkout>")
        payload = json.loads(CACHE.read_text())
        tasks = payload["tasks"]

    synced = dt.date.today().isoformat()
    ref = payload.get("ref", "")
    TASK_DIR.mkdir(parents=True, exist_ok=True)

    created = updated = unchanged = 0
    seen = set()
    for task in tasks:
        seen.add(task["id"])
        path = TASK_DIR / f"{task['id']}.md"
        fresh = upstream_block(task, synced, ref)
        if path.is_file():
            meta, body = read_page(path)
            current = dict(meta.get("upstream") or {})
            comparable = dict(fresh, synced=current.get("synced", synced))
            if current == comparable and not args.force:
                unchanged += 1
                continue
            meta["upstream"] = dict(fresh, synced=synced)
            if not args.dry_run:
                write_page(path, meta, body)
            updated += 1
        else:
            if not args.dry_run:
                write_page(path, scaffold(task, synced, ref), BODY_TEMPLATE)
            created += 1

    orphans = sorted(p.stem for p in TASK_DIR.glob("*.md") if p.stem not in seen and p.stem != "index")
    print(f"upstream tasks : {len(tasks)}")
    print(f"created        : {created}{' (dry run)' if args.dry_run else ''}")
    print(f"updated        : {updated}")
    print(f"unchanged      : {unchanged}")
    if orphans:
        print(f"no longer upstream ({len(orphans)}): {', '.join(orphans)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Export the published runs' replays and images for a host outside GitHub Pages (a Hugging Face dataset, say).

    python scripts/export_run_media.py [--out DIR]     (make export-run-media OUT=DIR; uploads nothing)

The public site shows every published trial's log (data/published_runs/, scripts/publish_runs.py) but not its media:
4.6 GB of replay video and 3 GB of images would not fit GitHub Pages. This writes them to DIR (default
.cache/run-media-export/, gitignored) with the same layout the log pages load them from:

    <benchmark>/<run>/<task>/<slot>/replay.mp4, replay.png, img/<n>.<ext>, snap/<n>.<ext>
    manifest.json      every file: path, bytes, sha256, content type; and the totals
    README.md          what this is, for the dataset card

Only the files a published log names are exported, from the local log data (docs/assets/<benchmark>/runs/, written by
scripts/import_runs.py). Files are hard-linked when DIR is on the same disk, so the export costs no space; copied
otherwise. Re-running brings DIR up to date (a file that is no longer named is moved to DIR/.stale/, not deleted).

Then upload DIR as it is and put its base address in data/public.yml (run_media_base), e.g. for a Hugging Face dataset
https://huggingface.co/datasets/<org>/<name>/resolve/main/ ; the public build then loads
<run_media_base><benchmark>/<run>/<task>/<slot>/<file>.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLISHED = ROOT / "data" / "published_runs"
LOCAL = ROOT / "docs" / "assets"
TYPES = {".mp4": "video/mp4", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}

README = """# Agent-run media

The replays and the images of the agent runs published on
https://embodied-agent-interface-v2-internal.github.io/ (the Runs section): for each trial,
the verifier's replay of the trajectory the agent handed in (`replay.mp4`, its last frame
`replay.png`), the images the model was shown (`img/`), and, where the agent handed in no
trajectory, the newest images it saved (`snap/`).

Layout: `<benchmark>/<run>/<task>/<slot>/<file>`, where slot is the mode (`unlimited`,
`limited`) or the mode of a run a rerun replaced (`<mode>-prev`). `manifest.json` lists every
file with its size and SHA-256.

Rendered in the simulators the benchmarks use; the scenes contain their assets (BEHAVIOR-1K,
RoboLab, RoboWits, RoboPaint). Written by `scripts/export_run_media.py` of the site's repository.
"""


def media_of(log: dict) -> list[str]:
    """The media files a published trial log names, relative to its slot directory."""
    media = log.get("media") or {}
    names = [media[k] for k in ("video", "last") if isinstance(media.get(k), str)]   # "problem" is a sentence
    for step in log.get("steps") or []:
        names += [x for x in step.get("img") or [] if isinstance(x, str)]
    names += [s.get("src") for s in log.get("snapshots") or [] if isinstance(s, dict) and s.get("src")]
    return sorted({n for n in names if n and not n.startswith("/") and ".." not in n})


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def place(src: Path, dst: Path) -> None:
    """dst becomes the same content as src: a hard link where possible, else a copy."""
    if dst.exists():
        if dst.stat().st_ino == src.stat().st_ino or (dst.stat().st_size == src.stat().st_size
                                                      and dst.stat().st_mtime >= src.stat().st_mtime):
            return
        dst.unlink()                                    # our own previous export of a file that changed
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / ".cache" / "run-media-export")
    args = ap.parse_args()
    out: Path = args.out.resolve()
    if not PUBLISHED.is_dir():
        sys.exit("no data/published_runs/: run `make publish-runs` first")
    files, missing = [], []
    for log_path in sorted(PUBLISHED.glob("*/*/*/*.json")):
        bench, run, task = log_path.parts[-4:-1]
        slot = log_path.stem
        log = json.loads(log_path.read_text(encoding="utf-8"))
        for name in media_of(log):
            rel = f"{bench}/{run}/{task}/{slot}/{name}"
            src = LOCAL / bench / "runs" / run / task / slot / name
            if not src.is_file():
                missing.append(rel)
                continue
            place(src, out / rel)
            files.append(rel)
    keep = set(files) | {"manifest.json", "README.md"}
    stale = [p for p in out.rglob("*") if p.is_file() and ".stale" not in p.parts
             and str(p.relative_to(out)) not in keep]
    for p in stale:                                     # no longer named by a published log: moved aside
        dst = out / ".stale" / p.relative_to(out)
        dst.parent.mkdir(parents=True, exist_ok=True)
        p.replace(dst)
    entries = []
    for rel in files:
        p = out / rel
        entries.append({"path": rel, "bytes": p.stat().st_size, "sha256": sha256(p),
                        "type": TYPES.get(p.suffix.lower(), "application/octet-stream")})
    total = sum(e["bytes"] for e in entries)
    by_type: dict[str, list[int]] = {}
    for e in entries:
        c = by_type.setdefault(e["type"], [0, 0])
        c[0] += 1
        c[1] += e["bytes"]
    manifest = {"written": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "files": len(entries),
                "bytes": total, "by_type": {k: {"files": v[0], "bytes": v[1]} for k, v in sorted(by_type.items())},
                "largest": max(entries, key=lambda e: e["bytes"])["path"] if entries else None,
                "missing": missing, "entries": entries}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    (out / "README.md").write_text(README)
    print(f"{len(entries)} files, {total / 2**30:.2f} GiB, in {out}")
    for k, v in manifest["by_type"].items():
        print(f"  {k:<11} {v['files']:>6} files  {v['bytes'] / 2**30:6.2f} GiB")
    if missing:
        print(f"  {len(missing)} named by a published log but absent here, e.g. {missing[0]}")
    if stale:
        print(f"  {len(stale)} no longer named: moved to {out / '.stale'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Compress the exported run media for the outside host (the Hugging Face dataset the public site loads them from).

    python scripts/compress_run_media.py [--src DIR] [--out DIR] [--benchmark ID ...] [--jobs N]

Reads the export of scripts/export_run_media.py (default .cache/run-media-export/) and writes, with the same layout
(<benchmark>/<run>/<task>/<slot>/<file>), to --out (default .cache/run-media-hf/, gitignored):

  * replay videos: H.264 (libx264), yuv420p, CRF 28, height at most 720, no audio, `-movflags +faststart` (the
    index first, so a browser plays and seeks before the whole file arrives). Each output is checked: its duration is
    within 1 % of the original's and it decodes without an error. Where the encode is not smaller, the original is
    remuxed with faststart instead (same frames);
  * PNG images: WebP at quality 80 (<name>.webp); the published logs name them so (scripts/publish_runs.py, with
    `run_media_images: webp` in data/public.yml);
  * JPEG images: as they are (hard-linked).

Re-running redoes only what is missing or older than its source, so it can follow a new `make export-run-media`.
Writes <out>/manifest.json (every file, its size and its source's) and prints the sizes before and after.
Nothing is uploaded: `make upload-run-media` does that.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CRF = 28
MAX_HEIGHT = 720
WEBP_QUALITY = 80


def _duration(path: Path) -> float | None:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def _decodes(path: Path) -> bool:
    r = subprocess.run(["ffmpeg", "-v", "error", "-threads", "2", "-i", str(path), "-map", "0:v:0", "-f", "null", "-"],
                       capture_output=True, text=True)
    return r.returncode == 0 and not r.stderr.strip()


def _video(src: Path, dst: Path) -> dict:
    """Encode src to dst (or remux it where the encode is not smaller); raise when the result does not check out."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.stem + ".tmp.mp4")
    want = _duration(src)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-map", "0:v:0", "-an", "-c:v", "libx264", "-preset",
                    "medium", "-crf", str(CRF), "-pix_fmt", "yuv420p", "-vf", f"scale=-2:'min({MAX_HEIGHT},ih)'",
                    "-threads", "2", "-movflags", "+faststart", str(tmp)], check=True, capture_output=True)
    how = "h264 crf28"
    if tmp.stat().st_size >= src.stat().st_size:          # no gain: keep the original frames, with the index first
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-map", "0:v:0", "-an", "-c", "copy",
                        "-movflags", "+faststart", str(tmp)], check=True, capture_output=True)
        how = "remux (faststart)"
    got = _duration(tmp)
    if not want or not got or abs(got - want) > 0.01 * want + 0.05:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"{src}: duration {got} against {want}")
    if not _decodes(tmp):
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"{src}: the output does not decode cleanly")
    tmp.replace(dst)
    return {"how": how, "duration": round(got, 2)}


def _image(src: Path, dst: Path) -> dict:
    """PNG -> WebP with ffmpeg's libwebp (no Python imaging library needed)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.stem + ".tmp.webp")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-c:v", "libwebp", "-quality", str(WEBP_QUALITY),
                    "-compression_level", "4", "-frames:v", "1", str(tmp)], check=True, capture_output=True)
    if not tmp.is_file() or tmp.stat().st_size == 0:
        raise RuntimeError(f"{src}: no WebP written")
    tmp.replace(dst)
    return {"how": f"webp q{WEBP_QUALITY}"}


def _link(src: Path, dst: Path) -> dict:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        import shutil
        shutil.copy2(src, dst)
    return {"how": "as is"}


def target(rel: str) -> str:
    """The published name of an exported file: a PNG becomes WebP, everything else keeps its name."""
    return rel[:-4] + ".webp" if rel.lower().endswith(".png") else rel


def work(src: str, dst: str) -> tuple[str, dict]:
    s, d = Path(src), Path(dst)
    if s.suffix.lower() == ".mp4":
        info = _video(s, d)
    elif s.suffix.lower() == ".png":
        info = _image(s, d)
    else:
        info = _link(s, d)
    return dst, info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, default=ROOT / ".cache" / "run-media-export")
    ap.add_argument("--out", type=Path, default=ROOT / ".cache" / "run-media-hf")
    ap.add_argument("--benchmark", action="append", help="only this benchmark's media (repeatable)")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 4) // 2), help="videos at a time (2 threads each)")
    ap.add_argument("--image-jobs", type=int, default=os.cpu_count() or 8, help="images at a time")
    a = ap.parse_args()
    src, out = a.src.resolve(), a.out.resolve()
    if not (src / "manifest.json").is_file():
        sys.exit(f"no export in {src}: run `make export-run-media` first")
    files = [p for p in sorted(src.rglob("*")) if p.is_file() and ".stale" not in p.parts
             and p.name not in ("manifest.json", "README.md")
             and (not a.benchmark or p.relative_to(src).parts[0] in a.benchmark)]
    todo, entries, failed = [], {}, []
    for p in files:
        rel = str(p.relative_to(src))
        d = out / target(rel)
        entries[target(rel)] = {"source": rel, "source_bytes": p.stat().st_size}
        if d.is_file() and d.stat().st_mtime >= p.stat().st_mtime:
            entries[target(rel)]["how"] = "kept"
            continue
        todo.append((str(p), str(d)))
    videos = [t for t in todo if t[0].endswith(".mp4")]
    others = [t for t in todo if not t[0].endswith(".mp4")]
    print(f"{len(files)} files: {len(videos)} videos and {len(others)} images to do, {len(files) - len(todo)} up to date",
          flush=True)
    for batch, jobs in ((videos, a.jobs), (others, a.image_jobs)):
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            futs = {ex.submit(work, s, d): s for s, d in batch}
            done = 0
            for f in as_completed(futs):
                done += 1
                try:
                    dst, info = f.result()
                    entries[str(Path(dst).relative_to(out))].update(info)
                except Exception as exc:  # noqa: BLE001 - report every failure, keep the rest going
                    failed.append(f"{futs[f]}: {exc}")
                if batch is videos and (done % 25 == 0 or done == len(batch)):
                    print(f"  videos {done}/{len(batch)}", flush=True)
    for rel, e in entries.items():
        p = out / rel
        e["bytes"] = p.stat().st_size if p.is_file() else None
    before = sum(e["source_bytes"] for e in entries.values())
    after = sum(e["bytes"] or 0 for e in entries.values())
    kinds = {}
    for rel, e in entries.items():
        k = Path(rel).suffix.lower()
        c = kinds.setdefault(k, [0, 0, 0])
        c[0] += 1
        c[1] += e["source_bytes"]
        c[2] += e["bytes"] or 0
    remuxed = sorted(rel for rel, e in entries.items() if e.get("how") == "remux (faststart)")
    (out / "manifest.json").write_text(json.dumps({
        "files": len(entries), "bytes": after, "source_bytes": before, "by_type": {
            k: {"files": v[0], "source_bytes": v[1], "bytes": v[2]} for k, v in sorted(kinds.items())},
        "remuxed": remuxed, "failed": failed, "entries": entries}, indent=1) + "\n")
    print(f"before {before / 2**30:.2f} GiB -> after {after / 2**30:.2f} GiB ({len(entries)} files)")
    for k, v in sorted(kinds.items()):
        print(f"  {k:<6} {v[0]:>6} files  {v[1] / 2**20:8.0f} MiB -> {v[2] / 2**20:8.0f} MiB")
    print(f"  {len(remuxed)} videos kept as a faststart remux (the encode was not smaller)")
    for f in failed:
        print("  FAILED", f)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

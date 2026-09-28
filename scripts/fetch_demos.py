#!/usr/bin/env python3
"""Download every oracle demo to a local MP4.

We serve local files rather than embedding YouTube/Vimeo players because an
<video> element gives us playback-rate control. Reviewing a 100-task suite at
1x is not viable; at 3x it is an afternoon.

Videos are NOT committed (see .gitignore) — roughly 1.2 GB at 480p. Each
contributor fetches what they need:

  python scripts/fetch_demos.py                 # everything missing
  python scripts/fetch_demos.py --only can_meat turning_on_radio
  python scripts/fetch_demos.py --height 720    # sharper, bigger
  python scripts/fetch_demos.py --repair        # re-remux + re-probe existing files
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import taskdb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
YTDLP = ROOT / ".venv" / "bin" / "yt-dlp"
# Per-benchmark referer: some hosts (Vimeo) refuse a request without one.
REFERERS = {
    "behavior-1k": "https://behavior.stanford.edu/",
    "robowits": "https://umass-embodied-agi.github.io/",
    "robolab": "https://research.nvidia.com/",
}
OUT = ROOT / "docs" / "assets"   # set to the benchmark's folder in main()


def ytdlp() -> str:
    return str(YTDLP) if YTDLP.exists() else "yt-dlp"


def faststart(path: Path) -> None:
    """Move the MP4 moov atom to the front.

    yt-dlp's merged output puts it at the end, so a browser cannot report the
    duration or seek until the whole file has downloaded — a 10 MB demo shows
    "0:06" and refuses to scrub. A stream copy fixes it in under a second.
    """
    if not shutil.which("ffmpeg"):
        return
    tmp = path.with_suffix(".fast.mp4")
    proc = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(path),
         "-c", "copy", "-movflags", "+faststart", str(tmp)],
        capture_output=True, text=True,
    )
    if proc.returncode == 0 and tmp.exists() and tmp.stat().st_size > 0:
        tmp.replace(path)
    else:
        tmp.unlink(missing_ok=True)


def make_poster(path: Path, at_fraction: float = 0.12) -> bool:
    """Extract a local poster frame from the MP4.

    Posters were being pulled from img.youtube.com / vumbnail.com, which makes
    the first paint depend on two third-party hosts for 100 images. A frame cut
    from the file we already have is faster, works offline, and actually shows
    the scene rather than a generic thumbnail.
    """
    dest = path.with_suffix(".jpg")
    if dest.exists() and dest.stat().st_size > 0:
        return True
    if not shutil.which("ffmpeg"):
        return False
    seconds = max(1, int(probe_duration(path) * at_fraction))
    proc = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-ss", str(seconds), "-i", str(path),
         "-frames:v", "1", "-vf", "scale='min(640,iw)':-2", "-q:v", "5", str(dest)],
        capture_output=True, text=True,
    )
    return proc.returncode == 0 and dest.exists()


def probe_dims(path: Path) -> tuple[int, int]:
    """Real pixel dimensions.

    These demos are square (the R1 Pro head camera is 720x720), not 16:9.
    Assuming widescreen pillarboxes every thumbnail, so the layout reads the
    true aspect from here instead of guessing.
    """
    if not shutil.which("ffprobe"):
        return (0, 0)
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        w, h = proc.stdout.strip().split(",")[:2]
        return (int(w), int(h))
    except (TypeError, ValueError):
        return (0, 0)


def probe_duration(path: Path) -> int:
    """Real duration in seconds, or 0.

    Worth measuring: upstream's published duration is the teleoperation episode
    length, which for the Vimeo cohort is longer than the video actually posted.
    We label rows with what the file really contains.
    """
    if not shutil.which("ffprobe"):
        return 0
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return int(float(proc.stdout.strip()))
    except (TypeError, ValueError):
        return 0


def fetch_direct(dest: Path, url: str, referer: str) -> tuple[bool, str]:
    """Download a plain MP4 that a project page serves itself.

    BEHAVIOR's demos sit behind YouTube and Vimeo and need yt-dlp; RoboWits and
    RoboLab publish static files, where a request is both simpler and more
    reliable than asking an extractor to recognise them.
    """
    import urllib.error
    import urllib.request

    req = urllib.request.Request(url, headers={
        "User-Agent": "robobench-docs/1.0", "Referer": referer or url})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as fh:
            shutil.copyfileobj(resp, fh)
    except (urllib.error.URLError, OSError) as exc:
        dest.unlink(missing_ok=True)
        return False, repr(exc)[:160]
    if dest.stat().st_size == 0:
        dest.unlink(missing_ok=True)
        return False, "empty file"
    return True, ""


def fetch_one(task_id: str, url: str, height: int, referer: str, retries: int = 2) -> tuple[str, bool, str]:
    dest = OUT / f"{task_id}.mp4"
    if dest.exists() and dest.stat().st_size > 0:
        return task_id, True, "cached"

    if url.lower().endswith(".mp4"):
        ok, err = fetch_direct(dest, url, referer)
        if ok:
            faststart(dest)
            make_poster(dest)
            return task_id, True, f"{dest.stat().st_size / 1e6:.1f} MB"
        return task_id, False, err

    fmt = (
        f"bv*[height<={height}][ext=mp4]+ba[ext=m4a]/"
        f"b[height<={height}][ext=mp4]/b[height<={height}]/b"
    )
    cmd = [
        ytdlp(), "--quiet", "--no-warnings", "--socket-timeout", "30",
        # Vimeo returns 401 to a plain client; impersonation is required.
        "--impersonate", "chrome", "--referer", referer,
        "-f", fmt, "--merge-output-format", "mp4",
        "-o", str(OUT / f"{task_id}.%(ext)s"), url,
    ]
    last = ""
    for _ in range(retries + 1):
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0 and dest.exists():
            faststart(dest)
            make_poster(dest)
            return task_id, True, f"{dest.stat().st_size / 1e6:.1f} MB"
        last = (proc.stderr or proc.stdout).strip().splitlines()[-1:] or [""]
        last = last[0][:160]
    return task_id, False, last or "failed"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--benchmark", default="behavior-1k")
    ap.add_argument("--height", type=int, default=480)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--repair", action="store_true",
                    help="faststart + re-probe files already on disk, download nothing")
    args = ap.parse_args()

    bench = taskdb.benchmarks().get(args.benchmark)
    if not bench:
        sys.exit(f"unknown benchmark {args.benchmark!r}")

    global OUT
    OUT = ROOT / "docs" / taskdb.demo_dir(args.benchmark)
    referer = REFERERS.get(args.benchmark, "")
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [
        (t.task_id, t.upstream.get("oracle_video", ""))
        for t in bench.tasks
        if t.upstream.get("oracle_video")
        and (not args.only or t.task_id in args.only)
    ]

    if args.repair:
        existing = sorted(OUT.glob("*.mp4"))
        print(f"repairing {len(existing)} local file(s)")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            list(pool.map(faststart, existing))
            list(pool.map(make_poster, existing))
        jobs = []

    print(f"{len(jobs)} demo(s) to consider, {args.jobs} at a time, max {args.height}p\n")
    ok = failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(fetch_one, tid, url, args.height, referer): tid for tid, url in jobs}
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            tid, good, note = fut.result()
            ok, failed = (ok + 1, failed) if good else (ok, failed + 1)
            print(f"[{i:3d}/{len(jobs)}] {'ok  ' if good else 'FAIL'} {tid:<48} {note}", flush=True)

    # The manifest records the real duration of each file so the site can label
    # rows with what the video actually contains.
    print("\nprobing durations…")
    manifest = {}
    for path in sorted(OUT.glob("*.mp4")):
        if path.stat().st_size > 0:
            w, h = probe_dims(path)
            manifest[path.stem] = {
                "seconds": probe_duration(path),
                "bytes": path.stat().st_size,
                "poster": path.with_suffix(".jpg").exists(),
                "width": w,
                "height": h,
            }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    total = sum(v["bytes"] for v in manifest.values())
    print(f"\n{ok} ok, {failed} failed · {len(manifest)} local demos in "
          f"{OUT.relative_to(ROOT)} · {total / 1e9:.2f} GB")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

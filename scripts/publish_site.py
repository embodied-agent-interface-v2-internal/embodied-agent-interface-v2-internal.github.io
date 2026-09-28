#!/usr/bin/env python3
"""Publish the finished agent runs on the public site in one gated, idempotent run: `make publish`.

Run it once a whole batch has finished, never on a loop: the public repository gets few, meaningful commits (owners,
2026-09-28: "跑完全部再上传"). It needs no one at the keyboard, and it stops at the first failed gate.

    python scripts/publish_site.py [--no-push]

One run, with a gate at every step. Each step is logged with its time; any failure exits non-zero with a one-line
reason as the last line, and nothing is pushed:

  1. import: a full `scripts/import_runs.py` (the importer's lock serialises it with the watchdog's quick cycles);
  2. snapshot: `scripts/publish_runs.py`, finished trials only. Its secret and privacy scan is the first gate: a hit
     stops the run, and the published snapshot stays as it was;
  3. no change in data/published_runs/: stop here, exit 0, no commit;
  4. media: export, compress (at most 4 videos and 8 images at a time) and upload to the Hugging Face dataset. Only
     what is new is converted, and hf upload-large-folder skips what the dataset already has. This happens before the
     push, so no published page names a file that is not there yet;
  5. gates: `make check` and `make public` (the size limit);
  6. commit data/published_runs/ only, naming the counts, then push to origin main as a fast-forward (never forced).

Hidden runs, stopped trials, excluded tasks and pages whose replay is truncated at the source keep their treatment:
the snapshot and the media come from the same rules as a manual `make publish-runs`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv" / "bin" / "python")
SNAP = ROOT / "data" / "published_runs"
LOCK = ROOT / ".cache" / "publish.lock"
LOGFILE = ROOT / ".cache" / "publish.log"          # every run appends here as well as to stdout
HF = os.environ.get("HF") or shutil.which("hf") or "hf"
REPO = os.environ.get("RUN_MEDIA_REPO", "eai-v2-internal/agent-runs")
TRAILER = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


class Stop(Exception):
    """A gate that failed: its message is the one-line reason."""


def say(line: str) -> None:
    print(line, flush=True)
    with LOGFILE.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def log(msg: str) -> None:
    say(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}")


def run(cmd: list[str], why: str, quiet: bool = False, env: dict | None = None) -> str:
    """Run cmd in the repository; on failure stop with `why` and the command's last line."""
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env={**os.environ, **(env or {})})
    out = (r.stdout + r.stderr).strip()
    if not quiet and out:
        for line in out.splitlines()[-6:]:
            say("    " + line)
    if r.returncode != 0:
        last = next((l for l in reversed(out.splitlines()) if l.strip()), "")
        raise Stop(f"{why}: {last[:200]}")
    return out


def counts() -> dict[str, int]:
    """benchmark -> published trial logs."""
    out = {}
    for f in SNAP.glob("*/*/*/*.json"):
        out[f.parts[-4]] = out.get(f.parts[-4], 0) + 1
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-push", action="store_true", help="stop after the commit")
    a = ap.parse_args()
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    lock = open(LOCK, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log("another publish is running; nothing to do")
        return 0
    try:
        before = counts()
        branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], "git", quiet=True)
        if branch != "main":
            raise Stop(f"not on main (on {branch})")
        if run(["git", "status", "--porcelain", "--", "data/published_runs"], "git", quiet=True):
            raise Stop("data/published_runs has uncommitted changes from elsewhere: commit or restore them first")

        log("1/6 import: every registered run, from every machine")
        run([PY, "scripts/import_runs.py"], "import failed")

        log("2/6 snapshot: finished trials, filtered and scanned")
        run([PY, "scripts/publish_runs.py"], "snapshot stopped (the secret and privacy scan, or an error)")
        if not run(["git", "status", "--porcelain", "--", "data/published_runs"], "git", quiet=True):
            log("3/6 no change in the published runs: nothing to publish")
            return 0
        after = counts()
        log("3/6 changed: " + ", ".join(f"{b} {before.get(b, 0)}->{n}" for b, n in sorted(after.items())
                                          if before.get(b, 0) != n) or "3/6 changed (records only)")

        log("4/6 media: export, compress, upload what is new")
        run([PY, "scripts/export_run_media.py"], "media export failed")
        run([PY, "scripts/compress_run_media.py", "--jobs", "4", "--image-jobs", "8"], "media compression failed")
        shutil.copyfile(ROOT / "data" / "run-media-card.md", ROOT / ".cache" / "run-media-hf" / "README.md")
        run([HF, "upload-large-folder", REPO, str(ROOT / ".cache" / "run-media-hf"), "--repo-type", "dataset",
             "--include", "*/**", "README.md", "manifest.json", "--num-workers", "4", "--no-bars", "--no-report"],
            "media upload failed")

        log("5/6 gates: make check, make public")
        run(["make", "check"], "make check failed")
        run(["make", "public"], "make public failed (links or the size limit)")
        run(["make", "check"], "make check failed")         # leaves site/ as a local build, as it was

        log("6/6 commit and push")
        total = sum(after.values())
        delta = total - sum(before.values())
        detail = ", ".join(f"{b} {n}" for b, n in sorted(after.items()))
        msg = (f"Publish runs: {total} trial logs ({delta:+d})\n\n{detail}.\nWritten by make publish "
               f"(scripts/publish_site.py) at {dt.datetime.now():%Y-%m-%d %H:%M}.\n\n{TRAILER}\n")
        run(["git", "add", "--", "data/published_runs"], "git add failed", quiet=True)
        run(["git", "commit", "-q", "-m", msg, "--", "data/published_runs"], "commit failed")
        if a.no_push:
            log("committed; not pushed (--no-push)")
            return 0
        run(["git", "fetch", "-q", "origin", "main"], "fetch failed", quiet=True)
        ahead = run(["git", "rev-list", "--count", "HEAD..origin/main"], "git", quiet=True)
        if ahead.strip() != "0":
            raise Stop(f"origin/main has {ahead.strip()} commit(s) this checkout lacks: pull them first (committed, not pushed)")
        run(["git", "push", "origin", "main"], "push failed (committed, not pushed)")
        log(f"published: {total} trial logs ({delta:+d}); pushed {run(['git', 'rev-parse', '--short', 'HEAD'], 'git', quiet=True)}")
        return 0
    except Stop as exc:
        log(f"STOPPED: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

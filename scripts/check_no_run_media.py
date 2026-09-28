#!/usr/bin/env python3
"""Fail when the repository tracks agent-run media, or run data that must stay local (CI and `make check`).

Run media (replays, the images the model saw) live on the Hugging Face dataset, never in this repository: the site
would outgrow GitHub Pages and the history would keep every copy. Only the published text snapshot is committed
(data/published_runs/*.json). Tracked files that fail:

  * anything under docs/assets/<benchmark>/runs/ (the local log pages' data) or data/runs/ (the local collection);
  * anything under data/published_runs/ that is not JSON;
  * a video (.mp4, .webm, .mov) anywhere but docs/assets/<benchmark>/demos/ (the oracle demos);
  * a file over 50 MB.

Checks what git tracks (`git ls-files`, the index included), so `git add -f` cannot slip past .gitignore.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIMIT = 50 * 1024 * 1024
VIDEO = (".mp4", ".webm", ".mov", ".mkv", ".avi")


def main() -> int:
    files = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, text=True,
                           check=True).stdout.split("\0")
    bad = []
    for f in filter(None, files):
        parts = f.split("/")
        if len(parts) > 3 and parts[:2] == ["docs", "assets"] and parts[3] == "runs":
            bad.append((f, "local log-page data (docs/assets/<benchmark>/runs/)"))
        elif f.startswith("data/runs/"):
            bad.append((f, "local run data (data/runs/)"))
        elif f.startswith("data/published_runs/") and not f.endswith(".json"):
            bad.append((f, "not JSON in the published snapshot: media go to the Hugging Face dataset"))
        elif f.lower().endswith(VIDEO) and not (len(parts) == 5 and parts[:2] == ["docs", "assets"] and parts[3] == "demos"):
            bad.append((f, "a video outside docs/assets/<benchmark>/demos/"))
        else:
            p = ROOT / f
            if p.is_file() and p.stat().st_size > LIMIT:
                bad.append((f, f"{p.stat().st_size / 2**20:.0f} MB, over {LIMIT // 2**20} MB"))
    for f, why in bad[:50]:
        print(f"  tracked: {f}: {why}")
    if bad:
        print(f"{len(bad)} file(s) must not be in this repository; run media go to the Hugging Face dataset "
              "(make upload-run-media), local run data stays local.")
        return 1
    print(f"no run media tracked ({len([f for f in files if f])} files checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

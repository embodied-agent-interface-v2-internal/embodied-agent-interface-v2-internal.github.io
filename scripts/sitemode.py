"""Which build this is: a local one (the default) or the public site (RB_PUBLIC=1, set by the deploy workflow).

The public site, https://embodied-agent-interface-v2-internal.github.io/, is read-only and carries only what is
committed. It differs from a local build in these ways (its settings: data/public.yml):

  * no edit controls: no Edit button on the task list (and no probe for the local edit daemon), no taxonomy editor,
    no "edit this page" link;
  * agent runs come from the committed snapshot, data/published_runs/ (`make publish-runs` writes it from the local
    data, filtered: no machines, no paths, no secrets), never from the local data/runs/ and docs/assets/*/runs/;
    their replays and images load from `run_media_base` (empty: "media not yet published");
  * machine names in the run notes of state/runs/ are hidden (scrub_hosts);
  * the benchmarks in `link_demos` show their demos as a link to the video upstream publishes instead of our copy,
    which keeps the site within GitHub Pages' 1 GB. Their MP4s stay in the repository and in every local build.

Preview the public site locally with: make public
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "public.yml"


def _flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() not in ("", "0", "false", "no")


def _config() -> dict:
    try:
        data = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


PUBLIC = _flag("RB_PUBLIC")
_CFG = _config()
# RB_PUBLIC_LINK_DEMOS=<benchmark>[,...] overrides data/public.yml for one build.
_LINK = os.environ.get("RB_PUBLIC_LINK_DEMOS")
LINK_DEMOS = frozenset(
    (b.strip() for b in _LINK.split(",") if b.strip()) if _LINK is not None
    else (str(b) for b in (_CFG.get("link_demos") or []))) if PUBLIC else frozenset()
RUN_MEDIA_BASE = str(_CFG.get("run_media_base") or "")


def links_demos(benchmark: str) -> bool:
    """Whether this build shows the benchmark's demos as links to upstream instead of playing our copies."""
    return benchmark in LINK_DEMOS


# The machines our runs ran on, as the notes in state/runs/ name them. Seen in a local build; the public site says
# "one of our machines" instead (owner, 2026-09-28: "备注的机器可以hide，这个是我们本地部署时候看到的").
_HOSTS = r"(?:ws3|ws|lab|laptop)"
_SCRUB = [
    (re.compile(rf"\bthe {_HOSTS} GPU\b"), "a GPU of ours"),
    (re.compile(rf"\b(on|to|from|in) (?:the )?{_HOSTS}(?:'s)?(?![\w-])"), r"\1 one of our machines"),
    (re.compile(rf"(?<![\w./-])(?:the )?{_HOSTS}(?![\w-])"), "one of our machines"),
]


def hide_hosts(text: str) -> str:
    """The text with the machines it names replaced by "one of our machines"."""
    if not isinstance(text, str) or not text:
        return text
    for rx, sub in _SCRUB:
        text = rx.sub(sub, text)
    return text


def scrub_hosts(text: str) -> str:
    """A run note as this build shows it: machine names hidden on the public site, kept in a local build."""
    return hide_hosts(text) if PUBLIC else text

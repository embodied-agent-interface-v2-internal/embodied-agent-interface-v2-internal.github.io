"""Read/write helpers for task pages.

A task page is a Markdown file with YAML frontmatter. The frontmatter is split
into zones that are governed differently:

  upstream:  mirrored from the benchmark's own published metadata (a gallery,
             a registry, the task source). Owned by scripts/import_*_tasks.py.
  verified:  facts read first-hand from the distribution we actually run — the
             goal definition, the dataset's own statistics, what a task costs
             to execute. Owned by scripts/import_*_verified.py.
  curated:   everything else. Owned by human collaborators. Never touched by
             any script.

Keeping the zones apart is what makes an importer safe to re-run: it rewrites
one nested key and leaves prose, judgement calls and the other zone alone.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

import yaml

FM_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.S)

# Curated state moved to state/ (see scripts/statedb.py). Frontmatter now
# carries only identity and the machine-owned mirrors, so these files change
# only when their source does.
CURATED_ORDER: list[str] = []

# Machine-owned blocks, in the order they appear on the page. Each is rendered
# key by key (not as one YAML dump) so short lists stay on one line and a
# re-sync produces a readable diff.
ZONES: dict[str, str] = {
    "upstream": "# --- upstream: mirrored from the benchmark's own published metadata by"
                " scripts/import_<benchmark>_tasks.py. Do not hand-edit. ---",
    "verified": "# --- verified: read first-hand from the stack we run, by"
                " scripts/import_<benchmark>_verified.py. Do not hand-edit. ---",
}


def read_page(path: Path) -> tuple[dict, str]:
    """Return (frontmatter, body). Missing frontmatter yields ({}, full text)."""
    text = path.read_text(encoding="utf-8")
    m = FM_RE.match(text)
    if not m:
        return {}, text
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, text[m.end():]


def _strip_doc_end(text: str) -> str:
    """Drop the trailing `...` document-end marker PyYAML adds for bare scalars.

    Must be line-wise: `rstrip("...")` would also eat a sentence's final period.
    """
    lines = text.rstrip("\n").split("\n")
    if lines and lines[-1].strip() == "...":
        lines.pop()
    return "\n".join(lines).strip()


def _dump_value(value) -> str:
    """Dump a single YAML value inline where it is short, block otherwise."""
    if isinstance(value, list) and not value:
        return "[]"
    if isinstance(value, dict) and not value:
        return "{}"
    if value is None or isinstance(value, (str, int, float, bool)):
        return _strip_doc_end(
            yaml.safe_dump(value, default_flow_style=True, allow_unicode=True, width=10**6)
        )
    if isinstance(value, list) and all(isinstance(v, (str, int, float)) and not isinstance(v, bool) for v in value):
        rendered = _strip_doc_end(
            yaml.safe_dump(value, default_flow_style=True, allow_unicode=True, width=10**6)
        )
        if len(rendered) <= 88:
            return rendered
    buf = io.StringIO()
    yaml.safe_dump(value, buf, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return "\n" + _indent(buf.getvalue().rstrip("\n"), 2)


def _sep(value) -> str:
    """No space before a value that starts its own indented block."""
    return "" if _dump_value(value).startswith("\n") else " "


def _indent(text: str, n: int) -> str:
    pad = " " * n
    return "\n".join(pad + line if line.strip() else line for line in text.split("\n"))


def render_frontmatter(meta: dict) -> str:
    """Emit frontmatter with stable ordering and the zone comments intact."""
    lines = ["---"]
    for key in ("title", "task_id", "benchmark"):
        if key in meta:
            lines.append(f"{key}:{_sep(meta[key])}{_dump_value(meta[key])}")

    for zone, comment in ZONES.items():
        block = meta.get(zone)
        if block is None and zone != "upstream":
            continue
        lines.append("")
        lines.append(comment)
        lines.append(f"{zone}:")
        for key, value in (block or {}).items():
            lines.append(_indent(f"{key}:{_sep(value)}{_dump_value(value)}", 2))

    for key in CURATED_ORDER:
        if key in meta:
            lines.append(f"{key}:{_sep(meta[key])}{_dump_value(meta[key])}")
    for key in meta:
        if key not in CURATED_ORDER and key not in ("title", "task_id", "benchmark", *ZONES):
            lines.append(f"{key}:{_sep(meta[key])}{_dump_value(meta[key])}")

    lines.append("---")
    return "\n".join(lines) + "\n"


def write_page(path: Path, meta: dict, body: str) -> None:
    body = body if body.startswith("\n") else "\n" + body
    path.write_text(render_frontmatter(meta) + body, encoding="utf-8")

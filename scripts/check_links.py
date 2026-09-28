#!/usr/bin/env python3
"""Resolve every internal link in the built site against the filesystem.

`mkdocs build --strict` validates links written in Markdown. It does not see
links emitted as raw HTML by our hooks — those ship verbatim. That gap let a
`href=".../index.md"` reach the site and 404, so this closes it.

Run after a build: python scripts/check_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urldefrag

SITE = Path(__file__).resolve().parent.parent / "site"
HREF = re.compile(r'(?:href|src)=(?:"([^"]+)"|\'([^\']+)\'|([^\s>]+))')

# 404.html is rendered with absolute site_url paths on purpose; it only
# resolves once deployed at that base path.
SKIP_PAGES = {"404.html"}
SKIP_PREFIXES = ("http://", "https://", "//", "#", "data:", "mailto:", "javascript:")


def main() -> int:
    if not SITE.is_dir():
        print("no site/ — run `make build` first", file=sys.stderr)
        return 1

    pages = [p for p in SITE.rglob("*.html")
             if p.relative_to(SITE).as_posix() not in SKIP_PAGES]
    broken: list[tuple[str, str]] = []
    checked = 0

    for page in pages:
        html = page.read_text(encoding="utf-8", errors="replace")
        for m in HREF.finditer(html):
            raw = m.group(1) or m.group(2) or m.group(3) or ""
            if not raw or raw.startswith(SKIP_PREFIXES):
                continue
            target, _ = urldefrag(unquote(raw.split("?")[0]))
            if not target:
                continue
            checked += 1
            dest = (page.parent / target).resolve()
            if not (dest.exists() or (dest / "index.html").exists()):
                broken.append((page.relative_to(SITE).as_posix(), raw))

    print(f"checked {checked} internal links across {len(pages)} pages")
    if broken:
        seen: set[str] = set()
        print(f"\n{len(broken)} broken link(s):")
        for src, href in broken:
            if href in seen:
                continue
            seen.add(href)
            print(f"  ERROR  {href}\n         e.g. on {src}")
        # A raw-HTML link ending in .md is always this bug, so name it.
        if any(h.endswith(".md") for _, h in broken):
            print("\n  A link ending in .md means raw HTML bypassed MkDocs' rewriting.")
            print("  Emit a finished URL instead — see doc_url() in scripts/hooks.py.")
        return 1

    print("all internal links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

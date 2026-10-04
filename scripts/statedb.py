"""Read and write everything a human edits.

All mutable curation lives under `state/` — the taxonomies and one file of
per-task records per benchmark. Task pages keep only upstream metadata and
prose, so a day of triage shows up as a diff of one file instead of a hundred.

Writes are whole-file and atomic (temp file + replace), sorted by key, so two
sessions editing different tasks produce a clean, reviewable diff.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
TASK_STATE = STATE / "tasks"
TAXONOMY = STATE / "taxonomy.yml"
DISPLAY_TAGS = STATE / "display_tags.yml"

# Fields a human owns. Anything else in a record is preserved untouched.
DEFAULTS = {
    "status": "pending",
    "difficulty": "unrated",
    "labels": [],
    "display_tags": [],
    "owner": "",
    "note": "",
    "excluded": "",
}

HEADER = """\
# Curated task state for {benchmark}.
#
# One block per task. Written by the site's Edit button and by hand; both are
# fine. Task ids match docs/benchmarks/{benchmark}/tasks/<id>.md.
#
#   status      keep | drop | needs-review | pending
#   difficulty  unrated | easy | medium | hard | extreme
#   labels      tier-2 ids from state/taxonomy.yml
#   display_tags  what the site shows: tag ids from state/display_tags.yml
#   owner       bare GitHub handle
#   note        free text; why you decided what you decided

"""


def _atomic_write(path: Path, text: str) -> None:
    """Write via a temp file in the same directory, then replace.

    A half-written state file would lose everyone's triage, and the editor
    writes on every save.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".yml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def state_path(benchmark: str) -> Path:
    return TASK_STATE / f"{benchmark}.yml"


def load_tasks(benchmark: str) -> dict[str, dict]:
    path = state_path(benchmark)
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def _own_comments(path: Path, header: str) -> str:
    """The comment lines a person added right under the file's header (a date, a quote, why a field is set).

    The records are rewritten from YAML on every save, which keeps no comment; these few lines are carried over, so
    the Edit button never erases them. Comments between records are still lost: keep notes under the header."""
    if not path.is_file():
        return ""
    head = header.rstrip("\n") + "\n"
    text = path.read_text(encoding="utf-8")
    if not text.startswith(head):
        return ""
    kept = []
    for line in text[len(head):].splitlines():
        if not line.startswith("#"):
            break
        kept.append(line + "\n")
    return "".join(kept)


def save_tasks(benchmark: str, records: dict[str, dict]) -> None:
    clean: dict[str, dict] = {}
    for task_id in sorted(records):
        rec = dict(records[task_id] or {})
        # Drop values equal to the default so the file stays about decisions.
        for key, default in DEFAULTS.items():
            if key in rec and rec[key] == default:
                del rec[key]
        if rec:
            clean[task_id] = rec
    body = yaml.safe_dump(clean, sort_keys=True, allow_unicode=True, default_flow_style=False)
    header = HEADER.format(benchmark=benchmark)
    own = _own_comments(state_path(benchmark), header)
    _atomic_write(state_path(benchmark), (header.rstrip("\n") + "\n" + own + "\n" if own else header) + body)


def get(benchmark: str, task_id: str) -> dict:
    rec = dict(DEFAULTS)
    rec.update(load_tasks(benchmark).get(task_id) or {})
    return rec


def update(benchmark: str, task_id: str, patch: dict) -> dict:
    records = load_tasks(benchmark)
    rec = dict(records.get(task_id) or {})
    rec.update(patch)
    records[task_id] = rec
    save_tasks(benchmark, records)
    return get(benchmark, task_id)


def load_taxonomy() -> dict:
    return yaml.safe_load(TAXONOMY.read_text(encoding="utf-8")) or {}


def load_display_tags() -> dict:
    return yaml.safe_load(DISPLAY_TAGS.read_text(encoding="utf-8")) or {}


def save_display_tags(doc: dict) -> None:
    """Rewrite the display tags (the Labels page's editor; state/taxonomy.yml is edited by hand).

    PyYAML drops the file's comments. Accepted deliberately: the alternative is
    refusing to let anyone edit the vocabulary from the page that shows it.
    """
    header = (
        "# Display tags — what the site shows on every task, in two groups.\n"
        "#\n"
        "#   capabilities      tier 1: a group — Capability (shown first), then Task Domain\n"
        "#     subcapabilities tier 2: a tag; a task lists its id under `display_tags:`\n"
        "#\n"
        "# A tagged task carries at least one tag from each group, and each group has its\n"
        "# own colour (`.chip--<group id>` in docs/stylesheets/extra.css). Tags with\n"
        "# `from_skills` roll up BEHAVIOR's official 31-primitive skill vocabulary, so\n"
        "# the editor can suggest them.\n"
        "#\n"
        "# The detailed labels (`labels:`, state/taxonomy.yml) are kept as they are and\n"
        "# not shown as chips; scripts/migrate_tag_groups.py derived the first display\n"
        "# tags from them.\n"
        "#\n"
        "# Rewritten by the Labels page; comments beyond this header are lost.\n\n"
    )
    body = yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, default_flow_style=False)
    _atomic_write(DISPLAY_TAGS, header + body)

"""Generates every index page at build time.

Nothing here is committed. That is the point: the gallery, the triage board and
the coverage matrix are the files a hundred collaborators would otherwise all
edit at once. Deriving them from per-task frontmatter means a contributor only
ever touches the one task file they own, and the shared views can never drift
out of sync with the data.

Run indirectly by `mkdocs build` via the mkdocs-gen-files plugin.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mkdocs_gen_files  # noqa: E402

import runpages  # noqa: E402
import runsdb  # noqa: E402
import sitemode  # noqa: E402
import taskdb  # noqa: E402

EDIT_BASE = "benchmarks"


def write(path: str, text: str) -> None:
    with mkdocs_gen_files.open(path, "w") as fh:
        fh.write(text)


# --------------------------------------------------------------------- capability reference


def gen_capability_reference() -> None:
    tax = taskdb.taxonomy()
    caps = taskdb.capability_index()

    usage: dict[str, list[taskdb.Task]] = {cid: [] for cid in caps}
    for bench in taskdb.benchmarks().values():
        for task in bench.tasks:
            for cid in task.capabilities:
                usage.setdefault(cid, []).append(task)

    out = [
        "---",
        "title: Label taxonomy",
        "---",
        "",
        "# Label taxonomy",
        "",
        "The shared vocabulary for the `labels:` field in `state/tasks/<benchmark>.yml`,",
        "written to span benchmarks rather than describe one. Each **facet** below is a",
        "question you ask about a task; the **labels** under it are the answers.",
        "",
        "!!! warning \"Where these came from, and how settled they are\"",
        "",
        "    Each benchmark publishes its own idea of capability and they do not agree:",
        "    BEHAVIOR a formal goal language and an object ontology, RoboLab an attribute",
        "    list about how the goal is *worded*, RoboWits a paragraph of prose per task,",
        "    HumanoidBench nothing but a reward function. Those are theirs.",
        "    **The labels below are ours**, fitted to fifteen suites — see the",
        "    [benchmark landscape](benchmark-landscape.md) — under one rule: a label earns",
        "    its place only if knowing it changes what you predict about the task.",
        "",
        "    Where a label can be derived from something a benchmark already publishes,",
        "    `state/taxonomy.yml` records the rule under `derived_from`, so the derivation",
        "    is inspectable and `scripts/suggest_labels.py` can propose labels for a task",
        "    instead of making anyone read the whole list. Labels showing a skill roll-up",
        "    map onto BEHAVIOR's own 31 primitives.",
        "",
        "    Treat this as a **starting point to argue with**, not a settled standard —",
        "    it has not been through a group discussion. Several labels are reached by",
        "    nothing we have today: they are the axes a suite with legs, hands or people",
        "    in it would occupy, and they are here so that adding one does not mean",
        "    rewriting the vocabulary.",
        "",
        "    Edit it in place below (with `make edit`), or in `state/taxonomy.yml`.",
        "",
        f"**{len(caps)} labels across {len(tax['capabilities'])} facets.**",
        "",
        "<!-- gen:taxonomy-editor -->",
        "",
    ]

    for group in tax["capabilities"]:
        ladder = " — *ladder: take the highest rung that applies*" if group.get("graded") else ""
        out += [f"## {group['name']}", "", group.get("description", "") + ladder, ""]
        for cap in group.get("subcapabilities") or []:
            used = usage.get(cap["id"], [])
            out += [
                f"### {cap['name']} {{ #{taskdb.anchor_for(cap['id'])} }}",
                "",
                f"`{cap['id']}`",
                "",
                cap["description"],
                "",
            ]
            if cap.get("flag"):
                out += ["*A flag, not a rung: it can apply at any level of this ladder.*", ""]
            if cap.get("evidence"):
                out += [f"*Why it exists:* {cap['evidence'].strip()}", ""]
            if cap.get("from_skills"):
                out += [
                    "*Rolls up BEHAVIOR skills:* "
                    + ", ".join(f"`{x}`" for x in cap["from_skills"]),
                    "",
                ]
            if used:
                links = ", ".join(
                    f"[{t.title}](../benchmarks/{t.benchmark}/tasks/{t.task_id}.md)"
                    for t in sorted(used, key=lambda t: t.title)
                )
                out += [f"*Tagged on {len(used)} task(s):* {links}", ""]
            else:
                out += ["*Not yet tagged on any task.*", ""]

    write("reference/capabilities.md", "\n".join(out))


# ------------------------------------------------------------------------------- coverage


def gen_coverage(bench: taskdb.Benchmark) -> None:
    caps = taskdb.capability_index()
    tasks = bench.included          # what the suite exercises: its tasks excluded from it (state `excluded:`) are not

    out = [
        "---",
        f"title: {bench.name} capability coverage",
        "---",
        "",
        f"# {bench.name} capability coverage",
        "",
        "What the suite actually exercises. Thin rows are the interesting ones: a",
        "capability tagged on one or two tasks is either genuinely rare or a sign we",
        "have not finished tagging.",
        "",
    ]

    tagged = [t for t in tasks if t.capabilities]
    out += [
        f"**{len(tagged)} of {len(tasks)} tasks tagged.**"
        + (f" The {len(bench.excluded)} tasks excluded from the benchmark are not counted." if bench.excluded else ""),
        "",
    ]
    if len(tagged) < len(tasks):
        out += [
            '!!! warning "Coverage is incomplete"',
            "",
            f"    {len(tasks) - len(tagged)} task(s) carry no capability tags yet, so every",
            "    count below is a lower bound. Treat this page as a progress tracker until",
            "    the triage board shows zero untagged tasks.",
            "",
        ]

    for family in taskdb.taxonomy()["capabilities"]:
        hits1 = [t for t in tasks if family["id"] in t.tier1]
        out += [f"## {family['name']}", "",
                f"*{len(hits1)} task(s) touch this capability.*", "",
                "| Sub-capability | Tasks | Coverage |", "| --- | --- | --- |"]
        for cap in family.get("subcapabilities") or []:
            hits = [t for t in tasks if cap["id"] in t.capabilities]
            bar = "▓" * round(20 * len(hits) / max(len(tasks), 1)) if hits else ""
            out.append(
                f"| [{cap['name']}](../../reference/capabilities.md#{taskdb.anchor_for(cap['id'])}) "
                f"| {len(hits)} | `{bar:<20}` |"
            )
        out.append("")

    # Skill primitives are descriptive, straight from the benchmark's vocabulary.
    vocab = bench.skill_vocabulary
    if vocab:
        out += [
            "## Skill primitives",
            "",
            "The benchmark's own annotation vocabulary, as recorded in `skills:`.",
            "Descriptive rather than normative — see the",
            "[capability reference](../../reference/capabilities.md) for the distinction.",
            "",
            "| Skill | Tasks |",
            "| --- | --- |",
        ]
        for skill in vocab:
            hits = sum(1 for t in tasks if skill in t.skills)
            out.append(f"| `{skill}` | {hits} |")
        out.append("")

    write(f"benchmarks/{bench.id}/coverage.md", "\n".join(out))


# ----------------------------------------------------------------------------------- runs


def gen_runs() -> None:
    """The Runs section (scripts/runpages.py): the overview, one page per registered benchmark, the log pages."""
    write("runs/overview.md", runpages.overview())
    write("runs/index.md", runpages.redirect())
    for bench in taskdb.benchmarks().values():
        write(f"runs/{bench.id}.md", runpages.benchmark_page(bench))
    pages = runpages.log_pages()
    for path, text in pages:
        write(path, text)
    # a renamed run's former log-page addresses redirect to the new ones (`formerly:` in data/agents/<run>.yml)
    for path, html in runpages.redirect_stubs([p for p, _ in pages]):
        write(path, html)
    # a withdrawn mode's log pages (`withdrawn:` in state/runs/): their addresses lead to the task's page
    for path, html in runpages.withdrawn_stubs([p for p, _ in pages]):
        write(path, html)
    if sitemode.PUBLIC:
        # The log pages' data on the public site: the published snapshot (data/published_runs/<b>/<run>/<task>/
        # <slot>.json, scripts/publish_runs.py), served at runs-data/<b>/<run>/<task>/<slot>/log.json.
        for src in sorted(runsdb.PUBLISHED.glob("*/*/*/*.json")):
            bench, run, task = src.parts[-4:-1]
            write(f"runs-data/{bench}/{run}/{task}/{src.stem}/log.json", src.read_text(encoding="utf-8"))


def main() -> None:
    gen_capability_reference()
    gen_runs()
    for bench in taskdb.benchmarks().values():
        gen_coverage(bench)
        for task in bench.tasks:
            mkdocs_gen_files.set_edit_path(
                f"benchmarks/{bench.id}/tasks/{task.task_id}.md", task.src_uri
            )


main()

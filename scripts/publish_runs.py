#!/usr/bin/env python3
"""Write the committed, filtered snapshot of the agent runs that the public site shows: data/published_runs/.

    python scripts/publish_runs.py            (make publish-runs; by hand, then review and commit it)
    python scripts/publish_runs.py --benchmark ID ...
                                              (make publish-runs BENCHMARK=<id>) only these benchmarks' part; the
                                              others stay as they are, even where their local data has moved on
    python scripts/publish_runs.py --scan     only scan the snapshot that is there

It reads the local data scripts/import_runs.py collects, for every registered run that is not hidden:
data/runs/<benchmark>/<run>.json and the log pages' data, docs/assets/<benchmark>/runs/<run>/<task>/<slot>/log.json.
It writes:

    data/published_runs/<benchmark>/<run>.json                  the trials: state, grade, metrics, progress, agent
                                                                time, requests, tokens, cost; no machine, job or
                                                                log check
    data/published_runs/<benchmark>/<run>/<task>/<slot>.json    one trial's log: the model's words, its tool calls and
                                                                their output, robot calls, token counts; its replay
                                                                and images by name only (they are hosted apart:
                                                                make export-run-media, data/public.yml)
    data/published_runs/SNAPSHOT.json                           when, what, and the result of the secret scan

What it strips, everywhere: the machine (host) and where a trial ran (the job directory, the host path, the key-scan
count and the log checks); user names in paths (/home/<user>, /data/<user>, ...); private IP addresses; anything shaped
like a credential (API keys, tokens, Authorization headers, private keys) and e-mail addresses. Trial ids stay as
they are, so a trial keeps its name between snapshots.

Then it scans everything it wrote for the same patterns. A hit fails the run (exit 1) and the new snapshot is not
switched in. The previous snapshot is moved to .cache/published_runs.prev/ (local, gitignored), never deleted.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import runsdb  # noqa: E402
import sitemode  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "published_runs"
PREV = ROOT / ".cache" / "published_runs.prev"
LOGS = ROOT / "docs" / "assets"

# What a trial record keeps (anything else, such as host, job, logs and scan, is dropped).
RECORD_KEYS = {"state", "started", "finished", "agent_wall_s", "calls", "calls_failed", "tokens", "tokens_source",
               "billed_usd", "billed_source", "reward", "progress", "metrics", "exception", "trial", "regraded",
               "followup", "last_call", "rerun", "stale", "supersedes"}
RUN_KEYS = {"v", "benchmark", "run", "label", "batches", "generated_at", "tasks"}
# What a trial's log keeps (host, job, where and scan are dropped).
LOG_KEYS = {"v", "benchmark", "run", "task", "mode", "previous", "state", "started", "finished", "agent_wall_s",
            "exception", "reward", "trial", "built", "start", "span", "totals", "calls", "steps", "robot", "media",
            "snapshots", "gen", "ended", "note"}

TLDS = r"(?:com|org|net|edu|gov|io|ai|cn|de|uk|jp|fr|ch|ca|us|info|dev|me|co|app|kr|sg|hk|tw|in|nl|eu)"
# (pattern, replacement): applied to every string, in this order.
SCRUB = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "<redacted private key>"),
    (re.compile(r"\b(?:sk-(?:or-v1-|proj-|ant-)?[A-Za-z0-9_-]{16,}|(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}"
                r"|github_pat_[A-Za-z0-9_]{20,}|hf_[A-Za-z0-9]{20,}|xox[abprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}"
                r"|(?:AKIA|ASIA)[0-9A-Z]{16})"), "<redacted>"),
    (re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{4,}"), "<redacted>"),
    (re.compile(r"(?i)(authorization[\"']?\s*[:=]\s*[\"']?)(?:bearer\s+|basic\s+|token\s+)?[^\s\"',;]+"), r"\1<redacted>"),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{8,}"), "Bearer <redacted>"),
    # an environment variable or setting that holds a secret: OPENAI_API_KEY=..., "api_key": "..."
    (re.compile(r"\b([A-Z][A-Z0-9_]*(?:API_KEY|ACCESS_KEY|SECRET|TOKEN|PASSWORD|PASSWD)[A-Z0-9_]*)(\s*=\s*)(?!<redacted>)[^\s\"',;]+"),
     r"\1\2<redacted>"),
    (re.compile(r"(?i)([\"'](?:api_?key|access_token|refresh_token|id_token|client_secret|password|secret)[\"']\s*:\s*[\"'])"
                r"(?!<redacted>)[^\"']+"), r"\1<redacted>"),
    # a login's account id (a Codex / ChatGPT auth.json carries one)
    (re.compile(r"(?i)([\"']?(?:chatgpt_)?account_id[\"']?\s*[:=]\s*[\"']?)(?!<redacted>)[A-Za-z0-9_-]{6,}"), r"\1<redacted>"),
    (re.compile(rf"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.{TLDS}\b"), "<email>"),
    # user names in paths, and machines named in host paths
    (re.compile(r"/(home|Users|scratch)/(?!<user>)[A-Za-z0-9._-]+"), r"/\1/<user>"),
    (re.compile(r"/data/qineng\b"), "/data/<user>"),
    (re.compile(r"/DATA\d*/(?!<user>)[A-Za-z0-9._-]+"), "/DATA/<user>"),
    (re.compile(r"(?<![\w.-])(?:ws3|ws|lab|laptop|mll-[a-z0-9-]+):(?=/|~)"), "<host>:"),
    (re.compile(r"\bssh\s+(?:ws3|ws|lab|laptop|mll-[a-z0-9-]+)\b"), "ssh <host>"),
    (re.compile(r"\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"), "<ip>"),
]

# What must not be left anywhere (the scan). A hit names the file and the kind, never the value.
LEFT = {
    "credential": re.compile(r"\b(?:sk-(?:or-v1-|proj-|ant-)?[A-Za-z0-9_-]{16,}|(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}"
                             r"|github_pat_|hf_[A-Za-z0-9]{20,}|xox[abprs]-|AIza[0-9A-Za-z_-]{35}|(?:AKIA|ASIA)[0-9A-Z]{16})"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\."),
    "private key": re.compile(r"BEGIN [A-Z ]*PRIVATE KEY"),
    "auth header": re.compile(r"(?i)(?:authorization[\"']?\s*[:=]\s*[\"']?(?!<redacted>)[^\s\"',;<]{4,}|\bbearer\s+(?!<redacted>)[A-Za-z0-9._~+/=-]{8,})"),
    "secret setting": re.compile(r"\b[A-Z][A-Z0-9_]*(?:API_KEY|ACCESS_KEY|SECRET|TOKEN|PASSWORD)[A-Z0-9_]*\s*=\s*(?!<redacted>)[^\s\"',;]{4,}"),
    "e-mail": re.compile(rf"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.{TLDS}\b"),
    "user path": re.compile(r"/(?:home|Users|scratch)/(?!<user>)[A-Za-z0-9._-]+|/data/qineng|/DATA\d*/(?!<user>)\w"),
    "private ip": re.compile(r"\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b"),
    "machine": re.compile(r"(?<![\w.-])(?:ws3|ws|lab|laptop):/|\bmll-[a-z0-9]+|\bssh\s+(?:ws3|ws|lab|laptop)\b"),
    "login material": re.compile(r"(?i)auth\.json|\.codex/|(?:chatgpt_)?account_id[\"']?\s*[:=]\s*[\"']?(?!<redacted>)[A-Za-z0-9_-]{6,}"
                                 r"|[\"'](?:access_token|refresh_token|id_token)[\"']\s*:\s*[\"'](?!<redacted>)"),
}
DROPPED = {"host", "hosts", "job", "where", "scan", "logs"}      # must be gone from every record and log
FINISHED = {"success", "failed", "error"}                          # the trial states a snapshot publishes


def scrub(x):
    """Every string in x, with the SCRUB patterns applied."""
    if isinstance(x, str):
        for rx, sub in SCRUB:
            x = rx.sub(sub, x)
        return x
    if isinstance(x, list):
        return [scrub(v) for v in x]
    if isinstance(x, dict):
        return {k: scrub(v) for k, v in x.items()}
    return x


def record(rec: dict) -> dict:
    out = {k: v for k, v in rec.items() if k in RECORD_KEYS}
    if isinstance(out.get("supersedes"), dict):
        out["supersedes"] = record(out["supersedes"])
    for k in ("followup", "exception"):          # notes and errors may name the machine ("rerun on the laptop")
        out[k] = sitemode.hide_hosts(out.get(k)) if out.get(k) else out.get(k)
    return scrub({k: v for k, v in out.items() if v is not None or k in rec})


def media_name(name):
    """A media file's name as published: a PNG in the format data/public.yml names (`run_media_images: webp`, as
    scripts/compress_run_media.py writes it); anything else as it is."""
    if isinstance(name, str) and sitemode.RUN_MEDIA_IMAGES == "webp" and name.lower().endswith(".png"):
        return name[:-4] + ".webp"
    return name


def rename_media(log: dict) -> dict:
    media = log.get("media")
    if isinstance(media, dict):
        log["media"] = {k: (media_name(v) if k in ("video", "last") else v) for k, v in media.items()}
    for step in log.get("steps") or []:
        if isinstance(step, dict) and step.get("img"):
            step["img"] = [media_name(x) for x in step["img"]]
    for snap in log.get("snapshots") or []:
        if isinstance(snap, dict) and snap.get("src"):
            snap["src"] = media_name(snap["src"])
    return log


def trial_log(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    out = rename_media({k: v for k, v in data.items() if k in LOG_KEYS})
    for k in ("exception", "note"):              # an error, or a note of where a record was recovered from
        if out.get(k):
            out[k] = sitemode.hide_hosts(out[k])
    if isinstance(out.get("media"), dict) and out["media"].get("problem"):
        out["media"] = {**out["media"], "problem": sitemode.hide_hosts(out["media"]["problem"])}
    return scrub(out)


def dump(path: Path, data) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    path.write_text(text + "\n", encoding="utf-8")
    return len(text) + 1


def scan(root: Path) -> dict[str, list[str]]:
    """kind -> the files (relative) that still contain it: the LEFT patterns in the text, and the DROPPED fields in
    a run's records and in a trial log's top level."""
    hits: dict[str, list[str]] = {}
    for f in sorted(root.rglob("*.json")):
        text = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(root))
        for kind, rx in LEFT.items():
            if rx.search(text):
                hits.setdefault(kind, []).append(rel)
        if f.name == "SNAPSHOT.json":
            continue
        data = json.loads(text)
        if "tasks" in data:          # a run: every record, and the run itself
            recs = [data] + [r for modes in data["tasks"].values() for r in modes.values()]
            recs += [r["supersedes"] for r in recs if isinstance(r.get("supersedes"), dict)]
        else:                        # a trial's log
            recs = [data]
        if any(DROPPED & set(r) for r in recs if isinstance(r, dict)):
            hits.setdefault("machine field", []).append(rel)
    return hits


def build(tmp: Path, only: set[str] | None = None) -> dict:
    runs, n_logs, n_bytes = [], 0, 0
    for br in runsdb.all_runs():            # hidden runs are not listed
        if only and br.benchmark not in only:
            continue
        data = runsdb.collected(br.benchmark, br.run)
        if not data:
            continue
        tasks = {}
        for tid, modes in (data.get("tasks") or {}).items():
            # finished trials only: a trial still queued or running is published once it ends
            done = {m: record(r) for m, r in modes.items() if isinstance(r, dict) and r.get("state") in FINISHED}
            if done:
                tasks[tid] = done
        run = {k: v for k, v in data.items() if k in RUN_KEYS}
        run["tasks"] = tasks
        n_bytes += dump(tmp / br.benchmark / f"{br.run}.json", scrub(run))
        logs = 0
        base = LOGS / br.benchmark / "runs" / br.run
        for tid, modes in tasks.items():
            for mode in modes:
                for slot in (mode, mode + "-prev"):
                    src = base / tid / slot / "log.json"
                    if src.is_file():
                        n_bytes += dump(tmp / br.benchmark / br.run / tid / f"{slot}.json", trial_log(src))
                        logs += 1
        n_logs += logs
        runs.append({"benchmark": br.benchmark, "run": br.run, "tasks": len(tasks), "logs": logs,
                     "collected_at": data.get("generated_at")})
    return {"runs": runs, "logs": n_logs, "bytes": n_bytes}


def keep_others(tmp: Path, only: set[str], info: dict) -> None:
    """The benchmarks not in `only`: their part of the current snapshot, as it is, and their lines in SNAPSHOT.json."""
    old = json.loads((OUT / "SNAPSHOT.json").read_text(encoding="utf-8")) if (OUT / "SNAPSHOT.json").is_file() else {}
    for d in sorted(OUT.iterdir()) if OUT.is_dir() else []:
        if d.is_dir() and d.name not in only:
            shutil.copytree(d, tmp / d.name)
            info["bytes"] += sum(len(f.read_text(encoding="utf-8")) for f in (tmp / d.name).rglob("*.json"))
    kept = [r for r in old.get("runs") or [] if r.get("benchmark") not in only]
    order = {(br.benchmark, br.run): n for n, br in enumerate(runsdb.all_runs())}
    info["runs"] = sorted(info["runs"] + kept, key=lambda r: order.get((r["benchmark"], r["run"]), len(order)))
    info["logs"] = sum(r.get("logs") or 0 for r in info["runs"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scan", action="store_true", help="only scan the snapshot that is there")
    ap.add_argument("--benchmark", action="append", help="only this benchmark's part (repeatable); the others stay")
    args = ap.parse_args()
    if args.scan:
        hits = scan(OUT)
        for kind, files in hits.items():
            print(f"  LEFT {kind}: {len(files)} file(s), e.g. {files[0]}")
        print("scan: clean" if not hits else "scan: NOT clean")
        return 1 if hits else 0

    tmp = ROOT / ".cache" / "published_runs.new"
    if tmp.exists():
        shutil.rmtree(tmp)        # our own half-written output from an interrupted run
    tmp.mkdir(parents=True)
    only = set(args.benchmark or ())
    info = build(tmp, only)
    if only:
        keep_others(tmp, only, info)
    hits = scan(tmp)
    info.update({"published_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                 "scan": {"clean": not hits, "patterns": sorted(LEFT), "hits": {k: len(v) for k, v in hits.items()}}})
    dump(tmp / "SNAPSHOT.json", info)
    for r in info["runs"]:
        print(f"  {r['benchmark']:<12} {r['run']}: {r['tasks']} tasks, {r['logs']} trial logs")
    print(f"{info['logs']} trial logs, {info['bytes'] / 1048576:.1f} MiB")
    if hits:
        for kind, files in hits.items():
            print(f"  LEFT {kind}: {len(files)} file(s), e.g. {files[0]}")
        print(f"scan: NOT clean; the new snapshot stays in {tmp.relative_to(ROOT)} and {OUT.relative_to(ROOT)} is unchanged")
        return 1
    print("scan: clean (" + ", ".join(sorted(LEFT)) + ")")
    if OUT.exists():
        if PREV.exists():
            shutil.rmtree(PREV)   # the snapshot before the previous one: one old copy is kept
        PREV.parent.mkdir(parents=True, exist_ok=True)
        OUT.rename(PREV)
    tmp.rename(OUT)
    print(f"written: {OUT.relative_to(ROOT)} (the one before: {PREV.relative_to(ROOT)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

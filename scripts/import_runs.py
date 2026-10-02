"""Collect the state of every registered agent run into data/runs/<benchmark>/<run>.json.

    python scripts/import_runs.py [--hosts FILE] [--benchmark ID ...] [--run ID ...] [--watch SECONDS | --once] [--no-sync]

What to collect is the run registry (scripts/runsdb.py): each benchmark's `state/runs/<benchmark>.yml` names, per run,
the Harbor batches of robot_coding_bench that hold its jobs. Where to look is local: every `data/runs/hosts*.local.yml`
(gitignored, one per person if several share a checkout) maps a machine to where it keeps its Harbor jobs:

    local:  {jobs: ../robot_coding_bench/jobs/agents}
    gpu1:   {ssh: gpu1, jobs: /data/<you>/rcb_jobs/agents}
    gpu2:   {ssh: gpu2, jobs: /scratch/<you>/rcb_jobs/agents, benchmarks: [behavior-1k]}   # optional filters: benchmarks, runs

Every host runs the same read-only probe (PROBE below), locally or through `ssh <alias> python3 -`. The probe reads:
- `result.json` and `verifier/reward.json`;
- the model gateway's per-request records, counted incrementally from a byte offset cached in
  ~/.cache/rcb_runs_probe.json on that host: tokens, and the charge OpenRouter reports in each response;
- sizes of the agent's logs and of their append-only mirror (`<jobs>_mirror/`);
- the key-scan lines of the batch log;
- whether the job's harbor process is still alive.
Both of the runner's layouts are understood: one Harbor job per task and mode (<batch>-<mode>-<task dir>/) and one job
per mode with a trial per task (<batch>-<mode>/, the trial's task read from its config.json).

It never opens a credential. A host that does not answer keeps its previous records and is marked stale. A benchmark's
run is written only once one of its batches has left a trace (its log or a job) on a host that answered, so a
colleague's run whose machines this one cannot see is not shown as all queued. Every output is rewritten only when it
changes, so a running `make serve` / `make edit` rebuilds only then.

Each time it writes a run, it also refreshes the log pages' data (scripts/runlog.py) of every trial of it whose state
or records changed: `docs/assets/<benchmark>/runs/<run>/<task>/<mode>/`. A page is rebuilt when its state, trial, gateway
log, replay video or robot call log changes (the files' size and mtime: a --no-sync cycle may build a page from a replay
that was still being written when it was last copied), or when its entry in the run's local-only
`data/runs/<benchmark>/<run>.backfill.yml` changes (`<task>/<slot>: {note, episode, video, video_problem}`, see
runlog.py); a trial whose replay was rendered again later (`video`) has it counted in its log checks.
A remote host's records are first copied with rsync into .cache/runs_remote/<host>/ (gateway log, robot call log,
graded replay).

`data/runs/status.json` keeps the shape it had before runs were per benchmark (one sweep): every benchmark's DEFAULT
run, for scripts that poll it (the sweep watchdog reads benchmarks.<b>.tasks.<t>.<mode>.state and hosts.<h>.ok).

Owns data/runs/<benchmark>/, data/runs/status.json, .cache/runs_remote/, .cache/runs_logs/ and docs/assets/*/runs/.
All of them are local and gitignored.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import runsdb  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HOSTS_DIR = ROOT / "data" / "runs"
OUT = ROOT / "data" / "runs" / "status.json"   # the default runs, in the pre-2026-09-28 shape (watchdog)
REMOTE = ROOT / ".cache" / "runs_remote"   # not under data/ (watched by `mkdocs serve`: an rsync there rebuilt the site non-stop)
LOGS_CACHE = ROOT / ".cache" / "runs_logs"  # <benchmark>/<run>.json: which log pages are up to date
LOCK = ROOT / ".cache" / "import_runs.lock"
# The files a log page is built from (scripts/runlog.py), as rsync include patterns.
LOG_FILES = ["agent/gateway.jsonl", "agent/sessions/**", "artifacts/data/episode.jsonl", "artifacts/out/episode.jsonl", "verifier/replay.mp4",
             "verifier/replay.last.png", "verifier_regrade/replay.mp4", "verifier_regrade/replay.last.png"]
# What a later batch's record keeps of the one it replaces.
SUPERSEDED = ("job", "state", "host", "trial", "reward", "progress", "exception", "started", "finished", "agent_wall_s", "scan")

PROBE = r'''
import glob, json, os, re, sys, time
jobs, spec = sys.argv[1], json.loads(sys.argv[2])
batches, modes, progress = spec["batches"], spec["modes"], spec.get("progress") or {}
declared = spec.get("metrics") or {}   # batch -> the reward.json keys its benchmark shows (state/runs/<b>.yml `metrics:`)
CACHE = os.path.expanduser("~/.cache/rcb_runs_probe.json")
try:
    cache = json.load(open(CACHE))
except Exception:
    cache = {}
live = set()
for p in glob.glob("/proc/[0-9]*/cmdline"):
    try:
        a = open(p, "rb").read().split(b"\0")
    except OSError:
        continue
    if b"--job-name" in a and any(b"harbor" in x for x in a[:3]):
        live.add(a[a.index(b"--job-name") + 1].decode("utf-8", "replace"))

def size(p):  # None = absent (an empty file, e.g. a grader's stderr log, is 0)
    try:
        return os.path.getsize(p)
    except OSError:
        return None

def load(p):
    try:
        return json.load(open(p))
    except Exception:
        return None

def mp4_ok(p):  # None = absent; False = no index (moov) or boxes that overrun the file: a render cut off mid-write
    try:
        size = os.path.getsize(p)
        with open(p, "rb") as f:
            off, moov = 0, False
            while off + 8 <= size:
                f.seek(off); h = f.read(16)
                n, kind = int.from_bytes(h[:4], "big"), h[4:8]
                if n == 1:
                    n = int.from_bytes(h[8:16], "big")
                elif n == 0:
                    n = size - off
                if n < 8:
                    return False
                moov = moov or kind == b"moov"
                off += n
            return moov and off == size
    except OSError:
        return None

# Token use per request: the final usage block of the Responses API stream (response.completed). input_tokens includes
# the cached ones, output_tokens the reasoning ones. OpenRouter adds what it charged for the request (cost, USD).
USAGE = re.compile(r'"input_tokens":(\d+),"input_tokens_details":\{[^}]*?"cached_tokens":(\d+)[^}]*\},'
                   r'"output_tokens":(\d+),"output_tokens_details":\{[^}]*?"reasoning_tokens":(\d+)'
                   r'(?:[^}]*\},"total_tokens":\d+,"cost":([0-9.eE+-]+))?')

def gateway(p):
    try:
        st = os.stat(p)
    except OSError:
        return None
    c = cache.get(p)
    # The entry stays format v2, which the probe before 2026-09-28 also reads (it rescans anything else). The charge
    # keys are extra: `cost_off` is where charge counting stands, None when an older probe counted part of the file.
    if not c or c.get("off", 0) > st.st_size or c.get("v") != 2:
        c = {"v": 2, "off": 0, "posts": 0, "ok": 0, "bad": 0, "last": None, "tin": 0, "tcached": 0, "tout": 0, "treason": 0,
             "cost": 0.0, "ncost": 0, "cost_off": 0}
    if c.get("cost_off", -1) != c["off"]:
        c["cost_off"], c["cost"], c["ncost"] = None, 0.0, 0
    if st.st_size > c["off"]:
        with open(p, "rb") as f:
            f.seek(c["off"])
            data = f.read()
        end = data.rfind(b"\n") + 1
        for line in data[:end].splitlines():
            try:
                x = json.loads(line)
            except ValueError:
                continue
            if x.get("method") != "POST":
                continue
            c["posts"] += 1
            c["ok" if x.get("status") == 200 else "bad"] += 1
            c["last"] = x.get("t") or c["last"]
            s = x.get("response")
            if x.get("status") == 200 and isinstance(s, str):
                m = None
                for m in USAGE.finditer(s):
                    pass
                if m:
                    c["tin"] += int(m[1]); c["tcached"] += int(m[2]); c["tout"] += int(m[3]); c["treason"] += int(m[4])
                    if m[5]:
                        c["cost"] += float(m[5]); c["ncost"] += 1
        c["off"] += end
        if c["cost_off"] is not None:
            c["cost_off"] = c["off"]
    cache[p] = c
    out = {k: c[k] for k in ("posts", "ok", "bad", "last", "tin", "tcached", "tout", "treason")}
    out["billed"] = c["cost"] if c["cost_off"] is not None and c["ncost"] else None
    return out

def billed_cc(a):
    """Claude Code over OpenRouter: agent/openrouter_costs.json, one entry per generation with its charge."""
    d = load(a + "/openrouter_costs.json")
    if not isinstance(d, dict):
        return None
    xs = [v.get("total_cost") for v in d.values() if isinstance(v, dict) and isinstance(v.get("total_cost"), (int, float))]
    return sum(xs) if xs else None

REWARD_KEYS = ("success", "deterministic", "live_success", "replay_success", "instance_ok", "instance_exact",
               "missing_trajectory", "grader_error", "missing_log", "n_actions", "video_rendered")

def started_at(d):
    return os.path.getmtime(d + "/config.json") if os.path.exists(d + "/config.json") else os.path.getmtime(d)

def record(job, jd, mode, task, trials, scan, pkey, mkeys=()):
    # a batch dir may be a symlink to the Harbor job (site_jobs/<batch>-<mode> -> jobs/<job name>): either name is live
    r = {"job": job, "mode": mode, "task": task, "alive": job in live or os.path.basename(os.path.realpath(jd)) in live, "trials": len(trials),
         "created": os.path.getmtime(jd), "scan": scan}
    if not trials:
        return r
    # The run is the task's first trial. A second one exists only where a runner inherited K=2 by mistake
    # (ws BEHAVIOR, 2026-09-26: trash and shoes unlimited).
    t = trials[0]; a = t + "/agent"
    m = os.path.join(jobs + "_mirror", job, os.path.basename(t), "agent")
    res = load(t + "/result.json") or {}
    # A trial regraded after its grading failed (regrade_robolab_ws3.sh) keeps both; the regrade is the verdict.
    vd = t + ("/verifier_regrade" if os.path.isfile(t + "/verifier_regrade/reward.json") else "/verifier")
    rw = load(vd + "/reward.json")
    ae = res.get("agent_execution") or {}
    ar = res.get("agent_result") or {}
    # Progress in [0, 1], the partial credit beside the binary success (user 2026-09-27); which key holds it is the
    # benchmark's `progress:` (state/runs/<benchmark>.yml). `q_score` (BEHAVIOR): the 2026 challenge's score, from one
    # extra replay (verifier_progress/, progress_backfill_lab.sh) or a grader that keeps it; BEHAVIOR graders before
    # 2026-09-27 wrote final_reward = 0 always (they read a key the replay does not have), so it is not used there.
    # Otherwise a reward.json key, by default the grader's final_reward (RoboLab: the fraction of subtasks done).
    prog = None
    if pkey == "q_score":
        pj = load(t + "/verifier_progress/replay.json")
        q = ((pj or {}).get("replays") or [{}])[0].get("q_score") if isinstance(pj, dict) else None
        q = (rw or {}).get("q_score") if q is None and isinstance(rw, dict) else q
        prog = float(q) if isinstance(q, (int, float)) else None
        # nothing handed in (no trajectory, or no robot action): nothing achieved, as in the challenge
        if prog is None and isinstance(rw, dict) and (rw.get("missing_trajectory") == 1 or rw.get("n_actions") == 0):
            prog = 0.0
    elif isinstance(rw, dict) and isinstance(rw.get(pkey), (int, float)):
        prog = float(rw[pkey])
    gw = gateway(a + "/gateway.jsonl")
    # What the provider charged, where it says: Claude Code over OpenRouter keeps it per generation; our gateway
    # sees OpenRouter's charge in every response.
    cc = billed_cc(a)
    if cc is not None:
        billed = {"usd": cc, "source": "openrouter_costs.json"}
    elif gw and gw.get("billed") is not None:
        billed = {"usd": gw["billed"], "source": "gateway"}
    else:
        billed = None
    if mkeys and isinstance(rw, dict):
        got = {k: rw[k] for k in mkeys if isinstance(rw.get(k), (int, float)) and not isinstance(rw.get(k), bool)}
        if got:
            r["metrics"] = got
    r.update(
        trial=os.path.basename(t),
        started=started_at(t),
        result=bool(res), agent_started=ae.get("started_at"), agent_finished=ae.get("finished_at"),
        finished=res.get("finished_at"),
        exception=(res.get("exception_info") or {}).get("exception_type"),
        reward={k: rw[k] for k in REWARD_KEYS if k in rw} if isinstance(rw, dict) else None,
        progress=prog,
        # The agent is over once Harbor wrote its ATIF trajectory or an exception (e.g. the 4 h AgentTimeoutError);
        # a limited trial's collect hook then replays for up to an hour before the verifier writes anything.
        grading=any(os.path.exists(t + "/verifier/" + f) for f in ("test-stdout.txt", "grade.log"))
        or os.path.exists(a + "/trajectory.json") or os.path.exists(t + "/exception.txt"),
        regraded=vd.endswith("_regrade"),
        gateway=gw,
        # Harbor's own count, for a harness without our model gateway (it has no reasoning split)
        harbor_tokens={"input": ar.get("n_input_tokens"), "cached": ar.get("n_cache_tokens"),
                       "output": ar.get("n_output_tokens")} if ar.get("n_input_tokens") is not None else None,
        billed=billed,
        logs={
            "codex": size(a + "/codex.txt"),
            "gateway": size(a + "/gateway.jsonl"),
            "sessions": len(glob.glob(a + "/sessions/**/*.jsonl", recursive=True)),
            "trajectory": size(a + "/trajectory.json"),
            "mirror_codex": size(m + "/codex.txt"),
            "mirror_gateway": size(m + "/gateway.jsonl"),
            # the sim service writes /data, or /out where /data is a licensed dataset mount (BEHAVIOR)
            "episode": next((x for x in (size(t + "/artifacts/data/episode.jsonl"), size(t + "/artifacts/out/episode.jsonl")) if x is not None), None),
            "reward": size(vd + "/reward.json"),
            "grade_log": size(vd + "/grade.log"),
            "video": size(vd + "/replay.mp4"),
            "video_ok": mp4_ok(vd + "/replay.mp4"),
            # how the live episode ended (limited: the sim service's final.json), e.g. "error" = a simulator error
            "episode_end": next((x.get("reason") for x in (load(t + "/artifacts/data/final.json"),
                                                           load(t + "/artifacts/out/final.json")) if isinstance(x, dict)), None),
        },
        modified=max((os.path.getmtime(x) for x in (a + "/codex.txt", a + "/gateway.jsonl") if os.path.exists(x)),
                     default=None),
    )
    return r

out = {}
for batch in batches:
    blog = os.path.join(jobs, batch + ".log")
    scans = {}
    if os.path.isfile(blog):
        for line in open(blog, errors="replace"):
            mm = re.match(r"\[(\S+)\] scanned \d+ files under .*: (\d+) contain one", line)
            if mm:
                scans[mm.group(1)] = int(mm.group(2))
    recs, seen = {}, os.path.isfile(blog)
    for jd in sorted(glob.glob(os.path.join(jobs, batch + "-*"))):
        if not os.path.isdir(jd):
            continue
        job = os.path.basename(jd)
        mode, _, task = job[len(batch) + 1:].partition("-")
        if mode not in modes:
            continue
        seen = True
        # In start order (config.json is written when a trial starts; a dir's own mtime moves when Harbor writes into it).
        trials = sorted((d for d in glob.glob(jd + "/*__*") if os.path.isdir(d)), key=started_at)
        if task:     # one Harbor job per task and mode: <batch>-<mode>-<task dir> (run_agent_batch.sh SEQ=1)
            recs[job] = record(job, jd, mode, task, trials, scans.get(job), progress.get(batch, "final_reward"),
                               declared.get(batch) or ())
            continue
        # one Harbor job per mode, a trial per task (SEQ=0): the trial's task from its config.json (dir names are cut)
        by_task = {}
        for t in trials:
            name = os.path.basename((((load(t + "/config.json") or {}).get("task") or {}).get("path") or "").rstrip("/"))
            if mode == "limited" and name.endswith("-limited"):
                name = name[:-len("-limited")]
            if name:
                by_task.setdefault(name, []).append(t)
        for name, ts in by_task.items():
            recs[job + "-" + name] = record(job, jd, mode, name, ts, scans.get(job), progress.get(batch, "final_reward"),
                                            declared.get(batch) or ())
    out[batch] = {"seen": seen, "jobs": recs}
os.makedirs(os.path.dirname(CACHE), exist_ok=True)
tmp = "%s.%d.tmp" % (CACHE, os.getpid())   # a name of its own: two probes on one host never share a half-written file
json.dump(cache, open(tmp, "w"))
os.replace(tmp, CACHE)
print(json.dumps({"now": time.time(), "batches": out}))
'''


def iso(ts: float | None) -> str | None:
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat(timespec="seconds") if ts else None


# ------------------------------------------------------------------------------------------------- hosts


def load_hosts(path: Path | None) -> tuple[dict, list[str]]:
    """host -> spec, merged from every data/runs/hosts*.local.yml (or only `path`), and the files read.

    One file per person on a shared checkout (hosts.local.yml, hosts.<name>.local.yml). A host may carry
    `benchmarks: [...]` and / or `runs: [...]`: then only those are looked for there."""
    files = [path] if path else sorted(HOSTS_DIR.glob("hosts*.local.yml"))
    hosts: dict[str, dict] = {}
    for f in files:
        try:
            got = yaml.safe_load(f.read_text()) or {}
            if not isinstance(got, dict):
                raise ValueError("not a mapping of host -> {ssh, jobs}")
        except (OSError, ValueError, yaml.YAMLError) as exc:   # someone else's file on a shared checkout: go on
            print(f"  skipped {f.name}: {str(exc).splitlines()[0][:200]}", file=sys.stderr, flush=True)
            continue
        for name, spec in got.items():
            if not isinstance(spec, dict) or not spec.get("jobs"):
                print(f"  skipped host {name!r} in {f.name}: it needs at least `jobs:`", file=sys.stderr, flush=True)
                continue
            if name in hosts and hosts[name] != spec:
                print(f"  skipped host {name!r} in {f.name}: another host file defines it differently; rename one",
                      file=sys.stderr, flush=True)
                continue
            hosts[name] = spec
    return hosts, [str(f.relative_to(ROOT)) if f.is_relative_to(ROOT) else str(f) for f in files]


def serves(spec: dict, br: runsdb.BenchRun) -> bool:
    return (not spec.get("benchmarks") or br.benchmark in spec["benchmarks"]) and (not spec.get("runs") or br.run in spec["runs"])


def jobs_dir(spec: dict) -> str:
    j = str(spec["jobs"])
    return j if spec.get("ssh") or j.startswith("/") else str((ROOT / j).resolve())


def probe(host: str, spec: dict, batches: list[str], modes: list[str], progress: dict[str, str],
          metrics: dict[str, list[str]] | None = None) -> dict:
    arg = json.dumps({"batches": batches, "modes": modes, "progress": progress, **({"metrics": metrics} if metrics else {})})
    if not spec.get("ssh"):
        cmd = [sys.executable, "-", jobs_dir(spec), arg]
    else:
        # Arguments travel through the remote shell, so quote them for it.
        cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", spec["ssh"],
               f"python3 - {spec['jobs']} '{arg.replace(chr(39), '')}'"]
    proc = subprocess.run(cmd, input=PROBE, capture_output=True, text=True, timeout=600)  # a cache rescan reads GBs of logs
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip()[-300:] or f"exit {proc.returncode}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


# ------------------------------------------------------------------------------------------------ records


def state_of(r: dict) -> str:
    """queued | setup | running | grading | success | failed | error | stalled"""
    if not r.get("trials"):
        return "setup" if r.get("alive") else "stalled"
    if r.get("result"):
        rw = r.get("reward")
        if rw is not None and "success" in rw:
            if rw["success"] != 1 and (rw.get("grader_error") == 1 or rw.get("missing_log") == 1):
                return "error"      # the grading failed or had nothing to grade: no verdict on the agent
            return "success" if rw["success"] == 1 else "failed"
        if r.get("alive"):          # harbor writes result.json before the collect hook and the verifier finish
            return "grading"
        return "error"
    if not r.get("alive"):
        return "stalled"
    if r.get("grading"):
        return "grading"
    return "running" if r["logs"]["codex"] else "setup"


def record(r: dict, host: str) -> dict:
    logs = r.get("logs") or {}
    gw = r.get("gateway") or {}
    wall = None
    if r.get("agent_started") and r.get("agent_finished"):
        f = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        wall = round((f(r["agent_finished"]) - f(r["agent_started"])).total_seconds())
    if gw.get("tin") is not None:
        tokens = {"input": gw.get("tin"), "cached": gw.get("tcached"), "output": gw.get("tout"), "reasoning": gw.get("treason")}
        source = "gateway"
    elif r.get("harbor_tokens"):
        tokens, source = {**r["harbor_tokens"], "reasoning": None}, "harbor"
    else:
        tokens, source = None, None
    billed = r.get("billed") or {}
    # A benchmark's declared continuous metrics (state/runs/<b>.yml `metrics:`), only where it declares any, so every
    # other benchmark's records (and data/runs/status.json) keep exactly the fields they had.
    extra = {"metrics": r["metrics"]} if r.get("metrics") else {}
    return {**extra,
        "state": state_of(r),
        "host": host,
        "job": r["job"],
        "trial": r.get("trial"),
        "started": iso(r.get("started") or r.get("created")),
        "finished": r.get("finished"),
        "agent_wall_s": wall,
        "calls": gw.get("posts"),
        "calls_failed": gw.get("bad"),
        "regraded": bool(r.get("regraded")),
        "tokens": tokens,
        "tokens_source": source,
        "billed_usd": billed.get("usd"),
        "billed_source": billed.get("source"),
        "last_call": iso(gw.get("last")),
        "exception": r.get("exception"),
        "reward": r.get("reward"),
        "progress": r.get("progress"),
        "scan": r.get("scan"),
        "logs": logs,
    }


def assemble(br: runsdb.BenchRun, found: dict, host_state: dict, prev: dict) -> dict:
    """task -> mode -> record for one benchmark's run, from the jobs found on every host (key -> (host, raw))."""
    tasks = {}
    runs = br.batches
    # `rerun_all: true`: the last rerun batch reruns every task and mode (BEHAVIOR 2026-09-27, the 8-thread cap). A job
    # it has not started yet is queued, with the earlier run kept as history, instead of showing that run's result.
    full = br.rerun_all
    # `followups`: what is already arranged for one run (a rerun, a regrade), keyed by its trial, so the note goes
    # away by itself once another trial replaces that one.
    notes = {(f.get("task"), f.get("mode"), f.get("trial")): f.get("note") for f in br.followups}
    before = prev.get("tasks") or {}
    down = lambda host: host and not host_state.get(host, {}).get("ok", True)
    for tid in br.tasks:
        per_mode = {}
        for mode in br.modes:
            key = lambda batch: f"{batch}-{mode}-{br.task_dir(tid)}"
            hits = [key(x) for x in runs if key(x) in found]
            last = (before.get(tid) or {}).get(mode) or {}
            last_key = f"{last['job']}-{br.task_dir(tid)}" if last.get("job") in [f"{x}-{mode}" for x in runs] else last.get("job")
            if last.get("job") and last_key not in found and down(last.get("host")):
                # its host did not answer this time: keep what it last reported (else a rerun batch's jobs on that
                # host would all show as queued, the earlier batch's jobs elsewhere winning; 2026-09-27 03:53, lab)
                per_mode[mode] = {**last, "stale": True}
            elif hits and full and hits[-1] != key(runs[-1]):
                old = record(found[hits[-1]][1], found[hits[-1]][0])
                if old.get("state") in ("setup", "running", "grading"):  # still going: show it, marked as history
                    per_mode[mode] = {**old, "followup": f"reruns in {runs[-1]}; this earlier run finishes as history"}
                else:
                    per_mode[mode] = {"state": "queued", "rerun": True, "supersedes": {k: old.get(k) for k in SUPERSEDED}}
            elif hits:
                per_mode[mode] = record(found[hits[-1]][1], found[hits[-1]][0])
                if len(hits) > 1:
                    old = record(found[hits[-2]][1], found[hits[-2]][0])
                    per_mode[mode]["supersedes"] = {k: old.get(k) for k in SUPERSEDED}
            else:
                # Keep what a stale host last reported rather than showing its jobs as queued.
                per_mode[mode] = {**last, "stale": True} if last and down(last.get("host")) else {"state": "queued"}
            note = notes.get((tid, mode, per_mode[mode].get("trial")))
            if note and per_mode[mode].get("trial"):
                per_mode[mode]["followup"] = note
        tasks[tid] = per_mode
    return tasks


def signature(status: dict) -> list:
    """What a reader acts on: each run's state, host, trial, grade and key scan, and which hosts answer."""
    keys = ("state", "host", "trial", "reward", "progress", "exception", "scan", "stale", "followup", "rerun")
    out = [sorted((h, s.get("ok")) for h, s in (status.get("hosts") or {}).items())]
    groups = ({"": status} if "tasks" in status else (status.get("benchmarks") or {}))
    for bid, b in sorted(groups.items()):
        for tid, modes in sorted((b.get("tasks") or {}).items()):
            for mode, r in sorted(modes.items()):
                out.append((bid, tid, mode, json.dumps({k: r.get(k) for k in keys}, sort_keys=True)))
    return out


def should_write(cur: dict, prev: dict, polling: bool, detail_every: float) -> bool:
    """A state change (a trial starting or ending, a host going down) is written at once; counts and sizes that
    merely grew wait for `detail_every`, so an open page is not rebuilt every few minutes."""
    strip = lambda d: {k: v for k, v in d.items() if k not in ("generated_at", "hosts")}
    changed = strip(cur) != strip(prev)
    if changed and polling and prev and signature(cur) == signature(prev):
        age = time.time() - dt.datetime.fromisoformat(prev.get("generated_at", "1970-01-01T00:00:00+00:00")).timestamp()
        changed = age >= detail_every
    return changed or not polling


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text()) if path.is_file() else {}
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    tmp.replace(path)


def aggregate(host_state: dict) -> dict:
    """data/runs/status.json: every benchmark's default run as collected here, in the shape of the one-sweep days."""
    out = {"hosts": host_state, "benchmarks": {}, "runs": {}}
    counts: dict[str, int] = {}
    for bid in runsdb.plans():
        br = runsdb.default_run(bid)
        data = read_json(br.out_path) if br else {}
        if not data:
            continue
        out["benchmarks"][bid] = {"batch": br.batches[0] if br.batches else None, "run": br.run, "tasks": data.get("tasks") or {}}
        out["runs"][bid] = br.run
        counts[br.run] = counts.get(br.run, 0) + 1
    main = max(counts, key=counts.get) if counts else None
    agent = runsdb.agents().get(main) or {}
    out["sweep"] = {"name": agent.get("sweep") or main, "agent": agent.get("label") or main,
                    "modes": agent.get("modes") or runsdb.DEFAULT_MODES, "run": main}
    return out


# --------------------------------------------------------------------------------------------- log pages


def sync_remote(hosts: dict, seen: dict[str, set[str]]) -> None:
    """Copy each remote host's log-page records of the batches it holds into .cache/runs_remote/<host>/."""
    for name, spec in hosts.items():
        if not spec.get("ssh"):
            continue
        dst = REMOTE / name
        dst.mkdir(parents=True, exist_ok=True)
        for batch in sorted(seen.get(name) or ()):
            # -z: the gateway logs are JSON; over a slow ssh hop (~1 MB/s) compression makes the copy several times faster
            cmd = ["rsync", "-az", "--prune-empty-dirs", "-e", "ssh -o BatchMode=yes -o ConnectTimeout=10",
                   "--include=*/", *(f"--include={f}" for f in LOG_FILES), "--exclude=*",
                   f"{spec['ssh']}:{spec['jobs']}/{batch}-*", f"{dst}/"]
            try:
                subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            except subprocess.TimeoutExpired:
                print(f"  rsync from {name} timed out", flush=True)


def fetch_output(spec: dict, r: dict, src: Path) -> None:
    """Copy a finished remote run's artifacts/app/output/ (images and gen.py only) for its log page."""
    (src / "artifacts" / "app").mkdir(parents=True, exist_ok=True)
    cmd = ["rsync", "-a", "--prune-empty-dirs", "-e", "ssh -o BatchMode=yes -o ConnectTimeout=10",
           "--include=*/", "--include=*.png", "--include=*.jpg", "--include=*.jpeg", "--include=gen.py", "--exclude=*",
           f"{spec['ssh']}:{spec['jobs']}/{r['job']}/{r['trial']}/artifacts/app/output", f"{src}/artifacts/app/"]
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        pass


def backfill(br: runsdb.BenchRun) -> dict:
    """<task>/<slot> -> the local-only notes and recovered records of one run's log pages:
    data/runs/<benchmark>/<run>.backfill.yml (see runlog.py)."""
    try:
        extras = yaml.safe_load((br.out_path.with_suffix(".backfill.yml")).read_text()) or {}
    except (OSError, yaml.YAMLError):
        extras = {}
    return extras if isinstance(extras, dict) else {}


def mark_rerendered(tasks: dict, extras: dict) -> None:
    """A trial whose replay was rendered again later (its backfill entry's `video`, a complete MP4): its record's
    logs.video_rerendered is that file's size, so the log checks count it instead of the graded replay's own video."""
    import runlog
    for key, extra in extras.items():
        tid, _, slot = str(key).partition("/")
        rec = (tasks.get(tid) or {}).get(slot)
        again = Path(extra["video"]) if isinstance(extra, dict) and extra.get("video") else None
        if isinstance(rec, dict) and isinstance(rec.get("logs"), dict) and again is not None and runlog.mp4_complete(again):
            rec["logs"] = {**rec["logs"], "video_rerendered": again.stat().st_size}


def build_logs(hosts: dict, br: runsdb.BenchRun, tasks: dict) -> int:
    """(Re)build the log-page data of every started trial of one benchmark's run whose state or records changed.

    A rerun that has started keeps the run it replaced on a page of its own, <mode>-prev (the rerun's own page takes
    <mode>); a queued rerun (`rerun_all`) still shows the earlier run on <mode>. Returns how many were rebuilt."""
    import runlog
    cache_file = LOGS_CACHE / br.benchmark / f"{br.run}.json"
    cache = read_json(cache_file)
    extras = backfill(br)

    def sig(p: Path):   # a file's size and mtime (rsync -a keeps the source's): None when absent
        try:
            st = p.stat()
            return [st.st_size, int(st.st_mtime)]
        except OSError:
            return None
    n = 0
    for tid, modes in tasks.items():
        for mode, rec in modes.items():
            sup = rec.get("supersedes") or {}
            slots = [(mode, rec)]
            if sup.get("trial") and not rec.get("rerun"):
                slots.append((mode + "-prev", sup))
            for slot, r in slots:
                if r.get("state", "queued") == "queued" or not r.get("trial") or r.get("host") not in hosts:
                    continue
                spec = hosts[r["host"]]
                if spec.get("ssh"):
                    src = REMOTE / r["host"] / r["job"] / r["trial"]
                    where = f"{spec['ssh']}:{spec['jobs']}/{r['job']}/{r['trial']}"
                else:
                    src = Path(jobs_dir(spec)) / r["job"] / r["trial"]
                    where = f"{jobs_dir(spec)}/{r['job']}/{r['trial']}"
                gw = src / "agent" / "gateway.jsonl"
                if spec.get("ssh") and r.get("state") in ("success", "failed", "error") and \
                        not (src / "verifier" / "replay.mp4").is_file() and not (src / "artifacts" / "app").is_dir():
                    fetch_output(spec, r, src)      # no replay: the page shows the agent's own images instead
                key = f"{tid}/{slot}"
                extra = extras.get(key) if isinstance(extras.get(key), dict) else {}
                # Sizes and mtimes, not mere presence: a --no-sync cycle builds from the last full sync's copies, which
                # may hold a replay still being written or predate the episode log; the next sync must rebuild the page.
                stamp = [runlog.VERSION, r.get("state"), r.get("trial"), gw.stat().st_size if gw.is_file() else None,
                         sig(src / "verifier" / "replay.mp4"), sig(src / "verifier_regrade" / "replay.mp4"),
                         sig(src / "artifacts" / "data" / "episode.jsonl") or sig(src / "artifacts" / "out" / "episode.jsonl"),
                         json.dumps(extra, sort_keys=True) if extra else None]
                if extra.get("video"):      # a replay rendered again later: rebuilt when it arrives or changes
                    stamp.append(sig(Path(extra["video"])))
                out = ROOT / "docs" / "assets" / br.benchmark / "runs" / br.run / tid / slot
                if cache.get(key) == stamp and (out / "log.json").is_file():
                    continue
                meta = {"benchmark": br.benchmark, "run": br.run, "task": tid, "mode": mode, "previous": slot != mode,
                        **{k: r.get(k) for k in ("state", "host", "job", "trial", "started", "finished",
                                                  "agent_wall_s", "exception", "reward", "scan")},
                        "where": where}
                try:
                    runlog.build(src, out, meta, extra)
                except Exception as exc:  # noqa: BLE001 - one broken record must not stop the rest
                    print(f"  log {br.benchmark}/{br.run}/{key}: {exc}", flush=True)
                    continue
                cache[key] = stamp
                n += 1
    if n or not cache_file.is_file():
        write_json(cache_file, cache)
    return n


# -------------------------------------------------------------------------------------------------- main


def cycle(a, hosts: dict, polling: bool) -> str:
    plan = [br for br in runsdb.all_runs()
            if (not a.benchmark or br.benchmark in a.benchmark) and (not a.run or br.run in a.run)]
    for path, err in runsdb.ERRORS:     # skipped; the other owners' runs go on (make check names the problem)
        print(f"  skipped {path}: {err}", flush=True)
    prev_hosts = read_json(OUT).get("hosts") or {}
    found: dict[str, tuple[str, dict]] = {}
    seen: dict[str, set[str]] = {}          # host -> batches with a trace there
    host_state = {}
    for name, spec in hosts.items():
        mine = [br for br in plan if serves(spec, br)]
        batches = sorted({b for br in mine for b in br.batches})
        if not batches:
            continue
        modes = sorted({m for br in mine for m in br.modes})
        progress = {b: br.progress_key for br in mine for b in br.batches if br.progress_key != "final_reward"}
        metrics = {b: [m["key"] for m in br.metrics] for br in mine for b in br.batches if br.metrics}
        try:
            data = probe(name, spec, batches, modes, progress, metrics)
            host_state[name] = {"ok": True, "at": iso(data["now"]), "error": None}
            for batch, got in data["batches"].items():
                if got.get("seen"):
                    seen.setdefault(name, set()).add(batch)
                for key, r in (got.get("jobs") or {}).items():
                    old = found.get(key)
                    # A job has one home; if two hosts hold it, trust the one that ran it.
                    if old is None or (r.get("trials", 0), r.get("modified") or 0) > (old[1].get("trials", 0), old[1].get("modified") or 0):
                        found[key] = (name, r)
        except Exception as exc:  # noqa: BLE001 - a host being down must not stop the others
            old = prev_hosts.get(name) or {}
            host_state[name] = {"ok": False, "at": old.get("at"), "error": str(exc)[:300]}

    writes = []
    for br in plan:
        served = {h: s for h, s in host_state.items() if serves(hosts[h], br)}
        prev = read_json(br.out_path)
        traced = any(b in seen.get(h, ()) for h in served for b in br.batches)
        if not (traced or prev):
            continue        # nothing of this run on the machines this checkout can see (a colleague's run)
        try:
            tasks = assemble(br, found, host_state, prev)
            mark_rerendered(tasks, backfill(br))
        except Exception as exc:  # noqa: BLE001 - one benchmark's broken file must not stop the others
            print(f"  skipped {br.benchmark}/{br.run}: {exc!r} (see make check)", flush=True)
            continue
        cur = {"v": 1, "benchmark": br.benchmark, "run": br.run, "label": br.label, "batches": br.batches,
               "hosts": served, "tasks": tasks}
        if should_write(cur, prev, polling, a.detail_every):
            writes.append((br, cur))

    # Log pages first, so the rebuild that the run files trigger finds them.
    if writes and not a.no_sync:
        sync_remote({h: s for h, s in hosts.items() if host_state.get(h, {}).get("ok")}, seen)
    logs = 0
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    for br, cur in writes:
        logs += build_logs(hosts, br, cur["tasks"])
        cur["generated_at"] = now
        write_json(br.out_path, cur)

    # hosts not asked this time (a narrower --benchmark / --run) keep what they last said
    status = aggregate({**{h: s for h, s in prev_hosts.items() if h in hosts}, **host_state})
    prev_status = read_json(OUT)
    wrote_status = should_write(status, prev_status, polling, a.detail_every)
    if wrote_status:
        status["generated_at"] = now
        write_json(OUT, status)
    states = [m.get("state") for b in status["benchmarks"].values() for t in b["tasks"].values() for m in t.values()]
    summary = ", ".join(f"{s} {states.count(s)}" for s in sorted(set(states)))
    down = [h for h, s in host_state.items() if not s["ok"]]
    return (f"[{time.strftime('%H:%M:%S')}] {'written' if wrote_status else 'unchanged'}: {summary}"
            + (f"; {len(writes)} run file(s) written" if writes else "")
            + (f"; {logs} log page(s) refreshed" if logs else "")
            + (f"; hosts down: {', '.join(down)}" if down else ""))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--hosts", type=Path, help="read only this host file (default: every data/runs/hosts*.local.yml)")
    ap.add_argument("--benchmark", action="append", help="collect only this benchmark's runs (repeatable)")
    ap.add_argument("--run", action="append", help="collect only this run (repeatable)")
    ap.add_argument("--watch", type=float, default=0, help="repeat every N seconds")
    ap.add_argument("--once", action="store_true",
                    help="one cycle with --watch's rules (write only on a change), then exit: for callers that poll")
    ap.add_argument("--no-sync", action="store_true",
                    help="skip the rsync of remote logs: status and log pages from what is already here (a quick fix-up)")
    ap.add_argument("--detail-every", type=float, default=900,
                    help="with --watch: when only counts and sizes moved, rewrite at most this often (s)")
    a = ap.parse_args()
    hosts, files = load_hosts(a.hosts)
    if not hosts:
        print("no data/runs/hosts*.local.yml: see this script's docstring", file=sys.stderr)
        return 2
    import fcntl
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    lock = open(LOCK, "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("another import_runs.py is running; nothing to do", flush=True)
        return 0
    while True:
        runsdb.reset_caches()     # state/runs/ may have been edited since the last cycle
        print(cycle(a, hosts, polling=bool(a.watch or a.once)), flush=True)
        if not a.watch or a.once:
            return 0
        time.sleep(a.watch)


if __name__ == "__main__":
    sys.exit(main())

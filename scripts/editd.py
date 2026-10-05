#!/usr/bin/env python3
"""Local edit daemon: lets the site write tag and status changes back to disk.

Why this exists: tagging a hundred tasks by hand-editing YAML frontmatter is
miserable, and the judgement happens while you are watching the demo — which
is in the browser, not the editor. This serves a tiny JSON API that the task
list calls, so a click on a row updates the real Markdown file. `mkdocs serve`
notices the write and reloads.

This is deliberately single-user and localhost-only. There is no auth, no
locking and no merge handling, because everyone runs their own copy on their
own machine. Do not expose it.

  python scripts/editd.py --upstream 127.0.0.1:8001 --port 8000
  make edit                          # daemon + mkdocs serve together
"""

from __future__ import annotations

import argparse
import errno
import json
import os
import re
import signal
import sys
import threading
import time
import urllib.request
import http.client
import select
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import yaml  # noqa: E402

import statedb  # noqa: E402
import taskdb  # noqa: E402

# How long the front door waits for `mkdocs serve` to bind before giving up.
# Generous: a cold build of 267 pages takes a few seconds, and waiting is
# invisible to the reader while an error page is not.
UPSTREAM_WAIT = 120.0

ROOT = Path(__file__).resolve().parent.parent
LOCK = threading.Lock()
STARTED = time.time()

SLUG_RE = re.compile(r"[^a-z0-9]+")


def taxonomy_payload() -> dict:
    """The display tags (state/display_tags.yml), shaped for the editor's checkboxes.

    The detailed labels (`labels:`, state/taxonomy.yml) are not edited from the site.
    """
    tax = taskdb.tag_vocabulary()
    return {
        "capabilities": [
            {
                "id": c["id"],
                "name": c["name"],
                "description": c.get("description", ""),
                "subcapabilities": [
                    {
                        "id": s["id"],
                        "name": s["name"],
                        "description": s.get("description", ""),
                        "from_skills": s.get("from_skills") or [],
                    }
                    for s in (c.get("subcapabilities") or [])
                ],
            }
            for c in tax.get("capabilities", [])
        ],
        # Lets the editor pre-suggest tags from a task's annotated skills.
        "skillMap": taskdb.skill_to_tags(),
    }


def reload_caches() -> None:
    """Drop the memoised views so the next read sees what we just wrote."""
    taskdb.reset_caches()


def find_task(task_id: str):
    for bench in taskdb.benchmarks().values():
        for task in bench.tasks:
            if task.task_id == task_id:
                return bench, task
    return None, None


def patch_task(task_id: str, body: dict) -> dict:
    with LOCK:
        reload_caches()
        bench, task = find_task(task_id)
        if task is None:
            return {"ok": False, "error": f"unknown task {task_id}"}

        tags = taskdb.tag_index()
        patch: dict = {}

        if "status" in body:
            if body["status"] not in taskdb.STATUSES:
                return {"ok": False, "error": f"bad status {body['status']!r}"}
            patch["status"] = body["status"]

        if "difficulty" in body:
            if body["difficulty"] not in taskdb.DIFFICULTIES:
                return {"ok": False, "error": f"bad difficulty {body['difficulty']!r}"}
            patch["difficulty"] = body["difficulty"]

        if "labels" in body:
            return {"ok": False, "error": "the detailed labels are edited by hand in state/tasks/; "
                    "the site edits display_tags"}
        if "display_tags" in body:
            chosen = list(dict.fromkeys(body["display_tags"]))
            unknown = [c for c in chosen if c not in tags]
            if unknown:
                return {"ok": False, "error": f"unknown tags: {', '.join(unknown)}"}
            groups = {tags[c]["group_id"] for c in chosen}
            missing = [g for g in taskdb.TAG_GROUPS if chosen and g not in groups]
            if missing:
                names = {c["id"]: c["name"] for c in taskdb.tag_vocabulary().get("capabilities", [])}
                return {"ok": False, "error": "pick at least one tag from "
                        + " and from ".join(names.get(g, g) for g in missing)}
            # Stored in vocabulary order, Capability tags first, as every page shows them.
            patch["display_tags"] = taskdb.ordered_tags(chosen)

        if "owner" in body:
            patch["owner"] = str(body["owner"]).lstrip("@").strip()
        if "note" in body:
            patch["note"] = str(body["note"])

        statedb.update(bench.id, task_id, patch)
        reload_caches()

        _, fresh = find_task(task_id)
        tags = taskdb.tag_index()
        return {
            "ok": True,
            "task": {
                "id": fresh.task_id,
                "status": fresh.status,
                "difficulty": fresh.difficulty,
                "displayTags": fresh.display_tags,
                "tagNames": [
                    tags[c]["name"] if c in tags else c for c in fresh.display_tags
                ],
                "tagGroups": [
                    tags[c]["group_id"] if c in tags else "" for c in fresh.display_tags
                ],
                "owner": fresh.owner,
                "note": fresh.note,
            },
        }


def add_capability(name: str, parent: str = "") -> dict:
    """Add a display tag under an existing group of state/display_tags.yml."""
    name = name.strip()
    if not name:
        return {"ok": False, "error": "empty name"}

    with LOCK:
        doc = statedb.load_display_tags()
        cap_id = SLUG_RE.sub("-", name.lower()).strip("-")
        if not cap_id:
            return {"ok": False, "error": "name has no usable characters"}

        existing = {
            s["id"] for c in doc["capabilities"] for s in (c.get("subcapabilities") or [])
        }
        if cap_id in existing:
            return {"ok": False, "error": f"{cap_id} already exists"}

        target = next((c for c in doc["capabilities"] if c["id"] == parent), None)
        if target is None:
            # No parent chosen: park it under `custom` for later triage rather
            # than guessing which group it belongs to.
            target = next((c for c in doc["capabilities"] if c["id"] == "custom"), None)
            if target is None:
                target = {
                    "id": "custom",
                    "name": "Custom",
                    "description": "Added from the site. Move these into a proper group once a pattern emerges.",
                    "subcapabilities": [],
                }
                doc["capabilities"].append(target)

        target.setdefault("subcapabilities", []).append(
            {"id": cap_id, "name": name,
             "description": "Added from the site; no definition written yet."}
        )
        statedb.save_display_tags(doc)
        reload_caches()
        return {"ok": True, "id": cap_id, "parent": target["id"], "taxonomy": taxonomy_payload()}


def _carried(source: dict | None, entry: dict, skip: tuple[str, ...] = ()) -> dict:
    """Fields to keep that the editor neither shows nor sends back."""
    if not isinstance(source, dict):
        return {}
    return {k: v for k, v in source.items()
            if k not in entry and k not in skip and k != "id"}


def save_taxonomy(doc: dict) -> dict:
    """Replace the whole display tag vocabulary (state/display_tags.yml) from the Labels page editor.

    The editor round-trips only id, name, description and from_skills. Every
    other field in the file — `graded`, `flag`, `derived_from`, `evidence` — is
    re-attached here from what is on disk, keyed by id. Trusting the POST to
    carry them looked fine in a test that passed the file straight back, and
    would have wiped all of it the first time a real browser saved.
    """
    caps = doc.get("capabilities")
    if not isinstance(caps, list) or not caps:
        return {"ok": False, "error": "the display tags need at least one group"}

    current = statedb.load_display_tags()
    on_disk_caps = {c["id"]: c for c in current.get("capabilities") or [] if c.get("id")}
    on_disk_subs = {s["id"]: s
                    for c in current.get("capabilities") or []
                    for s in (c.get("subcapabilities") or []) if s.get("id")}

    seen: set[str] = set()
    clean = []
    for cap in caps:
        cid = SLUG_RE.sub("-", str(cap.get("id") or cap.get("name", "")).lower()).strip("-")
        if not cid:
            return {"ok": False, "error": "a capability has no usable id"}
        subs = []
        for sub in cap.get("subcapabilities") or []:
            sid = SLUG_RE.sub("-", str(sub.get("id") or sub.get("name", "")).lower()).strip("-")
            if not sid:
                return {"ok": False, "error": f"a sub-capability of {cid} has no usable id"}
            if sid in seen:
                return {"ok": False, "error": f"duplicate sub-capability id {sid!r}"}
            seen.add(sid)
            entry = {"id": sid, "name": sub.get("name") or sid,
                     "description": sub.get("description", "")}
            if sub.get("from_skills"):
                entry["from_skills"] = list(sub["from_skills"])
            # `derived_from`, `evidence` and `flag` are not editable from the page
            # and the browser is never sent them, so they cannot come back in the
            # POST. Re-attach them from disk by id, or one Save silently deletes
            # the provenance the whole taxonomy is argued from.
            entry.update(_carried(on_disk_subs.get(sid), entry))
            # `from_skills` is set above, and only when not empty: the browser sends `[]` for every tag without.
            entry.update(_carried(sub, entry, skip=("from_skills",)))
            subs.append(entry)
        entry = {"id": cid, "name": cap.get("name") or cid,
                 "description": cap.get("description", ""),
                 "subcapabilities": subs}
        # Same as the labels: `graded` marks a facet as an ordinal ladder and is
        # never sent to the browser, so it has to come back from disk.
        entry.update(_carried(on_disk_caps.get(cid), entry, skip=("subcapabilities",)))
        entry.update(_carried(cap, entry, skip=("subcapabilities",)))
        clean.append(entry)

    with LOCK:
        # Tags still in use must survive, or task state silently breaks.
        reload_caches()
        in_use: set[str] = set()
        for bench in taskdb.benchmarks().values():
            for task in bench.tasks:
                in_use.update(task.display_tags)
        orphaned = sorted(in_use - seen)
        if orphaned:
            return {
                "ok": False,
                "error": "still used by tasks: " + ", ".join(orphaned),
            }

        # Keep the document's own version: hardcoding it reverted the file to an
        # older schema number on every save.
        statedb.save_display_tags({"version": doc.get("version") or taskdb.tag_vocabulary().get("version", 1),
                                   "capabilities": clean})
        reload_caches()
        return {"ok": True, "taxonomy": taxonomy_payload()}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        """Log writes and errors; stay quiet about routine health polling.

        The task list polls /api/health on every page load, which otherwise
        buries the mkdocs build output that people actually need to read.
        """
        line = fmt % args
        if "/api/health" in line and " 200 " in line:
            return
        sys.stderr.write("  edit API: " + line + "\n")

    def _send_html(self, body: str, code: int = 200) -> None:
        raw = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send(self, payload: dict, code: int = 200) -> None:
        raw = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        # The docs are served from another port, so the browser treats this as
        # cross-origin. Localhost only; see the module docstring.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):  # noqa: N802
        self._send({"ok": True})

    # ---------------------------------------------------------------- proxying
    #
    # This process is the single front door: it answers /api/* itself and hands
    # everything else to `mkdocs serve` on an internal port. The page therefore
    # calls /api/health on its own origin, with no port number anywhere in the
    # JavaScript. That removes the whole class of failure this replaced — a
    # second port that can be taken by something else, blocked by the browser,
    # or simply not forwarded to wherever the browser actually is.

    def _upstream(self) -> tuple[str, int] | None:
        return getattr(self.server, "upstream", None)

    def _proxy(self) -> None:
        host, port = self._upstream()
        if self.headers.get("Upgrade", "").lower() == "websocket":
            self._tunnel(host, port)
            return

        body = None
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            body = self.rfile.read(length)

        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ("host", "connection", "keep-alive",
                                        "proxy-connection", "te", "upgrade")}
        headers["Host"] = f"{host}:{port}"

        # The front door binds instantly; mkdocs needs a few seconds to build
        # before it binds. Hold the request until it answers instead of handing
        # back an error page that the reader has to notice and reload — the
        # browser shows its own loading state, and the first page just arrives.
        deadline = time.monotonic() + UPSTREAM_WAIT
        while True:
            try:
                conn = http.client.HTTPConnection(host, port, timeout=60)
                conn.request(self.command, self.path, body=body, headers=headers)
                resp = conn.getresponse()
                data = resp.read()
                break
            except OSError as exc:
                if time.monotonic() >= deadline:
                    self._send_html(
                        "<h2>The documentation server did not come up.</h2>"
                        f"<p>Waited {UPSTREAM_WAIT:.0f}s for mkdocs at {host}:{port} "
                        f"({exc}). Check the terminal running <code>make edit</code> "
                        "for a build error.</p>", 502)
                    return
                time.sleep(0.1)

        self.send_response(resp.status)
        for key, value in resp.getheaders():
            if key.lower() in ("transfer-encoding", "connection", "content-length",
                               "keep-alive", "upgrade"):
                continue
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)
        conn.close()

    def _tunnel(self, host: str, port: int) -> None:
        """Splice the connection to upstream — this is mkdocs' live reload."""
        self.close_connection = True
        deadline = time.monotonic() + UPSTREAM_WAIT
        while True:
            try:
                up = socket.create_connection((host, port), timeout=10)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    self.send_error(502, "live reload upstream unavailable")
                    return
                time.sleep(0.1)

        head = [f"{self.command} {self.path} HTTP/1.1"]
        head += [f"{k}: {v}" for k, v in self.headers.items()]
        try:
            up.sendall(("\r\n".join(head) + "\r\n\r\n").encode())
        except OSError:
            up.close()
            return

        down = self.connection
        socks = [up, down]
        try:
            while True:
                readable, _, broken = select.select(socks, [], socks, 300)
                if broken or not readable:
                    return
                for sock in readable:
                    chunk = sock.recv(65536)
                    if not chunk:
                        return
                    (down if sock is up else up).sendall(chunk)
        except OSError:
            return
        finally:
            up.close()

    def do_GET(self):  # noqa: N802
        if self.path.startswith("/api/health"):
            reload_caches()
            self._send({
                "ok": True,
                "pid": os.getpid(),
                "started": STARTED,
                "root": str(ROOT),
                "taxonomy": taxonomy_payload(),
            })
        elif self._upstream():
            self._proxy()
        elif self.path in ("/", "/index.html"):
            # Running without a front door (`python scripts/editd.py` on its
            # own): there is no site to serve, so say what this is.
            self._send_html(self._landing(), 200)
        else:
            self._send({"ok": False, "error": "not found. Without --upstream this serves /api/* only."}, 404)

    def _landing(self) -> str:
        docs = self.server.docs_url or ""
        link = (f'<p>The documentation is at <a href="{docs}">{docs}</a> — open that instead.</p>'
                if docs else "<p>The documentation is served on a different port; see the "
                             "<code>Docs at …</code> line printed by <code>make edit</code>.</p>")
        return (
            "<!doctype html><html><head><meta charset=utf-8>"
            "<title>Edit daemon</title><style>"
            "body{font:15px/1.6 system-ui,sans-serif;max-width:34rem;margin:12vh auto;padding:0 1.5rem}"
            "code{background:#f2f2f4;padding:.1em .35em;border-radius:4px}"
            "a{color:#3b48cc}</style></head><body>"
            "<h2>This is the edit daemon, not the documentation.</h2>"
            "<p>It is a local JSON API that lets the task list write to "
            "<code>state/</code>. There is no page to browse here.</p>"
            f"{link}"
            "<p style=\"color:#666;font-size:.9em\">Endpoints: "
            "<code>GET /api/health</code>, <code>POST /api/task/&lt;id&gt;</code>, "
            "<code>POST /api/capability</code>, <code>POST /api/taxonomy</code>.</p>"
            "</body></html>"
        )

    def do_HEAD(self):  # noqa: N802
        if self._upstream() and not self.path.startswith("/api/"):
            self._proxy()
        else:
            self._send({"ok": True})

    def do_POST(self):  # noqa: N802
        if not self.path.startswith("/api/") and self._upstream():
            # Decide before reading: _proxy needs the body still on the wire.
            self._proxy()
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            self._send({"ok": False, "error": "bad JSON"}, 400)
            return

        if self.path.startswith("/api/task/"):
            task_id = self.path.rsplit("/", 1)[-1]
            try:
                self._send(patch_task(task_id, body))
            except Exception as exc:  # surface the failure in the UI
                self._send({"ok": False, "error": str(exc)}, 500)
        elif self.path.startswith("/api/capability"):
            try:
                self._send(add_capability(body.get("name", ""), body.get("parent", "")))
            except Exception as exc:
                self._send({"ok": False, "error": str(exc)}, 500)
        elif self.path.startswith("/api/shutdown"):
            # Lets a newly started daemon retire an older one politely, rather
            # than killing a pid we only inferred from a port.
            self._send({"ok": True})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        elif self.path.startswith("/api/taxonomy"):
            try:
                self._send(save_taxonomy(body))
            except Exception as exc:
                self._send({"ok": False, "error": str(exc)}, 500)
        else:
            self._send({"ok": False, "error": "not found"}, 404)


def _health(host: str, port: int) -> dict | None:
    """The health payload of a daemon already on this port, or None."""
    try:
        with urllib.request.urlopen(f"http://{host}:{port}/api/health", timeout=2) as resp:
            data = json.loads(resp.read() or b"{}")
            return data if data.get("ok") is True else None
    except Exception:
        return None


def _shutdown(host: str, port: int) -> None:
    try:
        req = urllib.request.Request(f"http://{host}:{port}/api/shutdown", data=b"{}",
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=3).read()
    except Exception:
        pass


def _bind_when_free(host: str, port: int, tries: int = 30):
    """Poll for the port to become bindable; return the server or None."""
    for _ in range(tries):
        time.sleep(0.1)
        try:
            return ThreadingHTTPServer((host, port), Handler)
        except OSError:
            continue
    return None


def _holder_pid(host: str, port: int) -> int | None:
    """The pid listening on `port`, asked of the OS rather than of the daemon."""
    import shutil
    import subprocess

    if shutil.which("ss"):
        try:
            # Filter here rather than with `sport = :N`, whose argv quoting
            # differs between ss builds and silently matched nothing on this one.
            out = subprocess.run(["ss", "-lntpH"], capture_output=True, text=True, timeout=5).stdout
            for line in out.splitlines():
                local = line.split()[3] if len(line.split()) > 3 else ""
                if local.endswith(f":{port}"):
                    m = re.search(r"pid=(\d+)", line)
                    if m:
                        return int(m.group(1))
        except (OSError, subprocess.SubprocessError, IndexError):
            pass
    if shutil.which("lsof"):
        try:
            out = subprocess.run(["lsof", "-nP", "-tiTCP:%d" % port, "-sTCP:LISTEN"],
                                 capture_output=True, text=True, timeout=5).stdout
            first = out.split()
            if first:
                return int(first[0])
        except (OSError, subprocess.SubprocessError, ValueError):
            pass
    return None


def open_server(host: str, port: int):
    """Bind the API port, retiring an older daemon if one holds it.

    Never reuses an existing daemon: an orphan from a previous `make edit` is
    running whatever code and cached state existed when it started, so after a
    pull or a script edit it answers /api/health perfectly while serving stale
    behaviour. That failure is invisible and expensive to debug.

    Returns the bound server, or None after explaining why it could not bind.
    """
    try:
        return ThreadingHTTPServer((host, port), Handler)
    except OSError as exc:
        if exc.errno not in (errno.EADDRINUSE, errno.EACCES):
            raise

    info = _health(host, port)
    if info is None:
        print(
            f"  port {port} is taken by something that is not the edit API.\n"
            f"  Editing will be OFF. Free the port, or run:\n"
            f"      python scripts/editd.py --port <other>\n"
            f"  (the page probes {port} only, so another port needs a code change)",
            file=sys.stderr, flush=True,
        )
        return None

    print(f"  retiring an older edit API on port {port} (pid {info.get('pid', '?')})",
          flush=True)
    _shutdown(host, port)
    server = _bind_when_free(host, port)

    if server is None:
        # A daemon predating /api/shutdown ignores the polite request, and one
        # predating this file's health fields cannot even tell us its pid — which
        # is exactly the orphan most likely to be holding the port, since it has
        # been running since before the code changed. Ask the OS who holds it.
        # Safe because /api/health already answered as the edit API on this port.
        pid = info.get("pid") or _holder_pid(host, port)
        if pid:
            try:
                os.kill(int(pid), signal.SIGTERM)
                print(f"  it ignored shutdown; sent SIGTERM to pid {pid}", flush=True)
            except (OSError, ValueError):
                pass
            server = _bind_when_free(host, port)

    if server is None:
        print(
            f"  port {port} is still held. Editing will be OFF. Free it with:\n"
            f"      lsof -nP -iTCP:{port} -sTCP:LISTEN\n"
            f"      kill <pid>",
            file=sys.stderr, flush=True,
        )
    return server


def _watch_parent() -> None:
    """Exit when the shell that started us goes away.

    Watches the *specific* pid we were started by, not `getppid() == 1`. On a
    desktop Linux session `systemd --user` is registered as a child subreaper,
    so an orphan is re-parented to systemd, not to init: the old check never
    fired, and every `make edit` that ended without running its trap left a
    daemon behind. Two of those were still running days later.
    """
    start = os.getppid()
    if start == 1:
        return  # started detached on purpose; nothing to watch
    while True:
        time.sleep(2)
        if os.getppid() != start:
            os._exit(0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=0,
                    help="port to serve on; 0 lets the OS pick a free one")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--upstream", default="",
                    help="HOST:PORT of `mkdocs serve`. Given this, we are the front "
                         "door: /api/* is ours and everything else is proxied, so the "
                         "page reaches the API on its own origin with no port in the JS")
    ap.add_argument("--docs-url", default="",
                    help="where the docs are served, so the landing page can point there")
    args = ap.parse_args()

    server = open_server(args.host, args.port)
    if server is None:
        return 1

    server.docs_url = args.docs_url
    server.upstream = None
    if args.upstream:
        host, _, port = args.upstream.rpartition(":")
        server.upstream = (host or "127.0.0.1", int(port))
    threading.Thread(target=_watch_parent, daemon=True).start()
    # Deliberately does not print a browsable URL: this is an API, and a URL
    # printed next to the docs URL invites opening the wrong one.
    # flush: make runs this alongside mkdocs, so stdout is a pipe and would
    # otherwise be block-buffered — the line appears minutes later, or never.
    bound = server.server_address[1]
    if server.upstream:
        print(f"  editing is ON — same address as the site, no second port to open",
              flush=True)
    else:
        print(f"  edit API on port {bound} (no --upstream: /api/* only)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  edit API stopped", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

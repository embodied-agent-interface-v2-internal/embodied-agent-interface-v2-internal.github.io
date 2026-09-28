#!/usr/bin/env python3
"""Print the first free TCP port at or above a starting point.

`mkdocs serve` has no auto-port option and dies if its port is taken, which it
often is when two people share a box or you left an old preview running. The
Makefile's `serve` target calls this to pick a port instead of hardcoding one.

Usage:
  python scripts/free_port.py            # first free port from 8000 up
  python scripts/free_port.py --start 9000 --host 0.0.0.0
"""

from __future__ import annotations

import argparse
import socket
import sys


def is_free(host: str, port: int) -> bool:
    """True if we can bind the port right now.

    Deliberately no SO_REUSEADDR: a plain bind is the stricter test, so a port
    lingering in TIME_WAIT counts as busy. Better to skip to the next one than
    to hand back a port that fails a second later.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--start", type=int, default=8000)
    ap.add_argument("--tries", type=int, default=200)
    args = ap.parse_args()

    for port in range(args.start, min(args.start + args.tries, 65536)):
        if is_free(args.host, port):
            print(port)
            return 0

    print(
        f"no free port in {args.start}-{args.start + args.tries - 1}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

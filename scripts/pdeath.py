#!/usr/bin/env python3
"""Run a command that cannot outlive the shell that started it.

`make edit` starts two servers. Both used to survive a closed terminal or a
`kill -9` on the shell, because a trap cannot run when the shell is killed
outright, and because an orphan on a desktop Linux session is re-parented to
`systemd --user` rather than to init — so the usual "am I orphaned?" check
(getppid() == 1) never fires. Two daemons were found still running days later,
holding ports and serving code from whenever they were started.

This asks the kernel instead: PR_SET_PDEATHSIG makes the kernel send a signal
to this process the moment its parent dies, whatever kills the parent and
whether or not anything gets to clean up. Then we exec the real command, which
inherits that setting.

    python scripts/pdeath.py mkdocs serve --dev-addr 127.0.0.1:8001

Linux only; on anything else it execs the command unchanged, which is no worse
than not using it.
"""

from __future__ import annotations

import ctypes
import os
import signal
import sys

PR_SET_PDEATHSIG = 1


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit("usage: pdeath.py COMMAND [ARGS...]")

    if sys.platform.startswith("linux"):
        try:
            libc = ctypes.CDLL("libc.so.6", use_errno=True)
            libc.prctl(PR_SET_PDEATHSIG, signal.SIGKILL)
            # Between the fork and this call the parent may already have gone,
            # in which case the signal was never armed and we must not linger.
            if os.getppid() == 1:
                return 0
        except OSError:
            pass  # not fatal: the command still runs, it just may outlive us

    os.execvp(sys.argv[1], sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())

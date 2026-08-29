#!/usr/bin/env python3
"""
GATE-J0B-CLOSE Phase 2 — drive `goose configure` under a PTY.

J0B-RESUME recorded `goose configure` as interactive-only and left the path UNEXERCISED
(its C5 map's stated hole). It is interactive, not un-scriptable: a pty plus the arrow/enter
keys it expects drives it. The point is to make GOOSE write the extensions stanza, so the
schema in the report is goose's own output rather than a shape I guessed.

Usage: drive_configure.py <script-file>
  where each line of <script-file> is either  SEND <literal>  or  KEY <name>  or  WAIT <secs>.
Everything the child prints is echoed to stdout so the transcript is the evidence.
"""
import os, pty, sys, time, select

KEYS = {"DOWN": b"\x1b[B", "UP": b"\x1b[A", "ENTER": b"\r", "SPACE": b" ",
        "RIGHT": b"\x1b[C", "LEFT": b"\x1b[D", "ESC": b"\x1b", "CTRLC": b"\x03"}

steps = []
for ln in open(sys.argv[1]):
    ln = ln.rstrip("\n")
    if not ln or ln.startswith("#"):
        continue
    op, _, rest = ln.partition(" ")
    steps.append((op, rest))

pid, fd = pty.fork()
if pid == 0:
    os.environ["TERM"] = "xterm"
    os.execvp("goose", ["goose", "configure"])

out = []


def drain(t=0.8):
    end = time.time() + t
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.1)
        if r:
            try:
                d = os.read(fd, 65536)
            except OSError:
                return
            if not d:
                return
            out.append(d)


drain(2.0)
for op, rest in steps:
    if op == "KEY":
        for k in rest.split():
            os.write(fd, KEYS[k])
            time.sleep(0.25)
    elif op == "SEND":
        os.write(fd, rest.encode())
        time.sleep(0.25)
    elif op == "WAIT":
        time.sleep(float(rest))
    drain(1.0)
drain(3.0)
try:
    os.close(fd)
except OSError:
    pass
try:
    os.waitpid(pid, 0)
except ChildProcessError:
    pass
sys.stdout.write(b"".join(out).decode("utf-8", "replace"))

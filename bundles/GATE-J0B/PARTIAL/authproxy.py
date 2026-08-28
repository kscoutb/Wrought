#!/usr/bin/env python3
"""
GATE-J0B Phase 1 — the authenticating loopback proxy.

Purpose (C5): the disposable guest drives the local model WITHOUT ever holding the
API key, and every model call is centrally logged (the Decision-1 log-tap prototype).

Rails honoured:
  - The key arrives as the FIRST LINE OF STDIN and lives in memory only. It is never
    written to a file, never placed in argv or the environment, never sent to the guest.
  - Listens on 127.0.0.1 only. Upstream is 127.0.0.1:8080 only. No other destination
    is reachable from this process by construction (UPSTREAM is a constant).
  - apicalls.log records ONLY: ISO-8601 timestamp, method, path, response status.
    No bodies, no headers, no key material. The key is additionally scrubbed from the
    logged path as a belt-and-braces measure.

DESIGN NOTE — deviation from the prompt's literal wording, stated out loud.
  The prompt says: "parse the request head, inject Authorization, forward, then BLIND
  BIDIRECTIONAL BYTE RELAY for the rest". Taken literally that parses exactly one head
  per TCP connection. Two of the prompt's OWN requirements cannot be met that way:
    (1) "Appends one line per request" — under HTTP/1.1 keep-alive an agent reuses one
        connection for many requests, so a one-head-per-connection proxy would log the
        first and silently miss the rest. Phase 5 then asks us to COUNT those calls, so
        the literal design would undercount the very number it exists to measure.
    (2) "response status" cannot be known without reading the response status line, so
        the upstream->client direction was never going to be fully blind either.
    (3) Worse than miscounting: requests 2..N on a reused connection would reach
        llama-server with NO Authorization header and be answered 401, which would
        present as a Goose failure and be misdiagnosed.
  So this proxy is head-aware in both directions and blind for every BODY byte:
  request bodies and response bodies are relayed byte-for-byte using only their framing
  (Content-Length / chunked), never interpreted. Any framing this proxy cannot account
  for (upgrade, 1xx, unparseable head, missing framing) DEGRADES that connection to a
  pure blind byte relay — i.e. to exactly the prompt's literal behaviour — rather than
  guessing. For a single-request connection the two designs are byte-identical.
"""

import os
import socket
import sys
import threading
import time
from collections import deque

LISTEN = ("127.0.0.1", 8081)
UPSTREAM = ("127.0.0.1", 8080)
LOGPATH = "/var/lib/wrought/j0b/apicalls.log"
PIDPATH = "/var/lib/wrought/j0b/authproxy.pid"
BUF = 65536
HEAD_LIMIT = 262144

_log_lock = threading.Lock()
KEY = None


def log_call(method, path, status):
    """One line per request. Timestamp, method, path, status. Nothing else, ever."""
    if KEY and KEY in path:
        path = path.replace(KEY, "<REDACTED>")
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = "%s %s %s %s\n" % (ts, method, path, status)
    with _log_lock:
        with open(LOGPATH, "a") as f:
            f.write(line)
            f.flush()


class Reader(object):
    """Buffered reader that never loses bytes when we hand off to a blind relay."""

    def __init__(self, sock):
        self.sock = sock
        self.buf = b""
        self.eof = False

    def fill(self):
        if self.eof:
            return False
        try:
            d = self.sock.recv(BUF)
        except OSError:
            self.eof = True
            return False
        if not d:
            self.eof = True
            return False
        self.buf += d
        return True

    def read_head(self):
        while b"\r\n\r\n" not in self.buf:
            if len(self.buf) > HEAD_LIMIT:
                return None
            if not self.fill():
                return None
        head, self.buf = self.buf.split(b"\r\n\r\n", 1)
        return head + b"\r\n\r\n"

    def read_line(self):
        while b"\r\n" not in self.buf:
            if len(self.buf) > HEAD_LIMIT:
                return None
            if not self.fill():
                return None
        line, self.buf = self.buf.split(b"\r\n", 1)
        return line + b"\r\n"


def parse_headers(head):
    """Return (start_line, [(name, value_bytes_raw_line)]) without interpreting bodies."""
    text = head[:-4]
    lines = text.split(b"\r\n")
    start = lines[0]
    hdrs = []
    for ln in lines[1:]:
        if not ln:
            continue
        if b":" not in ln:
            return None, None
        name, _, val = ln.partition(b":")
        hdrs.append((name.strip().lower(), val.strip(), ln))
    return start, hdrs


def get_hdr(hdrs, name):
    for n, v, _ in hdrs:
        if n == name:
            return v
    return None


def body_framing(hdrs):
    """(mode, n): 'chunked' | ('length', n) | 'none' | 'until_eof'."""
    te = get_hdr(hdrs, b"transfer-encoding")
    if te is not None and b"chunked" in te.lower():
        return ("chunked", 0)
    cl = get_hdr(hdrs, b"content-length")
    if cl is not None:
        try:
            return ("length", int(cl))
        except ValueError:
            return ("bad", 0)
    return ("none", 0)


def relay_exact(reader, out, n):
    while n > 0:
        if not reader.buf and not reader.fill():
            return False
        take = reader.buf[:n]
        reader.buf = reader.buf[len(take):]
        try:
            out.sendall(take)
        except OSError:
            return False
        n -= len(take)
    return True


def relay_chunked(reader, out):
    while True:
        line = reader.read_line()
        if line is None:
            return False
        try:
            out.sendall(line)
        except OSError:
            return False
        try:
            size = int(line.strip().split(b";")[0], 16)
        except ValueError:
            return False
        if size == 0:
            while True:
                t = reader.read_line()
                if t is None:
                    return False
                try:
                    out.sendall(t)
                except OSError:
                    return False
                if t == b"\r\n":
                    return True
        if not relay_exact(reader, out, size + 2):
            return False


def blind(reader, out):
    """Pure byte relay — the prompt's literal behaviour, used as the degrade path."""
    if reader.buf:
        try:
            out.sendall(reader.buf)
        except OSError:
            return
        reader.buf = b""
    while True:
        try:
            d = reader.sock.recv(BUF)
        except OSError:
            break
        if not d:
            break
        try:
            out.sendall(d)
        except OSError:
            break
    try:
        out.shutdown(socket.SHUT_WR)
    except OSError:
        pass


def client_to_upstream(reader, up, pending, state):
    """Head-aware: inject Authorization on EVERY request head. Bodies relayed blind."""
    while True:
        head = reader.read_head()
        if head is None:
            break
        start, hdrs = parse_headers(head)
        if start is None:
            state["degraded"] = "unparseable-request-head"
            try:
                up.sendall(head)
            except OSError:
                pass
            blind(reader, up)
            return
        parts = start.split()
        method = parts[0].decode("latin-1", "replace") if parts else "?"
        path = parts[1].decode("latin-1", "replace") if len(parts) > 1 else "?"

        rebuilt = [start]
        for n, _v, raw in hdrs:
            if n == b"authorization":
                continue          # replace any client-supplied Authorization
            rebuilt.append(raw)
        rebuilt.append(b"Authorization: Bearer " + KEY.encode())
        newhead = b"\r\n".join(rebuilt) + b"\r\n\r\n"
        try:
            up.sendall(newhead)
        except OSError:
            break

        with state["lock"]:
            pending.append((method, path))

        mode, n = body_framing(hdrs)
        if mode == "chunked":
            if not relay_chunked(reader, up):
                break
        elif mode == "length":
            if n and not relay_exact(reader, up, n):
                break
        elif mode == "bad":
            state["degraded"] = "unparseable-request-content-length"
            blind(reader, up)
            return
        # mode == 'none': no request body; loop for the next head (keep-alive)
    try:
        up.shutdown(socket.SHUT_WR)
    except OSError:
        pass


def upstream_to_client(reader, cl, pending, state):
    """Head-aware only to read the status line. Bodies relayed blind."""
    while True:
        head = reader.read_head()
        if head is None:
            break
        start, hdrs = parse_headers(head)
        if start is None:
            state["degraded"] = "unparseable-response-head"
            try:
                cl.sendall(head)
            except OSError:
                pass
            blind(reader, cl)
            return
        bits = start.split()
        status = bits[1].decode("latin-1", "replace") if len(bits) > 1 else "?"
        try:
            cl.sendall(head)
        except OSError:
            break

        method, path = "?", "?"
        with state["lock"]:
            if pending:
                method, path = pending.popleft()
        code = 0
        try:
            code = int(status)
        except ValueError:
            pass
        if 100 <= code < 200:
            # informational: no body, and the real response still follows
            with state["lock"]:
                pending.appendleft((method, path))
            continue
        log_call(method, path, status)

        if code in (204, 304) or method == "HEAD":
            continue
        mode, n = body_framing(hdrs)
        if mode == "chunked":
            if not relay_chunked(reader, cl):
                break
        elif mode == "length":
            if n and not relay_exact(reader, cl, n):
                break
        elif mode == "none":
            # No framing: HTTP/1.1 says read to EOF. Blind for the rest (covers SSE
            # served without chunked framing) and the connection ends here.
            state["degraded"] = "response-without-framing-read-to-eof"
            blind(reader, cl)
            return
        else:
            state["degraded"] = "unparseable-response-content-length"
            blind(reader, cl)
            return
    try:
        cl.shutdown(socket.SHUT_WR)
    except OSError:
        pass


def handle(cl):
    up = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        up.connect(UPSTREAM)
    except OSError:
        try:
            cl.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
        except OSError:
            pass
        cl.close()
        log_call("-", "-", "502-upstream-unreachable")
        return
    pending = deque()
    state = {"lock": threading.Lock(), "degraded": None}
    cr, ur = Reader(cl), Reader(up)
    t1 = threading.Thread(target=client_to_upstream, args=(cr, up, pending, state), daemon=True)
    t2 = threading.Thread(target=upstream_to_client, args=(ur, cl, pending, state), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    with state["lock"]:
        while pending:
            m, p = pending.popleft()
            log_call(m, p, "NO-RESPONSE")
    if state["degraded"]:
        log_call("-", "-", "CONNECTION-DEGRADED-TO-BLIND-RELAY:" + state["degraded"])
    for s in (cl, up):
        try:
            s.close()
        except OSError:
            pass


def main():
    global KEY
    first = sys.stdin.readline()
    if not first:
        sys.stderr.write("authproxy: no key on stdin line 1 — refusing to start\n")
        sys.exit(2)
    KEY = first.rstrip("\r\n")
    if not KEY:
        sys.stderr.write("authproxy: empty key on stdin line 1 — refusing to start\n")
        sys.exit(2)
    # The key is now in memory only. Prove nothing about its VALUE is ever printed.
    sys.stderr.write("authproxy: key read from stdin (%d bytes), held in memory only\n" % len(KEY))

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(LISTEN)
    srv.listen(64)
    with open(PIDPATH, "w") as f:
        f.write("%d\n" % os.getpid())
    sys.stderr.write("authproxy: listening on %s:%d -> %s:%d  pid=%d\n"
                     % (LISTEN[0], LISTEN[1], UPSTREAM[0], UPSTREAM[1], os.getpid()))
    sys.stderr.flush()
    while True:
        try:
            conn, _addr = srv.accept()
        except OSError:
            break
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()

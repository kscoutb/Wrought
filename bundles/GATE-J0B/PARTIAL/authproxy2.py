#!/usr/bin/env python3
"""
GATE-J0B Phase 3 — the authenticating loopback proxy, CORRECTED for the transport
QEMU actually provides. authproxy.py (v1) is kept unedited as the record of what was
tried and why it failed; this file supersedes it from Phase 3 onward.

WHAT CHANGED AND WHY (measured, see raw/32-P3-pinhole-diagnosis.txt):
  QEMU's guestfwd=<addr>:<port>-tcp:<host>:<port> is NOT a per-connection forwarder.
  libslirp opens ONE chardev socket to the target AT VM STARTUP and funnels every guest
  connection into that single, always-on byte stream. v1 was written to the prompt's
  per-connection model: it opened an upstream socket eagerly on accept and tore the
  connection down when either side EOF'd. llama-server closed that idle upstream socket
  within seconds, v1 closed the one chardev with it, and the pinhole was dead for the
  rest of the VM's life — which is precisely the curl exit 28 (SYN accepted, 0 bytes) the
  guest measured.

  So v2 speaks the stream it is actually given. The client side is treated as a SEQUENCE
  OF REQUESTS that never closes on our initiative; each request gets its OWN fresh
  upstream connection, whose lifetime is that request. An idle upstream close can no
  longer take the pinhole down, because there is no idle upstream.

Rails unchanged from v1:
  - Key arrives as the FIRST LINE OF STDIN, lives in memory only, never in argv, env,
    a file, the log, or the guest.
  - Listens on 127.0.0.1 only; UPSTREAM is a constant, so no other destination is
    reachable from this process by construction.
  - apicalls.log carries ONLY: ISO-8601 timestamp, method, path, response status.
    Bodies are relayed byte-for-byte using their framing and are never interpreted.
    Diagnostics go to stderr, never to apicalls.log.
"""

import os
import socket
import sys
import threading
import time

LISTEN = ("127.0.0.1", 8081)
UPSTREAM = ("127.0.0.1", 8080)
LOGPATH = "/var/lib/wrought/j0b/apicalls.log"
PIDPATH = "/var/lib/wrought/j0b/authproxy2.pid"
BUF = 65536
HEAD_LIMIT = 262144

_log_lock = threading.Lock()
KEY = None
_stream_seq = 0
_seq_lock = threading.Lock()


def log_call(method, path, status):
    if KEY and KEY in path:
        path = path.replace(KEY, "<REDACTED>")
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with _log_lock:
        with open(LOGPATH, "a") as f:
            f.write("%s %s %s %s\n" % (ts, method, path, status))
            f.flush()


def diag(msg):
    sys.stderr.write("authproxy2: %s\n" % msg)
    sys.stderr.flush()


class Reader(object):
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
    lines = head[:-4].split(b"\r\n")
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


def framing(hdrs):
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


def relay_to_eof(reader, out):
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
            return
        if not d:
            return
        try:
            out.sendall(d)
        except OSError:
            return


def serve_one(creader, csock, sid, n):
    """One request/response exchange. Returns True to keep the client stream open."""
    head = creader.read_head()
    if head is None:
        return False                                   # client stream ended: normal
    start, hdrs = parse_headers(head)
    if start is None:
        diag("stream %d req %d: unparseable request head, closing stream" % (sid, n))
        log_call("-", "-", "BAD-REQUEST-HEAD")
        return False
    parts = start.split()
    method = parts[0].decode("latin-1", "replace") if parts else "?"
    path = parts[1].decode("latin-1", "replace") if len(parts) > 1 else "?"
    client_wants_close = (get_hdr(hdrs, b"connection") or b"").lower() == b"close"

    up = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        up.connect(UPSTREAM)                            # FRESH upstream, per request
    except OSError as e:
        diag("stream %d req %d: upstream connect failed: %s" % (sid, n, e))
        log_call(method, path, "502-upstream-unreachable")
        try:
            csock.sendall(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n"
                          b"Connection: close\r\n\r\n")
        except OSError:
            pass
        return False

    try:
        rebuilt = [start]
        for nm, _v, raw in hdrs:
            if nm == b"authorization":
                continue                                # replace, never pass through
            rebuilt.append(raw)
        rebuilt.append(b"Authorization: Bearer " + KEY.encode())
        up.sendall(b"\r\n".join(rebuilt) + b"\r\n\r\n")

        mode, ln = framing(hdrs)
        if mode == "chunked":
            if not relay_chunked(creader, up):
                log_call(method, path, "REQUEST-BODY-TRUNCATED")
                return False
        elif mode == "length":
            if ln and not relay_exact(creader, up, ln):
                log_call(method, path, "REQUEST-BODY-TRUNCATED")
                return False
        elif mode == "bad":
            log_call(method, path, "BAD-REQUEST-FRAMING")
            return False

        ureader = Reader(up)
        while True:
            rhead = ureader.read_head()
            if rhead is None:
                log_call(method, path, "NO-RESPONSE")
                return False
            rstart, rhdrs = parse_headers(rhead)
            if rstart is None:
                log_call(method, path, "BAD-RESPONSE-HEAD")
                return False
            bits = rstart.split()
            status = bits[1].decode("latin-1", "replace") if len(bits) > 1 else "?"
            try:
                csock.sendall(rhead)
            except OSError:
                return False
            try:
                code = int(status)
            except ValueError:
                code = 0
            if 100 <= code < 200:
                continue                                 # informational; real one follows
            log_call(method, path, status)

            if code in (204, 304) or method == "HEAD":
                body = "none"
            else:
                body = framing(rhdrs)[0]
            if body == "chunked":
                if not relay_chunked(ureader, csock):
                    return False
            elif body == "length":
                if not relay_exact(ureader, csock, framing(rhdrs)[1]):
                    return False
            elif body == "none" and not (code in (204, 304) or method == "HEAD"):
                # No determinate framing: HTTP/1.1 says read to EOF. We can relay it,
                # but the stream boundary is then unrecoverable, so the client stream
                # must end with it.
                diag("stream %d req %d: response without framing; relaying to EOF and "
                     "ending the stream" % (sid, n))
                relay_to_eof(ureader, csock)
                return False
            break

        srv_close = (get_hdr(rhdrs, b"connection") or b"").lower() == b"close"
        return not (client_wants_close or srv_close)
    finally:
        try:
            up.close()
        except OSError:
            pass


def handle(csock):
    global _stream_seq
    with _seq_lock:
        _stream_seq += 1
        sid = _stream_seq
    peer = ""
    try:
        peer = "%s:%d" % csock.getpeername()
    except OSError:
        pass
    diag("stream %d opened from %s" % (sid, peer))
    creader = Reader(csock)
    n = 0
    try:
        while True:
            n += 1
            if not serve_one(creader, csock, sid, n):
                break
    except Exception as e:                               # never let one stream kill the proxy
        diag("stream %d: unexpected %r" % (sid, e))
    finally:
        diag("stream %d closed after %d request(s)" % (sid, n - 1))
        try:
            csock.close()
        except OSError:
            pass


def main():
    global KEY
    first = sys.stdin.readline()
    if not first:
        sys.stderr.write("authproxy2: no key on stdin line 1 — refusing to start\n")
        sys.exit(2)
    KEY = first.rstrip("\r\n")
    if not KEY:
        sys.stderr.write("authproxy2: empty key on stdin line 1 — refusing to start\n")
        sys.exit(2)
    diag("key read from stdin (%d bytes), held in memory only" % len(KEY))

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(LISTEN)
    srv.listen(64)
    with open(PIDPATH, "w") as f:
        f.write("%d\n" % os.getpid())
    diag("listening on %s:%d -> %s:%d  pid=%d" % (LISTEN[0], LISTEN[1],
                                                  UPSTREAM[0], UPSTREAM[1], os.getpid()))
    while True:
        try:
            conn, _ = srv.accept()
        except OSError:
            break
        threading.Thread(target=handle, args=(conn,), daemon=True).start()


if __name__ == "__main__":
    main()

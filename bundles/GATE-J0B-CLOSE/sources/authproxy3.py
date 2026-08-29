#!/usr/bin/env python3
"""
GATE-J0B-CLOSE Phase 3 — authproxy3.py. authproxy2.py, plus the two behaviours F-5 needs.
authproxy2.py is kept UNEDITED as the record of what it was; this file supersedes it.

F-5, as GATE-J0B-RESUME measured it (bundles/GATE-J0B-RESUME/REPORT-J0B.md §4, raw/62):
  goose issues `stream:true` with `max_tokens` UNSET. Abandoning the client does NOT stop
  llama-server, which keeps generating to its context limit and serves requests serially, so
  every later call — goose's own retries and a diagnostic curl alike — queues behind ~9
  abandoned unbounded generations and appears to hang. The SLIRP guestfwd then degraded and
  answered instantly with an empty HTTP/0.9 response until the guest was rebooted.

TWO CHANGES, both aimed at that chain:

(a) BOUNDED GENERATION. Any `chat/completions` request whose `max_tokens` is null or absent
    gets `max_tokens` injected. A request that sets its own value is left ALONE — this bounds
    the failure mode, it does not override a caller.

    THE VALUE IS NOT INVENTED (CLAUDE.md hard rule 1). It is 24000, taken from
    `pins.lock` `serving.reasoning_budget: 24000`, whose own committed derivation
    (build-evidence/session-13/03-truncation/S13-reasoning-budget-derivation.txt, n=78) records
    it as "the same bound already ratified for --escalation-max-tokens". It is the only ratified
    per-generation token bound in `pins.lock`. Against `ctx_size: 65536` it cuts the worst-case
    abandoned generation by ~2.7x. NOTE FOR THE FERRY: the NUMBER is ratified, but the proxy
    KEY that carries it is new, so it is written up in PROPOSED-PINS-DELTA rather than minted
    here as settled.

(b) CANCEL ON CLIENT DISCONNECT. authproxy2 closes its upstream socket in serve_one's `finally`,
    so it did already cancel — but only once it NOTICED, and it noticed only when it next tried
    to write to the client. While it blocks in `ureader.read_head()` waiting for a first response
    byte that an unbounded generation will not send for minutes, it never tries to write, so it
    never notices. That is exactly the wedge window. UpReader therefore selects on the UPSTREAM
    and the CLIENT together: a client EOF aborts the read, and the existing `finally` closes
    upstream immediately, which is what cancels the abandoned generation.

    The client is peeked with MSG_PEEK, never consumed, so a pipelined request is not eaten;
    on seeing real bytes the watch is dropped so select cannot spin. STATED LIMIT: a client that
    half-closes with shutdown(SHUT_WR) and then keeps reading would be read as gone. Nothing on
    this path does that, and the alternative is not noticing a real disconnect.

EVERYTHING ELSE IS authproxy2 BYTE-FOR-BYTE — key on stdin line 1 and nowhere else, Authorization
replaced never forwarded, a FRESH upstream connection per request, the SSE/chunked relay, and
apicalls.log's timestamp/method/path/status contract. Injection is reported to STDERR only,
because authproxy2's rule is that diagnostics never enter apicalls.log.

Fails OPEN: a body that is not JSON, or not a JSON object, is relayed byte-for-byte unchanged.
"""

import json
import os
import select
import socket
import sys
import threading
import time

# pins.lock serving.reasoning_budget — see the docstring. Not a value chosen by this gate.
MAX_TOKENS_BOUND = 24000

LISTEN = ("127.0.0.1", 8081)
UPSTREAM = ("127.0.0.1", 8080)
LOGPATH = "/var/lib/wrought/j0b/apicalls.log"
PIDPATH = "/var/lib/wrought/j0b/authproxy3.pid"
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
    sys.stderr.write("authproxy3: %s\n" % msg)
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


class UpReader(Reader):
    """A Reader on the UPSTREAM socket that also watches the CLIENT for a disconnect.

    This is change (b). authproxy2 used a plain Reader here, so while it blocked waiting for
    the first response byte it could not learn that the client had gone, and the abandoned
    generation ran on. Selecting on both sockets closes that window; serve_one's existing
    `finally: up.close()` is what actually cancels it.
    """

    def __init__(self, sock, watch):
        Reader.__init__(self, sock)
        self.watch = watch
        self.client_gone = False

    def fill(self):
        if self.eof:
            return False
        while True:
            watching = [self.sock] if self.watch is None else [self.sock, self.watch]
            try:
                ready, _, _ = select.select(watching, [], [])
            except OSError:
                self.eof = True
                return False
            if self.watch is not None and self.watch in ready:
                try:
                    peek = self.watch.recv(BUF, socket.MSG_PEEK)
                except OSError:
                    peek = b""
                if not peek:
                    self.client_gone = True     # EOF from the client: it is gone
                    self.eof = True
                    return False
                self.watch = None               # real bytes, peeked not consumed; stop spinning
            if self.sock in ready:
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


def read_body(reader, hdrs):
    """Buffer a whole request body. Used ONLY on the injection path (change (a)).

    Returns the body bytes, or None if the client stream ended mid-body.
    """
    mode, ln = framing(hdrs)
    if mode == "none":
        return b""
    if mode == "length":
        buf = b""
        while len(buf) < ln:
            if not reader.buf and not reader.fill():
                return None
            take = reader.buf[:ln - len(buf)]
            reader.buf = reader.buf[len(take):]
            buf += take
        return buf
    if mode == "chunked":
        buf = b""
        while True:
            line = reader.read_line()
            if line is None:
                return None
            try:
                size = int(line.strip().split(b";")[0], 16)
            except ValueError:
                return None
            if size == 0:
                while True:
                    t = reader.read_line()
                    if t is None:
                        return None
                    if t == b"\r\n":
                        return buf
            need = size + 2                      # the chunk and its trailing CRLF
            chunk = b""
            while len(chunk) < need:
                if not reader.buf and not reader.fill():
                    return None
                take = reader.buf[:need - len(chunk)]
                reader.buf = reader.buf[len(take):]
                chunk += take
            buf += chunk[:size]
    return None


def inject_max_tokens(body):
    """Change (a). Returns (body, what_happened). FAILS OPEN — anything unparseable is
    returned byte-for-byte, because relaying a request unchanged is always safe and
    rewriting one we do not understand is not."""
    try:
        obj = json.loads(body)
    except Exception:
        return body, "not-json: relayed verbatim"
    if not isinstance(obj, dict):
        return body, "not a JSON object: relayed verbatim"
    if obj.get("max_tokens") is None:            # covers BOTH absent and explicit null
        obj["max_tokens"] = MAX_TOKENS_BOUND
        return json.dumps(obj).encode(), "max_tokens INJECTED = %d" % MAX_TOKENS_BOUND
    return body, "max_tokens already set by client (%r): left alone" % (obj["max_tokens"],)


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

    # ---- change (a): bound the generation on the chat path. The body is buffered HERE,
    # before the upstream connect, because rewriting it changes Content-Length and the head
    # therefore cannot be sent until the new length is known.
    inject = (method == "POST") and (b"chat/completions" in start)
    newbody = None
    if inject:
        raw_body = read_body(creader, hdrs)
        if raw_body is None:
            diag("stream %d req %d: client stream ended mid-body" % (sid, n))
            log_call(method, path, "REQUEST-BODY-TRUNCATED")
            return False
        newbody, what = inject_max_tokens(raw_body)
        diag("stream %d req %d: %s (body %d -> %d bytes)"
             % (sid, n, what, len(raw_body), len(newbody)))

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
            if inject and nm in (b"content-length", b"transfer-encoding"):
                continue                                # re-framed below with the new length
            rebuilt.append(raw)
        rebuilt.append(b"Authorization: Bearer " + KEY.encode())
        if inject:
            rebuilt.append(b"Content-Length: " + str(len(newbody)).encode())
        up.sendall(b"\r\n".join(rebuilt) + b"\r\n\r\n")

        if inject:
            up.sendall(newbody)                         # already buffered and re-framed
        else:
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

        ureader = UpReader(up, csock)                   # change (b): watch the client too
        while True:
            rhead = ureader.read_head()
            if rhead is None:
                if ureader.client_gone:
                    # The wedge case. Returning here runs serve_one's `finally: up.close()`,
                    # which drops the upstream socket and cancels the abandoned generation
                    # instead of leaving it to run to the context limit.
                    diag("stream %d req %d: CLIENT GONE while awaiting upstream; "
                         "closing upstream to cancel the generation" % (sid, n))
                    log_call(method, path, "CLIENT-GONE-UPSTREAM-CANCELLED")
                else:
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
        sys.stderr.write("authproxy3: no key on stdin line 1 — refusing to start\n")
        sys.exit(2)
    KEY = first.rstrip("\r\n")
    if not KEY:
        sys.stderr.write("authproxy3: empty key on stdin line 1 — refusing to start\n")
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

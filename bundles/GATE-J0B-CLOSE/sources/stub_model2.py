#!/usr/bin/env python3
"""
GATE-J0B-CLOSE Phase 2 — STUB endpoint, v2: SPEAKS SSE.

v1 answered with a plain JSON body. Measured consequence: goose sends `stream: true`
(cap/req-02.json) and reported "The model returned an empty response", then retried 4x.
That is a real datapoint about goose's client and is kept in raw/25 rather than edited away.
v2 answers `stream:true` requests as `text/event-stream`, which is what goose asked for.

Modes, from /home/probe/stub-mode:
    observe   -> stream a plain assistant message
    toolcall  -> stream a tool_call built from stub-tool-name / stub-tool-args on the FIRST
                 POST that carries tools, then plain text afterwards so the turn terminates.
No credential is present in this process. It binds 127.0.0.1 inside a disposable guest.
"""
import http.server, json, os, time, sys

CAP = "/home/probe/stub-capture"
os.makedirs(CAP, exist_ok=True)
SEQ = {"n": 0, "tool_emitted": False}


def mode():
    try:
        return open("/home/probe/stub-mode").read().strip()
    except OSError:
        return "observe"


def readf(p, d=""):
    try:
        return open(p).read().strip()
    except OSError:
        return d


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _sse(self, chunks):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        for c in chunks:
            payload = b"data: " + (c if isinstance(c, bytes) else json.dumps(c).encode()) + b"\n\n"
            self.wfile.write(b"%x\r\n" % len(payload) + payload + b"\r\n")
            self.wfile.flush()
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()

    def do_GET(self):
        with open(os.path.join(CAP, "paths.log"), "a") as f:
            f.write("GET %s\n" % self.path)
        if "models" in self.path:
            self._json({"object": "list", "data": [
                {"id": "primary-qwen27b", "object": "model", "owned_by": "wrought"}]})
        else:
            self._json({"ok": True})

    def do_POST(self):
        n = SEQ["n"] = SEQ["n"] + 1
        ln = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(ln) if ln else b""
        try:
            body = json.loads(raw)
        except Exception:
            body = {}
        has_tools = bool(body.get("tools"))
        with open(os.path.join(CAP, "paths.log"), "a") as f:
            f.write("POST %s len=%d seq=%d stream=%s tools=%d\n"
                    % (self.path, len(raw), n, body.get("stream"), len(body.get("tools") or [])))
        with open(os.path.join(CAP, "req-%02d.json" % n), "wb") as f:
            f.write(raw)

        cid = "stub-%d" % n
        created = int(time.time())
        model = body.get("model", "primary-qwen27b")

        def frame(delta, finish=None):
            return {"id": cid, "object": "chat.completion.chunk", "created": created,
                    "model": model,
                    "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}

        usage = {"id": cid, "object": "chat.completion.chunk", "created": created,
                 "model": model, "choices": [],
                 "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}

        emit_tool = (mode() == "toolcall" and has_tools and not SEQ["tool_emitted"])
        if emit_tool:
            SEQ["tool_emitted"] = True
            name = readf("/home/probe/stub-tool-name", "write")
            args = readf("/home/probe/stub-tool-args", "{}")
            chunks = [
                frame({"role": "assistant", "content": None, "tool_calls": [
                    {"index": 0, "id": "call_stub_1", "type": "function",
                     "function": {"name": name, "arguments": ""}}]}),
                frame({"tool_calls": [{"index": 0, "function": {"arguments": args}}]}),
                frame({}, "tool_calls"),
                usage, b"[DONE]",
            ]
        else:
            chunks = [
                frame({"role": "assistant", "content": ""}),
                frame({"content": "STUB-OK"}),
                frame({}, "stop"),
                usage, b"[DONE]",
            ]

        if body.get("stream"):
            self._sse(chunks)
        else:
            self._json({"id": cid, "object": "chat.completion", "created": created, "model": model,
                        "choices": [{"index": 0, "finish_reason": "stop",
                                     "message": {"role": "assistant", "content": "STUB-OK"}}],
                        "usage": usage["usage"]})


if __name__ == "__main__":
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 9999), H)
    sys.stderr.write("stub2 listening on 127.0.0.1:9999\n")
    srv.serve_forever()

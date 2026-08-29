#!/usr/bin/env python3
"""
GATE-J0B-CLOSE Phase 2 — a STUB OpenAI-compatible endpoint, run INSIDE the guest.

Why this exists. The prompt forbids confirming the extension schema "by a config parse" and asks
for goose LISTING its tools or a probe run that WRITES A FILE. Both need a model turn, and the
real model is gated behind a key that must never enter a guest (rails §5). A stub decouples the
two questions completely:

    Q1  does goose ADVERTISE a filesystem-write tool to the model?   -> the request body it sends
    Q2  will goose EXECUTE that tool if the model calls it?          -> we make the stub call it

Neither answer depends on the real model's willingness to use a tool, which is the confound that
would otherwise sit inside the Phase-4 work-product test. This process speaks only to 127.0.0.1
inside a disposable guest, holds no credential, and is deleted with the guest.

MODE is read from the file /home/probe/stub-mode:
    observe   -> answer with a plain assistant message (captures the advertised tool list)
    toolcall  -> answer with a tool_call built from TOOL_NAME/TOOL_ARGS files, then a plain message
"""
import http.server, json, os, time, sys

CAP = "/home/probe/stub-capture"
os.makedirs(CAP, exist_ok=True)
SEQ = {"n": 0}


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

    def _send(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        with open(os.path.join(CAP, "paths.log"), "a") as f:
            f.write("GET %s\n" % self.path)
        if "models" in self.path:
            self._send({"object": "list", "data": [
                {"id": "primary-qwen27b", "object": "model", "owned_by": "wrought"}]})
        else:
            self._send({"ok": True})

    def do_POST(self):
        n = SEQ["n"] = SEQ["n"] + 1
        ln = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(ln) if ln else b""
        with open(os.path.join(CAP, "paths.log"), "a") as f:
            f.write("POST %s len=%d seq=%d\n" % (self.path, len(raw), n))
        with open(os.path.join(CAP, "req-%02d.json" % n), "wb") as f:
            f.write(raw)

        base = {"id": "stub-%d" % n, "object": "chat.completion",
                "created": int(time.time()), "model": "primary-qwen27b",
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}

        # A tool_call is emitted only on the FIRST post of a toolcall run; the follow-up post
        # (which carries the tool RESULT back) is answered with plain text so the turn terminates.
        if mode() == "toolcall" and n == 1:
            name = readf("/home/probe/stub-tool-name", "developer__text_editor")
            args = readf("/home/probe/stub-tool-args", "{}")
            base["choices"] = [{"index": 0, "finish_reason": "tool_calls", "message": {
                "role": "assistant", "content": None, "tool_calls": [
                    {"id": "call_stub_1", "type": "function",
                     "function": {"name": name, "arguments": args}}]}}]
        else:
            base["choices"] = [{"index": 0, "finish_reason": "stop", "message": {
                "role": "assistant", "content": "STUB-OK"}}]
        self._send(base)


if __name__ == "__main__":
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 9999), H)
    sys.stderr.write("stub listening on 127.0.0.1:9999\n")
    srv.serve_forever()

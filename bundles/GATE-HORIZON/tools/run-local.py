#!/usr/bin/env python3
"""Drive the RESIDENT local model (127.0.0.1:8080, OpenAI-compatible) — shared, never restarted.
Auth: key read from the path in env LOCAL_KEY_FILE (header only); if unset, sent with no auth.

APPENDIX B VERBATIM IS KEPT ALONGSIDE AS `run-local.py.appendix-verbatim`. THIS FILE CARRIES
THREE MINIMAL, MEASURED DEVIATIONS, EACH FORCED BY A MEASUREMENT AND NONE BY PREFERENCE
(GATE-HORIZON, 2026-08-31; the prompt's own closing clause: do the correct thing on the box and
say plainly what you changed).

  1. SUMMARIZE_MAX_TOKENS replaces the hard-coded 512. The resident profile serves
     `--reasoning on --reasoning-budget 24000`, so the model spends the WHOLE completion budget
     on reasoning before emitting any content. MEASURED on bin/assert-power-profile:
         max_tokens=512   -> finish_reason=length, 512 completion tokens, reasoning 2069 B,
                             content 0 B
         max_tokens=2048  -> finish_reason=length, 2048 completion tokens, reasoning 8256 B,
                             content 0 B
         max_tokens=25000 -> finish_reason=stop,   2254 completion tokens, reasoning 8230 B,
                             content 637 B
     Appendix B AS WRITTEN produces an EMPTY summary for every file under the served profile,
     while printing "summarized N/N files" and exiting 0 -- rails §18 exactly: the exit code is
     not the work product. Verified by running it: 3/3 files, 3/3 empty.
  2. reasoning_content FALLBACK, the same pattern the committed bin/gate-review-send-panel
     already uses (`used_reasoning_fallback`). If content is empty but reasoning is not, the
     reasoning is preserved and LABELLED rather than the call being silently lost.
  3. RESUME. An existing non-trivial output file is skipped, so a killed run resumes instead of
     re-spending an hour of GPU. The prompt asks for exactly this property at the phase level.

Nothing else is changed. The prompts, the modes, the CLI, the truncation bound and the
credential handling are Appendix B's.
Modes:
  run-local.py summarize <file-list.txt> <outdir>   one grounded summary per listed path
  run-local.py ask <packet.txt> <ask.txt> <outfile> one call over packet+ask (baseline panelist)
"""
import json, os, sys, urllib.request, urllib.error

URL = os.environ.get("LOCAL_URL", "http://127.0.0.1:8080/v1/chat/completions")
MODEL = os.environ.get("LOCAL_MODEL", "primary-qwen27b")
# Must exceed the served --reasoning-budget (24000) or content is never reached. See docstring.
SUMMARIZE_MAX_TOKENS = int(os.environ.get("SUMMARIZE_MAX_TOKENS", "25000"))
ASK_MAX_TOKENS = int(os.environ.get("ASK_MAX_TOKENS", "32000"))

def key_header():
    p = os.environ.get("LOCAL_KEY_FILE")
    if p and os.path.exists(p):
        return {"Authorization": "Bearer " + open(p).read().strip()}
    return {}

def call(messages, max_tokens):
    body = {"model": MODEL, "stream": False, "max_tokens": max_tokens, "messages": messages}
    hdr = {"Content-Type": "application/json"}; hdr.update(key_header())
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers=hdr)
    with urllib.request.urlopen(req, timeout=1800) as resp:
        r = json.load(resp)
    m = r["choices"][0]["message"]
    text = m.get("content") or ""
    if not text.strip():
        reasoning = m.get("reasoning_content") or ""
        if reasoning.strip():
            return ("_(model returned no `content`; the following is its `reasoning_content`, "
                    "preserved so the call is not lost -- NOT a summary)_\n\n" + reasoning)
    return text

def summarize(list_f, outdir):
    os.makedirs(outdir, exist_ok=True)
    paths = [l.strip() for l in open(list_f) if l.strip()]
    sysmsg = ("You summarize one source file. Output 3-6 lines: purpose; key functions or classes "
              "BY EXACT NAME as they appear; direct imports/dependencies; any obvious risk. "
              "Cite only names that literally appear in the file. No preamble.")
    done = 0
    for path in paths:
        if not os.path.exists(path): continue
        dest = os.path.join(outdir, path.replace("/", "__") + ".md")
        if os.path.exists(dest) and os.path.getsize(dest) > 200:
            done += 1; continue          # resume: already summarized, do not re-spend the GPU
        src = open(path, encoding="utf-8", errors="replace").read()
        if len(src) > 48000: src = src[:48000] + "\n...[truncated]"
        try:
            out = call([{"role": "system", "content": sysmsg},
                        {"role": "user", "content": f"FILE: {path}\n\n{src}"}], SUMMARIZE_MAX_TOKENS)
        except Exception as e:
            out = f"ERROR summarizing: {e}"
        safe = path.replace("/", "__")
        open(os.path.join(outdir, safe + ".md"), "w", encoding="utf-8").write(f"# {path}\n{out}\n")
        done += 1
    print(f"summarized {done}/{len(paths)} files -> {outdir}")

def ask(packet_f, ask_f, outfile):
    packet = open(packet_f, encoding="utf-8").read()
    q = open(ask_f, encoding="utf-8").read()
    sysmsg = ("You are a staff-level software architect doing a gap analysis and roadmap. "
              "Answer every lettered part concretely.")
    try:
        out = call([{"role": "system", "content": sysmsg},
                    {"role": "user", "content": packet + "\n\n" + q}], ASK_MAX_TOKENS)
    except Exception as e:
        out = f"ERROR: {e}"
    open(outfile, "w", encoding="utf-8").write(out)
    print(f"baseline -> {outfile} ({len(out)} chars)")

def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    if sys.argv[1] == "summarize": summarize(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "ask": ask(sys.argv[2], sys.argv[3], sys.argv[4])
    else: sys.exit(__doc__)

if __name__ == "__main__":
    main()

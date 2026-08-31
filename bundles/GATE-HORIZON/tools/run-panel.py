#!/usr/bin/env python3
"""External gap-review panel over OpenRouter. Key from CREDENTIALS_DIRECTORY, header only.
Usage: run-panel.py <packet.txt> <ask.txt> <outdir>  (launched under systemd LoadCredentialEncrypted)"""
import json, os, sys, time, urllib.request, urllib.error

BASE = "https://openrouter.ai/api/v1"
CEILING_USD = 15.0
MAX_TOKENS = 40000
LINEAGES = ["google", "openai", "deepseek", "z-ai", "x-ai", "mistralai", "qwen"]  # try in order, one each of first 5 that have a ZDR model

def key():
    d = os.environ.get("CREDENTIALS_DIRECTORY")
    if not d: sys.exit("no CREDENTIALS_DIRECTORY; launch under systemd LoadCredentialEncrypted")
    return (open(os.path.join(d, "openrouter-review-key")).read().strip())

def GET(path, k):
    r = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {k}"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.load(resp)

def POST(body, k):
    data = json.dumps(body).encode()
    r = urllib.request.Request(BASE + "/chat/completions", data=data,
        headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=1200) as resp:
        return json.load(resp)

def pick_models(zdr_ids):
    chosen, seen = [], set()
    for lin in LINEAGES:
        if len(chosen) >= 5: break
        if lin in seen: continue
        cands = [m for m in zdr_ids if m.split("/")[0] == lin]
        # prefer non-reasoning-pro variants
        cands.sort(key=lambda s: ("pro" in s or "thinking" in s or "reasoning" in s, len(s)))
        if cands:
            chosen.append(cands[0]); seen.add(lin)
    return chosen

def main():
    packet_f, ask_f, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    k = key()
    keyinfo = GET("/key", k).get("data", {})
    rem = keyinfo.get("limit_remaining")
    if rem is not None and rem < 16:
        sys.exit(f"limit_remaining {rem} < 16; aborting")
    models = GET("/models?zdr=true", k).get("data", [])
    zdr_ids = [m["id"] for m in models]
    chosen = pick_models(zdr_ids)
    if not chosen: sys.exit("no ZDR-eligible models resolved")
    packet = open(packet_f, encoding="utf-8").read()
    ask = open(ask_f, encoding="utf-8").read()
    user_msg = packet + "\n\n" + ask
    sysmsg = ("You are an independent staff-level software architect performing a gap analysis "
              "and roadmap, not a code review. Be concrete, honest, and specific.")
    total = 0.0
    panel = []
    for mid in chosen:
        lin = mid.split("/")[0]
        # rough pre-call bound: assume ~4 chars/token input, output at max_tokens
        est_in = len(user_msg)//4
        # skip if plausibly over ceiling (crude guard; real cost read after)
        if total >= CEILING_USD:
            panel.append((mid, "SKIPPED: ceiling reached", 0.0, 0, 0)); continue
        body = {"model": mid,
                "provider": {"zdr": True, "data_collection": "deny"},
                "usage": {"include": True},
                "max_tokens": MAX_TOKENS, "stream": False,
                "messages": [{"role": "system", "content": sysmsg},
                             {"role": "user", "content": user_msg}]}
        try:
            resp = POST(body, k)
        except urllib.error.HTTPError as e:
            panel.append((mid, f"HTTPError {e.code}: {e.read()[:300]!r}", 0.0, 0, 0)); continue
        except Exception as e:
            panel.append((mid, f"ERROR: {e}", 0.0, 0, 0)); continue
        content = ""
        try: content = resp["choices"][0]["message"]["content"] or ""
        except Exception: content = json.dumps(resp)[:2000]
        usage = resp.get("usage", {}) or {}
        cost = float(usage.get("cost", 0) or 0)
        total += cost
        slug = mid.replace("/", "-")
        open(os.path.join(outdir, f"{lin}-{slug}.md"), "w", encoding="utf-8").write(content)
        open(os.path.join(outdir, f"{lin}-{slug}.raw.json"), "w", encoding="utf-8").write(json.dumps(resp, indent=1))
        panel.append((mid, "OK", cost, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)))
        time.sleep(1)
    with open(os.path.join(outdir, "PANEL.md"), "w", encoding="utf-8") as f:
        f.write(f"# PANEL — external gap-review\nkey limit_remaining at start: {rem}\nceiling: ${CEILING_USD}\n\n")
        f.write("| model | status | in | out | cost |\n|---|---|---|---|---|\n")
        for mid, st, cost, i, o in panel:
            f.write(f"| {mid} | {st} | {i} | {o} | ${cost:.4f} |\n")
        f.write(f"\n**total spend: ${total:.4f}**\n")
    print(f"panel done: {sum(1 for p in panel if p[1]=='OK')}/{len(panel)} OK, ${total:.4f}")

if __name__ == "__main__":
    main()

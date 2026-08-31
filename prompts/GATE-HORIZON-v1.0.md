# GATE-HORIZON — complete operator prompt (self-contained; a fresh Claude Code session on the box runs this end to end)

YOU ARE the local Claude Code executor on forge-mini. This file is your COMPLETE instructions — read it fully, then execute Phases 0–7 in order. You need nothing outside the box. When done you will have: stabilized the security docs, run a free local review pass and a paid external frontier panel, consolidated both into a candidate 1.0 roadmap, written up open questions as a research prompt, and published everything to the courier for the off-box advisor. This run is itself a prototype of the 1.0 goal: one agent delegating bulk to a local model and judgment to a cloud panel toward one objective.

## ORIENT (do this first, before any phase)
- Foundry repo: `/home/kalib/foundry`, branch `review-fixes`. Courier: `/home/kalib/courier/Wrought`.
- `cd /home/kalib/foundry && git status` — confirm branch `review-fixes`; note if dirty, do not discard. `git -C /home/kalib/courier/Wrought pull`.
- READ, to load the operating rules and current state before acting: `docs/EXECUTOR-RAILS.md`, `docs/PHASE-J-STATE.md`, and the courier `QUEUE.md`. Honor the rails you read there over anything ambiguous here.
- Record this gate: copy this file to `/home/kalib/courier/Wrought/prompts/GATE-HORIZON.md`, add a `GATE-HORIZON | RUNNING` row to `QUEUE.md`, commit and push. That is your first courier action.

## RAILS (hold all of these)
- Byte-freeze `/var/lib/wrought/state/orchestrator.db{,-wal,-shm}` to `raw/00` now and `raw/99` at the end; both must be identical (HOLD). Never write under `state/`.
- Never restart or overload `wrought-inference.service` — you SHARE the resident model, you do not stop it (the gate13 lesson).
- Run `bin/wrought-precommit-secret-scan` (rails §5.1) at exit 0 before every commit, every push, and over anything that leaves the box. Exit 2 is a refusal, not a pass.
- `docs/PHASE-J-STATE.md` cannot be written whole (the hook denies it) — use surgical `Edit`; if an edit is denied, record the refused block and continue, never rephrase to evade.
- TWO credentials, each value only ever in an HTTP `Authorization` header — never argv, never a file you write, never a log: the external review key sealed as `openrouter-review-key`; the resident inference key reached the way the manufacturing path already reaches `127.0.0.1:8080` (you supply its path to `run-local.py` via `LOCAL_KEY_FILE`; if the resident server needs no key in this config, leave it unset). If either credential is unavailable, do that stream as far as you can and record the gap — do not improvise a key path.

## TIME, TOKENS, CHECKPOINTS
- Aim to finish in ~4 hours; you may take up to 12. COMMIT AND PUSH after every phase so a killed run resumes from the last pushed phase.
- Token discipline is a first-class constraint AND a thing this gate measures: push bulk reading/summarizing to the free local model, keep your own context lean (read digests, not raw files), and record your own approximate token/turn cost per phase in the final report.

## SCRIPTS — create these two files exactly (full source in Appendix A and B at the bottom), then `python3 -m py_compile` each before use. If paste damaged their indentation, the Appendix is authoritative; regenerate them cleanly.
- `review/horizon/run-panel.py` (Appendix A) — external OpenRouter panel.
- `review/horizon/run-local.py` (Appendix B) — resident local model.

## PHASE 0 — record the GATE-ORACLE-ISOLATION verdict
Re-verify against `bundles/GATE-ORACLE-ISOLATION/` (manifest begins `33291886`, base `52fade2`); trust the bundle over this text if they differ. VERDICT: ACCEPTED (advisor 2026-08-31), exemplary — it measured that a second candidate uid is both unavailable (Ubuntu `unpriv_bwrap` AppArmor denies `capability setuid` unconditionally, atop a seccomp filter denying nested-userns clone) and insufficient (candidate code IS the pytest process; committed fixture `exit0c` proves any relocation-based fix still passes). Net state at HEAD: Faces A (import hijack) and C (decision-code replacement) CLOSED and fixture-proven; Face B (a candidate forging its own single in-process verdict) is detected-not-prevented and contained by the network-less capability-dropped disposable sandbox to one tool falsely stamped COMPLETED, never escape or persistence. Write it to `bundles/GATE-ORACLE-ISOLATION/ADJUDICATION.md`, set that QUEUE row `ADJUDICATED`, commit, push.

## PHASE 1 — STABILIZE the docs (surgical `Edit` to `docs/PHASE-J-STATE.md`)
(a) Restate the invariant honestly — `COMPLETED ⟹ the oracle passed` holds against escape and persistence (Faces A, C) but NOT against an adversarial candidate forging its own in-process verdict (Face B). (b) Put that sentence in NON-CLAIMS verbatim. (c) Record the COMPENSATING CONTROL — a COMPLETED artifact is PROVISIONALLY verified and must be re-verified out-of-band before it is trusted or shipped. (d) Record KNOWN-OPEN item 16's real fix and cost — candidate tests must run out of the reporting process, closing Face B but eliminating the in-process coverage check. Commit behind a 5.1 scan, push. Do NOT tag; the operator tags `review-rc3` after the advisor adjudicates this gate.

## PHASE 2 — LOCAL REPO-MAP (free, air-gapped, first real-work proof of the local model)
Build a file list of every script under `bin/` and every module under `src/` (`git ls-files bin src | grep -E '\.(py|sh)$|^bin/[^.]+$'` then refine). Run `run-local.py summarize <list> review/horizon/repo-map/`. Then verify groundedness cheaply: for a sample of the names each summary cites, `grep` the tree; a summary citing invented symbols is marked UNRELIABLE and not trusted. Assemble `review/horizon/REPO-MAP.md` from the reliable summaries. Record in the eventual report how long it took and how many summaries were reliable. Commit, push.

## PHASE 3 — assemble the HORIZON PACKET under `review/horizon/packet/` (ARCHITECTURE + STATE + VISION, not raw source)
(1) `ARCHITECTURE.md` — a 2–4 page overview YOU write, curating REPO-MAP (do NOT ship raw local summaries to the panel): the substrate (KVM/QEMU disposable guests, Strix Point node, RX 7900 XTX, Vulkan llama.cpp, UMA/NPU), orchestrator and FSM, the deterministic oracle and its sandbox, the autonomous runner and containment, the Goose agent surface, the git-courier gate protocol and its context discipline, the model tiers. (2) the live state docs — `PHASE-J-STATE.md` as stabilized, KNOWN-OPEN, NON-CLAIMS, `pins.lock`. (3) `SECURITY-HISTORY.md` — a short digest of the code review and the two fix gates so the panel does not re-litigate hardened ground. (4) `VISION.md`, verbatim from the VISION block below. Concatenate the four into `packet/PACKET.txt`; write `packet/ASK.txt` verbatim from the ASK block below; record PACKET size and estimated tokens; scan at exit 0; commit, push.

## PHASE 4 — EXTERNAL PANEL
`python3 -m py_compile review/horizon/run-panel.py`, then launch:
`sudo systemd-run --wait --collect --quiet --pipe -p User=kalib -p LoadCredentialEncrypted=openrouter-review-key:/etc/credstore.encrypted/openrouter-review-key /usr/bin/python3 /home/kalib/foundry/review/horizon/run-panel.py /home/kalib/foundry/review/horizon/packet/PACKET.txt /home/kalib/foundry/review/horizon/packet/ASK.txt /home/kalib/foundry/review/horizon/`
It resolves current ZDR-eligible models (one per non-Anthropic lineage, up to 5, preferring non-"-pro" variants), enforces the 15-dollar ceiling, saves each review and `PANEL.md`. Commit and push whatever returned, even on a model error.

## PHASE 4b — LOCAL BASELINE (free air-gapped baseline panelist, not a peer vote)
`LOCAL_KEY_FILE=<the resident inference key path> python3 review/horizon/run-local.py ask review/horizon/packet/PACKET.txt review/horizon/packet/ASK.txt review/horizon/LOCAL-BASELINE.md`. Commit, push.

## PHASE 5 — CONSOLIDATE (the synthesis the operator asked you to do)
Read every panel review, the local baseline, and REPO-MAP. Write `review/horizon/CONSOLIDATED-ROADMAP.md`: a per-capability gap map (as-built / missing / hardest gap, noting cross-lineage agreement); one ordered critical path of stable, independently-useful milestones to 1.0 with rough sizes; a cut/defer list; the compliance-and-safety control set the 1.0 must carry; and the top risks each with a first de-risking experiment. Mark it a CANDIDATE synthesis for the advisor, not a verdict. Commit, push.

## PHASE 6 — RESEARCH ROUND
Write `review/horizon/RESEARCH-QUESTIONS.md`: the lingering best-practices and unknown-technical questions this review surfaced, one section per subsystem (e.g. best local video-gen and 3D-avatar stacks under Vulkan on an RX 7900 XTX; the strongest open computer-use/vision loop drivable by a ~27B local model; what genuinely offloads to the Strix NPU; provenance-checking for web-sourced public-domain assets; the out-of-process oracle redesign for Face B), each framed as a crisp research prompt a future research gate could run. Commit, push.

## PHASE 7 — wind-down
`raw/99` freeze re-assert (must HOLD). Scan the courier tree at exit 0; confirm everything under `review/horizon/` is pushed and nothing key-bearing was committed (grep the diff for `sk-` and `Bearer`); read back the remote log to confirm. Write `REPORT-HORIZON.md`: what was stabilized; REPO-MAP timing and reliability; packet size; panel roster with per-model ZDR and spend and total; the local baseline's gist; your own approximate token/turn cost per phase (the context-scaling datapoint); and one paragraph naming the strongest cross-lineage agreement (data for the advisor, not an adjudication). Set the QUEUE row `BUNDLED` and STOP. The advisor then pulls read-only, produces the final gap map and milestoned roadmap to 1.0 weighted by cross-lineage agreement, and returns it; that plus the operator tagging `review-rc3` closes the review phase.

If any instruction here is wrong on the box — a slug that will not resolve, a ZDR field that moved, a local endpoint or key path that differs, a doc edit the hook refuses — do the correct thing, get as much of both review streams back and published as possible, and say plainly what you changed. Getting the consolidated roadmap and the research questions published matters more than following this to the letter.

---

## VISION (write verbatim to packet/VISION.md)
The 1.0 goal: the operator loads a local-LLM tool, points it at this box, gives it a free-range agentic task in plain language, and it just goes — the framework provides structure and lifts output quality so the local model can carry work end to end, leaning on as much public-domain and open software as possible. Concrete target tasks a 1.0 must handle with stability: "generate an AI video of a tiger hunting a polar bear using public-domain images sourced from the web"; "organize a video library by the person depicted"; "take a training video and replace each person with a 3D-modeled avatar"; and, for slower turn-based games, play using the local LLM plus the NPU plus optionally a cloud model. Required subsystems the review must assess: an agentic multi-step task planner/executor that maximizes the single-node GPU and system RAM; media generation and editing pipelines (image and video generation, segmentation, compositing, 3D/avatar) on less-filtered local models; asset acquisition with provenance (public-domain/licensed-source verification); a VM-hosted computer-use loop with vision (screenshot plus vision-model) so the agent drives software like a person; tiered model routing across local GPU, NPU, and cloud; and — because the system is built and run entirely by AI — context management as a first-class engineering discipline. COMPLIANCE IS A HARD REQUIREMENT, not a feature: every media capability must enforce content provenance and licensing, and likeness/consent controls for anything depicting real people (avatar replacement, identity-based organization, and face recognition carry legal and consent constraints); the cyber-capable, deliberately-slightly-adversarial agent must operate within explicit legal, logged, human-approved boundaries. The operator is unsure how close the current system is to any of this and wants an honest, concrete assessment.

## ASK (write verbatim to packet/ASK.txt; run-panel.py appends it after PACKET.txt)
You are an independent staff-level software architect reviewing a working, security-hardened single-node local-AI code-manufacturing pipeline against the operator's 1.0 vision. Be concrete and honest. (A) For each vision capability — agentic task planner/executor maximizing local GPU and RAM; media generation and editing on local models (image/video/segmentation/3D-avatar); asset acquisition with provenance; VM-hosted computer-use with vision; tiered local-GPU/NPU/cloud routing; AI-managed context discipline — state what already exists here, what is missing, and the single hardest gap. (B) Give the critical path to a viable 1.0 as an ordered list of stable, independently-useful milestones, each with a rough size, such that the operator could ship and use each one before the next. (C) Name what to cut or defer versus gold-plate. (D) Assess whether the git-courier AI-managed gate protocol scales to this ambition and what most improves it. (E) COMPLIANCE AND SAFETY as a first-class deliverable: specify the provenance, licensing, likeness/consent, logging, and human-in-the-loop controls a 1.0 must have for the media and cyber capabilities to stay legal and auditable, and name where the current design is inadequate. (F) What could sink this, and what to prototype or measure first to de-risk it. (G) Recommend specific public-domain or open-source components for each subsystem where they exist.

---

## APPENDIX A — review/horizon/run-panel.py (write exactly)
```python
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
```

## APPENDIX B — review/horizon/run-local.py (write exactly)
```python
#!/usr/bin/env python3
"""Drive the RESIDENT local model (127.0.0.1:8080, OpenAI-compatible) — shared, never restarted.
Auth: key read from the path in env LOCAL_KEY_FILE (header only); if unset, sent with no auth.
Modes:
  run-local.py summarize <file-list.txt> <outdir>   one grounded summary per listed path
  run-local.py ask <packet.txt> <ask.txt> <outfile> one call over packet+ask (baseline panelist)
"""
import json, os, sys, urllib.request, urllib.error

URL = os.environ.get("LOCAL_URL", "http://127.0.0.1:8080/v1/chat/completions")
MODEL = os.environ.get("LOCAL_MODEL", "primary-qwen27b")

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
    return r["choices"][0]["message"]["content"] or ""

def summarize(list_f, outdir):
    os.makedirs(outdir, exist_ok=True)
    paths = [l.strip() for l in open(list_f) if l.strip()]
    sysmsg = ("You summarize one source file. Output 3-6 lines: purpose; key functions or classes "
              "BY EXACT NAME as they appear; direct imports/dependencies; any obvious risk. "
              "Cite only names that literally appear in the file. No preamble.")
    done = 0
    for path in paths:
        if not os.path.exists(path): continue
        src = open(path, encoding="utf-8", errors="replace").read()
        if len(src) > 48000: src = src[:48000] + "\n...[truncated]"
        try:
            out = call([{"role": "system", "content": sysmsg},
                        {"role": "user", "content": f"FILE: {path}\n\n{src}"}], 512)
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
                    {"role": "user", "content": packet + "\n\n" + q}], 8000)
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
```

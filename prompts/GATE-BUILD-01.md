# GATE-BUILD-01 — complete operator prompt (self-contained; a fresh Claude Code session on the box runs this end to end)

YOU ARE the local Claude Code executor on forge-mini. This file is your COMPLETE instructions — read it fully, then execute Phases 0–5 in order. This is the FIRST BUILD gate of the project: the review phase is closing and this opens the build toward 1.0. Its deliverable is the context-scoping tool the operator asked for — the thing that lets a future session load only the slices of the project a task needs, instead of the whole tree. You may take up to 16 hours; aim to have Phases 0–3 done in the first 6. CHECKPOINT (commit + push the courier) after every phase so a killed run resumes from the last pushed phase.

## ORIENT (first, before any phase)
- Foundry repo: `/home/kalib/foundry`, branch `review-fixes`. Courier: `/home/kalib/courier/Wrought`.
- `cd /home/kalib/foundry && git status` (confirm branch, note if dirty, do not discard). `git -C /home/kalib/courier/Wrought pull`.
- READ to load the operating rules and current state: `docs/EXECUTOR-RAILS.md`, `docs/PHASE-J-STATE.md`, courier `QUEUE.md`. Honor the rails you read there.
- Record this gate: copy this file to `/home/kalib/courier/Wrought/prompts/GATE-BUILD-01.md`, add a `GATE-BUILD-01 | RUNNING` row to `QUEUE.md`, commit, push.

## RAILS
- Byte-freeze `/var/lib/wrought/state/orchestrator.db{,-wal,-shm}` to `raw/00` now and `raw/99` at the end; identical = HOLD. Never write under `state/`.
- Never restart or overload `wrought-inference.service` — you SHARE the resident model.
- Run `bin/wrought-precommit-secret-scan` at exit 0 before every commit and push. Exit 2 is a refusal.
- `docs/PHASE-J-STATE.md` cannot be written whole (hook-denied) — surgical `Edit` only; a denied edit is recorded and skipped, never rephrased to evade.
- **NEW RAIL, learned from GATE-HORIZON: any call to the resident model MUST set `max_tokens` ABOVE the served reasoning budget (currently 24000) — the model is served `--reasoning on --reasoning-budget 24000`, and a smaller `max_tokens` makes it spend the whole budget on reasoning and return EMPTY content while exiting 0. Use `max_tokens` ≥ 28000 and check `finish_reason` and non-empty content on every response.**
- Compensating control (Face B open): any COMPLETED artifact from the pipeline is PROVISIONALLY verified — re-verify out-of-band before trusting it. This gate's Phase 3 does exactly that.

## PHASE 0 — record the GATE-HORIZON verdict
Re-verify against `bundles/GATE-HORIZON/` on the courier. VERDICT: **GATE-HORIZON ACCEPTED** (advisor 2026-09-01), exemplary. Both review streams landed and published; five non-Anthropic ZDR lineages carried the synthesis for $0.7749 of $15; the roadmap and research questions are published. The resident 27B produced **113 RELIABLE grounded file summaries of 127** (14 uncheckable, zero invented sampled) — the first real bulk work by the local model, well past the 5-byte write. Recorded honestly: **two advisor-supplied instruments were defective and both were caught by RUNNING them** — `run-panel.py` selected a 4B model by shortest slug (excluded, topped up correctly), and `run-local.py` passed `max_tokens=512` to a reasoning model and got empty summaries (fixed, re-run). Rails §18 three times. Write this to `bundles/GATE-HORIZON/ADJUDICATION.md`, set that QUEUE row `ADJUDICATED`, commit, push.

## PHASE 1 — LOCK THE ROADMAP
Write `docs/ROADMAP-1.0.md` from `bundles/GATE-HORIZON/CONSOLIDATED-ROADMAP.md`, amended by the operator's eight rulings below (these ARE the M0 scope-freeze — reproduce them as M0):
1. **Task decomposition is two-tier.** Big projects are decomposed into project docs / gates by the operator and advisor (the human trust anchor). WITHIN a bounded task the agent may call tools and dynamically solve problems. 1.0 does NOT build a full autonomous project planner; it builds a bounded within-task tool-use loop whose scope is authored, not invented.
2. **Media assurance = automated scan + human-in-the-loop, NOT a deterministic oracle and NOT an AI-judge-as-verdict** (an AI judge reproduces Face B). Cheap automated checks (format, resolution, safety/quality, provenance) plus operator feedback; the human is the media verdict authority.
3. **Context scoping tool is elevated** to the first build milestone (this gate). The cloud orchestrator holds the big picture; the local model gets scoped slices — the project need not fit the local model, only the current task's slice must.
4. **Measure-first stands, hands-off** — the manufacturing/escalation measurement runs unattended (Phase 3 here); the operator launches, does not babysit.
5. **Compliance right-sized to personal use.** KEEP as good engineering: provenance/asset-tracking, a light audit log, and human approval on cloud spend and destructive ops. DROP the corporate scaffolding: consent registry, jurisdictional switches, biometric prohibitions. The "compliance gate in the FSM" becomes a POLICY gate enforcing the operator's own rules (air-gap mode, spend caps, protected paths).
6. **Avatar replacement and library-sorting-by-cast are IN SCOPE** for personal use (legally-acquired media, no distribution of real-person deepfakes assumed).
7. **Air-gap MODE** — a per-task/global switch restricting to local GPU/NPU + pre-staged assets, no network egress, no cloud tier. A privacy+resource choice, not a security boundary; the natural default for media work. Resolves the "air-gapped vs web" contradiction: two modes, operator selects.
8. **NPU deferred, time-boxed** — do not build 1.0 around it; two weeks then fall back to CPU/iGPU and say so.
Then reproduce the milestone sequence (M0 scope-freeze; M-scope THIS gate; M1 VRAM scheduler; M2 prove+measure; M3 Face B before adversarial/unattended-production; then provenance→image→video→computer-use→vision→bounded planner), with the advisor's fork ruling recorded: **measure manufacturing + escalation (M2) before the Face B redesign (M3), but nothing adversarial or unattended-in-production ships until Face B is closed.** Commit behind a 5.1 scan, push. Do NOT tag; the operator tags `review-rc3` when ready.

## PHASE 2 — BUILD `bin/wrought-scope` (the deliverable). Build it yourself, reliably; this is not a pipeline test.
Purpose: given a task description or keywords, return the MINIMAL ranked set of files (and, where cheap, sections) a session must load for that task — so most of the project stays unloaded. Inputs already on the courier: the 113 grounded summaries under `bundles/GATE-HORIZON/repo-map/` and `bundles/GATE-HORIZON/REPO-MAP.md`.
Build, under `bin/` and/or `src/`, committed to the foundry:
- An INDEX builder: for every tracked file under `bin/` and `src/` (and `docs/`), record its one-line purpose (from the repo-map where reliable, else a fresh local-model summary with `max_tokens` ≥ 28000), its exported/defined symbols (grep/AST), and its direct imports/dependencies. Store as a small on-disk index (JSON) the tool reads — the index itself is the compact artifact, not the whole tree.
- `bin/wrought-scope query "<task or keywords>"` → a ranked minimal file list, each with a one-line why and an estimated load-token cost (use the served `/tokenize` endpoint for honesty, not a chars/token guess — another GATE-HORIZON lesson), and a total. Cap the default result at a sane size and let `--max-files` override.
- `bin/wrought-scope symbol <name>` → the file(s) that define or use it.
- `bin/wrought-scope rebuild` → regenerate the index (local model calls obey the ≥28000 rail).
TESTS (deterministic, committed alongside, and the definition of done):
- A fixtures file mapping known queries to must-include files, e.g. "oracle verdict logic" → `bin/verify-job`, `src/wrought_supervisor/classify.py`, `src/wrought_verifier/__main__.py`; "courier transport rules" → `docs/EXECUTOR-RAILS.md`; "runner containment" → `bin/wrought-runner`, `bin/wrought-runner-hook`. The tool MUST return every must-include file for each query, and MUST keep the returned set small (assert it is far below the whole-tree count).
- A symbol lookup returns the correct defining file for a sample of real symbols.
- `rebuild` is stable: two runs produce the same file set for the same query.
Run the tests, capture output to `raw/`, and record the headline number: **for the fixtures queries, average files-to-load and tokens-to-load versus loading the whole tree** — that ratio is what this tool buys every future gate. Commit behind a 5.1 scan, push.

## PHASE 3 — FIRST MANUFACTURING MEASUREMENT (M2 probe), TIME-BOXED to ~3 hours, quarantined
This is the first honest test of whether the autonomous pipeline manufactures real work, and at what escalation rate. It must NOT block or endanger Phase 2's deliverable. Choose ONE small, genuinely useful, oracle-checkable tool spec — for example a `bin/wrought-scope-lint` that checks the index is in sync with the tree (every indexed file exists; no tracked `bin`/`src` file is missing from the index), with pytest tests as its oracle. Run it through the actual manufacturing pipeline (the autonomous runner / agent surface + the deterministic oracle), UNATTENDED, and measure: did it produce real multi-line code (not a stub); did the oracle pass on the work product; how many repair loops; did it escalate to the cloud tier and how often; wall-clock and cost. If the pipeline cannot complete it inside the time-box, STOP the probe and report exactly how far it got — an honest "it reached the repair loop and stalled here" is the measurement, and is worth more than a forced success. Out-of-band re-verify any COMPLETED artifact (Face B compensating control). Write the measurement to `raw/` and summarize in the report. Commit, push.

## PHASE 4 — wind-down
`raw/99` freeze re-assert (must HOLD). 5.1 scan at exit 0; confirm nothing key-bearing was committed. Write `bundles/GATE-BUILD-01/REPORT.md`: the roadmap lock; `wrought-scope` built with its test results and the load-reduction ratio; the M2 probe measurement (real-work? escalation rate? how far?); your own token/turn cost per phase; OTHER SURPRISES; WHAT THIS DID NOT ESTABLISH. Manifest by the proven method (one `sha256sum`, `Write`, round-trip `-c`). Set the QUEUE row `BUNDLED`, push, STOP. The advisor pulls read-only, adjudicates, and the operator tags `review-rc3` and picks the next milestone (M1 VRAM scheduler or M2-in-earnest).

## NOTE FOR THE REPORT
If any instruction here is wrong on the box — a repo-map path that moved, a `/tokenize` endpoint that differs, a doc edit the hook refuses, a pipeline that cannot take the probe — do the correct thing, land `wrought-scope` and the roadmap regardless, and say plainly what you changed. The scoping tool is the deliverable that matters; the M2 probe is a measurement, not a gate on shipping it.

=== END GATE-BUILD-01 ===

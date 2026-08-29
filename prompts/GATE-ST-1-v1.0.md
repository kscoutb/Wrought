# GATE-ST-1 — substrate self-test + drift disposition (v1.0, ATTENDED-DIRECT)

*(Executor: Claude Code on forge-mini, Opus, ultracode — ATTENDED, run as a DIRECT session, NOT
through wrought-runner: the CPU reference load of the 27B needs ~17–20 GB RAM, far more than the
runner's 8 G scope, and ST-1 is correctness-critical. Advisor: Fable. Two ST-1 triggers are
unsatisfied: kernel drifted 7.0.0-28 → -30, and AppArmor 5.0.0~beta1 → 5.0.2 (under the oracle's
own bwrap). The standing rule: gate every kernel/Mesa/model change on the CPU-vs-GPU temp-0 diff +
canary suite, NEVER on llama-bench throughput — a clean bench on a model emitting noise is the exact
failure this exists to catch. This gate re-verifies the served model is still correct on the current
substrate, then dispositions the drift.)*

ALLOWED-TOOLS: Read Edit Write Bash
HEARTBEAT: push STATUS.md=RECEIVED, keep current per phase.
TRANSPORT INTEGRITY CHECK: this prompt is a FILE and contains ZERO indented blocks (all literals
inline). If it looks garbled, STOP and tell the operator.

## Rails — by reference
Read docs/EXECUTOR-RAILS.md. This is a DIRECT session, so §2.1 applies: the box hashes the three
state/ paths itself at start and before finalizing (byte freeze is your duty here, not the runner's).
Do not touch wrought-* units except read-only. Re-pinning is a foundry commit (operator-authored).

## Phase 1 — device identity assertion (the R1 boot-time self-test)
Assert, fail-loud, before any correctness run: the dGPU is the RX 7900 XTX by device id `0x744c`;
`llama-server --list-devices` (or the box's device-assert) shows the real NAVI31 as the served
device and **no `llvmpipe`** anywhere in the enumeration; `amdgpu.runpm=0`; VRAM used ≈ the resident
27B. Record Mesa and kernel versions. If the served instance is on llvmpipe or the wrong device,
STOP — everything downstream is void.

## Phase 2 — run the ST-1 correctness suite against the CURRENT substrate
Use the project's existing ST-1 harness / trigger-prompt fixtures / canary suite if one is defined
(search `bin/`, `docs/`, and the corpus). If there is no named harness, run the FINDINGS-R2 Stage-1
methodology explicitly:
- **CPU-vs-GPU temp-0 diff** on the 3–5 trigger prompts (a technical/math prompt, a code prompt, a
  long-context prompt) at the pinned shape `-b 2048 -ub 512 -np 1`, greedy (`--temp 0`). GPU side:
  the already-served instance (do NOT load a second copy into VRAM — only ~5.8 G is free; query the
  running llama-server). CPU side: a separate `llama-cli -ngl 0` load of the same pinned GGUF.
  **Any divergence = corruption on this substrate.**
- **Canaries:** extraction-based (assert a specific value/field appears) with exact-match as a
  secondary check pinned to that same batch shape, per the standing recommendation.
Record every output with the command that produced it (J-95). Note the CPU run is slow (27B on CPU);
budget for it.

## Phase 3 — disposition the drift
- **If the suite PASSES** (no CPU-vs-GPU divergence, canaries green): the kernel and AppArmor moves
  are **ST-1-VALIDATED**. Re-pin in `pins.lock` — `substrate.kernel: 7.0.0-30-generic` and record
  AppArmor `5.0.2-0ubuntu1~26.04.1` as validated — moving each pin **in the gate that re-measured
  it**, which is the only correct place. Record the prior values in `drift_observed` as resolved.
- **If ANY divergence or canary trip:** HARD STOP, fail loud. Do NOT re-pin. The substrate corrupted
  the model — this is the Devstral-Small-2 fallback decision (a ferry call), and no MANUFACTURING
  run may proceed until it is resolved. Capture the exact divergence.

## Phase 4 — wind-down
Byte-freeze re-assert (your duty, §2.1) + diff. PROPOSED-PINS-DELTA (the kernel/AppArmor re-pin, or
the divergence + fallback flag). Update docs/PHASE-J-STATE (ST-1 triggers cleared, or the hard stop).
REPORT-ST-1.md: device assert, the CPU-vs-GPU results per prompt, the canary results, the
disposition. Ultracode audit (verdicts computed from measured values). SHA256SUMS last. Return
through the courier (bundles/GATE-ST-1/), set BUNDLED, push, report the sha, both trees clean, STOP.

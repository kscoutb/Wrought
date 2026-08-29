# GATE-RUNNER-POLISH — fix the correctness/safety items J0B-RESUME surfaced (v1.0, ATTENDED-direct)

*(Executor: Claude Code on forge-mini, Opus, ultracode — ATTENDED, run as a DIRECT session, NOT
through the runner: this gate edits the runner and rails, so it must not run under the thing it is
changing. Advisor: Fable. GATE-J0B-RESUME passed mechanically and settled the two big questions —
the runner works unattended on real work, and the interception seam is BUILD-able — but surfaced a
batch of correctness/safety fixes. Per hygiene-before-capability, land these before the next runner
batch. The capability follow-on (J0B-CLOSE: the extensions schema + the F-5 proxy fix + the
work-product proof) is a separate, later gate.)*

ALLOWED-TOOLS: Read, Edit, Write, Bash
HEARTBEAT: push STATUS.md=RECEIVED, then keep current per phase.
TRANSPORT INTEGRITY CHECK: this prompt is a FILE and contains exactly TWO indented blocks. If any
is empty or garbled, STOP after the RECEIVED push and tell the operator.

PRIOR-ADJUDICATION — GATE-J0B-RESUME: **ACCEPTED, mechanical PASS (advisor Fable, 2026-08-28).** The
runner is validated on real unattended-shape work — scope measurably contained the guest, byte
freeze held (runner-owned), reaper clean, deadman untroubled, verdict PASS. **Interception seam
POSITIVE → Decision-1 = BUILD** (a two-line unprivileged tee shim intercepted JSON-RPC
initialize/tools/list/tools/call both directions — the log-tap can be built). Pinhole re-proved,
Goose pin reproduced, C5 map finished (nothing in the guest to steal). **CAPABILITY NOT CLOSED:**
the agent turn reached the model but wrote no work product (extensions attach didn't load; F-4:
goose exits 0 on total failure) — J0B-CLOSE will close it. Rulings enacted here: F-1 (amend rails
§2), F-2 (doc guest-RAM-vs-scope), the reaper pgrep false-positive, the secret-scan argv leak, the
bare-Bash boundary, a per-batch cost cap. Deferred to J0B-CLOSE: F-5 (proxy bounds max_tokens +
cancels abandoned generations) and the goose 1.46 extensions schema. ST-1 still owed before any
manufacturing run. Record per §10 (bundles/GATE-J0B-RESUME/ADJUDICATION.md, set ADJUDICATED).

## Rails — by reference
Read docs/EXECUTOR-RAILS.md. Byte freeze on state/ (this gate writes nothing there). `/etc/wrought/`
edits need sudo (attended, operator-present); bin/ edits are kalib-owned, no sudo. Foundry commits
operator-authored. Every fix VERIFIED by measurement, not inspection — the J0B-RESUME lesson.

## Phase 1 — record + baseline
Do the §10 recording. Byte-freeze baseline. Health (service active, /health 200, runpm 0, dGPU 0x744c).

## Phase 2 — the reaper's false-positive (highest priority: it could halt the NEXT good batch)
The reaper detects survivors with `pgrep -f qemu-system`, which matches ANY command line CONTAINING
that string — a gate prompt that mentions qemu, a monitoring command, this very gate. Replace the
`-f` substring match with a PRECISE test — match the actual process executable and/or the gate
scope's own cgroup membership, not an arbitrary command-line substring. Prove it:

    # a decoy whose command line contains "qemu-system-x86_64" but is NOT a guest must NOT be swept;
    # a real scope-descendant guest-shaped process MUST be. Show both, with the reaper's own output.

Apply the same scrutiny to the residue snapshot's listener/domain detection if it shares the flaw.

## Phase 3 — the secret-scan argv leak (a recurring hard-rule violation)
The orchestrator's pre-commit secret scan ran `KEY=$(sudo -n cat …); git diff --cached | grep -c -- "$KEY"`,
which briefly placed the sealed key in `grep`'s argv (visible in /proc) — the exact exposure the
stdin-only design exists to prevent. Replace every secret-scan site with a form that never puts the
value on a command line — a digest comparison, or `grep -f <(printf '%s' "$KEY")` with the value fed
on a file descriptor. Record where the scan is defined (rails/tooling) and prove the corrected form
detects a planted secret AND never exposes the value in argv:

    # demonstrate: plant a known token in a staged diff; the corrected scan flags it; and
    # `tr '\0' ' ' </proc/<scan-pid>/cmdline` never contains the token during the scan.

## Phase 4 — F-1 and F-2: rails amendments (docs, no code)
- **F-1:** amend docs/EXECUTOR-RAILS §2 — UNDER THE RUNNER, the byte freeze is the RUNNER's duty,
  performed outside the child over the three state/ paths; a gate child MUST NOT attempt it and the
  hook denying its `sha256sum` is correct behaviour, not a failure. A direct (non-runner) gate still
  does §2 itself. State both cases.
- **F-2:** document (rails §13 + docs/PHASE-J-STATE) — a gate that boots a guest under the runner
  budgets guest RAM against `limits.memory_max` (the scope), NOT host free RAM; J0B's proven `-m 8192`
  OOM-kills the gate inside an 8 G scope. Note the current scope size and the headroom a guest+agent needs.

## Phase 5 — small provenance/documentation fixes
- Document the `NOT RUN` QUEUE status in the parser's recognized set + the README/legend (it is
  ratified-in-use but undocumented; keep it non-runnable).
- Fix the hardcoded `reset_by: "operator via --reset-breaker"` false-provenance string to record the
  ACTUAL actor/method, or make it a measured value — no invented provenance (the class of defect
  this project keeps catching).

## Phase 6 — arm the bare-Bash workspace boundary (the careful one — do BOTH halves together)
Every gate so far declared bare `Bash`, and GATE-RUNNER-ARM raw/31 measured that bare `Bash`
ESCAPES the workspace boundary entirely — so `--add-dir` has never constrained a real gate child.
The box warned: scoping the Bash rules WITHOUT also fixing `ADD-DIRS` converts a non-issue into a
hard denial. So do both, together, and verify:
- teach the runner/prompt convention to emit SCOPED Bash allowlist entries (e.g. `Bash(cmd:*)`), and
  require every gate's `ADD-DIRS:` to name exactly the out-of-cwd trees it needs;
- correct the overbroad "workspace boundary" ESTABLISHED FACT in runner.conf's `_add_dirs_note`,
  `runner-arm/raw/31`-derived docs, and docs/PHASE-J-STATE to the measured conditional truth.
Prove on a scratch gate: with scoped Bash + a correct `ADD-DIRS`, the child reaches its declared
tree and is DENIED outside it. If this cannot be made to hold cleanly, STOP and report — do not ship
a boundary that is half-armed.

## Phase 7 — the per-batch cost cap + wind-down
Add a PROVISIONAL `breakers.max_batch_cost_usd` to /etc/wrought/runner.conf (sudo) that halts the
runner when cumulative child cost in one run crosses it — J0B-RESUME hit 94% of the per-GATE cap on
one wedged gate, so a multi-gate unattended run needs a batch ceiling too. Mark it PROVISIONAL and
note in the report that the per-gate $8 cap must be RE-CALIBRATED after F-5 is fixed (the wedge
inflated this gate's cost; a clean gate is far cheaper). Then: byte-freeze raw/99 + diff; update
docs/PHASE-J-STATE (all fixes, and the two open capability items for J0B-CLOSE); REPORT-RUNNER-POLISH.md;
ultracode audit with counts; SHA256SUMS last; return through the courier (bundles/GATE-RUNNER-POLISH/),
set BUNDLED, push, report the sha, both trees clean, STOP.

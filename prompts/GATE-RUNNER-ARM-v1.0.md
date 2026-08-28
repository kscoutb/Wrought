# GATE-RUNNER-ARM — pin the CLI, re-verify safety, fix startup, arm the runner (v1.0, ATTENDED)

*(Executor: Claude Code on forge-mini, Opus, ultracode. Advisor: Fable. GATE-RUNNER-HARDEN closed
both unattended blockers but surfaced two showstoppers before any real batch: the `claude` CLI
self-updated 2.1.238 → 2.1.250 under its own pin (safety model now unverified), and the runner
cannot start against the installed config (PermissionError on `/var/lib/wrought/runner-state`).
This gate resolves both, drops one env var, and proves the runner STARTS on the INSTALLED config
and runs one real gate end-to-end. It runs as a DIRECT attended session — NOT through the runner,
which is not yet armed. The supervised J0B batch is the NEXT prompt, after this clears.)*

ALLOWED-TOOLS: Read, Edit, Bash   (declared per rails §13; this gate runs attended-direct, not via the runner)

HEARTBEAT: on reading this file push STATUS.md=RECEIVED, then the transport check, then keep
STATUS current at every phase.

TRANSPORT INTEGRITY CHECK: this prompt travels as a FILE (rails §7 — failed three times as chat
text; upload it) and contains exactly ONE indented block. If either is empty or garbled, STOP
after the RECEIVED push and tell the operator.

PRIOR-ADJUDICATION — GATE-RUNNER-HARDEN: **ACCEPTED (advisor Fable, 2026-08-28).** Both unattended
blockers CLOSED and measured — and the box corrected the prompt's mechanism: steering isolation
needs BOTH a private `$HOME` (the peer listing) AND a private `$XDG_RUNTIME_DIR` (the addressable
socket); "not listed" is not "not addressable," and a child in the isolated shape authenticated and
pushed to `origin/main`. Reaper: post-gate sweep detects/terminates/HALTS-latched, scope-parenting
proven. Config ratified, zero values changed. The `classify()` signal-code defect (-15/-9 vs
143/137) fixed. Two load-bearing unasked catches drive THIS gate: the CLI self-update, and the
runner's PermissionError startup failure. Course-check untouched, still disabled.

## Rails — by reference
Read docs/EXECUTOR-RAILS.md. Byte freeze on state/ across the session. Record the HARDEN
adjudication above per §10 as the first courier action (bundles/GATE-RUNNER-HARDEN/ADJUDICATION.md,
set that row ADJUDICATED). Foundry commits operator-authored. Authorized changes: pins.lock (CLI
pin + drift), the runner env allowlist, docs; the ONE operator root action in Phase 1; a scratch
end-to-end runner start. NO real J0B work, NO course-check enablement, NO package installs, NO VM.

## Phase 1 — operator action + baseline
1. **OPERATOR (root), the only privileged action this gate needs — run it and paste the result:**

    sudo mkdir -p /var/lib/wrought/runner-state && sudo chown kalib:kalib /var/lib/wrought/runner-state && sudo chmod 700 /var/lib/wrought/runner-state && ls -ld /var/lib/wrought/runner-state

   0700 is load-bearing: `ephemeral_home.root` sits inside `state_dir` and holds per-gate copies of
   the Claude + git credentials. If the operator is not present, STOP here and report — the runner
   cannot start without this and it is outside the box session's authorized scope (rails §1).
2. Byte-freeze baseline. Health (service active, /health 200, runpm 0, dGPU 0x744c VRAM).

## Phase 2 — pin the CLI against further self-update
Record the installed version and stop the autoupdater. `raw/03` of HARDEN found `DISABLE_AUTOUPDATER`
exists in the binary. Set it in whatever persistent, load-bearing place the runner's own environment
is defined (measure where — a wrapper, the systemd-run env allowlist, or a profile the runner
sources), so that neither an interactive session nor a runner-spawned `claude -p` child can silently
update mid-batch. Record the installed version `2.1.250` in `pins.lock` as the runner's tool pin,
with the `2.1.238 → 2.1.250` move recorded in `drift_observed` (a pin moves only in the gate that
re-measures it — this is that gate for the CLI). Confirm by measurement that a fresh `claude`
invocation does not attempt an update.

## Phase 3 — RE-VERIFY the four safety properties on 2.1.250 (the load-bearing phase)
The runner's containment was measured on 2.1.238. Re-run HARDEN/RUNNER's own harnesses against the
installed 2.1.250 and record, pass/fail, each of:

- **(b)** `dontAsk` still refuses an un-allowlisted Bash call and honours an allowlist; **and the
  trap still holds** — `acceptEdits`/`auto` still silently RUN it (if that changed either way,
  say so; the runner refuses non-`dontAsk` modes regardless).
- **(c)** PreToolUse hooks still FIRE under `claude -p` and a malformed settings file is still
  silently ignored (so the pre-launch `json.load` guard is still required).
- **(d)** `--max-budget-usd` still behaves as a soft ceiling; `BASH_DEFAULT_TIMEOUT_MS` still
  backgrounds rather than kills (kernel remains the only stop).
- **(a)** fresh context per invocation still holds; the private-HOME + private-runtime-dir isolation
  from HARDEN still takes a child off both the listing and the socket.

**If ANY of the four changed on 2.1.250, STOP and report — do not clear the runner.** If a change
is benign-but-real, adapt the runner and say exactly what changed. If all four hold, say so with
the evidence.

## Phase 4 — drop DBUS from the child env allowlist
Remove `DBUS_SESSION_BUS_ADDRESS` from the gate-child environment allowlist (tighter surface; the
session bus is a cross-session vector). Note that the RUNNER PARENT may still need it for
`systemd-run --user`; scope the removal to the CHILD env only. Prove a gate child still runs with
it absent; if some gate operation genuinely fails without it, report the exact failure rather than
silently re-adding it.

## Phase 5 — prove the runner starts on the INSTALLED config and runs one real gate
With Phase 1 done, `wrought-runner` must now start against the **installed** `/etc/wrought/runner.conf`
(the PermissionError is gone). Prove it end-to-end against a **scratch courier + scratch DB** (never
the real store): one trivial real `claude` gate, run through the full armed path — private HOME +
private runtime dir, kernel scope, `dontAsk`, mechanical verdict, post-gate orphan sweep clean, push
to the scratch courier. This is the first time the installed config and the hardened runner run
together on a real child. Report the child's session_id, the verdict, and the sweep result.

## Phase 6 — wind-down
Byte-freeze raw/99 + diff. Update docs/PHASE-J-STATE.md: runner ARMED — startup fixed, CLI pinned
at 2.1.250 with autoupdate disabled, four safety properties re-verified, DBUS dropped, installed-
config start proven; next = supervised GATE-J0B (Phases 5–7 + seed rebuild). PROPOSED-PINS-DELTA
(the CLI pin). REPORT-RUNNER-ARM.md. Ultracode adversarial audit with counts. SHA256SUMS last.
Return through the courier (bundles/GATE-RUNNER-ARM/), set BUNDLED, push, report the shas, both
trees clean, STOP.

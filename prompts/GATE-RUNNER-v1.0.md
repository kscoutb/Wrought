# GATE-RUNNER — build the day-long autonomous batch runner (v1.0, ATTENDED)

*(Executor: Claude Code on forge-mini, Opus, ultracode. Advisor: Fable. Adjudicated design:
ADJUDICATION-RT0 v1.0 + operator ruling 2026-08-21 — once-a-day operator ferry, box runs a
batch autonomously between ferries. THIS GATE IS ATTENDED: the operator watches it build and
dry-run the runner. You do NOT bootstrap an autonomous runner autonomously. The runner this gate
produces is what later runs unattended.)*

HEARTBEAT: on reading this file push STATUS.md=RECEIVED per docs/EXECUTOR-RAILS.md, then the
transport check, and keep STATUS current at every phase.

TRANSPORT INTEGRITY CHECK: this prompt travels as a FILE and contains exactly THREE indented
blocks. If any is empty or garbled, STOP after the RECEIVED status push and tell the operator.

PRIOR-ADJUDICATION — GATE-HJ2: record per the standing rule if not already ADJUDICATED.

## Rails — by reference
Read docs/EXECUTOR-RAILS.md and follow it. Session-specific points:
- Authorized state changes: create the runner under /opt/wrought/runner/ (or the repo's bin/, per
  existing convention — match what's there, don't invent a tree) and its config under
  /etc/wrought/; a dry-run that executes ONE no-op test gate in a scratch workdir. NOTHING else —
  no package installs, no unit changes beyond an optional operator-reviewed timer left DISABLED,
  no firewall changes, no VM work.
- Byte freeze on /var/lib/wrought/state/orchestrator.db{,-wal,-shm} across the whole session.
- Secrets: the course-correction API key is the SAME sealed inference/escalation credential,
  passed on stdin only, never argv/env/file/repo. Its use here is NEW and is flagged for operator
  ratification (see §4); build the capability, gate its enablement behind a config flag defaulting
  OFF.

## What you are building: `wrought-runner`
A shell (or python-stdlib) harness that runs a batch of PRE-APPROVED gate prompts, one per fresh
context, pacing itself, contained, with circuit breakers and an optional halt-only cloud check.
It is STARTED MANUALLY by the operator once per day; it is not an always-on daemon.

### Phase 1 — RT0 on-box verifications (settle before designing containment)
The RT0 research made version-dependent claims; the box is the arbiter. Verify and record:

    # (a) does a fresh non-interactive run clear context? prove two invocations share no memory
    # (b) does --permission-mode default-deny actually block an un-allowlisted Bash call?
    # (c) do PreToolUse hooks fire under `claude -p`?  (RT0 pass-2 claims they do NOT)
    # (d) do the token/output caps + bash-timeout env vars take effect?
    claude --version; claude --help | grep -iE 'permission-mode|allowedTools|print|session'

Record exactly which of (a)-(d) hold on THIS pinned build. The containment design in Phase 2
follows the evidence: if hooks don't fire under `claude -p`, containment is KERNEL-level only.

### Phase 2 — the runner. Per approved gate, in a loop over the courier queue:
1. `git pull` courier; confirm the gate is `APPROVED` in QUEUE.md and not yet run. If none are
   APPROVED, exit cleanly (nothing to do).
2. Byte-freeze baseline.
3. Run the gate in a FRESH, sessionless context, kernel-contained, default-deny:

    systemd-run --user --scope -p MemoryMax=<cap> -p RuntimeMaxSec=<per-gate-timeout> \
      env CLAUDE_CODE_MAX_OUTPUT_TOKENS=<cap> BASH_DEFAULT_TIMEOUT_MS=600000 \
      claude -p "$(cat prompts/<gate>.md)" --permission-mode <default-deny-mode> \
      --allowedTools "<the minimal set the gate declares>"
   # NEVER --dangerously-skip-permissions. Fresh invocation each gate = cleared history.
   # (adapt flag names to what Phase 1 proved this build accepts)

4. The gate pushes its own bundle + sets BUNDLED (gate prompts already do this).
5. Byte-freeze re-assert + mechanical diff. ANY change → HALT the whole runner (tripwire).
6. Optional halt-only cloud course-correction (see §3), if enabled.
7. Pace: sleep <interval> between gates; on API 429/529 back off exponentially and retry a bounded
   number of times, then HALT.
8. Update STATUS.md heartbeat; push.

### Phase 3 — circuit breakers (all default to HALT-AND-WAIT)
- consecutive-failure ledger: N failed/errored gates in a row → disable further runs, require
  operator reset.
- gate-count cap and wall-clock budget per run (e.g. ≤ K gates, ≤ ~20h) → stop, wait for the
  daily ferry.
- byte-freeze tripwire (step 5) → immediate HALT.
- per-gate `RuntimeMaxSec` and `MemoryMax` (kernel) → the scope is killed; runner logs and halts.
- refuse inbound cross-session messages during a run (config the box so the runner's `claude`
  invocations can't be steered by another local session).
- dead-man: if a run starts but STATUS.md stops advancing for > T, the wrapper self-terminates
  the current scope and halts.

## §3 — the halt-only cloud course-correction (optional, config-flag OFF by default)
Between gates, compile a COMPACT summary — gate name, pass/fail signals, byte-freeze verdict, the
next queued gate — and send it to a cloud reviewer model, key on stdin:

    printf '%s' "$SUMMARY" | run-course-check   # reads sealed key on stdin, POSTs to the pinned
                                                 # escalation endpoint, prints exactly one token

The reviewer is prompted as a skeptic asked ONE question: "does anything here warrant halting for
human review? Answer HALT or OK." **OK is not approval to proceed** — it only means "no alarm";
forward progress is already gated by the APPROVED state the advisor+operator set at the daily
ferry. **HALT — or any non-OK / unparseable / errored / budget-exhausted response — stops the
runner** and records the summary for the daily review. Cap the number of course-checks per run and
respect the $50 prepaid backstop (STOP-4); log spend. This is a one-way safety valve, never an
authority.

## Phase 4 — DRY RUN (the proof this gate delivers)
Author ONE throwaway no-op test gate (writes a marker to a scratch workdir, pushes a trivial
bundle) and run the whole runner against a one-item APPROVED queue. Prove, with captured evidence:
fresh context per gate (the two-invocation test), the systemd-run containment actually caps
memory/time, pacing sleeps occurred, the byte-freeze tripwire fires when you deliberately dirty a
scratch copy (NOT the real DB), a forced gate-failure trips the consecutive-failure breaker, and —
with course-correction toggled on against a stubbed/echo endpoint (no real key, no real spend) — a
stubbed HALT stops the runner. Tear the test gate down (enumerated).

## Phase 5 — wind-down
Update PROPOSED-PINS-DELTA.md (runner + config paths, any new pinned assumption). Update
docs/PHASE-J-STATE.md: runner built, its config, the RT0 verification results, the daily operating
loop. Byte-freeze raw/99 + diff BEFORE finalizing. REPORT-RUNNER.md: the Phase-1 verification
findings (which of a-d hold), the runner design as-built, the dry-run evidence, the course-check
design + the ratification-needed flag, circuit breakers, OTHER SURPRISES, WHAT THIS DID NOT
ESTABLISH. Ultracode adversarial audit with counts. SHA256SUMS last. Return the bundle through the
courier (bundles/GATE-RUNNER/), set BUNDLED, push, report the courier sha, both trees clean, STOP.

## The daily operating loop this enables (for the report's "how to run" section)
Each day the operator: `git pull` courier → advisor adjudicates the returned bundles → operator
commits the next batch of advisor-APPROVED prompts and marks them APPROVED in QUEUE.md → starts
`wrought-runner` → walks away. The runner works the batch with fresh context per gate, pacing,
containment, and the halt-only cloud check, then halts at batch end or on any breaker, awaiting the
next daily ferry. No always-on daemon; the operator's manual start each day IS the human gate.

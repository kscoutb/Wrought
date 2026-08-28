# GATE-RUNNER-HARDEN — close the two unattended-run blockers + ratify (v1.0, ATTENDED)

*(Executor: Claude Code on forge-mini, Opus, ultracode. Advisor: Fable. GATE-RUNNER was ACCEPTED
as a build but NOT cleared for unattended use. This gate closes the two safety blockers the runner
and the reconcile snapshot surfaced — the cross-session steering breaker and the missing reaper —
ratifies the operator's decisions into config/docs, and records two pending adjudications. It does
NOT run a real batch; the first real batch is supervised J0B, next. ATTENDED — it modifies
safety-critical runner code.)*

HEARTBEAT: on reading this file push STATUS.md=RECEIVED per docs/EXECUTOR-RAILS.md, then the
transport check, then keep STATUS current at every phase.

TRANSPORT INTEGRITY CHECK: this prompt travels as a FILE (rails §7 — it has now failed twice as
chat text; upload it) and contains exactly TWO indented blocks. If any is empty or garbled, STOP
after the RECEIVED push and tell the operator.

PRIOR-ADJUDICATION — GATE-RUNNER: **ACCEPTED as an attended build (advisor Fable, 2026-08-28).**
Runner correct; containment MEASURED not assumed (dontAsk + kernel scope + MemorySwapMax=0 + env
allowlist + a mechanical verdict that ignores the child's self-report); course-check is halt-only
on its own spend path and ships disabled. **NOT CLEARED for unattended use** — three conditions:
(1) close the steering breaker via a private $HOME per gate child; (2) add the reaper; (3) first
real use is a SUPERVISED batch that sets the provisional scale numbers. Operator ratifications:
APPROVED status YES, ALLOWED-TOOLS header YES, runner.conf structure/safety RATIFIED with scale
numbers PROVISIONAL, course-check credential HELD (stays disabled).

PRIOR-ADJUDICATION — GATE-RECONCILE: **ACCEPTED (advisor Fable, 2026-08-28).** Tangle resolved
honestly — corrected three of the prompt's premises rather than executing them (purge already done
2026-08-20, J-159 collision → J-160, no guest to stop), self-caught a §5 argv-leak in its own
secret scan and fixed by addition, preserved J0B's partial evidence, wrote an authoritative
snapshot. Byte freeze held. The reaper finding is a genuine blind-spot catch, addressed here.

## Rails — by reference
Read docs/EXECUTOR-RAILS.md and follow it. Byte freeze on state/ across the session (this gate
writes nothing under state/). Foundry commits operator-authored. Enumerated deletes only. Record
the two adjudications above per the §10 rule as the FIRST courier action: write each verbatim to
bundles/GATE-RUNNER/ADJUDICATION.md and bundles/GATE-RECONCILE/ADJUDICATION.md, set both QUEUE rows
to ADJUDICATED (GATE-RUNNER's note: "build accepted; unattended-blocked pending this gate + a
supervised batch"). Authorized changes: the runner scripts in bin/, /etc/wrought/runner.conf, docs,
and a scratch dry-run. NO real batch, NO course-check enablement, NO package installs, NO VM work.

## Phase 1 — record adjudications, baseline
Do the §10 recording above. Byte-freeze baseline. Health (service active, /health 200, runpm 0,
dGPU 0x744c VRAM).

## Phase 2 — BLOCKER 1: close the cross-session steering breaker
**Requirement:** a running gate child must NOT be discoverable or addressable by any other local
Claude Code session — so the untested "what does an APPROVED steering message do" case cannot
arise, because there is nothing to address. raw/16 established discovery is keyed under `$HOME`
(`~/.claude/daemon/roster.json`).
**Approach (measure, don't assume — you are the arbiter):** launch each gate child with `HOME` set
to a per-gate ephemeral directory holding ONLY the minimal files a headless `claude -p` needs to
(a) authenticate and (b) still push its bundle to the courier — determine that minimal set by
measurement, including the git credential the gate's own push needs, and record exactly what had to
be present. Tear the ephemeral HOME down with the gate.

    # prove the closure, both directions:
    #  - a gate child under the private HOME does NOT appear in the real ~/.claude/daemon/roster.json
    #    and cannot be listed/addressed from a separate normal session on the real HOME
    #  - the same child still authenticates, runs its tools, AND completes a courier push
    # if a private HOME breaks auth or the push, find the minimal additions that restore them,
    # record them, and re-prove non-discoverability with those additions present.

If a fully private HOME cannot both isolate the roster AND preserve auth+push, report the exact
conflict and the closest achievable isolation — do not silently ship a child that is still on the
roster. Wire the working mechanism into `wrought-runner` (config-driven path for the ephemeral HOME
root) and note it in the report.

## Phase 3 — BLOCKER 2: the reaper
**Requirement:** no gate may leave a running guest, libvirt domain, or credential-holding proxy
after it exits, and a killed/dead gate must strand none. Two layers:
1. **Scope-parenting.** A guest/proxy launched as a descendant of the gate's `systemd-run --scope`
   is in the scope cgroup and dies on scope kill — but a `virsh`/`virt-install` domain re-parents to
   libvirtd's `machine.slice` and ESCAPES the scope. Add to docs/EXECUTOR-RAILS a rule that a gate
   which must be reapable-by-scope launches plain `qemu-system` as a scope descendant, not via
   libvirtd; and if a gate uses libvirt, it owns explicit teardown.
2. **Mandatory post-gate orphan sweep in `wrought-runner` (the real backstop).** Snapshot
   {qemu-system PIDs, `virsh list --all` domains, listeners on the configured proxy port(s)} at gate
   start; after the gate child exits, diff. Any NEW survivor → enumerate it, terminate it, and HALT
   with a latching "gate left residue" fault. A gate that leaks a process is a defect, treated loud.

    # prove it two ways:
    #  - a stub gate spawns a background process + a listener and does NOT clean them; the runner's
    #    post-gate sweep detects both, kills them (enumerated in the log), and HALTS latched
    #  - a scope-descendant stub is reaped automatically when the gate scope is killed (RuntimeMaxSec)
    # use stubs (a sleeper + a trivial listener); do NOT boot a real guest this gate.

## Phase 4 — ratify the operator decisions into config + docs
1. `/etc/wrought/runner.conf`: annotate each setting **RATIFIED** or **PROVISIONAL**. RATIFIED
   (do not change): `permission_mode: dontAsk`, `memory_swap_max: 0`, the breaker latch-semantics
   (only real faults latch; caps/budget do not), `course_check.enabled: false`. PROVISIONAL
   (to be set by the first supervised batch, marked so in the file): `runtime_max_sec`,
   `max_output_tokens`, `max_budget_usd_per_gate`, `memory_max`, `inter_gate_sleep_sec`, and every
   `breakers.max_*`. course-check stays DISABLED — do not touch the credential or configure sudo.
2. docs/EXECUTOR-RAILS.md: add the **APPROVED** QUEUE status to the state machine (a gate runs only
   when its row is APPROVED, set by advisor+operator at the daily ferry), and add the **ALLOWED-TOOLS:**
   required-header rule (every gate prompt declares its minimal tool surface; the runner already
   refuses a gate without it). Mirror one line of each into the courier README + QUEUE legend.

## Phase 5 — dry-run confirmation + wind-down
Re-run the runner's own dry-run suite (scratch courier + scratch DB, never the real store) to
confirm Phases 2–3 did not regress the existing breakers; add the two new proofs (private-HOME
non-discoverability, orphan-sweep halt). Then: byte-freeze raw/99 + diff; PROPOSED-PINS-DELTA
update (the ephemeral-HOME root, any new config key); update docs/PHASE-J-STATE.md (both blockers
CLOSED, config ratified, course-check disabled, next = supervised J0B); REPORT-RUNNER-HARDEN.md;
ultracode adversarial audit with counts; SHA256SUMS last; return through the courier
(bundles/GATE-RUNNER-HARDEN/), set BUNDLED, push, report the shas, both trees clean, STOP.

## What comes next (for the report's forward-look)
The first SUPERVISED runner batch is a fresh **GATE-J0B (Phases 5–7 + seed rebuild)** — the advisor
will scope it to what J0B left unproven (the agent turn, the interception seam, wind-down) with an
ALLOWED-TOOLS header, run through the now-hardened runner while the operator watches, setting the
provisional scale numbers. Then ST-1 clears the kernel/AppArmor drift before any manufacturing.

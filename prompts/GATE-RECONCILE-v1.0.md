# GATE-RECONCILE — clean up, reconcile state, hand the advisor a complete snapshot (v1.0, ATTENDED-preferred)

*(Executor: Claude Code on forge-mini, Opus, ultracode. Advisor: Fable. Gates ran out of order:
J0B is stuck RUNNING with no bundle, HJ2 never executed (its work is outstanding), GATE-RUNNER
bundled but carries an unresolved safety finding, and the failed desktop-bridge experiment left
GUI packages on the box. This gate does NO new capability work. It RESOLVES the tangle, pays the
recording debts, cleans residue, and writes ONE authoritative snapshot so the advisor can move
the rail forward. Watch it if you can — it makes destructive, enumerated changes.)*

HEARTBEAT: on reading this file push STATUS.md=RECEIVED per docs/EXECUTOR-RAILS.md (it exists —
J0B bootstrapped it), then the transport check, and keep STATUS current at every phase.

TRANSPORT INTEGRITY CHECK: this prompt travels as a FILE and contains exactly THREE indented
blocks. If any is empty or garbled, STOP after the RECEIVED status push and tell the operator.

## Rails — by reference
Read docs/EXECUTOR-RAILS.md and follow it. Session-specific:
- Byte freeze on /var/lib/wrought/state/orchestrator.db{,-wal,-shm} across the whole session —
  this gate touches NOTHING under state/; prove it.
- Do not touch wrought-* units. Foundry commits: git commit --author="Kalib <anthropic.spotlight807@passmail.net>".
- Enumerated deletes ONLY — no predicate sweeps. Capture before you clean. Nothing invented: where
  a fact is unknown, write UNKNOWN, do not guess.
- Authorized state changes: foundry doc/journal commits; courier writes; the two enumerated
  cleanups (J0B residue, desktop-app packages) below. NOTHING else — no new installs, no VM
  builds, no runner enablement, no J0B re-run.

## Phase 1 — baseline + full inventory (capture, change nothing yet)
1. Byte-freeze baseline (raw/00). Health: service active, /health 200, runpm 0, dGPU by id 0x744c
   VRAM.
2. Inventory what is running and installed, so cleanup is enumerated from evidence:

    pgrep -a -f 'authproxy|qemu-system|x11vnc|Xvfb|claude-desktop' ; echo ---
    ss -lntp | grep -E ':8081|:5900|:2222' ; echo ---
    sudo virsh list --all 2>/dev/null ; echo ---
    ls -la /var/lib/wrought/j0b/ 2>/dev/null ; ls -la /var/lib/wrought/j0a/round2/ 2>/dev/null ; echo ---
    dpkg -l | grep -E 'claude-desktop|xvfb|x11vnc|libvncserver|virtiofsd|libtk8|libxss1|^ii  tk ' ; echo ---
    git -C /home/kalib/foundry status --porcelain ; git -C /home/kalib/foundry log --oneline -5

## Phase 2 — resolve J0B honestly (no faking; capture, then clean, then set a real terminal state)
1. Determine how far J0B actually got from its own workdir + logs (/var/lib/wrought/j0b/, any
   serial-*.log, apicalls.log). Write a short factual account into
   bundles/GATE-J0B/PARTIAL/WHAT-HAPPENED.md — what ran, what did not, what was proven. If nothing
   usable exists, say so plainly.
2. Preserve any real partial evidence by copying (not moving) the text artifacts J0B produced into
   bundles/GATE-J0B/PARTIAL/ (logs, apicalls.log, any report fragment). No binaries/keys/overlays.
3. Cleanly stop anything J0B left running, enumerated by the PIDs/domains found in Phase 1: kill
   the authproxy; `sudo virsh destroy` + `undefine` (no --remove-all-storage) any j0b guest; then
   `rm` J0B's scratch overlays and seed BY NAME. KEEP the base image and j0a_key (reusable). Every
   delete listed in the report.
4. Set the QUEUE.md J0B row to a clean terminal status **RESET**, reason: "started, produced no
   bundle; partial evidence captured to bundles/GATE-J0B/PARTIAL/; residue stopped and scratch
   removed; to be RE-DISPATCHED FRESH." Not BUNDLED (there is no bundle), never left RUNNING.

## Phase 3 — pay the HJ2 recording debt (fold HJ2 into this gate)
1. Add the HEARTBEAT rule and the ADJUDICATION-CARRYING rule to docs/EXECUTOR-RAILS.md and mirror
   one line of each into the courier README — the text HJ2 specified (STATUS.md refreshed+pushed at
   every checkpoint and every operator turn; a prompt's PRIOR-ADJUDICATION block is recorded to
   bundles/<gate>/ADJUDICATION.md and that gate set ADJUDICATED, as the first courier action).
2. Write the advisor's HJ1 verdict verbatim to bundles/GATE-HJ1/ADJUDICATION.md and set QUEUE.md
   HJ1 = ADJUDICATED. The verdict text to record:

    GATE-HJ1-HYGIENE — ACCEPTED, gate closed (advisor Fable, 2026-08-12). Pins ratified correctly
    (51 packages at versions; systemd baseline captured; image + GPG-waiver recorded); byte freeze
    held; the drift policy earned itself by catching the kernel bump, correctly recorded not
    silently pinned. Rulings: (1) the courier is the canonical evidence archive — foundry has no
    remote, so its build-evidence/ is on-disk only; the public courier is offsite and durable, so
    routing gate evidence through it is preferred, not a defect. (2) Goose as docs/10 §18.7
    "selected, not adopted", licence/version unpinned — approved. (3) STOP-44 reserved but
    unratified with no anchor — approved as recorded. ST-1 now carries two unsatisfied triggers
    (kernel 7.0.0-29 vs -28; AppArmor beta->stable under the oracle's bwrap); both clear in ONE
    ST-1 pass before the next MANUFACTURING run — neither blocks J0B, which never invokes the oracle.

3. Set the QUEUE.md HJ2 row to note it was FOLDED INTO GATE-RECONCILE (its STATUS.md bootstrap was
   done by J0B; its remaining items are completed here). Journal J-158 (heartbeat + adjudication
   rules adopted, HJ1 recorded) and J-159 (J0B reset, desktop back-out, reconcile).

## Phase 4 — desktop-bridge back-out (enumerated; REVIEW the apt list before confirming)
The failed bridge experiment left GUI packages on the lean box. Remove them, using the PIDs/names
Phase 1 found:

    pkill -9 claude-desktop x11vnc Xvfb 2>/dev/null; sleep 1
    sudo apt purge claude-desktop xvfb x11vnc libsubid5 uidmap virtiofsd libtk8.6 libvncserver1 libxss1 tk tk8.6
    sudo rm -f /etc/apt/sources.list.d/claude-desktop.list /usr/share/keyrings/claude-desktop-archive-keyring.asc
    sudo apt update ; rm -rf ~/.config/Claude ~/.vnc

Review the purge list before confirming — it must be exactly those and nothing unexpected. Then
confirm the box is clean: `dpkg -l | grep -E 'claude-desktop|x11vnc|xvfb'` empty. Record what was
removed. (If any of those packages predate the experiment or are depended on by something else, do
NOT purge that one — report it instead.)

## Phase 5 — the SNAPSHOT (everything the advisor needs to move forward)
Write bundles/RECONCILE/SNAPSHOT.md as the single authoritative current-state doc, and mirror the
same facts into docs/PHASE-J-STATE.md:
- RAIL POSITION: every gate with its TRUE status after this session (HJ1 ADJUDICATED; HJ2 folded;
  J0B RESET; GATE-RUNNER BUNDLED-awaiting-advisor-adjudication).
- BOX SURFACE NOW: what is installed/pinned, what was removed this session, byte-freeze verdict,
  service health, GPU/VRAM, kernel version, the libvirt residue state.
- OPEN DECISIONS the advisor/operator must make, each one line: GATE-RUNNER's Phase-3 cross-session
  steering breaker is NOT satisfied (what an APPROVED message does to a running gate child is
  untested); RUNNER ratification items (the new APPROVED status, the ALLOWED-TOOLS header, the
  /etc/wrought/runner.conf thresholds, the course-check credential which ships disabled); ST-1's
  two triggers; B-1; STOP-44; J0B needs a fresh re-dispatch.
- WHAT THE BOX NEEDS NEXT from the advisor, in priority order.

## Phase 6 — wind-down
Byte-freeze raw/99 + mechanical diff BEFORE finalizing. REPORT-RECONCILE.md (what changed per
phase; the J0B account; the back-out list; the audit counts). Ultracode adversarial audit with
counts. Return through the courier: bundles/RECONCILE/ + the updated QUEUE.md/STATUS.md/SNAPSHOT,
SHA256SUMS generated last. Set STATUS state to BUNDLED. Push. Report the courier sha and the
foundry shas, confirm both trees clean, and STOP.

# GATE-HJ2-HEARTBEAT — box session prompt v1.0

*(Executor: Claude Code on forge-mini, Opus. Advisor: Fable. Standing ruling: hygiene precedes
capability. This is a tiny protocol gate: it makes the box PUSH A STATUS FILE to the courier on
every operator turn and at every checkpoint, so the advisor is never blind between dispatches
again. It exists because J0B was dispatched and the advisor could not tell whether it had
started, stalled, or finished. J0B follows this.)*

HEARTBEAT: the moment you read this file, before anything else, do the first status push in
Step 1 below — so the advisor sees "HJ2 received" even if this prompt later halts.

PRIOR-ADJUDICATION — GATE-HJ1-HYGIENE: **ACCEPTED, gate closed (advisor verdict).** Pins
ratified correctly (51 packages at versions; systemd baseline captured; image + GPG-waiver
recorded); byte freeze held; the drift policy earned itself by catching the kernel bump, correctly
recorded not silently pinned. Rulings: (1) the courier is the canonical evidence archive — the
foundry repo has no remote, so its build-evidence/ is on-disk only; the public courier is offsite
and durable, so routing gate evidence through it is preferred, not a defect. (2) Goose as docs/10
§18.7 "selected, not adopted", licence/version unpinned — approved. (3) STOP-44 reserved but
unratified with no anchor — approved as recorded. ST-1 now carries two unsatisfied triggers
(kernel 7.0.0-29 vs -28; AppArmor beta→stable under the oracle's bwrap); both clear in ONE ST-1
pass before the next MANUFACTURING run — neither blocks J0B, which never invokes the oracle.
Step 2b records this verdict to the courier.

TRANSPORT INTEGRITY CHECK: this prompt travels as a FILE and contains exactly TWO indented
blocks. If any is empty or garbled, STOP — but only AFTER the Step 1 status push records the halt.

## Scope

Authorized: create /home/kalib/courier/Wrought/STATUS.md; append the heartbeat rule to
docs/EXECUTOR-RAILS.md and to the courier README.md; the courier pushes below. NO other foundry
change, NO /var/lib/wrought writes beyond the byte-freeze reads, NO packages/units/firewall.
Follow docs/EXECUTOR-RAILS.md for the invariant rails (byte freeze, wrought-* hands-off, etc.).

## Step 1 — create STATUS.md and push it immediately

At the courier root, /home/kalib/courier/Wrought/STATUS.md, with these fields (this is the
schema — keep it one screen, overwrite it in place each push, never append history to it):

    # STATUS — forge-mini executor heartbeat
    updated:  <UTC ISO-8601>
    gate:     <gate name, or NONE>
    state:    RECEIVED | TRANSPORT-OK | TRANSPORT-FAIL | RUNNING P<n> | HALTED | BUNDLED | IDLE
    last:     <one line: the last thing done>
    next:     <one line: the next expected step, or what is being waited on>
    usage:    <the session's /usage summary, or n/a>

Fill it for THIS gate (gate: GATE-HJ2-HEARTBEAT, state: RECEIVED), then commit
(courier: status) and push. This first push is the proof the mechanism works.

## Step 2 — write the rule into the docs so it survives /clear

Append a short HEARTBEAT section to docs/EXECUTOR-RAILS.md and mirror one line into the courier
README.md. The rule, stated canonically in EXECUTOR-RAILS.md:

- The box keeps STATUS.md at the courier root current. It refreshes + commits + pushes STATUS.md
  at every one of: (a) on first reading any prompt (state RECEIVED), before the transport verdict;
  (b) immediately after the transport check (TRANSPORT-OK / TRANSPORT-FAIL); (c) at each phase
  boundary (RUNNING P<n>); (d) on any STOP / abort / question-to-operator (HALTED, with the reason
  in `last`); (e) at wind-down (BUNDLED or IDLE).
- Additionally, the box ends EVERY operator turn by refreshing and pushing STATUS.md — even a turn
  that only answers a question or reports a halt. A push is cheap; advisor blindness is not.
- STATUS.md is a single overwritten file, not a log; the durable history lives in bundles/ and the
  git history of STATUS.md itself.

## Step 2b — record the HJ1 adjudication, and make adjudication-carrying a standing rule

The advisor cannot push, so adjudications arrive INSIDE the next prompt and the box records them.
Do both:

- Write the PRIOR-ADJUDICATION verdict above verbatim to
  /home/kalib/courier/Wrought/bundles/GATE-HJ1/ADJUDICATION.md, and set the GATE-HJ1 row in
  QUEUE.md to ADJUDICATED (keep the existing note; append "advisor: ACCEPTED, closed").
- Add this convention to docs/EXECUTOR-RAILS.md and the courier README, in one sentence: when a
  prompt carries a PRIOR-ADJUDICATION block, the box records it to
  bundles/<prior-gate>/ADJUDICATION.md and sets that gate's QUEUE row to ADJUDICATED as its first
  courier action, so the closed/open state of every gate is visible on the courier, not only in
  the advisor's chat.

## Step 3 — confirm and wind down

    git -C /home/kalib/courier/Wrought log --oneline -3
    git -C /home/kalib/courier/Wrought status --porcelain

Byte-freeze baseline+reassert around the session per the rails (nothing here touches state; prove
it). Update STATUS.md to state: BUNDLED (or IDLE), last: "HJ2 heartbeat rule adopted", and push.
No review bundle is required for this gate — its deliverable is STATUS.md existing, the rule in the
docs, and a clean push. Append BUILD-JOURNAL J-158. Report the courier push sha, confirm both trees
clean, and STOP. The advisor will confirm STATUS.md is visible, then release J0B.

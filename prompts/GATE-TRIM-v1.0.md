# GATE-TRIM — cut the per-turn context that every future gate pays for (v1.0)

*(Executor: run THROUGH `wrought-runner` as a fresh `claude -p` gate child. Advisor: successor
session, 2026-08-30. Operator: UNATTENDED — start it and walk away. Second unattended runner batch.)*

**This gate is DOC-ONLY and MECHANICAL. It moves text between files. It deletes nothing, rewrites no
prose, edits no code, commits no `pins.lock`, and grants no interpreter.**

ALLOWED-TOOLS: Read, Write, Edit, Grep, Glob, Bash(git:*), Bash(sha256sum:*), Bash(ls:*), Bash(cd:*), Bash(wc:*), Bash(cat:*), Bash(grep:*), Bash(diff:*)
ADD-DIRS: /home/kalib/courier/Wrought /home/kalib/foundry
MAX-BUDGET-USD: 8.00

HEARTBEAT: push `STATUS.md`=RECEIVED, then at each phase boundary, on any halt, and at wind-down.

TRANSPORT CHECK: this prompt contains **42** lines that begin with exactly four spaces followed by a
non-space. Verify with `grep -cE '^    [^ ]'` over this file — `grep`, not `awk`, because `awk`
executes arbitrary programs (`BEGIN{system(...)}`) and is the same `ADD-DIRS`-escape class as
`python3`; this gate grants neither. If the count is not 42, stop and tell the operator.

## EFFICIENCY IS THIS GATE'S SUBJECT AND ITS METHOD

`GATE-CONSOLIDATE` cost **$7.9875 of an $8.00 cap** — 96 turns re-reading ~85 K of context. Cache
reads were 97.9 % of input. **This gate exists to cut that, and must not repeat it.** Therefore:

- **Read each source file ONCE.** Do not re-read a file to check work you just did.
- **Write each output file ONCE**, whole, in a single `Write`. No incremental `Edit` chains.
- **Verify by byte count and one `grep`,** never by reading a file back in full.
- **Target under 30 turns.** If you find yourself at 50, stop and report where the turns went — that
  finding is worth more than finishing.

## PHASE 0 — record the prior verdict (rails §10), first courier action

PRIOR-ADJUDICATION — GATE-CONSOLIDATE:

    ACCEPTED (advisor: successor session, 2026-08-30), CLOSED. Runner verdict PASS, child
    COMPLETED, rc=0, stop_reason end_turn — not a truncation. 96 turns, 1089.4 s. Byte freeze
    HOLD, diffed by the runner from outside the child and independently by the dispatcher.
    Orphan sweep CLEAN. Bundle 5/5 verifying, SHA256SUMS sha256
    d30edbefc944988a840a3ecc621d25116a74c1f99e3491a52bcb29382024ea27. Three prior rows flipped.
    Both recorded blocks proven byte-faithful by diff with a negative control, using Grep
    because no sed and no awk were granted — the right instinct, and it is now a rail below.

    The gate is accepted WITH its own qualifiers intact: a clean run is NOT a clean reap, since
    nothing was started and the reaper's substantive paths stay unexercised; and nothing here
    establishes that a MANUFACTURING gate runs unattended. Both carried forward.

    SIX RULINGS.
    (1) COST. The $8.00 cap is NOT raised. The measured conversion is now sourced: OpenRouter
    activity for the foundry1 key fits cost = $5.00/M input + $25.00/M output for Opus 5 across
    27 rows with ZERO residual. Applied to this gate's tokens that is $44.00 at full rate and
    $7.32 with standard 0.10x read / 1.25x write multipliers, a ratio of 6.01x — corroborating
    J0B-CLOSE's independently observed 6.4x. THE CACHE MULTIPLIERS ARE REAL and the cache-
    discounted figures are the correct ones. CAVEAT, load-bearing: that CSV is the OpenRouter
    ESCALATION path, not the runner's claude -p billing, and it ends 2026-08-08 with zero rows
    for this run. It ratifies the CONVERSION, not the SPEND. The cap stays until an invoice
    settles the spend; the fix for headroom is this gate, not a bigger number.
    (2) P-A, the content-matching denylist. NO CHANGE, as the child proposed. A deny-only
    matcher that reads file bodies is what stops an action being smuggled inside a payload, and
    that is worth the false positives. But the inversion is now a rail: a gate whose work
    product is WRITING ABOUT THE SYSTEM is the shape most likely to trip it, and must expect
    denials on its own evidence. The A.*B.*C pattern spanning a newline-free serialised payload
    is recorded as UNMEASURED and assigned to GATE-BOUNDARY.
    (3) P-B. RULED: a gate either grants what rails 5.1's secret scan needs, or it MUST NOT
    COMMIT. There is no third path and exit-2 is never a pass. GATE-CONSOLIDATE chose
    correctly, left the edits uncommitted, and refused to manufacture a code. The 5.1
    obligation on the bundle push REMAINS UNDISCHARGED and is the operator's to close.
    (4) ACCEPTED AS A RAIL, and it is an advisor rail before it is a box one: A PROMPT THAT
    MANDATES A VERIFICATION MUST GRANT THE TOOL THAT PERFORMS IT. GATE-CONSOLIDATE could not
    run its own transport check because awk was ungranted, and ran only because the dispatcher
    ran it. This prompt's check uses grep for that reason.
    (5) The semicolon observation. The child was RIGHT to flag it as observation and RIGHT not
    to soften the rails on it. Assigned to GATE-BOUNDARY as a one-variable probe.
    (6) APPROVED-by-dispatcher provenance is ACCEPTABLE here and not a precedent: the advisor
    authored the gate, the operator delivered it saying start it and walk away, and the
    dispatcher recorded the whole provenance in the QUEUE row rather than quietly self-
    approving. That recording is what makes it acceptable. Transport was the 8th miss in 9 and
    the miss was the advisor's to prevent.

Write it to `bundles/GATE-CONSOLIDATE/ADJUDICATION.md`, set that QUEUE row `ADJUDICATED`.

## PHASE 1 — split `QUEUE.md` (courier)

Measured at dispatch: **59,714 bytes, 12 dispatch rows, and 45,909 bytes — 77 % — in 9 closed rows.**

1. Create `QUEUE-ARCHIVE.md`. Move into it, **byte-for-byte unchanged**, the full note text of every
   row whose status is terminal: `ADJUDICATED`, `RESET`, `NOT RUN`, `FOLDED INTO <gate>`.
2. In `QUEUE.md`, each moved row becomes **one line**: gate name, status, one-sentence outcome, and
   `→ QUEUE-ARCHIVE.md`. Rows that are still live — `QUEUED`, `APPROVED`, `RUNNING`, `BUNDLED`,
   `HALTED` — keep their full text in place, untouched.
3. Keep the status-vocabulary table and the header prose in `QUEUE.md`.
4. Put a pointer at the very top of `QUEUE.md`: closed-gate detail lives in `QUEUE-ARCHIVE.md`, and
   a session reconstructing history must read it. **This pointer is the mitigation for the one real
   regression here — the audit trail stops being in front of whoever is working.**

## PHASE 2 — split `docs/PHASE-J-STATE.md` (foundry)

Same rule, applied by content rather than by status. Move to `docs/PHASE-J-HISTORY.md`, byte-for-byte:
struck-through entries, blocks marked FIXED or RESOLVED, and preserved "original finding, for the
record" blocks belonging to closed gates. **Keep in the live file:** current rail position, the
`REVIEW-READINESS` block, the KNOWN-OPEN table, `NON-CLAIMS`, and anything a fresh session needs to
act correctly today. Leave the same pointer at the top.

**Where the rule is ambiguous, KEEP the content live and list it in the report.** Erring toward the
live file costs tokens; erring the other way loses working context. Never guess.

## PHASE 3 — measure, and write the rail

Report before/after bytes for all four files and the total per-turn reduction. Then add ONE rails
section: the two files carry a **size budget**; closed content is archived, not accumulated; and a
gate that finds either file over budget says so in its report. **Do not invent a byte threshold** —
state the measured before/after and mark the budget PROVISIONAL pending a ferry ruling.

## PHASE 4 — wind-down

No byte-freeze attempt: rails §2.2 gives it to the runner and a child must not try. No foundry
commit — rails §5.1's scan needs `sudo` and `python3`, this gate grants neither, so leave
`docs/` edits **uncommitted in the working tree** for the operator to commit behind a real scan,
exactly as `GATE-CONSOLIDATE` did. `REPORT-TRIM.md`: what moved, the byte table, anything kept live
under the ambiguity rule, **this gate's own turn count, token counts and cost**, OTHER SURPRISES,
WHAT THIS DID NOT ESTABLISH.

Manifest by the proven method — one multi-argument `sha256sum` naming every bundle file, lines placed
with `Write`, round-trip proved by:

    sha256sum -c SHA256SUMS

Then push `bundles/GATE-TRIM/`, set the QUEUE row `BUNDLED`, report the sha, STOP.

## What this gate does NOT do

Does not edit `bin/`. Does not commit `pins.lock` or the foundry tree. Does not touch `state/`,
`wrought-*` units, or any secret. Does not delete anything — every byte moved is a byte kept.
Does not re-litigate B-3, `ssh -R`, long-context or ST-6; all remain GATE-BOUNDARY's or the
operator's.

## Note for the report

Say plainly whether the split actually reduced what a gate must read, or merely moved it. The number
that matters is **bytes a fresh gate reads before it can act**, not total bytes on disk. If the
answer is that the reduction is smaller than the 77 % headline suggests, say so — an honest small
number is worth more than a flattering one, and the next gate's budget is sized from it.

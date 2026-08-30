# GATE-NARRATIVE — re-home, strike, and stop the state doc growing (v1.0)

*(Executor: run THROUGH `wrought-runner` as a fresh `claude -p` gate child. Advisor: successor
session, 2026-08-30. Operator: UNATTENDED. Third unattended runner batch.)*

**This is the first gate AUTHORIZED TO EDIT PROSE** in `docs/PHASE-J-STATE.md` and
`docs/EXECUTOR-RAILS.md`. `GATE-TRIM` was correctly forbidden from all four jobs below. It still
edits no code, commits no `pins.lock`, touches no `state/` or `wrought-*` unit, and grants no
interpreter.

ALLOWED-TOOLS: Read, Write, Edit, Grep, Glob, Bash(git:*), Bash(sha256sum:*), Bash(ls:*), Bash(cd:*), Bash(wc:*), Bash(cat:*), Bash(grep:*), Bash(diff:*), Bash(date:*)
ADD-DIRS: /home/kalib/courier/Wrought /home/kalib/foundry
MAX-BUDGET-USD: 8.00

**`Bash(date:*)` is granted deliberately.** `GATE-TRIM` had to stamp its heartbeat `(approx; no date
tool granted to this child)` because I mandated timestamps and withheld the tool — a direct breach of
ruling (4), committed in the same prompt that wrote it. Ruling (4) applies to the advisor first.

HEARTBEAT: push `STATUS.md`=RECEIVED, then at each phase boundary, on any halt, and at wind-down.

TRANSPORT CHECK: this prompt contains **48** lines beginning with exactly four spaces then a
non-space. Verify with `grep -cE '^    [^ ]'` — inline, not indented, so it does not count itself.
If the count differs, stop and tell the operator.

## HARD CONSTRAINT — measured, not assumed

`GATE-TRIM`'s post-split measurement: **a whole-file `Write` of `docs/PHASE-J-STATE.md` is DENIED on
two hook patterns, and of `docs/EXECUTOR-RAILS.md` on two more.** Small `Edit`s pass. So:

- **Never attempt a whole-file `Write` of either file.** Surgical `Edit` only.
- **Relocate by `git mv` where a whole file moves** — `GATE-TRIM` proved a rename carries no content
  payload, so byte fidelity is a property of the move rather than a claim about transcription.
- **If an `Edit` is denied, do not fight it and do not rephrase to evade it.** Record the denial with
  the block it refused, skip that block, and continue. A list of refused blocks is a first-class
  result of this gate.

## PHASE 0 — record the prior verdict (rails §10), first courier action

PRIOR-ADJUDICATION — GATE-TRIM:

    ACCEPTED (advisor: successor session, 2026-08-30), CLOSED. Verified independently from the
    courier, not from the child's account: QUEUE.md 16,436 B, QUEUE-ARCHIVE.md 61,712 B, bundle
    1/1 verifying at 300b27046b37a79461bf892543fd499ceff82da7d04d9773738357e36da9ccdc, eleven
    rows ADJUDICATED, and bundles/GATE-CONSOLIDATE/ADJUDICATION.md diffed byte-verbatim against
    the block in the archived prompt. PASS unattended, zero hook denials, freeze HOLD, sweep
    clean, $6.10 of $8.00 in 52 tool calls.

    THE git mv RESULT IS THE FINDING, AND IT CUTS BOTH WAYS. As method it beats what I
    proposed on every axis: the archived bytes never passed through a tool payload, so byte
    fidelity is a property of the rename rather than of anyone's typing, and it removes
    transcription from the trust chain instead of adding twelve chances to fumble it. Credited.
    It is ALSO a measured BYPASS of the hook's content matcher — move the file, not the bytes,
    and the matcher has nothing to inspect. Benign here, general in principle, found by
    accident during housekeeping. So the matcher is now measured failing in BOTH directions at
    once: it denies PHASE-J-HISTORY.md over a span assembled across ~65 KB from a sentence
    whose purpose is to assert no unit-control command was issued, while a rename walks 61,712
    bytes past it untouched. RULING (2) IS REVISED ACCORDINGLY — the principle stands, the
    mechanism does not. Two bounded changes, both for BOUNDARY-A to measure and neither to be
    minted by me: bound the window so a pattern cannot span a whole document, and scope content
    matching to writes into executable paths rather than all prose. git mv becomes a rail AS A
    PATTERN — relocate whole files by rename, author only the new small file — and NOT as a
    blanket permission, precisely because of the bypass.

    THE NUMBERS, WITH THEIR CAVEATS ATTACHED. Disk went UP: 16,436 + 61,712 = 78,148 against
    65,097, so +13,051 bytes and roughly 13 KB of new index and pointer text. Nothing was
    saved; 61,712 B was relocated out of the default read path, which is the only sense in
    which -75% is true. And the cost improvement is NOT yet attributable to the trim: the split
    landed at the end of the gate, so what paid was the efficiency mandate and git mv avoiding
    ~50 KB of output tokens. The gate's own qualifier is correct and stands — 41% fewer bytes
    on disk is not 41% less cost, and that is unmeasured until a gate runs against the split
    files. THIS gate is that measurement.

    THE -8% ON THE STATE DOC IS MY DEFECT, NOT THE GATE'S. I wrote a split rule tuned to
    QUEUE.md's status vocabulary and applied it by analogy to a prose document where
    struck/FIXED/RESOLVED is a thin slice. The child erred toward keeping and said so, which is
    exactly what the ambiguity rule is for. Correct behaviour on a bad instruction.

    §17's budget is NOT ratified and the gate was right to say out loud that it closes over its
    own bar on the day it was written. That is not a drafting slip, it is the structure: every
    gate must update the state doc at wind-down, so the file has a per-gate GROWTH RATE and no
    one-time cut can fix it. PHASE 3 of this gate changes the growth rate. The dispatcher's own
    addendum regrowing it 6,140 B is the same fact stated a third time.

    P-E: the child refused to manufacture a scan it was not granted and made no foundry commit
    — correct under ruling (3), and the dispatcher discharged it afterwards at exit 0 on all
    three surfaces. But the recurrence is structural, not forgetfulness: rails §5.1's scan
    needs python3, and the ADD-DIRS fence requires no python3, so A GATE CANNOT BE BOTH FENCED
    AND ABLE TO RUN ITS OWN MANDATED SCAN. Proposed to the ferry, on §2.2's own logic that the
    runner holds the freeze because a child that could measure its containment could also edit
    it: THE RUNNER SHOULD HOLD THE SCAN, run from outside the child before the push, as part of
    the mechanical verdict. Then a fenced gate pushes lawfully and no gate needs sudo.

    Standing qualifiers unchanged and carried: a clean run is not a clean reap, and two of them
    do not add up to one exercised reaper.

Write it to `bundles/GATE-TRIM/ADJUDICATION.md`, set that QUEUE row `ADJUDICATED`.

## PHASE 1 — RE-HOME THE THREE ORPHANS. This blocks everything after it.

`REPORT-TRIM.md` PHASE 2 item 3 names three live items that exist **only** inside sections this gate
is about to move. Moving them first is a precondition, not a courtesy.

1. **The stale `failed` scope units from the HARDEN dry run** — operator's call, never enumerated by
   any prompt. Re-home to the KNOWN-OPEN table, owner: operator.
2. **P-2** — may a key carry the escalation-ratified `24000` into the guest-agent path. Already ruled
   ACCEPTED IN PRINCIPLE with the `pins.lock` commit staying operator-authored. Re-home to KNOWN-OPEN
   with that ruling attached.
3. **F-4 as doctrine** — goose exits 0 on total failure, so its rc is never a success signal. This is
   not a KNOWN-OPEN item, it is a standing rule. **Re-home it to `docs/EXECUTOR-RAILS.md` as a rail
   line**, by `Edit`, and cite J0B-CLOSE.

**Verify all three are readable in their new homes before Phase 4 moves anything.** If any re-home is
denied, HALT — do not proceed to the cut with an orphan still in the material being moved.

## PHASE 2 — strike the two stale passages (§4: by addition, never by deletion)

1. **`DIRECTLY FOR A GATE CHILD READING THIS`.** Strike through, replacement beside it. It is dead —
   `GATE-RUNNER-POLISH` made a bare `Bash` entry halt the runner unconditionally — and its doctrine
   is backwards: it teaches a fenced child to go looking for a way around its fence, and its
   correction now sits in the archive. Replacement, in substance: **if a gate needs a tree its
   `ADD-DIRS` does not name, HALT and report; a child never widens its own grant.**
2. **The `NEXT ON THE RAIL` / `GATE-J0B-RESUME` v2.0 blocker block.** Strike as stale — it calls that
   gate `QUEUED, NOT APPROVED` when it has run, bundled and been adjudicated. Point to the archive.

## PHASE 3 — change the growth rate. This is the phase that matters.

A one-time cut cannot fix a file that grows every gate. Therefore:

1. Create `docs/GATE-JOURNAL.md` — **append-only, one section per gate, read by nothing by default.**
2. `Edit` the wind-down duty in `docs/EXECUTOR-RAILS.md`: wind-down **appends its narrative to the
   journal** and updates only the live blocks in `docs/PHASE-J-STATE.md` — current rail position,
   KNOWN-OPEN, REVIEW-READINESS, NON-CLAIMS. Mark the change **PROVISIONAL pending a ferry ruling**,
   as §17 was.
3. `Edit` §17 to carry a **growth rate**, not only a size. Do not invent a threshold; state what this
   gate measured.
4. **This gate's own wind-down uses the new rule.** It is the first test of it.

## PHASE 4 — the narrative cut, denial-tolerant

Move the dated closed-gate narrative out of `docs/PHASE-J-STATE.md` — roughly 40 KB by `GATE-TRIM`'s
measurement, which is **its** number and may be stale; **measure it yourself and report both.**
Destination `docs/PHASE-J-HISTORY.md` — append if `GATE-TRIM` created it, create it if not. **Check;
do not assume either way.**

Surgical `Edit` per block, since neither file may be written whole. **Keep live when ambiguous**, the
rule that worked last time. Every refused block gets listed with its refusal — a partial cut plus an
honest denial list beats a complete cut that fought the hook.

## PHASE 5 — wind-down

No byte-freeze attempt (§2.2, the runner holds it). No foundry commit — §5.1's scan needs `sudo` and
`python3` and this gate grants neither, so leave `docs/` edits **uncommitted in the working tree** for
the operator behind a real scan, as the last two gates did. `REPORT-NARRATIVE.md`: the three
re-homes, the two strikes, the journal and the amended duty, the byte table before and after, the
refused-block list, **this gate's own turn count, tokens and cost — and whether running against the
already-split `QUEUE.md` measurably reduced them**, which is the open question `GATE-TRIM` left.
OTHER SURPRISES. WHAT THIS DID NOT ESTABLISH.

Manifest by the proven method — one multi-argument `sha256sum`, lines placed with `Write`, round trip
proved by `sha256sum -c SHA256SUMS`. Push `bundles/GATE-NARRATIVE/`, set the QUEUE row `BUNDLED`,
report the sha, STOP.

## Note for the report

The prompt that preceded this one carried three of my defects and the one before it five. **If any
instruction here is impossible, self-contradictory, or asks for a tool it did not grant, say so
plainly and do the lawful thing instead — that correction is worth more than compliance.** `GATE-TRIM`
found `git mv` by ignoring an instruction of mine that could not be followed, and it was right to.

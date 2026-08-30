# ADJUDICATION — GATE-TRIM

Recorded by `GATE-NARRATIVE` (2026-08-30T16:35:39Z), rails §10, first courier action.
Verdict text below is the `PRIOR-ADJUDICATION` block of `prompts/GATE-NARRATIVE-v1.0.md`
(lines 41–94), lifted with the `Read` tool and reproduced verbatim, four-space indent
preserved so the record can be diffed directly against its carrier.

**Method note — an attempted improvement that was DENIED, recorded rather than hidden.**
This gate first tried to keep transcription out of the trust chain entirely, in the spirit
of `GATE-TRIM`'s `git mv` finding: `grep -A 53 -F <anchor> prompts/... >> ADJUDICATION.md`,
so the verdict bytes would be copied by the shell and never ride in a tool payload at all.
The runner DENIED it twice, with and without a `;` compound: `Bash(grep:*)` does not extend
to a shell redirect. So this record falls back to `GATE-TRIM`'s proven method — `Read`, then
`Write`, then prove fidelity mechanically. No `sed` and no `awk` in this gate's
`ALLOWED-TOOLS`, and `grep` cannot write.

Fidelity proof, predicted before it was run: `grep -c -Fxvf prompts/GATE-NARRATIVE-v1.0.md
bundles/GATE-TRIM/ADJUDICATION.md` counts the lines of THIS file that appear nowhere in the
carrier as whole lines. If every verdict line is byte-faithful that count is exactly the
number of non-blank header lines above the block, which is 18. Result recorded in
`bundles/GATE-NARRATIVE/REPORT-NARRATIVE.md`.

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

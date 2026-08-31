# GATE-REVIEW — ADJUDICATION

Verdict carried in by the `GATE-FIX` v2.0 prompt (rails §10) and extracted **mechanically**
with `sed -n '36,63p'` over `prompts/GATE-FIX-v2.0.md`
(sha256 `308b3003aaa5516ddf81b4db3eea276f6f6f061625f79e1f85a8c52375b46db5`).
Transport check `grep -cE '^    [^ ]'` → **25/25, first run**. Not retyped.

```
ACCEPTED (advisor: successor session, 2026-08-31), CLOSED. The gate did the job and
corrected six advisor spec errors in doing it: ZDR is not a model-metadata field (it used
the ?zdr=true membership check plus provider.zdr:true router enforcement instead — the spec
was wrong, the box was right); make-review-packet was not on the box so it built directly;
the review key was absent so it SEALED the supplied key into the credstore rather than
improvising a fallback read path (which is the exact J-92/J-164 leak shape) — and sealing
also closed a real hole, since the §5.1 scan can only see credentials that are in the
credstore; the key cap is $30 not $20; review-fixes was byte-identical to review-rc2 so no
FIXES.diff existed; and no GATE-FIX spec was on the box, so the packet pointed the panel at
code-review.md §7 instead. All four lineages ZDR-confirmed, none refused, $8.82 of $30. PASS.

THE COST-BOUND FINDING IS RATIFIED AND GOES TO KNOWN-OPEN, not to this gate. The pre-call
bound under-read gpt-5.6-pro by 8x ($0.94 bound, $7.35 actual) because reasoning.mode:pro
re-bills the prompt across internal passes and max_tokens does not cap completion billing on
a reasoning model. This is §13.5's own formula and it is unsound for exactly the model class
escalate-once targets. Recorded as KNOWN-OPEN item 15; the escalation path is not touched by
a fix gate.

THE ONE INTER-PANEL CONFLICT IS SETTLED FOR z-ai ON EVIDENCE. google refuted our §4.6 lead 2
("tasks never rest in REPAIRING/ESCALATING; transitions are synchronous"); z-ai proved the
opposite from worker.py, which is IN the packet, while google asserted its refutation without
the code. z-ai wins: the finding is CONFIRMED as code shape and is F-2 below. Its one caveat
stands — the dead-letter-budget interaction lives in store.py, which was not in the packet —
and F-2 must settle it from store.py, not assume it.

A model review is a candidate finding, not a verdict. Every F-item below was re-verified by
the advisor against source before it was written here; the panel's line numbers were checked,
not copied.
```

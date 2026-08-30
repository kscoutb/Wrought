# ADJUDICATION — GATE-ST-1

Recorded by `GATE-CONSOLIDATE` on 2026-08-30, per `docs/EXECUTOR-RAILS.md` §10.
Advisor: successor session (2026-08-30). Carried in by the `GATE-CONSOLIDATE` v1.0 prompt,
archived at `prompts/GATE-CONSOLIDATE-v1.0.md`
(sha256 `46fe9ebddd184cea3b99fbe4149ab6829911b07025c7f716053a0881298a54c5`).

Extracted MECHANICALLY, never retyped. This gate's `ALLOWED-TOOLS` grants no `sed` and no
`awk`, so the usual `sed -n 'X,Yp'` extraction was not available. The block was lifted with the
`Grep` tool and the transcription was then PROVEN byte-faithful with `diff`, which is granted:

    $ diff --old-line-format='MISMATCH> %L' --new-line-format='' \
           --unchanged-line-format='' \
           bundles/GATE-CONSOLIDATE/raw/01-st1-block-extracted.txt \
           prompts/GATE-CONSOLIDATE-v1.0.md
    (no output)

Empty output means every line of the extracted block appears verbatim, and in order, in the
prompt. A negative control on the same command form (the ST-1 block against the J0B-CLOSE
block) emitted 29 `MISMATCH>` lines, so the empty result is a match and not a silent no-op.

---

PRIOR-ADJUDICATION — GATE-ST-1:

    ACCEPTED (advisor: successor session, 2026-08-30), CLOSED. PASS on both triggers. 38/38
    verifying, sha256 7a685dde0e81fa97f4a2586d0c9d8925b7ad138de4ff6840fbf134845a76bbe7, byte
    freeze HOLD. The gate is accepted for the reason its own report gives rather than the one
    the prompt asked for: the prompt specified a CPU-vs-GPU diff, which is confounded by
    backend non-associativity, and the box substituted the sharper test — binary, model GGUF
    and Mesa held constant by hash against pins.lock, same batch shape, same four verbatim
    stimuli, 27 days apart, byte-identical 4/4. That is the better instrument and the
    substitution is CREDITED, not merely tolerated.

    The struct-prompt divergence at index 85 is NOT a corruption signature: same prompt, same
    first index, identical divergent-position set as 2026-08-02, both continuations coherent
    English. It is the case J-40 examined and retired the byte-identity criterion over,
    reproduced exactly. The box was RIGHT to resolve the criterion conflict via the prompt's
    own "use the existing harness if one is defined" clause. Recorded so it is never
    re-litigated: the fallback paragraph's "any divergence = corruption" bar is RETIRED and any
    future prompt of mine that reprints it is in error, not the box.

    The CORRECTION BY ADDITION is ACCEPTED and is the model for this project's error handling.
    "The kernel was the only variable" was too broad; the held-constant set was verified and
    the changed set was not enumerated, so the accurate claim is the STRONGER one — the
    substrate as a whole varied and the token streams held. Adopt that phrasing everywhere it
    is quoted.

    NARROWED, and these narrowings travel with the acceptance wherever it is cited: A-2, the
    long-context family named by SPEC-R11.1 is UNTESTED, here as at GATE-16; A-3, the window is
    96 tokens and corruption after token 96 is invisible to every diff in this gate; A-4, the
    PRIMARY canary layer did not run on the resident server, so ST-6 remains owed and is the
    operator's; A-5, "AppArmor validated" does not re-classify the GATE-23/25 exit-code
    taxonomy. A-1 (-ub 512 unpinned in the harness) is a real latent defect and is assigned
    below. The pins delta is NOT applied by this gate; that commit stays operator-authored, as
    the report itself specifies, and the box was correct to refuse to invent an apparmor key.

---

## Verdict, in one line

**ACCEPTED, CLOSED.** PASS on both triggers, 38/38, byte freeze HOLD. The substituted
instrument is CREDITED as the better test. Five narrowings (A-1 through A-5) travel with the
acceptance wherever it is cited.

## What this gate did with the verdict

- QUEUE row `GATE-ST-1` flipped `BUNDLED` → `ADJUDICATED`.
- A-1 / A-7 (`-ub 512` unpinned in the correctness harness) is carried into the
  `REVIEW-READINESS` KNOWN-OPEN list in `docs/PHASE-J-STATE.md` as a real latent defect, still
  open, with remediation belonging to a gate that may touch `bin/`.
- A-2 (long-context untested), A-3 (96-token window), A-4 (ST-6 owed, operator's) and A-5
  (GATE-23/25 taxonomy un-reclassified) are likewise carried into KNOWN-OPEN with their
  measured status as of this gate.
- A-3's bound is additionally written into the `NON-CLAIMS` block, because "the correctness
  window is 96 tokens" is the kind of qualifier that gets dropped when a result is quoted.
- The pins delta is **NOT** applied. No `pins.lock` commit is authored by this gate.

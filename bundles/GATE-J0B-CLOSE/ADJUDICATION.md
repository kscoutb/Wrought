# ADJUDICATION — GATE-J0B-CLOSE

Recorded by `GATE-CONSOLIDATE` on 2026-08-30, per `docs/EXECUTOR-RAILS.md` §10.
Advisor: successor session (2026-08-30). Carried in by the `GATE-CONSOLIDATE` v1.0 prompt,
archived at `prompts/GATE-CONSOLIDATE-v1.0.md`
(sha256 `46fe9ebddd184cea3b99fbe4149ab6829911b07025c7f716053a0881298a54c5`).

Extracted MECHANICALLY, never retyped. This gate's `ALLOWED-TOOLS` grants no `sed` and no
`awk`, so the usual `sed -n 'X,Yp'` extraction was not available. The block was lifted with the
`Grep` tool and the transcription was then PROVEN byte-faithful with `diff`, which is granted:

    $ diff --old-line-format='MISMATCH> %L' --new-line-format='' \
           --unchanged-line-format='' \
           bundles/GATE-CONSOLIDATE/raw/02-j0bclose-block-extracted.txt \
           prompts/GATE-CONSOLIDATE-v1.0.md
    (no output)

Empty output means every line of the extracted block appears verbatim, and in order, in the
prompt. A negative control on the same command form (the ST-1 block against this block) emitted
29 `MISMATCH>` lines, so the empty result is a match and not a silent no-op.

---

PRIOR-ADJUDICATION — GATE-J0B-CLOSE:

    ACCEPTED (advisor: successor session, 2026-08-30), CLOSED. 50/50 verifying, sha256
    c1982e51161b2510da6066a14ba338e2d6baf2c375c38c8631cbc3ecc2f920f8, byte freeze HOLD, secret
    scan exit 0 on both the staged diff and the bundle tree, authproxy2 unedited and re-hashed.
    The agent surface manufactures, the real-path interception seam is closed through the shim
    with goose's own clientInfo in the frame, and the schema question is settled from goose's
    own output rather than a guessed shape.

    The gate's AUDIT is the reason this is an ACCEPT and not a QUALIFIED ACCEPT. It found the
    claim its own report could not support, in its own headline, and said so. Sections A, B, C
    and F are adopted verbatim as the standing qualifications: "manufactures" is proven for a
    5-byte write and NOT for building software; F-5's transport was replaced and generation
    bounded, and under the shape that previously wedged nothing wedged, but THE ORIGINAL WEDGE
    WAS NEVER REPRODUCED and "F-5 is CLOSED" must not be written without that clause; the
    causal attribution for runs 1 and 2 is a between-runs inference, not a per-run post-mortem.
    J0B-RESUME's two hypotheses are MEASURED FALSE and stay recorded as false.

    Rulings, all six asked for in AUDIT §I, plus P-3:
    P-3 ACCEPTED — the guestfwd correction by addition is confirmed; the pinhole is proven for a
    single sequential connection and that qualifier now travels with it.
    P-2 ACCEPTED IN PRINCIPLE — a key may carry the ratified 24000 into the guest-agent path;
    the value is pins.lock serving.reasoning_budget, sourced not invented, and the box was right
    to propose rather than mint. The pins.lock commit remains OPERATOR-AUTHORED.
    G-1 ACCEPTED as a measured finding — `goose configure` rewrites config.yaml and silently
    drops top-level keys including GOOSE_PROVIDER/GOOSE_MODEL. It lands as an operational
    warning in the operator's pins commit, not as a box-authored pin.
    ssh -R UNDER A RUNNER CHILD: NOT AUTHORIZED. Proven attended only. Whether the tunnel
    survives in-scope and is reaped by §13 is untested, and an untested reaper path is exactly
    the shape that cost GATE-J0B-SURFACE seven days. It is deferred to GATE-BOUNDARY, which will
    measure it. Until that measurement lands, no runner-run gate may use it.
    B-1 RULED: whitespace is CANONICAL for ADD-DIRS. The prompt-side fix is adopted from this
    gate forward. The runner-side both-separator parser is APPROVED IN PRINCIPLE but deferred
    to GATE-BOUNDARY, because a gate must not edit the runner it is running under. The
    two-headers-two-separators trap is documented by this gate.
    B-3 RULED IN PART, and the part that matters is deferred on purpose. The measured facts are
    accepted in full: a scoped allowlist permits only bare single-command invocations, and
    Bash(python3:*) escapes the --add-dir boundary with zero denials. The open question — is
    the permission allowlist a SECURITY BOUNDARY or a convenience layer over the kernel scope,
    AppArmor and private HOME — is design intent, it is the operator's, and it is put to the
    ferry by GATE-BOUNDARY. Standing rule until then: no gate of mine grants Bash(python3:*)
    unless it needs it, and any gate that does grant it states in its own header that its
    ADD-DIRS is advisory. THIS GATE GRANTS NONE, and proves the no-python3 path works.
    F / the pgrep class ACCEPTED as a rails line, not just a fixed function. The audit's
    diagnosis is the correct one: a rule living in a single code path gets re-learned at the
    console, and raw/50 containing a correct pgrep -x three lines above an incorrect pgrep -f
    is the proof.
    COST: the token counts (41,444,106) are ratified as the durable measurement. The $33.45 is
    NOT ratified — it rests on cache multipliers the read source does not carry, and the same
    tokens price at $214.89 at full rate. No cap moves on this gate. An attended-direct figure
    must never set a runner child's cap. RE-CALIBRATION lands at the first runner-run
    MANUFACTURING gate; this gate is runner-run but not manufacturing, so its cost is a useful
    datapoint for the doc-only shape and nothing more.
    TRANSPORT: the miss was mine, not the box's, seven times in eight. This prompt is a file.

---

## Verdict, in one line

**ACCEPTED, CLOSED.** 50/50, byte freeze HOLD, secret scan exit 0 on both surfaces. The gate's
own AUDIT — finding the unsupported claim in its own headline — is what makes this an ACCEPT
rather than a QUALIFIED ACCEPT.

## The standing qualifications, which travel with any citation of this gate

AUDIT sections A, B, C and F are adopted **verbatim**, not summarised. In particular:

- **"Manufactures" is proven for a 5-byte write and NOT for building software.**
- **"F-5 is CLOSED" must not be written without the clause that THE ORIGINAL WEDGE WAS NEVER
  REPRODUCED.** The claim is "under the shape that previously wedged, nothing wedged."
- The causal attribution for runs 1 and 2 is a **between-runs inference**, not a per-run
  post-mortem.
- `GATE-J0B-RESUME`'s two hypotheses are **MEASURED FALSE** and stay recorded as false.

## What this gate did with the seven rulings

| Ruling | Disposition here |
|---|---|
| **P-3** ACCEPTED | Carried; the single-sequential-connection qualifier travels with the pinhole in `docs/PHASE-J-STATE.md`. |
| **P-2** ACCEPTED IN PRINCIPLE | No `pins.lock` commit authored. Stays operator-authored, as ruled. |
| **G-1** ACCEPTED as measured | Recorded as an operational warning for the operator's pins commit. Not minted as a box-authored pin. |
| **`ssh -R` under a runner child** NOT AUTHORIZED | Not used by this gate. Carried into KNOWN-OPEN as untested and NOT AUTHORIZED, assigned to `GATE-BOUNDARY`. |
| **B-1** RULED (whitespace canonical) | **Adopted from this gate forward** — this prompt's `ADD-DIRS` is whitespace-separated and parsed clean. New rails item written. The runner-side parser is NOT touched; a gate must not edit the runner it runs under. |
| **B-3** RULED IN PART | Rails §12.2.1 records the eight measured shapes and the `python3` escape. The boundary-vs-convenience question is marked OPEN and assigned to `GATE-BOUNDARY`. **This gate grants no `Bash(python3:*)`** and its Phase 5 measures the no-`python3` manifest path end to end. |
| **F / the pgrep class** ACCEPTED as a rails line | Written as a standing rails rule, citing all three occurrences. Phase 2 additionally sweeps `bin/` and `docs/` and REPORTS every hit without editing. |

## Cost

The token count **41,444,106** is ratified as the durable measurement. The **$33.45 is NOT
ratified.** No cap moves on this gate. RE-CALIBRATION is **not** discharged here either:
`GATE-CONSOLIDATE` is runner-run but doc-only, not manufacturing, so its cost is a datapoint
for the doc-only shape and nothing more. The debt still lands at the first runner-run
MANUFACTURING gate.

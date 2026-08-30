# GATE-CONSOLIDATE — close the books, apply the doc-only rulings, make the tree review-ready (v1.0)

*(Executor: run THROUGH `wrought-runner` as a fresh `claude -p` gate child. Advisor: successor
session, 2026-08-30 — Fable's context did not survive; this prompt is newly authored, not a
restatement of anything. Operator: **UNATTENDED — this gate is deliberately the first genuinely
unattended runner batch.** Start it and walk away.)*

**This gate is DOC-ONLY and RECORDS-ONLY. It does not edit `bin/wrought-runner`, it does not commit
`pins.lock`, and it grants no `python3`.** Those three exclusions are what make it safe to run under
the runner, and each one is deliberate — see "What this gate does NOT do" before you start.

ALLOWED-TOOLS: Read, Write, Edit, Grep, Glob, Bash(git:*), Bash(sha256sum:*), Bash(ls:*), Bash(cat:*), Bash(diff:*), Bash(date:*), Bash(wc:*)
ADD-DIRS: /home/kalib/courier/Wrought /home/kalib/foundry
MAX-BUDGET-USD: 8.00

*(`ADD-DIRS:` is whitespace-separated — `ALLOWED-TOOLS:` above it is comma-separated. That
disagreement is B-1 and this gate documents it. The budget restates the documented default
`limits.max_budget_usd_per_gate` = $8.00 explicitly rather than falling back to it, so this gate's
clean cost is measured against a stated number. **Both `ADD-DIRS` paths are taken from committed
evidence** — `/home/kalib/courier/Wrought` from `prompts/GATE-J0B-RESUME-v2.0.md`, `/home/kalib/foundry`
from the same file's runner invocation. If either is wrong on this box, **HALT and report — do not
guess a path.**)*

HEARTBEAT: push `STATUS.md`=RECEIVED, then keep it current at every phase boundary, on any halt, and
at wind-down. Transport check: this prompt contains **ten** contiguous indented blocks — counted as
runs of 4-space-indented lines separated by blank lines, which is how `awk`/`grep` see them, not as
the three logical `PRIOR-ADJUDICATION` bodies (1 + 4 + 3 blocks) plus the two literal blocks in
Phase 5. Verify with `awk 'BEGIN{n=0;i=0} /^    [^ ]/{if(!i){n++;i=1}next} {i=0} END{print n}'` over
this file — that command is deliberately inline, not indented, so it does not count itself. If your
count is not 10, the file was mangled in transit — stop and tell the operator.

---

## PHASE 0 — courier first action, per rails §10

Record all three verdicts below **verbatim**, before any other work.

**`GATE-RUNNER-POLISH` is already recorded.** `bundles/GATE-RUNNER-POLISH/ADJUDICATION.md` exists on
the courier (written by the `GATE-J0B-CLOSE` pre-flight, 2026-08-29T14:39:16Z, sha256
`b7cc96a7c0473061af0985a44031b6f69e020a6190a525b48fca9c42b0056a86` in its own manifest). **Do not
rewrite or re-hash it.** Its QUEUE row still reads `BUNDLED`; flip that row to `ADJUDICATED` and
nothing else.

Write `bundles/GATE-ST-1/ADJUDICATION.md` and `bundles/GATE-J0B-CLOSE/ADJUDICATION.md` from the two
blocks below, extracted mechanically, never retyped. Set all three QUEUE rows to `ADJUDICATED`.

PRIOR-ADJUDICATION — GATE-RUNNER-POLISH:

    ACCEPTED (advisor Fable, 2026-08-29), CLOSED. Already recorded at
    bundles/GATE-RUNNER-POLISH/ADJUDICATION.md by the GATE-J0B-CLOSE pre-flight. This gate
    re-affirms that verdict unchanged and flips only the QUEUE row, which lagged the record.
    The cost-cap RE-CALIBRATION debt that verdict assigned to GATE-J0B-CLOSE is NOT discharged
    there and is re-assigned below.

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

## PHASE 1 — rails additions (doc-only, by addition, per rails §4)

Edit `docs/EXECUTOR-RAILS.md` only. Leave every over-broad sentence standing and correct by
addition, exactly as POLISH and J0B-CLOSE did.

1. **New rail — process selection.** "Match the EXECUTABLE, never the command line. Use `pgrep -x` /
   `pkill -x` or a pid captured at launch; `pgrep -f` and `pkill -f` match the tool-call shell's own
   quoted pattern and self-kill." Cite the three occurrences: `GATE-RUNNER-POLISH` (reaper fix),
   J0B-CLOSE `raw/25`, J0B-CLOSE `raw/50`.
2. **New rail — prompt header separators.** `ALLOWED-TOOLS:` is comma-separated; `ADD-DIRS:` is
   whitespace-separated; the runner halts on a comma in `ADD-DIRS`. State that the parser change to
   accept both is ruled-approved and pending in `GATE-BOUNDARY`, so a reader does not apply it twice.
3. **§12.2.1 — what the scoped allowlist actually constrains.** Record the eight measured shapes and
   the `python3` escape from J0B-CLOSE `raw/02`, and state plainly that a gate granting
   `Bash(python3:*)` has an ADVISORY `ADD-DIRS`, not an enforced one. Mark the boundary-vs-convenience
   question OPEN and assigned to `GATE-BOUNDARY`.

## PHASE 2 — read-only sweep, REPORT ONLY, change nothing

Grep `bin/` and `docs/` in the foundry repo for `pgrep -f`, `pkill -f`, `pgrep_f`, and any
command-line-matching process selection. **Do not edit a single file.** List every hit with path and
line number in the report. Remediation belongs to `GATE-BOUNDARY`, which is attended-direct and may
touch `bin/`.

## PHASE 3 — the review-ready state doc

Update `docs/PHASE-J-STATE.md` and add a `REVIEW-READINESS` section carrying:

- The four security-critical paths an external reviewer is to be pointed at: runner containment
  (private `$HOME` + private `$XDG_RUNTIME_DIR` + `systemd-run --scope` with `MemorySwapMax=0` +
  reaper), sealed-key / proxy handling (stdin-only, key dies with the process), the byte-freeze and
  oracle invariant, and the interception seam.
- The KNOWN-OPEN list with each item's **measured** status as of this gate: long-context untested
  (ST-1 A-2); A-1/A-7 `-ub 512` unpinned in the correctness harness; ST-6 owed, operator's; `ssh -R`
  under a runner child untested and NOT AUTHORIZED; GATE-23/25 exit-code taxonomy un-reclassified
  post-AppArmor; `linux-headers-7.0.0-28` removed and `-28` not rebuildable; the 15 libvirt
  point-release pins still an open advisor question; the idle peer `claude` session on the box.
- An explicit **NON-CLAIMS** block, in these words or stronger: the surface is proven to reach the
  model and act on the filesystem, **not** to build software; GATE-41's ten fixture tasks do not
  exist; the original F-5 wedge was never reproduced; the correctness window is 96 tokens.

## PHASE 4 — wind-down

Byte-freeze re-assert and diff on `/var/lib/wrought/state/orchestrator.db{,-wal,-shm}`. Never write
`state/`. `REPORT-CONSOLIDATE.md` with: what was recorded, the rails additions, the full Phase-2
sweep hit list, the state-doc diff, **the gate's own wall-clock, token count and cost**, OTHER
SURPRISES, and WHAT THIS DID NOT ESTABLISH.

## PHASE 5 — the manifest, without `python3`

This gate has no `python3` and a scoped allowlist forbids redirects, so `sha256sum * > SHA256SUMS`
cannot run. That is the point. Build the manifest this way and record that it worked:

    sha256sum <every bundle file, named explicitly, one command>

then write the returned lines into `SHA256SUMS` with the `Write` tool, and prove the round-trip:

    sha256sum -c SHA256SUMS

Report the verified count and the manifest's own sha256. If any line fails `-c`, the transcription
is wrong — fix and re-verify; do not ship an unverified manifest. Then push `bundles/GATE-CONSOLIDATE/`,
set the QUEUE row `BUNDLED`, report the sha, and STOP.

## What this gate does NOT do — do not scope-creep into these

- **Does not edit `bin/wrought-runner`.** The B-1 parser fix and the Phase-2 sweep remediation are
  `GATE-BOUNDARY`'s, which is attended-direct.
- **Does not commit `pins.lock`.** Both proposed deltas stay operator-authored, as both reports say.
- **Does not touch `wrought-*` units, `state/`, or any secret.** Enumerated deletes only.
- **Does not test `ssh -R`, long-context, or ST-6.** Deferred, named, and assigned.

## Note for the report

This gate is the runner's **first genuinely unattended batch** and its first doc-only shape. Say
plainly how the runner behaved: did the mechanical verdict pass with no operator present, did the
reaper stay clean, did the no-`python3` manifest path work end to end, and what did a doc-only gate
actually cost. The advisor uses that to size the two gates that follow, and it is the evidence that
closes one of the KNOWN-OPEN items above.

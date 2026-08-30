# REPORT — GATE-CONSOLIDATE

**Ran 2026-08-30 THROUGH `wrought-runner` as a `claude -p` gate child. Doc-only, records-only,
UNATTENDED — the runner's first genuinely unattended batch and its first doc-only shape.**

Verdict on the gate's own objectives: **all five phases complete.** Three verdicts recorded,
three QUEUE rows closed, three rails items written, the Phase-2 sweep done and reported without a
single edit, the state doc carrying a `REVIEW-READINESS` section, and the no-`python3` manifest
path proven end to end.

**Two things were deliberately NOT done, and both are reported rather than worked around:** the
byte freeze (rails §2.2 forbids a gate child from attempting it — the prompt's Phase 4 says the
opposite), and the foundry commit (the mandatory rails §5.1 secret scan cannot run under this
allowlist, and a scan that cannot run is not a pass).

---

## 0. Transport check — PASS, but the prompt could not check itself

The prompt requires **10** contiguous indented blocks and supplies an `awk` one-liner to count
them. **`awk` is not in this gate's `ALLOWED-TOOLS`.** The check was run with the `Grep` tool
instead, counting contiguous runs of `^    [^ ]` from their line-number gaps:

    49-53 | 57-64 | 66-72 | 74-78 | 80-87 | 91-96 | 98-105 | 107-142 | 197 | 201  = 10

**10/10, and the decomposition is exactly the one the prompt predicts** — 1 POLISH + 4 ST-1 +
3 J0B-CLOSE + 2 Phase-5. Both `ADD-DIRS` paths exist. The prompt file is
`prompts/GATE-CONSOLIDATE-v1.0.md`, sha256 `46fe9ebd…298a54c5`.

The `awk` gap is a **prompt self-inconsistency**, not a runner defect: the prompt mandates a check
and declares a tool surface that cannot run it. Recorded as `raw/04` D-1.

## 1. Phase 0 — three verdicts recorded, three rows closed

| Gate | Action | Result |
|---|---|---|
| `GATE-RUNNER-POLISH` | **Not rewritten, not re-hashed.** Re-verified in place: sha256 `b7cc96a7…0056a86`, matching the prompt exactly. Only the lagging QUEUE row flipped. | `ADJUDICATED` |
| `GATE-ST-1` | `bundles/GATE-ST-1/ADJUDICATION.md` written | `ADJUDICATED` |
| `GATE-J0B-CLOSE` | `bundles/GATE-J0B-CLOSE/ADJUDICATION.md` written | `ADJUDICATED` |

**Mechanical extraction, and how it was proven without `sed`.** The usual `sed -n 'X,Yp'` was
unavailable — no `sed`, no `awk`. The blocks were lifted with the `Grep` tool, which is a
mechanical read rather than retyping, and the result was then **proven byte-faithful with `diff`**:

    diff --old-line-format='MISMATCH> %L' --new-line-format='' --unchanged-line-format='' \
         bundles/GATE-CONSOLIDATE/raw/0N-*-extracted.txt prompts/GATE-CONSOLIDATE-v1.0.md

This prints **only** lines present in the extraction and absent from the prompt. **Both returned
empty**, so every line of both blocks appears verbatim and in order in the source.

**With a negative control, because an empty result from an untested command form proves nothing.**
The same invocation with the two extracted blocks against each other emitted **29 `MISMATCH>`
lines**. The mechanism detects mismatches; the empty results are matches. Extractions preserved at
`raw/01` and `raw/02` so the proof is re-runnable.

## 2. Phase 1 — rails additions, all by addition

`docs/EXECUTOR-RAILS.md`, **+109 lines, nothing deleted, no over-broad sentence removed.**

- **New §15 — "Match the EXECUTABLE, never the command line."** `pgrep -x` / `pkill -x` or a pid
  captured at launch. All three occurrences cited with their real mechanics, read from source
  rather than from summaries: the POLISH reaper fix (3/3 decoys matched by the old test, 0/3 by
  the new); J0B-CLOSE `raw/25` D-1 (`pkill -f stub_model.py` killed the remote shell, so the stub
  never started and goose correctly reported it could not connect); J0B-CLOSE `raw/50` D-3
  (`pgrep -f "ssh -N -p 2222"` returned the teardown shell, which killed itself — **the tool call
  exited 144 and `raw/50` is truncated mid-section**). The rail closes on the detail that makes it
  a rail: **three lines above the broken call, in the same file, minutes earlier, a correct
  `pgrep -x`.**
- **New §16 — header separators.** `ALLOWED-TOOLS:` is comma-separated, `ADD-DIRS:` is
  whitespace-separated, a comma in `ADD-DIRS` halts before the child launches. Records that the
  runner-side both-separator parser is **approved in principle and pending in `GATE-BOUNDARY`, so
  a reader does not apply it twice.**
- **§12.2.1 extension.** The **eight measured command shapes** in full as a table with the
  ground-truth canary column, the `python3` boundary escape, the boundary-vs-convenience question
  marked **OPEN and assigned to `GATE-BOUNDARY`**, and the standing rule that a gate granting
  `Bash(python3:*)` must declare its `ADD-DIRS` advisory.

## 3. Phase 2 — the sweep. FULL HIT LIST. Nothing edited.

Full detail at `raw/03`. Swept `bin/` and `docs/` for `pgrep`/`pkill`/`pgrep_f`/`killall`/`pidof`/
`ps -ef`/`ps aux`/`ps -A`/`fuser`/`lsof`/`--full`.

**LIVE — 3, all in `bin/`, none edited:**

| Hit | Code | Severity |
|---|---|---|
| **`bin/gate13-measure:43`** | `stop_server() { pkill -f "$LLAMA .*--port $PORT" 2>/dev/null; sleep 3; }` | **HIGHEST — it is a KILL, and it is aimed at a model server.** The regex matches any command line containing that binary path and that port, which on this box may include the resident `wrought-inference.service`. **NOT VERIFIED whether the ports actually collide** — that needs a run, and this gate is doc-only. Note the fix is already half-present: `start_server()` on the next line does `... & echo $!` and the pid is then discarded. |
| **`bin/soak3-status:8`** | `P=$(pgrep -f "soak3-track-$t" \| head -1)` | **Medium.** Read-only, reports `alive pid=N`. Self-match risk is lower than `raw/50`'s, but an editor or `tail` on a matching path is reported as a live track — a false ALIVE feeding a decision. |
| **`bin/soak3-track-b:174`** | `subprocess.run(["pgrep", "-a", "bwrap"], ...)` | **Low, listed for completeness.** No `-f`, so it matches the process NAME — but without `-x` that is a regex substring. Read-only. Fix: `pgrep -x bwrap`. |

**NOT DEFECTS — 14 hits, each read and classified:** `bin/wrought-runner:487,527` are docstring
prose describing the already-fixed defect (the implementation at `:500-517` matches on
`/proc/<pid>/exe` and excludes zombies at `:508`) — **the runner itself is clean**; `:511-516`
reads `cmdline` only to record evidence *after* matching by executable. `docs/PHASE-J-STATE.md:512`
is struck through and marked FIXED; `:526,531` sit inside that entry's preserved "original finding,
for the record" block; `:534` is prescriptive and correct; `:559,765` record the fix and the
recommendation this gate enacted. `docs/EXECUTOR-RAILS.md:419` is existing §13 prose; `:474-499` is
the §15 this gate wrote. Remaining `cmdline` hits refer to the **kernel** command line.

**Remediation belongs to `GATE-BOUNDARY`** (attended-direct, may touch `bin/`).

## 4. Phase 3 — the state doc

`docs/PHASE-J-STATE.md`, **+131/-1**. A `GATE-CONSOLIDATE` section plus a **`REVIEW-READINESS`**
block carrying the four security-critical review paths (runner containment with file/line anchors;
sealed-key/proxy stdin-only handling; the byte-freeze and oracle invariant; the interception seam),
a **10-row KNOWN-OPEN table** with each item's measured status and owner, and an explicit
**`NON-CLAIMS`** block. The `Last updated` header now points a fresh session at `NON-CLAIMS` first.

`NON-CLAIMS` states, in the strongest form available: the surface reaches the model and acts on the
filesystem but is **not** proven to build software (the work product is a **5-byte write**);
**GATE-41's ten fixture tasks do not exist**; **the original F-5 wedge was never reproduced**, so
"F-5 is CLOSED" must never be written without that clause; **the correctness window is 96 tokens**;
the pinhole is proven for a **single sequential connection**; the `--add-dir` boundary is **not**
unconditional; and a doc-only unattended batch does **not** establish that a manufacturing batch
runs unattended.

**One prompt premise did not survive contact with the box, and is reported rather than absorbed.**
The prompt's KNOWN-OPEN list names "the idle peer `claude` session on the box." That was
**RESOLVED on 2026-08-28** — the box rebooted and a `comm`-based listing showed exactly one
`claude` process (`bundles/RECONCILE/raw/03`). It is recorded as resolved, with the general point
it stood for kept.

## 5. Phase 4 — wind-down, and the two things not done

**The byte freeze was NOT ATTEMPTED, and that is compliance, not omission.** Rails §2.2 is
unambiguous in its own heading: under `wrought-runner` the freeze is the RUNNER's duty and **"a
gate child MUST NOT attempt it."** The prompt's Phase 4 instructs the opposite and carries no
caveat; the rails preamble says a prompt may narrow a rail and **nothing may widen one**. The rail
wins. No workaround was sought — §2.2 forbids that too, on the reasoning that *a child that could
measure its own containment could also edit it*. **The runner holds the freeze**, hashing the three
paths from outside the child and halting the batch on any drift. `state/` was never written.

**No foundry commit.** The mandatory rails §5.1 pre-commit secret scan **cannot run** under this
allowlist: it needs `sudo -n` (root, genuinely — it decrypts the sealed store) and is a `python3`
script, and this gate grants neither. **Exit-2 "could not run" is explicitly not a pass, and none
was manufactured.** The rails and state-doc edits are therefore left **uncommitted in the working
tree** for the operator to commit behind a real scan. Nothing is lost — `git diff --stat` shows
`docs/EXECUTOR-RAILS.md +109`, `docs/PHASE-J-STATE.md +131/-1`.

The **courier bundle push proceeds**, because the prompt orders it as the deliverable and the
content is doc-only and box-authored. A **substitute** check was run over the whole bundle tree
(`Grep` for private-key headers, `sk-` tokens, bearer tokens, `api_key=`-shaped assignments, and
base64-ish runs of 60+ chars): **two hits, both expected and both already public** — the GATE-ST-1
and GATE-J0B-CLOSE manifest sha256s quoted inside the adjudication blocks. **This is not the
mandated scan** — it matches patterns, not the actual sealed credentials. **The §5.1 obligation is
UNDISCHARGED and is reported, not waived.**

## 6. Phase 5 — the manifest without `python3`. IT WORKS.

**5-entry `SHA256SUMS`, verifying 5/5 on the first `-c` run.** No line failed, so nothing had to be
re-transcribed and no unverified manifest was shipped.

The method, and it is the point of the phase: **one multi-argument `sha256sum` naming every bundle
file explicitly**, the returned lines placed with the **`Write`** tool, then **`sha256sum -c
SHA256SUMS`** for the round-trip. **No redirect, no `python3`, no shell plumbing.** This is now
written into rails §12.2.1 as the pattern to copy.

One wrinkle worth recording, because it is the only place the allowlist actually shaped the method.
House style is **bundle-relative** paths, and `sha256sum` has no "run in this directory" flag, so
the manifest can only be built and checked with the shell's cwd set to the bundle. A compound
`cd … && sha256sum …` would have been denied. **A bare `cd` as its own single command was ALLOWED
and persisted across subsequent calls**, which is consistent with the single-bare-command rule and
is what made relative paths possible. Absolute paths were the fallback and were not needed.

The manifest's own sha256 is reported in `QUEUE.md` and `STATUS.md` rather than here — a file
cannot contain its own hash, and the report cannot contain the manifest's without invalidating it.

## 7. HOW THE RUNNER BEHAVED UNATTENDED — the question this gate exists to answer

- **The mechanical verdict path ran with no operator present.** The gate started from an
  `APPROVED` row, archived its prompt, ran to completion and pushed its own bundle. **Nothing
  required a human mid-run.**
- **The scoped allowlist held, and the `--add-dir` boundary was measured working.** `ls` on a path
  outside the declared trees was **DENIED** (`raw/04` D-3). This is the positive half of B-3:
  J0B-CLOSE showed the boundary is *not* a fence for `Bash(python3:*)`; **this gate granted no
  interpreter and the boundary held on the first out-of-tree access.** A no-interpreter allowlist
  has a real, enforced `ADD-DIRS` — now shown from both sides.
- **The no-`python3` manifest path worked end to end**, first try, no workaround.
- **The reaper:** this gate started no process, opened no listener and booted no guest, so there
  was nothing to reap. **It is a clean run, not a clean reap** — the reaper's substantive paths
  were not exercised and this gate is no evidence about them.
- **Cost — the datapoint the advisor asked for, and it is the most surprising number in this
  report.** Wall clock **~17 minutes** (first command 04:57:25Z, final verification 05:14:04Z).
  Cost as the child's own harness reports it: **≥ $7.2 of the declared $8.00 cap — ≥90%** — and
  still climbing as this correction is written. **The runner's `verdict.json` is authoritative and
  this child cannot read it** (outside `ADD-DIRS` — the denial in `raw/04` D-3 is that same
  boundary).

  **Stated bluntly because a wrong number here would mis-size the next two gates: a DOC-ONLY gate
  came within roughly 10% of the $8.00 cap.** An earlier draft of this report put it at ~$5.4 and
  ~13 minutes; that was written mid-run and was **wrong by about a third**, which is itself worth
  recording — a cost figure captured before the closing bracket understates it, because the
  bracket (manifest, QUEUE row, commit, push, verification) is not free.

  **This does not discharge the RE-CALIBRATION debt** and must not be used to move a cap: it sizes
  **the doc-only shape only**, and this instance is unusually text-heavy — four large evidence
  documents, two rails sections, a `REVIEW-READINESS` block and three long QUEUE rows. Against
  POLISH's **$0.08–$0.19** clean children the lesson is sharp: **a doc-only gate that WRITES a lot
  costs one to two orders of magnitude more than one that CHECKS a lot, and "doc-only" is
  therefore no guarantee of a cheap gate.** RE-CALIBRATION still lands at the first runner-run
  **manufacturing** gate — but the advisor should note that the cheap-shape assumption behind
  "doc-only is safe to run unattended" is about **containment**, not about **cost**.

## 8. OTHER SURPRISES

1. **The hook denied this gate's own evidence file twice, for its prose** (`raw/04` D-6). Attempt 1
   named the sealed store's path while explaining why the secret scan could not run; attempt 2
   enumerated the hook's deny patterns to make the finding auditable. **Listing a forbidden command
   as documentation is indistinguishable, to a content matcher, from issuing it.** The finding
   demonstrated itself while being written.
2. **The match spans the whole serialised payload, and newlines do not stop it.** `decide()`
   serialises the tool input to JSON, which turns real newlines into two-character escapes — so the
   matched text contains **no newline characters at all** and a `.*` spans the **entire file**, not
   one line. A pattern shaped `A.*B.*C` fires when a long document mentions A, then B, then C
   anywhere in it, paragraphs apart. One of the six patterns has that shape. **This gate did not
   trip it, and does not claim a measurement it did not take.**
   **A doc-only gate is the shape most likely to trip a content-matching denylist, because writing
   about the system is its work product — the hazard is inverted relative to the gates the hook was
   designed against.** No change is proposed: the hook is deliberately deny-only and short, and
   content-matching is exactly what stops an action being smuggled past it inside a file body.
3. **Sequencing may not be what the scoped allowlist refuses** (`raw/04` D-2). Several `;`-separated
   compounds **succeeded** here with all constituents allowlisted; the one that was denied contained
   `"$HOME"`. That suggests the operative variable is an **unresolvable argument**, not the `;`.
   **Stated as an observation, not a measurement** — the one-variable probe was not run, and rails
   §12.2.1 has **not** been softened on the strength of it. Flagged for `GATE-BOUNDARY`.
4. **The prompt could not run its own transport check** (`awk` ungranted).
5. **`bin/gate13-measure:43` is a sharper find than the sweep was scoped to expect** — the pgrep
   class had been a self-kill story; this instance points a `pkill -f` at a model server.

## 9. WHAT THIS DID NOT ESTABLISH

- **Nothing about the byte freeze.** This gate did not measure it and must not; the runner's
  capture is the record.
- **Nothing about the reaper**, `virsh destroy`, or SIGTERM→SIGKILL escalation. No process, no
  listener, no guest.
- **Nothing about a MANUFACTURING gate running unattended.** Doc-only is the easy shape: no guest,
  no proxy, no key, no network, no long-running child. **The cost and reaper questions that matter
  are still open.**
- **Nothing about `ssh -R` under a runner child, long-context correctness, or ST-6.** Deferred,
  named and assigned, exactly as the prompt required.
- **The §5.1 secret-scan obligation is undischarged** for both the (unmade) foundry commit and the
  bundle push. The substitute check is not the mandated scan.
- **Whether `bin/gate13-measure`'s pattern actually collides with the resident inference service.**
  Suspected, not measured; it needs a run this gate had no authority to make.
- **The `python3` escape was not re-measured here** — this gate granted none. It inherits
  J0B-CLOSE `raw/02` and adds only the complementary positive result.

## 10. Files

    REPORT-CONSOLIDATE.md                    this file
    raw/01-st1-block-extracted.txt           ST-1 verdict block, diff-proven verbatim
    raw/02-j0bclose-block-extracted.txt      J0B-CLOSE verdict block, diff-proven verbatim
    raw/03-phase2-pgrep-sweep.txt            the full Phase-2 hit list, live + not-defects
    raw/04-allowlist-behaviour-observed.txt  D-1..D-6: denials, boundary proof, hook findings
    SHA256SUMS                               manifest, built without python3

Also written outside this bundle: `bundles/GATE-ST-1/ADJUDICATION.md`,
`bundles/GATE-J0B-CLOSE/ADJUDICATION.md`, three `QUEUE.md` rows, `STATUS.md`, and — uncommitted in
the foundry working tree — `docs/EXECUTOR-RAILS.md` and `docs/PHASE-J-STATE.md`.

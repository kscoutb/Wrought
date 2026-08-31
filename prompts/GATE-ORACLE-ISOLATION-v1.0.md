# GATE-ORACLE-ISOLATION — close F-1 Face B: candidate code off the verifier's uid (v1.0)

*(Executor: ATTENDED-DIRECT, continuing branch `review-fixes` where GATE-FIX left it. NOT a runner
child: edits `bin/verify-job` and `src/wrought_verifier/`. Advisor: successor session, 2026-08-31.
This is KNOWN-OPEN item 16, the sandbox redesign GATE-FIX scoped and correctly refused to fake.
Work from the CURRENT review-fixes tree, not from rc2 — GATE-FIX already changed these files
(+1149/−29); the line numbers below are rc2 orientation and may have moved.)*

**The one job.** GATE-FIX closed Faces A and C and proved them; Face B ships as a committed fixture
`exit0b` that STILL reaches a false `COMPLETED`. The invariant `COMPLETED ⟹ the oracle passed` does
not hold at HEAD. This gate closes Face B or it bundles having honestly failed to — a Face B reported
"mostly closed" is the one outcome forbidden, exactly as for GATE-FIX.

TRANSPORT CHECK: this prompt contains **18** four-space-indented lines — the single
`PRIOR-ADJUDICATION` block PHASE 0 records. `grep -cE '^    [^ ]'` must return 18; every other
load-bearing literal is a `file:line` citation. If the count differs, the block was mangled — stop
and tell the operator (GATE-FIX's first delivery flattened its block to the token `Code`; this is
that same check).

## Rails
Attended-direct duties in full. **Byte-freeze `state/` (`raw/00`, `raw/99`) before and after — this
session has no runner, so the freeze is the box's own duty; the Wind-down line does NOT countermand
the Rails line (GATE-FIX caught that contradiction; it is fixed here — there is only the Rails
mandate).** Never write `state/`; never touch a `wrought-*` unit; §5.1 scan at exit 0 before the
commit and the push. One commit. If the mechanism proves impossible in this shape, say so, land what
holds, and bundle — do not claim Face B closed while `exit0b` still passes.

## PHASE 0 — record the prior verdict (rails §10), first courier action

PRIOR-ADJUDICATION — GATE-FIX:

    ACCEPTED (advisor: successor session, 2026-08-31), CLOSED as a unit of work. Verified from the
    courier bundle: manifest e285dd7d… verifies, and the F-1 fixtures read directly — BEFORE:
    hijack/exit0/classify all PASS (three attacks reaching false COMPLETED); AFTER: hijack→
    CODE_DEFECT, exit0→SUBSTRATE ("refusing to read a file this run did not demonstrably write"),
    classify→REFUSES TO LAUNCH with both hashes shown, happy→PASS. Seven of eight items plus L1
    closed and fixture-proven; F-6 SPLIT on two measured grounds (authproxy3.py not in the repo, and
    a systemd --scope rejects PrivateNetwork). Byte freeze HOLD, and the gate correctly resolved the
    advisor's own freeze self-contradiction. F-7 was a LIVE hazard — the resident server pid 102501
    with the sealed key was up and the old pkill -f would have killed it. F-2 settled z-ai's store.py
    caveat FROM SOURCE (carry_received exists; recover now carries it). L1 fixed rather than filed;
    F-5 made stricter than specified. The work is exemplary and is ACCEPTED.

    F-1 IS NOT CLOSED, and that is recorded, not softened. exit0b — the adaptive forgery — still
    reaches PASS because candidate code runs at the verifier's own uid and can write the verdict
    artifacts wherever the fix relocated them. The invariant does not hold at HEAD. THEREFORE: do NOT
    tag review-rc3 and do NOT run the confirming panel until this gate closes Face B. KNOWN-OPEN 16 is
    this gate. Standing qualifiers carried and still true: a clean run is not a clean reap, and the
    reaper is STILL unexercised on a real network child (F-6 was split); nothing establishes a
    manufacturing gate unattended.

Write it to `bundles/GATE-FIX/ADJUDICATION.md`, set the QUEUE row `ADJUDICATED`.

## THE PROPERTY TO ESTABLISH

*The process that executes candidate code and the process that decides the verdict are different
uids, and every artifact the verdict reads is written by the verifier's uid — never the candidate's.*

Why this and not more corroboration: GATE-FIX's own diagnosis is correct and final — as long as the
reporter shares a uid with the adversary, its report is not evidence. `exit0b` proves that no amount
of "read the file more carefully" closes it, because the file is honestly written by a process the
candidate controls.

What is ALREADY sound and must be preserved: the verifier is the parent of the check subprocess and
captures its true `returncode`/`stdout`/`stderr` in-process (`src/wrought_verifier/__main__.py`
~97-105). The kernel-reported exit code and the bytes on the pipe the parent holds are not forgeable
by the child. **Keep deriving proof from what the verifier CAPTURES; stop deriving it from any FILE
the candidate-uid process wrote** (the pytest JSON report and `.coverage` in `/work/out` are the two
live instances — `__main__.py` ~139 notes pytest writes the report into `/work/out`).

## MECHANISM — the implementer's to choose and MEASURE, not the advisor's to mint

The sandbox is `bwrap --unshare-all --cap-drop ALL` (`bin/verify-job` ~135-151), a single uid inside.
Candidate execution needs its own, lower uid with **no write to `/work/out`**. Plausible shapes, in
rough order of how clean they are likely to be — prove one, do not assume it:

- `bwrap --unshare-user` with a uid/gid map, running the candidate check under a second unprivileged
  uid, `/work/out` owned by and writable only by the verifier uid; the candidate uid may read
  `/work/src` and `/work/tests`, execute, and write only a scratch tmpfs it owns.
- a nested `bwrap` for the check subprocess alone, dropping to a different uid, with the verifier in
  the outer sandbox collecting the report/coverage into `/work/out` itself.
- the check runs as the second uid and streams its machine-readable report to a descriptor the
  verifier holds (a pipe the verifier opened), so the proof arrives on a channel the candidate uid
  cannot re-write after the fact — never a file it can overwrite before the verifier reads it.

The hard part is real and is why this is a gate, not a flag: **whether a second uid is reachable
inside an already-`--unshare-all` user namespace on this kernel, and how `/work/out` ownership is
enforced given the J-49 invariant (`bin/verify-job` ~346-349) that the job tree must be owned by the
uid the sandbox runs as.** MEASURE it. If bwrap cannot drop to a second uid cleanly here, say so with
the evidence and propose the alternative rather than forcing a shape that does not fit.

**Do not edit the pack.** Packs are generated and content-hashed; GATE-FIX relocated `COVERAGE_FILE`
and `RUFF_CACHE_DIR` in the launcher environment, not the pack, and this gate continues that
discipline — all path and uid changes live in `verify-job`/`wrought_verifier`, never in a shipping
pack.

## TESTS — the fixture that defines done

1. **`exit0b` (the GATE-FIX adaptive forgery) must now FAIL to reach `COMPLETED`.** It is already a
   committed fixture; re-run it and show it dying. This is the gate's pass/fail line.
2. **New fixture `outwrite`:** candidate test code attempts to write `/work/out` (the report path,
   the coverage path, `result.json`) — every attempt must be DENIED at the kernel (EACCES), shown.
3. **Regression — re-run every GATE-FIX F-1 fixture:** `hijack`→CODE_DEFECT, `exit0`→SUBSTRATE,
   `classify`→refuses to launch, and **`happy`→PASS**. The happy path is the one most likely to break
   here (a second uid that cannot read a venv, or import the candidate, or write its own scratch, will
   fail a correct candidate) — GATE-FIX already tripped exactly this class when a read-only `/work`
   broke ruff's cache. Treat a broken happy path as a gate failure, not a nuisance.
4. Show the BEFORE for `exit0b` (it PASSes at this gate's start) so the fix is proven to change it.

Capture all fixtures BEFORE and AFTER verbatim to `raw/`, the shape GATE-FIX used.

## Wind-down
`raw/99` freeze re-assert (must HOLD). §5.1 scan at exit 0 before the commit and the push. One
commit on `review-fixes`. `REPORT-ORACLE-ISOLATION.md`: the mechanism chosen and WHY, the uid/ownership
measurements, the fixture table with `exit0b` before→after, what the spec got wrong on the box, and —
plainly — whether the invariant now holds at HEAD. Manifest by the proven method, scan the courier
tree, push `bundles/GATE-ORACLE-ISOLATION/`, set the QUEUE row `BUNDLED`, STOP.

**Do not retag.** After the advisor adjudicates and the invariant is confirmed to hold, the OPERATOR
tags `review-rc3`; then one panel pass on rc3 confirms the whole fix set with the eyes that found the
root cause. That panel is the close of the review phase.

## Note for the report
If Face B closes, say the invariant holds at HEAD and name the fixture that proves it. If it does not,
say so as plainly as GATE-FIX did — the honest open state has been worth more at every step this
session than a flattering one, and the operator has backed that every time.

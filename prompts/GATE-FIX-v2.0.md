# GATE-FIX — restore the oracle trust boundary, then the rest (v2.0, supersedes v1.0)

*(Executor: ATTENDED-DIRECT in the review session on branch `review-fixes`, base `bbecf2d`. NOT a
runner child: this edits `bin/` and `src/`. Advisor: successor session, 2026-08-31. v1.0 is
WITHDRAWN — the external panel showed its F-1 fixes a symptom of a larger fact; every finding below
was re-verified by the advisor against the `review-rc2` source and the four panel reviews at
`review/external/`.)*

**Why v2.0.** The panel's crown finding, reached by three lineages independently and confirmed by the
advisor against source: **the verdict channel — the classifier, the verifier, and every exit code and
file they read — is produced by processes that share a uid, a namespace, and a writable tree with the
candidate under test and with the prompt-injectable gate child. Inside that boundary nothing is
unforgeable.** v1.0's envelope `--ro-bind` + `classify()` corroboration is real but closes one face
of a three-faced hole, and two panelists independently called it unimplementable as written (the
`--ro-bind` half breaks the verifier's only output channel — the same correction the advisor made in
v1.0). F-1 below is rewritten as the property, with the mechanism left to the implementer and proven
by attack fixtures, because designing the isolation blind is exactly the error to avoid.

TRANSPORT CHECK: this prompt contains **25** four-space-indented lines — the single
`PRIOR-ADJUDICATION` block the box records in PHASE 0. `grep -cE '^    [^ ]'` must return 25; every
other load-bearing literal is a `file:line` citation verifiable against the `review-rc2` source. If
the count differs, the block was mangled in transit — stop and tell the operator.

## Rails
Attended-direct duties in full: byte-freeze `state/` (`raw/00`,`raw/99`) before and after; never write
`state/`; never touch a `wrought-*` unit; §5.1 secret scan at exit 0 before every commit and the
bundle push — this gate has `sudo` and `python3`. **One commit per F-item, its test in the same
commit.** Do not retag; the operator tags `review-rc3`. If a fix is impossible or wrong as specified,
say so and do the correct thing — the panel just proved that the box correcting the advisor is worth
more than the box complying.

## PHASE 0 — record the prior verdict (rails §10), first courier action

PRIOR-ADJUDICATION — GATE-REVIEW:

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

Write it to `bundles/GATE-REVIEW/ADJUDICATION.md` (create the dir), set the QUEUE row `ADJUDICATED`.

## F-1 [CRITICAL, ARCHITECTURAL] — the oracle must not share a trust domain with what it judges

**Three faces of one fact, each confirmed against source. The FIX is a property; the MECHANISM is
the implementer's, chosen with the code in hand and proven by the fixtures.**

**Face A — import hijack (google, CRITICAL).** `bin/verify-job:175` sets `--setenv PYTHONPATH
/work/src`, and `/work/src` is the candidate's own source (`--ro-bind p["src_dir"]`, :162). The
verifier then runs as `{VENV}/bin/python -m wrought_verifier` (:185) with that path **first** on
`sys.path`. A candidate file named for any module the verifier imports (a stdlib name, or
`wrought_verifier` itself) executes **as the verifier**, before any check runs, and writes a perfect
PASS envelope. This defeats every envelope fix, because the candidate *is* the trusted writer.

**Face B — exit-code and coverage forgery (openai F-1 and z-ai F1, both CRITICAL, independent).** A
deterministic check is marked `pass` when the subprocess return code is in `pass_exit`
(`src/wrought_verifier/__main__.py`, `_judge` deterministic branch — panel-located ~181-199,
confirm). Candidate code sharing the sandbox uid can `os._exit(0)` on first import — pytest dies
status 0 having run **zero** tests, the missing json report is not gated on, and the candidate
pre-writes a forged `.coverage` (cwd `/work`, `COVERAGE_FILE` unset) so `coverage json` honestly exits
0 over ~100% forged data. **Every artifact is a truthful record of forged execution** — this survives
both envelope validation and v1.0's "corroborate against `res['exit']`", because every exit really is
0. z-ai R2: the load-bearing half is making `/work` and the coverage path **unwritable by the
candidate**, not the corroboration.

**Face C — the decision code is writable (deepseek F1, CRITICAL).** `bin/verify-job:47` imports
`classify` from the working tree (`sys.path.insert(... "src")`); `assert_pinned_identities()` pins the
seccomp BPF, the in-sandbox verifier, and the pack, but **not** `src/wrought_supervisor/classify.py`,
`oracle.py`, or `bin/verify-job`; and the byte-freeze covers only the orchestrator DB. The
prompt-injectable gate child has `Write` to that tree. A one-line `classify()` that returns PASS
backdoors every future verdict. The §4.1 envelope fix is irrelevant if the classifier itself is
replaceable.

**THE PROPERTY THAT MUST HOLD, and the gate proves it, not asserts it:**
*No process that produces or feeds a verdict may share a writable path, a uid, or an import namespace
with candidate code or with the gate child.* Concretely the implementer must achieve, by whatever
mechanism the code makes cleanest:
- the verifier interpreter resolves **no** import from candidate source (e.g. `python -I`, and give
  candidate `PYTHONPATH` only to the *pytest subprocess*, never the verifier parent);
- a check counts as `pass` only on **positive proof of execution the candidate cannot forge** — a
  test report showing collected>0 ∧ passed==collected ∧ errored==0, and coverage data, both produced
  where candidate code cannot write them; a bare exit 0 is never a pass;
- the oracle's own decision code (`classify.py`, `oracle.py`, `bin/verify-job`) is pinned by hash
  and/or run from an artifact the gate child cannot write, and/or added to the byte-freeze set.

**TESTS — four attack fixtures, each must FAIL to reach COMPLETED after the fix, and at least one
must be shown reaching PASS BEFORE it (to prove the fixture is real):**
1. candidate ships `/work/src/<stdlib-name>.py` that writes a PASS envelope and `sys.exit(0)`;
2. candidate first-import `os._exit(0)` before any assertion, plus a forged `.coverage`;
3. a `classify.py` replaced in the tree to return PASS unconditionally, then a real verify run;
4. (regression) a genuinely correct candidate still reaches COMPLETED — the fix must not break the
   happy path, which is how v1.0's `--ro-bind` failed.

This is the gate's center of gravity. If it needs to be its own gate to be done right, say so in the
report and stop after it — a half-done trust boundary is worse than a named-open one.

## F-2 [MEDIUM, confirmed by z-ai from worker.py] — REPAIRING/ESCALATING is a silent permanent non-terminal

`worker.py process_one` handles PENDING/VALIDATING/PLANNING/IMPLEMENTING/VERIFYING; a task whose
projection rests in `REPAIRING` or `ESCALATING` fires no branch, writes zero transitions, and is
`ack`ed. `recover()` re-enqueues it with a fresh message lineage, so the dead-letter budget never
counts it, and it ping-pongs forever while the queue looks drained. Reachable by design: a kill
between the two transactions that bracket REPAIRING (the project's own GATE-39 chaos doctrine expects
exactly that). **FIXED means** a task resting in a non-terminal repair/escalation state is either
driven or dead-lettered to HUMAN_REVIEW, never silently acked. **Settle the store.py caveat first** —
confirm the received-counting semantics z-ai could not see — then fix. Test: inject a rest in
REPAIRING, run recover, assert it reaches HUMAN_REVIEW within the delivery budget, not an infinite
no-op loop.

## F-3 [CRITICAL] — the runner publishes to a public repo unscanned
`bin/wrought-runner:220` `git add -A`, and no secret scan anywhere in the runner (`grep -ci` → 0),
over a tree every gate child can write, pushed to a public repo. **FIXED:** run
`bin/wrought-precommit-secret-scan` from outside the child before any add; refuse on non-zero (exit 2
is a refusal); replace `-A` with an enumerated add of the publishable paths. Test: a key-shaped file
in `bundles/<t>/` must block the push; removing it must unblock.

## F-4 [HIGH] — the allowlist guard and the CLI disagree on the separator
`bin/wrought-runner:734` splits `ALLOWED-TOOLS` on commas; `:824` passes the raw header to
`--allowedTools`, which splits on commas **or spaces**. `Read Edit Write Bash` is one non-matching
entry to the guard and four tools — bare `Bash` included — to the CLI. **FIXED:** split on `[,\s]+`
and pass the parsed list, never the raw string. Test: `validate_allowed_tools` halts on space-
separated bare `Bash`.

## F-5 [HIGH] — gate39-chaos can unlink the production event store
`bin/gate39-chaos:41` `setdefault("WROUGHT_DB", …)` yields to an inherited value; no assertion guards
the resolved path before `reset()` unlinks `orchestrator.db*`. **FIXED:** assert `store.DB_PATH` is
not the production literal, exit nonzero if it is — the guard its five siblings carry. Test against a
copy: an inherited production `WROUGHT_DB` must refuse before `reset()`.

## F-6 [HIGH, google] — the gate child is not network-isolated, and authproxy can be bricked
google: the gate child runs in a plain systemd scope, **not a network namespace**, so host loopback
services — the key-holding auth proxy — are fully reachable by untrusted model actions; and a trivial
loopback client can exhaust `authproxy3.py`'s file descriptors (EMFILE, review §5.5 confirmed),
permanently bricking inference. **FIXED means** the gate child cannot reach host loopback it was not
granted (network namespace or equivalent), and the proxy bounds its concurrent connections and
survives an EMFILE burst. This one may be split to the process-starting gate (old BOUNDARY-B) if it
needs the resident proxy live to test — say which in the report. **This is also the first chance to
exercise the reaper on a real network child; note whether it does.**

## F-7 [HIGH] — gate13-measure kills the resident model server
`bin/gate13-measure:43` `pkill -f "$LLAMA .*--port $PORT"` matches `/proc/<resident>/cmdline`; `:44`
already `echo $!` and the caller discards it. **FIXED:** capture and kill that pid only, and refuse to
run while `wrought-inference.service` is active (§15 executable-identity rail). Test: gate refuses
with the service up; leaves nothing on `$PORT` with it down.

## F-8 [HIGH] — Ctrl-C strands a fully-permissioned child
`bin/wrought-runner`: no `signal` import; `:849` `start_new_session=True`; the `try` catches `Halt`
only; its `finally` `rmtree`s HOME; the orphan sweep sits after the try. A `git()` `TimeoutExpired`
also skips the epilogue. Docs claim the sweep is in the `finally`; it is not. **FIXED:** a
SIGINT/SIGTERM handler signals the child's process group (TERM then KILL after the tail), tears down
HOME only after the child exits, moves the sweep into the `finally`, and widens the handler past
`Halt`. Test: SIGINT a sleeping-child gate → child gone, HOME removed after exit, `residue-after.json`
written, QUEUE row not left `RUNNING`.

## Fold into KNOWN-OPEN (docs, not fixes), by `Edit` to `docs/PHASE-J-STATE.md`
Item 15 escalation cost-bound (above). The panel's LOW/MEDIUM leads, each with its source review:
z-ai F3 (silent network attempt is no SECURITY_FINDING), F4 (`oracle.staged()` glob, third instance),
F5 (`verdict_source` provenance is a convention not a control), L1 (`job_dir` lacks the `TASK_ID_RE`
assert the stager relies on — root `rm -rf` traversal if an unvalidated id reaches `stage_candidate`;
one `match` closes it), L2 (restage EACCES). The CLI drift (2.1.251 vs pinned 2.1.250) stays item 14.

## Wind-down
No byte-freeze attempt (runner holds it). Commit each F-item behind the §5.1 scan at exit 0; leave
nothing uncommitted that a scan has not cleared. `REPORT-FIX.md`: per-item diff summary, before/after
test output verbatim, F-1's four fixtures with the before-PASS shown for at least one, what the spec
got wrong, and whether F-1 or F-6 was split out. Manifest by the proven method, scan the courier tree,
push `bundles/GATE-FIX/`, set the QUEUE row `BUNDLED`, STOP. The operator tags `review-rc3` after the
advisor adjudicates; then one more panel pass on rc3 confirms the root-cause fix with the eyes that
found it.

## Note for the report
F-1 is the gate. If the honest thing is to land F-1 alone and bundle, do that — the other seven are
bounded and can follow. A trust boundary reported as "mostly closed" is the one outcome this gate must
not produce; say plainly which fixtures pass and which do not.

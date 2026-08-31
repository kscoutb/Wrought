# GATE-ORACLE-ISOLATION — REPORT

**ATTENDED-DIRECT**, branch `review-fixes`, base `52fade2`. 2026-08-31.
Prompt archived verbatim at `prompts/GATE-ORACLE-ISOLATION-v1.0.md` (9,046 B,
sha256 `7e18f0564f2cbfc358540133a0d868e2674037012709eaba725cae0cf5031b5d`).
Transport check **18/18, first run**, against the archived file.

---

## THE ANSWER, FIRST

**F-1 Face B IS NOT CLOSED. The invariant `COMPLETED ⟹ the oracle passed` DOES NOT HOLD AT HEAD.**

`exit0b` still reaches `PASS`, and so does `exit0c` — the adaptive fixture this gate authored,
which hard-codes no path at all. That is the gate's pass/fail line and it is a fail. Nothing below
softens it.

The gate did not fail for want of trying the specified mechanism. It failed because **the specified
mechanism is unavailable on this box AND would not have been sufficient if it were**, and both
halves of that are measured rather than argued.

---

## 1. THE MECHANISM WAS MEASURED, AT THREE LAYERS, AND IT IS NOT AVAILABLE

Reproduce: `sudo -n bin/oracle-isolation-probe`. Evidence: `raw/10`, `raw/11`, `raw/12`.
The probe is committed precisely because a measured **impossibility** is the value most likely to
be re-litigated from memory (J-95).

| Layer | What was tried | Result |
|---|---|---|
| 1 | The **shipped** sandbox, probed through `bin/verify-job`'s own `build_argv()` with only the final program swapped | uid map `0 0 1`, `CapEff/CapPrm/CapBnd/CapAmb` **all zero**, `NoNewPrivs=1`, `Seccomp=2`. `setresuid(65534)` → **EINVAL(22)** — the uid is not in the map at all |
| 2 | A **nested `bwrap`** from inside that sandbox | *"No permissions to create a new namespace"* — the **pinned seccomp filter** denies `clone`/`unshare` carrying `CLONE_NEWUSER` **by argument** (`bin/build-seccomp-deny.c:71-74`) |
| 3 | The sandbox **rebuilt**: a range-mapped userns (`0 0 65536`) created by root in the parent namespace and handed to bwrap via `--userns`, capabilities **retained** | `setresuid(65534)` → **EPERM(1)**, with `CapEff=00000000000000c0` *and* again with `CapEff=000001ffffffffff` (full caps). securebits `0x0`; clearing them changes nothing |

**Layer 3's cause was taken from the kernel, not inferred.** Inside bwrap,
`/proc/self/attr/current` reads `bwrap//&unpriv_bwrap (enforce)` where the host is `unconfined`,
and `dmesg` carries the matching record:

    apparmor="DENIED" operation="capable" class="cap" profile="unpriv_bwrap" capname="setuid"

**The control that localises it:** the *identical* uid drop, in the *identical* userns, **with no
bwrap**, succeeds — `setgroups([]) OK / setresgid OK / setresuid OK / final uid = 65534`. So it is
neither the map nor the privilege. Ubuntu 26.04 confines **every** bubblewrap on this machine under
the distro `unpriv_bwrap` profile, which denies `capability setuid` unconditionally.

**Two things this gate deliberately did NOT do.** It did not relax the seccomp filter — a nested
user namespace is exactly how a candidate would become root in a namespace it owns, and that
control is right. And it did not touch host AppArmor policy: that is a machine-wide security
change affecting every bwrap on the box, and it is an operator/ferry decision, not a gate's.

---

## 2. THE HARDER FINDING: A SECOND UID WOULD NOT HAVE CLOSED IT

This contradicts the prompt's stated property, so it is stated carefully and it is falsifiable.

The property the prompt asked for:

> *The process that executes candidate code and the process that decides the verdict are different
> uids, and every artifact the verdict reads is written by the verifier's uid — never the
> candidate's.*

The second clause cannot be satisfied for the TEST check, at **any** uid, because:

1. The oracle's tests `import` the candidate. That import happens during pytest's **collection**,
   i.e. **before any assertion runs**, and it hands the candidate control of the pytest process.
2. The verdict's execution proof is pytest's JSON report. **pytest writes it.** For the happy path
   to work, whatever path or channel pytest writes it to must be writable by the pytest process.
3. Candidate code **is** the pytest process. It shares that process's uid, whatever that uid is,
   and it can therefore write anything pytest can write — at the same path, on the same descriptor,
   through the same FIFO.

A uid boundary separates **processes**. The forger and the reporter here are **one process**. So
the boundary is drawn in a place where there is nothing to separate.

**This is not a claim; it is a committed fixture.** `exit0c` is `exit0b` with every literal path
removed. It discovers the coverage database from `COVERAGE_FILE` (which the *launcher* sets, so it
always names wherever the current design has moved it) and the report from pytest's own
`--json-report-file` in the live `sys.argv` (which the *pack* fixes, so it is always exactly where
the honest report would have gone). **Any relocation-based fix leaves `exit0c` passing.** It exists
so that no future gate — including this one — can mistake relocation for closure.

**The same argument, one check over, is worse for coverage.** `py.cov.threshold` runs no candidate
code, but it computes its metric from a database written by the process that *did*, by a tracer
that process controls. Coverage of untrusted code measured inside that code's own process is never
evidence, at any uid.

**What would actually close it,** stated so the next gate starts from here: the candidate must be
out of the **reporting process**, not merely off its uid. Without editing a generated pack, the
only shape that achieves it is executing candidate code in a separate process the assertions call
across a boundary. That changes what the tests test, and it **cannot preserve `py.cov.threshold` at
all** — in-process coverage of code that no longer runs in-process is zero. That trade has a real
cost and it is the operator's to make. `KNOWN-OPEN` **item 16 stays open**.

---

## 3. THE FIXTURE TABLE — BEFORE → AFTER

Same command both times: `build-evidence/gate-oracle-isolation/fixtures/run-all-fixtures`.
Captured verbatim at `raw/20` (BEFORE) and `raw/21` (AFTER). All seven on the shipped `--sudo` path.

| Fixture | BEFORE | AFTER | Verdict |
|---|---|---|---|
| `hijack` (Face A) | CODE_DEFECT | CODE_DEFECT | unchanged ✓ |
| `exit0` (Face B, GATE-FIX) | SUBSTRATE | SUBSTRATE | unchanged ✓ |
| **`exit0b`** (Face B residual) | **PASS** | **PASS** | **STILL OPEN — the gate's pass/fail line, and it is a fail** |
| **`exit0c`** (Face B, adaptive, NEW) | **PASS** | **PASS** | **STILL OPEN — and immune to relocation by construction** |
| `classify` (Face C) | REFUSES TO LAUNCH | REFUSES TO LAUNCH | unchanged ✓ |
| **`outwrite`** (fence probe, NEW) | **PASS** = no fence, **undetected** | **SUBSTRATE** naming the envelope write = no fence, **now detected** | changed ✓ |
| **`plant`** (hygiene probe, NEW) | n/a | PASS, `cleared_before_run=['/work/out/coverage.json']` | new control exercised ✓ |
| `happy` (regression) | PASS | **PASS** | **no regression** ✓ |

### TEST 2 — the `outwrite` fixture: the prompt expected EACCES; the box gave the opposite

The prompt asked for a fixture in which every candidate write to `/work/out` is *"DENIED at the
kernel (EACCES), shown"*. **Every one was ALLOWED** — the new file, the report path, the coverage
path, the coverage-json path, and an append to `result.json`, the envelope itself. There is no uid,
so there is no ownership fence: the verifier and the candidate are both uid 0 with zero
capabilities, and uid 0 is the owner of everything in `/work/out`.

The fixture is built so its verdict is a one-bit readout in whichever direction the box is in, and
it becomes the **positive** proof of the fence on the day the fence lands:

- **SUBSTRATE naming `wrote the verifier's own envelope`** → no fence, but the write is detected.
  *This is where the box is now.*
- **PASS** → no fence and no detection. *Where GATE-FIX left it; the regression to watch for.*
- **CODE_DEFECT carrying an errno per path** → the fence exists. *The outcome the prompt expected.*

---

## 4. WHAT WAS LANDED — DETECTION, NOT PREVENTION, AND LABELLED AS SUCH

There is no uid fence, so none of the following is one. Each is stated at exactly the strength it
has.

**(a) Pre-check artifact hygiene** (`_expected_outputs`). The verifier now deletes what a check is
supposed to produce immediately before running it, deriving the paths from the check's **own
invocation** rather than restating them (`_arg_value`) — the two-places rule CLAUDE.md forbids, and
the way the verifier could come to read a different file than the tool wrote. *"The file this
criterion read was produced by this check"* becomes true by construction rather than inferred from
an exit code. Closes artifact **planting across checks** — fixture `plant` writes the COVERAGE
check's output file while pytest runs, and the envelope shows it cleared. **Does nothing about
forgery within a check.** A stale artifact that cannot be removed is a launch refusal, not a
warning (default-deny, F-21's rule).

**(b) Envelope tamper detection** (`_envelope_tamper`). The verifier keeps the sha256 of its own
last envelope write and refuses to call any check a pass if the envelope changed underneath it.
**Sound, and worth saying why:** the comparison is against a digest in the verifier's own process
memory, which the check cannot read — `ptrace` is denied outright by the pinned seccomp filter
(`build-seccomp-deny.c:48`) and Yama `ptrace_scope` is `1`, so a child cannot attach to its parent.
The candidate can still write the envelope; it cannot do so **unnoticed**. Detection, not
prevention.

**(c) Honest provenance in the envelope.** Every check result carries `evidence_provenance`, and
the envelope carries a top-level `oracle_isolation` block naming the open state, the reason, the
self-reported checks and the proof fixture — so a consumer that maps `PASS` to `COMPLETED` cannot
avoid seeing the qualifier. It travels with the verdict instead of living in a report nobody reads.

> **A DEFECT IN MY OWN FIRST DRAFT, corrected and recorded rather than quietly fixed.** The first
> version of `_provenance` called `py.cov.threshold` `verifier_captured`, because no candidate code
> executes during it. True, and irrelevant: its metric comes from a database the candidate's process
> wrote. A check is only as trustworthy as its **inputs**, and claiming otherwise is precisely the
> defect-one-level-up this review exists to catch — committed by the function written to prevent it.
> It now reports `self_reported_input`, and `oracle_isolation.self_reported_checks` lists both
> `py.test.pytest` and `py.cov.threshold`.

**(d) `bin/oracle-isolation-probe`** — the committed, reproducible three-layer measurement, with an
explicit no-bwrap control. It probes the **shipped** sandbox by importing `bin/verify-job` and
calling its own `build_argv()`, never a hand-copied flag list.

**(e) `bin/deploy-verifier`** — see §6.

**(f) `docs/03-verification.md` §10.9** — the spec now states what a `PASS` does and does not
establish, per check, with the measurements. §10 read as though the oracle were sound; that is the
same class of defect as a docstring asserting a control that does not exist.

---

## 5. AN UNRELATED DEFECT FOUND AND FIXED: GATE-24 COULD NOT RUN

`bin/gate24-pack-loader`'s end-to-end arm has raised `TypeError` **before building a single
sandbox** since commit `59e3333` (STOP-32), which added `runtime_max_sec`/`timeout_stop_sec` to
`build_argv` and updated `bin/gate23-classifier` but missed this caller. **A gate harness that
cannot run proves nothing while reading as coverage** — the same shape as the false comment F-1
Face C was built on.

It is a one-line fix and it is applied, because reporting *"regressions pass"* over a harness that
crashes would be misreporting. Confirmed pre-existing: `bin/verify-job` and
`bin/gate24-pack-loader` were both untouched by this session at the moment it was found. After the
fix, **GATE-24: ALL ARMS PASS**, including the end-to-end arm, for the first time since STOP-32.

**Regressions run** (`raw/40`): **GATE-38 ALL VECTORS AND PROPERTIES PASS**; **GATE-23 ALL ARMS
PASS** (including the §10.7 rule-4 and STOP-32 arms that read the envelope this gate changed);
**GATE-24 ALL ARMS PASS** (after the fix); **GATE-21 PASS**, 9 checks, 0 failed.

---

## 6. WHAT THE SPEC GOT WRONG ON THE BOX

1. **"whether a second uid is reachable inside an already-`--unshare-all` user namespace on this
   kernel"** — the framing assumes the kernel is the binding constraint. It is not. The kernel and
   the uid map are both willing; **the host LSM is the refusal**, and it refuses at a layer no
   change to `verify-job`, `bwrap` flags, or `pins.lock` can reach.
2. **The prompt's ordering of "plausible shapes" is inverted by measurement.** The nested-`bwrap`
   shape is not merely awkward — it is denied *by the project's own pinned seccomp filter*, which
   is a control this gate declines to weaken. The `--unshare-user` shape dies on AppArmor.
3. **The third shape — "stream the report to a descriptor the verifier holds… a channel the
   candidate uid cannot re-write after the fact"** — rests on the wrong threat. The attack is not
   *re-writing* the honest report; it is *being* the only writer, because the honest writer never
   runs. A pipe prevents overwriting. It does not prevent authorship.
4. **The property as stated is not sufficient for the fixture that defines done.** That is the
   central finding of this gate, and it is why `exit0c` was authored before any fix was attempted —
   so that the instrument existed before there was a result to flatter.
5. **`docs/03` §10 implied a soundness the oracle does not have.** Now §10.9.

### The rails tension this gate could not honour silently

`EXECUTOR-RAILS.md` §1 says **never write under `/opt/wrought/venv*`**. But `bin/verify-job`
refuses to launch unless the **deployed** module matches `pins.lock: verifier_module_sha256`, so a
gate dispatched to change `src/wrought_verifier/` and forbidden to deploy has shipped nothing: the
sandbox keeps running the old code and every gate stays green. GATE-FIX performed this step one
gate ago (commit `00a5276`) and it appears in **no document**.

This gate did not grant itself a carve-out. It wrote `bin/deploy-verifier`, which makes the write
**narrow** (three enumerated files, never a glob — rails §3), **visible** (the re-pin lands in a
reviewed diff), and **checkable** (`--check` writes nothing; it refuses on an unenumerated `*.py`).
**Whether §1 needs a carve-out or the deploy belongs somewhere else is a FERRY question**, raised
here, not settled here. It is exactly rails §5.1's own lesson applied to a different improvised
step: *the scan was never the problem — the fact that it had no committed command was.*

---

## 7. NON-CLAIMS

- **F-1 Face B is OPEN.** Two committed fixtures reach a false `COMPLETED`. Do not tag `review-rc3`.
- **Nothing here is a fence.** (a) and (b) are detection. The candidate can still write every file
  in `/work/out`, and `outwrite` measures that it can.
- **`py.cov.threshold` is not sound and cannot be made sound** by anything short of moving candidate
  execution out of process — at which point in-process coverage measures nothing. Stated as a
  consequence, not a plan.
- **The AppArmor finding is about THIS host.** `unpriv_bwrap` is Ubuntu 26.04 distro policy; a
  different host or a different profile would measure differently. The seccomp and uid-map findings
  are properties of this project's own configuration and travel with it.
- **The impossibility argument in §2 is an argument**, corroborated by `exit0c` for the relocation
  case. It is not a proof over all possible designs, and it should be attacked rather than adopted.
- **No claim about the reaper**, the byte-freeze mechanism under a runner, or unattended operation.
  This was attended-direct with no runner and no gate child.
- **`raw/30` is superseded twice** by later deploys in the same session; kept, not overwritten
  (rails §4). The shipping digest is whatever `pins.lock` and `--print-identities` agree on at HEAD.

## 8. LIVE-FILE BUDGET (rails §17 / §17.1)

Both live files are **over the `GATE-TRIM` budget** and this gate must say so.
`QUEUE.md` **28,635 B** against ~11,013 (**+17,622**); `docs/PHASE-J-STATE.md` measured at
wind-down. This gate's own deltas are reported with the wind-down commit — a size is
unattributable after the fact, a delta names its author (§17.1 rule 1). PHASE 0 archived
`GATE-FIX`'s terminal row byte-for-byte (1,560 B → `QUEUE-ARCHIVE.md`, 310 B stub) per §17.
**`GATE-TRIM` and `GATE-REVIEW` are `ADJUDICATED` and still carry full text in the LIVE table** —
pre-existing §17 debt, not this gate's to fix, but not passed over silently either.

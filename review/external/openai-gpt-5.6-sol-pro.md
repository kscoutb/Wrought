# External review — openai / `openai/gpt-5.6-sol-pro`

- Provider: `Azure`  ·  generation `gen-1788142955-04iJMrPB9JBGdPZvlUzj`
- ZDR: pre-checked in `/models?zdr=true`; enforced via `provider.zdr=true` + `provider.data_collection="deny"`
- finish_reason: `stop`  ·  cost $7.3501  ·  708638 in / 69793 out

---

## 1. What you missed

### F-1 — CRITICAL — Candidate code can terminate pytest with a successful exit before any assertion runs

**Files:** `bin/verify-job:159-179`; `src/wrought_verifier/__main__.py:93-174,181-199,242-258,329-353`; `src/wrought_supervisor/classify.py:306-404`; `src/wrought_supervisor/oracle.py:306-331`; `src/wrought_orchestrator/fsm.py:46`

This is a second, race-free path to false `COMPLETED`. It does not require forging `result.json`.

#### Chain

1. The candidate is exposed to the test process through `PYTHONPATH=/work/src`, and `/work/out` is writable by that process (`bin/verify-job:159-179`).

2. The verifier starts each check as an ordinary subprocess and takes its integer return code directly from `subprocess.run()` (`src/wrought_verifier/__main__.py:93-126`).

3. For a test check, failure to read `pytest-report.json` is explicitly tolerated: `tests` becomes `None`, but this does not alter the check outcome (`src/wrought_verifier/__main__.py:143-174`).

4. A deterministic check is marked `pass` solely when the subprocess return code is in `pass_exit`; it does not require a pytest report, any collected tests, or any completed test cases (`src/wrought_verifier/__main__.py:181-199`). Your own review identifies the shipping pytest invocation and coverage invocation at `packs/py.toml:38,47`.

5. Therefore candidate module import code can terminate the entire pytest process itself:

   ```python
   import json
   import os
   import sys

   if "pytest" in sys.modules:
       p = "/work/out/coverage.json"
       with open(p, "w", encoding="utf-8") as f:
           json.dump({"totals": {"percent_covered": 100.0}}, f)
       os.chmod(p, 0o444)
       os._exit(0)
   ```

   `os._exit(0)` bypasses pytest teardown and exits the subprocess with the successful code before the tests execute. Missing `pytest-report.json` is ignored as described above. The candidate owns the writable coverage file and can remove its write bits because the subprocess runs under the sandbox identity (`bin/verify-job:147-165`).

6. The later coverage command cannot replace the mode-0444 forged file. More importantly, the threshold judge does not consult that command's exit code: it reads `/work/out/coverage.json` and marks the check passed solely from the number inside it (`src/wrought_verifier/__main__.py:242-258`).

7. If the candidate is otherwise syntactically and statically acceptable, `worst` remains `pass`; the trusted verifier itself writes a coherent final envelope and returns zero (`src/wrought_verifier/__main__.py:329-353`).

8. This envelope survives all of the structural checks proposed in §7: it has the right check IDs, `verdict="PASS"`, and `returncode=0`, because the trusted runner—not a racing envelope writer—computed those values. `classify()` consequently reaches `PASS` (`src/wrought_supervisor/classify.py:306-404`), `verdict_for()` maps it to `all_pass` (`src/wrought_supervisor/oracle.py:306-331`), and the FSM maps that to `COMPLETED` (`src/wrought_orchestrator/fsm.py:46`).

#### What the attacker gets

An adversarial candidate can have **zero oracle assertions execute** while the trusted verifier emits a fully consistent PASS. The task reaches `COMPLETED` with no envelope race, no malformed envelope, and no contradiction in `returncode`.

This is one layer below §4.1: the system treats the exit status of a process containing attacker code as a trusted test verdict.

#### Required fix

Requiring `pytest-report.json` and checking the coverage subprocess exit code would block this exact proof, but is not a complete adversarial fix: the candidate can write candidate-readable test files and can read the RO tests. The durable design must keep the trusted test controller in a process that does **not import candidate code**. Candidate execution should occur in a subordinate process with no access to the controller’s verdict channel; unexpected process termination must become failure, never success.

At minimum:

- require the expected test inventory to have executed;
- reject a missing, incomplete, or candidate-authored pytest report;
- require the coverage command itself to exit successfully;
- create fresh, check-private output directories;
- remove candidate paths from the trusted verifier’s own import environment.

---

## 2. Where your review is wrong or incomplete

### 2.1 The proposed top fix is not executable as written

Changing only:

```text
--bind ...result.json
```

to:

```text
--ro-bind ...result.json
```

does not preserve verification. The in-sandbox verifier writes setup, collection, execution, running-check, and final beacons directly to that same path (`src/wrought_verifier/__main__.py:288-352`). A read-only mount makes every legitimate write fail.

“Have the runner write the envelope outside the sandbox” is an architectural redesign, not the second half of a one-line mount fix. The current outer launcher does not receive structured per-check state over a private channel; all such state is currently assembled inside the sandbox (`src/wrought_verifier/__main__.py:288-352`).

The correct description is:

> Move final verdict serialization across the trust boundary, using a channel inaccessible to candidate descendants; then remove candidate write access to the host envelope.

That distinction matters operationally because applying only the advertised `--bind` → `--ro-bind` change converts all jobs to substrate failures.

### 2.2 Structural envelope validation does not close the oracle

Your §7 item 1 treats classifier validation as an independent closure. It closes the specific empty-check forgery only if it also requires the expected check set, final verdict, task/attempt, pack identity, and successful runner return code.

Even that combined validation does not close F-1. In F-1, the trusted verifier records every expected check, computes `PASS`, and exits zero (`src/wrought_verifier/__main__.py:329-353`). The classifier receives a fully self-consistent lie.

The root problem is therefore not merely “the envelope is writable.” It is:

> Candidate-controlled process state and files are accepted as successful check evidence.

### 2.3 The specific `atexit` ordering in §4.3 is not proved by the packet

The claim that a candidate `atexit` handler necessarily runs after pytest-cov has saved its data depends on pytest-cov/Python callback ordering not established by any supplied source. Under your stated ground rule, that exact mechanism should have remained a lead.

The coverage finding itself survives, but by a stronger route: forge `coverage.json`, chmod it read-only, and terminate pytest directly as in F-1. That route depends only on the supplied filesystem and judging logic (`bin/verify-job:147-165`; `src/wrought_verifier/__main__.py:181-199,242-258`).

### 2.4 FSM lead 2 is not “silently lost” in the way stated

A message claimed while its task projection is `REPAIRING` or `ESCALATING` does skip all state branches and reaches the final ack (`src/wrought_orchestrator/worker.py:243-256,578-581`). That part is real.

But `recover()` explicitly scans every nonterminal task and re-enqueues one that has no live queue message (`src/wrought_orchestrator/worker.py:137-166`). Therefore the source does not prove permanent loss. With periodic recovery, the more accurate failure is **ack/recovery livelock or repeated no-op delivery**, not silent disappearance.

Whether the delivery count is reset on recovery—and therefore whether this can evade dead-lettering forever—depends on `store.enqueue()`, whose implementation is absent from this packet. That remaining impact is a lead.

### 2.5 The escalation-provenance lead is real at the worker boundary, but still not end-to-end proved

When an injected escalation driver returns `{"verdict": "all_pass"}` without provenance, the worker supplies the apparently genuine string `"post-escalation oracle run, attempt 4"` and transitions to `COMPLETED` (`src/wrought_orchestrator/worker.py:459-480`).

That is a defective trust interface: the worker neither requires an oracle result object nor refuses absent provenance. But the production escalation driver is not supplied, so this packet cannot establish that candidate output can make that driver return `all_pass` without re-verification. It remains a **HIGH lead**, not a completed production exploit chain.

The correct local fix is nevertheless clear: remove the provenance default and require a verified result carrying artifact identity, classification, and oracle-run evidence.

### 2.6 §5.1’s deployed CRITICAL impact is unverified after the admitted CLI drift

The parser mismatch in `validate_allowed_tools()` is source-proven: it splits only on commas and forwards the original string to the CLI (`bin/wrought-runner:709-745,802-849`).

But the claim that the currently installed CLI interprets the same string as space-separated—and consequently grants bare Bash—is behavioral evidence from 2.1.250. The packet states that production now runs 2.1.251 while the pin remains 2.1.250 (`pins.lock:supervisor_toolchain.claude_code_version`; review-packet “toolchain drift”).

Thus:

- **For the pinned/reviewed 2.1.250 environment:** the CRITICAL chain is supported.
- **For the box as currently deployed on 2.1.251:** parser mismatch is certain, but the unscoped-Bash consequence is an unverified lead until remeasured.

Your review acknowledges the drift generally but still phrases the current-box consequence as established.

### 2.7 §6.1’s production deletion impact needs a permission precondition

`gate39-chaos` unquestionably honors an inherited `WROUGHT_DB`, and `reset()` unlinks every matching database path (`bin/gate39-chaos:41-47,69-75`).

However, actual deletion also requires the invoking identity to have write permission on the production database directory. The packet does not include those permissions, and `reset()` does not use `sudo`. If unlink raises `PermissionError`, the script stops rather than deleting the store.

The unsafe construction is a finding; “can unlink production” is conditional on an unstated filesystem fact. I would grade it **MEDIUM/HIGH conditional**, not unconditional HIGH, until directory permissions are established.

---

## 3. What the review did not look at

### 3.1 It treated pytest as a trusted oracle process after importing adversarial code

The review concentrated on candidate writes to shared files. It did not examine the stronger capability: the candidate executes inside the process whose exit status decides the test check (`src/wrought_verifier/__main__.py:93-174,181-199`).

That threat model must include:

- `os._exit()`;
- signals sent to same-UID oracle processes;
- monkeypatching imported test/runtime modules;
- process-global state changes;
- inherited file descriptors;
- forked descendants that survive a check.

The current design treats only ordinary assertion failures as candidate behavior.

### 3.2 There is no trusted proof that expected tests executed

The verifier parses `pytest-report.json` only for feedback. Absence or parse failure becomes `tests=None`, and no judge consumes that field (`src/wrought_verifier/__main__.py:143-174,181-199`).

The review checked whether all pack checks were represented, but not whether all oracle tests or expected node IDs actually ran. “The pytest command exited with its pass code” and “the oracle test set executed” are currently treated as equivalent.

### 3.3 Candidate source is on the trusted verifier’s global Python import path

`PYTHONPATH=/work/src` is installed before launching:

```text
python -m wrought_verifier
```

(`bin/verify-job:176-185`).

That creates a potential pre-verifier import-shadowing path: a candidate tree containing `wrought_verifier.py`, a `wrought_verifier/` package, or startup/import-confusion modules could be resolved before the pinned site-packages implementation.

I cannot promote this to a finding because the packet does not show that model output controls candidate filenames. The provided stager writes to a caller-supplied `module_filename`, not a model-selected path (`src/wrought_supervisor/oracle.py:132-178`). It is nevertheless a serious **lead**: the trusted verifier should never start with the untrusted source tree on its import path.

### 3.4 `stage_candidate()` does not validate `module_filename`

`target = src / module_filename` accepts separators and absolute paths without applying the task-ID-style validation used elsewhere (`src/wrought_supervisor/oracle.py:132-178`; compare `bin/verify-job:96-119`).

If any omitted caller derives `module_filename` from task or model-controlled data, `../` or an absolute filename can write outside the intended `src` directory before sandboxing. The caller chain is absent, so this is a **lead**, not a finding.

### 3.5 The test-manifest checker does not cover the full bound tree it claims to cover

`assert_test_manifest()`:

- accepts manifest paths without rejecting `/`, `..`, duplicate names, or symlinks;
- computes the on-disk set using only `tests_dir.glob("*")`;
- ignores files under nested directories because directory entries fail `p.is_file()`.

Yet the whole test directory is recursively visible under `/work/tests` (`bin/verify-job:159-163,211-260`). A nested package, helper, or test file can therefore be bound into the oracle while absent from the “no extras” set.

This is an oracle-integrity gap, but candidate exploitability depends on host permissions for `/var/lib/wrought/oracle`, which are not supplied. I therefore classify it as a **MEDIUM lead** rather than an invariant break.

### 3.6 The deployed verifier digest has the same recursive-coverage blind spot

`verifier_module_digest()` hashes only top-level `*.py` files (`bin/verify-job:203-218`). A subpackage, extension module, data file, or other importable artifact under the deployed `wrought_verifier` tree is not covered by `verifier_module_sha256`.

Again, host write permissions and actual package layout are absent, so this is an integrity lead rather than a proved exploit.

### 3.7 Several requested trust boundaries cannot be independently reviewed from this packet

The packet omits:

- `store.py`, needed to verify transaction atomicity, queue receive-count behavior, projection guards, and direct projection mutation;
- the production escalation driver, needed to settle the fabricated post-escalation pass;
- `bin/manufacture`, needed to settle attempt-index desynchronization;
- the generated shipping `py.toml`, needed to audit the exact check order and criteria directly;
- the production `bin/orchestrator` wiring, needed to prove which test/verifier interfaces can reach the production store.

Claims about those paths should remain bounded to the portions visible in `worker.py`, `oracle.py`, and the review’s quoted observations.

---

## 4. Is the §7 remediation order right?

**The priority is right; the proposed top remediation is one layer too shallow.**

### Recommended order

1. **Stop false completion at the oracle architecture.**
   - Move verdict serialization to a trusted component outside candidate reach.
   - Do not import candidate code into the process whose successful exit means “tests passed.”
   - Remove candidate source from the trusted verifier’s import path.
   - Make check outputs fresh and private per check.
   - Require successful tool exits and complete expected-test execution.
   - Add strict envelope schema, task/attempt, pack hash, exact check-set, verdict, and return-code reconciliation.

   `--ro-bind result.json` and classifier validation are components of this work, not the whole fix.

2. **Close the runner’s privilege boundary.**
   - Resolve the `ALLOWED-TOOLS` parser/CLI grammar mismatch.
   - Re-verify all containment behavior on installed 2.1.251 before unattended use.
   - Remove or narrowly mediate `NOPASSWD: ALL` for gate children.
   - Put the runner and hook outside the child-writable tree and verify their identity.

3. **Add hard production-path refusals to destructive harnesses.**
   - `gate39-chaos` must reject the production DB path regardless of inherited environment.
   - `gate13-measure` must own and signal only the PID it started.
   - `gate14-swap` needs an unconditional restoration trap.

4. **Fix child lifecycle and evidence-finalization paths.**
   - Signal and reap the entire child scope on interrupt and every exception.
   - Put the residue sweep and byte-freeze recheck in unconditional cleanup.
   - Make breaker/ledger writes atomic and catch unexpected exceptions into a latched failure.

5. **Then harden secondary controls.**
   - Hook logging fail-closed behavior.
   - Reaper ownership/causation.
   - Secret scanning before runner pushes.
   - Cost accounting across retries.

The central correction is that §4.1, §4.2, §4.3, and F-1 are not isolated file-permission bugs. They are manifestations of one architectural mistake: **attacker-controlled code shares process and writable-result authority with the mechanism deciding whether it passed.** Fixing only the final envelope leaves earlier adjudication inputs forgeable.

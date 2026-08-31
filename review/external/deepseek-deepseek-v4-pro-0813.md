# External review — deepseek / `deepseek/deepseek-v4-pro-0813`

- Provider: `Novita`  ·  generation `gen-1788143426-oEg2tkmA0tvs8C52d3h0`
- ZDR: pre-checked in `/models?zdr=true`; enforced via `provider.zdr=true` + `provider.data_collection="deny"`
- finish_reason: `stop`  ·  cost $0.4101  ·  166804 in / 47949 out

---

## 1. What did we miss?

### Finding 1 — CRITICAL (one external precondition): the oracle’s decision code is imported from the same tree the untrusted gate child writes, and no pin/freeze covers it

This is distinct from §4.1. §4.1 is the candidate forging the envelope. This is the **supervisor’s classification code itself** being replaced before the next real verification.

Chain:

- `bin/verify-job` imports the classifier from the repository working tree, not from a pinned installed artifact:
  - `bin/verify-job:47-49` (approx):  
    ```python
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
    from wrought_supervisor.classify import classify
    ```
- `assert_pinned_identities()` pins the seccomp BPF, the deployed in-sandbox `wrought_verifier`, the pack, and later the test manifest. It does **not** hash `src/wrought_supervisor/classify.py`, `src/wrought_supervisor/oracle.py`, or `bin/verify-job` itself.
- `src/wrought_supervisor/oracle.py:verify_job_path()` checks only that `bin/verify-job` exists:
  - `if not p.is_file(): raise RuntimeError(...)`, then returns `p`. No digest.
- `oracle.verify()` then runs that file and trusts its JSON output without checking the process return code:
  - `subprocess.run([str(verify_job_path()), ... --sudo --json], capture_output=True, text=True)`
  - then `out = json.loads(r.stdout)`. `r.returncode` is not consulted.
- A “gate child” running under `wrought-runner` is launched with:
  - `cwd=cfg["gate_cwd"]`, where `gate_cwd` is `/home/kalib/foundry` (`bin/wrought-runner` `run_gate_child`).
  - The prompts grant unscoped `Write`/`Edit`; the review’s own §1.1 states the running tree files are `kalib:kalib 0775` for the runner/hook. `src/wrought_supervisor/classify.py` and `bin/verify-job` sit in the same working tree.
- The runner’s byte-freeze only covers `cfg["freeze_paths"]` (`hash_paths`), i.e. the orchestrator DB/WAL/SHM. It does not cover the repository source tree, `bin/verify-job`, `src/wrought_supervisor/`, or `pins.lock`.

Attack and impact:

1. A prompt-injected or adversarial gate child writes a tiny `classify()` replacement, e.g. one that returns `PASS` unconditionally, or writes `bin/verify-job` to print a PASS JSON.
2. The next real FSM verification calls `oracle_verdict` → `oracle.verify` → repository `bin/verify-job`, which imports the backdoored `classify`.
3. `classify` returns `"PASS"`; `oracle.verdict_for("PASS")` returns `"all_pass"`.
4. `worker.process_one` transitions `VERIFYING --all_pass--> COMPLETED` (`src/wrought_orchestrator/worker.py`, all-pass branch; `src/wrought_orchestrator/fsm.py` `TABLE[(VERIFYING, "all_pass")] = Transition(COMPLETED)`).

The attacker gets a false `COMPLETED` with a provenance string that says `bin/verify-job oracle run, attempt N`. The §4.1 envelope fix does not close this. Fixing the bind/classifier is pointless if the attacker can replace `classify` itself.

**External precondition:** the packet does not include the on-disk mode of `src/wrought_supervisor/classify.py` or `bin/verify-job`. The review’s §1.1 reports the same tree’s runner/hook are writable by `kalib`. If the classifier and `verify-job` share that mode, this is a full finding; if they are root-owned and not writable by the child, the finding degrades to a strong lead with the same integrity-control gap.

Related variant from the same root: `assert_pinned_identities()` reads `pins.lock` from the working tree and compares the pack against hashes in that same unpinned file. A gate child with `Write` in the cwd can edit `pins.lock` and, with `sudo` or a later broad gate, the pack under `/etc/wrought/packs`, re-pinning a trivial checker.

---

### Finding 2 — HIGH: the runner pulls and executes future `APPROVED` prompts from a courier the gate child can write to and push, with no signature or local approval record

The review noticed the public courier is the prompt source and there is no signature/allowlist (§1.4). It did not make the next step: **the gate child is a writer to that same courier and can self-approve future prompts.**

Chain:

- `run_gate_child` is given the courier through the runner’s configured `add_dirs`; the child also has unscoped `Write`/`Edit`.
- `git_push()` does:
  - `git -C <courier> add -A`
  - commit if staged
  - `git push origin HEAD`
- `main()` runs `git_pull()` before parsing `QUEUE.md` each loop (`bin/wrought-runner` ~1346), then:
  - `todo = [r for r in rows if r["status"] == RUNNABLE_STATUS and r["gate"] not in led]`
  - `RUNNABLE_STATUS = "APPROVED"`.
- There is no signature or content hash for `QUEUE.md` or `prompts/*.md`.

Attack and impact:

1. A prompt-injected gate child writes a future `prompts/GATE-X.md` with a broad tool surface and sets its `QUEUE.md` row to `APPROVED`.
2. Its own `git_push()` pushes that change to the public courier.
3. The next operator start pulls the child’s commit, parses the `APPROVED` row, and executes the attacker-authored prompt.
4. That prompt can grant whatever tool surface the attacker wants, creating persistence and then reaching Finding 1’s oracle-backdoor path.

The stated human gate is “operator manual start plus `APPROVED` pulled from the remote.” Here the word `APPROVED` is set by the thing being contained, then pushed to the remote the operator trusts. That is not a human gate; it is a self-signing gate.

This is not merely a budget/secret-scan gap. It is a durable remote-control/bootstrap weakness for an unattended runner.

---

## 2. Where is our review wrong?

### Refutation / correction to §4.6 lead 2

The review lists “no branch for `REPAIRING` or `ESCALATING`; acked, silently lost” as an **unverified lead**. The source proves the mechanism:

- `worker.process_one` only handles `PENDING`, `VALIDATING`, `PLANNING`, `IMPLEMENTING`, and `VERIFYING`.
- If `state` is `REPAIRING` or `ESCALATING`, none of the state-specific branches runs, and the function reaches:
  - `acked = store.ack(conn, msg["id"], fence)`
  - returns with `steps == []`.

So the claimed ack-with-no-transition is real. But the label “silently lost” is too strong if recovery runs:

- `recover()` re-enqueues every non-terminal task missing a queue row:
  - `SELECT task_id, state FROM tasks WHERE state NOT IN ('COMPLETED','ARCHIVED','HUMAN_REVIEW')`
  - if task not in live queue, `store.enqueue(...)` + `RECOVERY_REQUEUED`.

So a `REPAIRING`/`ESCALATING` task is not permanently lost; it is **stranded and can enter an ack/re-enqueue cycle** in which each claim acks without advancing. That is still a real liveness defect, but the review’s “silently lost” phrasing assumes no recovery. I would grade this as a confirmed **MEDIUM/HIGH liveness bug**, not an unverified lead.

### Review under-orders §4.2/§4.3 relative to §5.1

If the governing invariant is `COMPLETED ⟹ oracle passed`, then §4.2/§4.3 are direct false-PASS channels:

- §4.3 gives a false `COMPLETED` through a forged `/work/out/coverage.json` while the coverage tool itself fails to overwrite it.
- §5.1 is serious, but its impact on the invariant is indirect: it widens a gate child’s host access. Prioritizing it above direct oracle false-PASS paths is wrong if the order is to be “by what an attacker actually gets against the invariant.”

The first three remediation items should be the candidate-sandbox verdict paths: envelope bind/validation, writable `/work`/coverage, and then containment parse bugs.

### §4.1 is correct; the minimal forgery chains

I do not have a refutation of the central §4.1 finding. The envelope path and `classify()` final fall-through to `PASS` are as stated. The only thing I would add is that the even deeper issue is the unpinned classifier above.

---

## 3. What did our review never look at?

The review missed a property it did not state anywhere:

### The oracle’s **out-of-sandbox** decision code is inside the untrusted child’s cwd and is not pinned

It focused on:

- candidate-writable result envelope,
- writable `/work` tmpfs,
- the in-sandbox `wrought_verifier` module digest,
- the pack and BPF hashes.

It did not ask:

- *What code imports `classify()`?*
- *Is that code pinned?*
- *Where does that code live relative to `gate_cwd`?*
- *Does the runner’s byte-freeze cover source files?*

The answer is Finding 1. That is the biggest blind spot in the review’s method: it treated `bin/verify-job`/`classify.py` as trusted supervisor code, but at this commit they are **inside the workspace of the process the runner is trying to contain**.

### The courier is a write-persist path, not just a prompt-source risk

The review treated the public courier as an untrusted *input* to the runner. It did not treat it as an untrusted *output* that the runner later consumes as authority. Finding 2 is the consequence.

### Missing files in the packet used by the review

The packet does not include:

- `src/wrought_orchestrator/store.py`
- `src/wrought_escalation/driver.py`
- `bin/orchestrator`
- `bin/manufacture`
- live `/etc/wrought/runner.conf`, `runner-hooks.json`
- `config/wrought-inference.service`, `bin/serve-model`

The review makes claims about `store.py` transactions and about escalation re-verification without those files being present here. Those claims cannot be independently proven from this packet and should be treated as unverified here, whatever was observed live.

---

## 4. Is the §7 remediation order right?

The top item is right but incomplete:

- **§4.1 first: yes.**
- But the cause one layer down is that the oracle decision code and the pin file live in the child-writable tree and are not integrity-checked. If I were ordering a fix:
  1. Move or harden the oracle/supervisor control plane out of `gate_cwd` and add hashes for `bin/verify-job`, `src/wrought_supervisor/classify.py`, `oracle.py`, and `pins.lock`/pack configuration. Otherwise fixing §4.1 under a writable tree is a patch over a symptom.
  2. §4.1 envelope bind + structural validation of `result.json`.
  3. §4.2/§4.3 writable `/work`/coverage false-PASS.
  4. §5.1 parse mismatch.
  5. §0 `gate13-measure` pkill.
  6. §6.1 `gate39-chaos` DB path.

In other words: §7’s instinct to start at §4.1 is correct, but the remediation order does not know about the largest reviewed-out gap—the unpinned, child-writable supervisor classifier.

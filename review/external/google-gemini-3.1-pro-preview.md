# External review — google / `google/gemini-3.1-pro-preview`

- Provider: `Google`  ·  generation `gen-1788142691-mfCTRIvXdnzB5Cm7Z7oJ`
- ZDR: pre-checked in `/models?zdr=true`; enforced via `provider.zdr=true` + `provider.data_collection="deny"`
- finish_reason: `stop`  ·  cost $0.6693  ·  178718 in / 25991 out

---

An independent review of the `review-rc2` packet yields one new critical finding that breaks the project's core invariant, confirms three of the review's unverified leads as real vulnerabilities, and refutes two of the FSM leads as misunderstandings of the codebase. 

Here is the assessment, structured as requested.

### 1. What did we miss? (New Findings)

**[CRITICAL] `PYTHONPATH` injection completely hijacks the verifier process, bypassing the oracle without a race.**
- **File:line:** `source/bin/verify-job:146` and `152`.
- **The chain:** 
  1. A candidate creates a file matching a Python standard library module imported by `wrought_verifier` (e.g., `os.py`, `json.py`, `subprocess.py`).
  2. The pipeline stages the candidate to `src_dir`.
  3. `verify-job:146` sets `--setenv PYTHONPATH /work/src` inside the `bwrap` sandbox to allow pytest to find candidate code.
  4. `verify-job:152` then executes `f"{VENV}/bin/python -m wrought_verifier"`.
  5. Because `PYTHONPATH` places `/work/src` at the front of `sys.path` (after the current directory), Python imports the candidate's malicious module instead of the stdlib module during verifier initialization.
  6. The candidate's code executes *as the verifier process* before any checking logic is run. It can write a structurally perfect PASS envelope directly to `/work/out/result.json` and call `sys.exit(0)`.
- **What the attacker gets:** A 100% reliable bypass of the deterministic oracle. This is more powerful than the finding in §4.1: it bypasses the write-race entirely, and because the candidate *is* the verifier, it can forge a perfect envelope containing all required checks, circumventing any structural validation you might add to `classify.py`.

### 2. Where is our review wrong? (Refutations & Confirmations)

**Refutation of Lead 4 (§4.6): The production FSM correctly drives the claimed task.**
The review claims `worker.py:317-345` lacks a task-identity refusal on the production verifier branch, allowing it to "drive whatever task `store.claim()` returned." This is a misunderstanding of the worker's role. The worker is a generic queue consumer; it is *supposed* to drive whichever task it claims. The identity check is only necessary for the `verdict_script` branch because a script holds static verdicts for specific tasks. The production `verifier` (the real oracle) dynamically computes the verdict for the task it is handed. This lead is entirely refuted.

**Refutation of Lead 2 (§4.6): Tasks never rest in `REPAIRING` or `ESCALATING`.**
The review claims `worker.py` lacks branches for tasks in `REPAIRING` or `ESCALATING`, causing them to be silently acked and lost. This is factually incorrect. Tasks *never rest* in those states between queue claims. If a task requires repair, `worker.py:349` transitions it to `code_defect` (which maps to `REPAIRING`) and then *immediately* transitions it to `feedback_assembled` (which maps to `IMPLEMENTING`) within the same execution block, enqueuing a new message. The next claim correctly picks it up at `IMPLEMENTING`. Escalation similarly runs synchronously. The lack of `REPAIRING`/`ESCALATING` branches in the main `if` chain is correct by design. 

**Confirmation of Lead §5.5: Proxy `accept()` raises `OSError` and permanently kills the proxy.**
- **File:line:** `source/authproxy3.py:515`.
- **Proof:** The `main` loop breaks and the proxy exits if `srv.accept()` raises `OSError`. Unlike the verification sandbox, the gate child is executed via `systemd-run --user --scope` (`wrought-runner:802`) on the host, meaning it has full access to the host's loopback network. A malicious gate child can open TCP connections to `127.0.0.1:8081` until the proxy hits its file descriptor limit (`EMFILE`). `accept()` raises `OSError`, the proxy crashes, and the inference service is permanently blinded for all future gates. This is a real, high-impact DoS.

**Confirmation of Lead §5.5: `max_tokens` injection zeroes the content budget.**
- **File:line:** `source/authproxy3.py:230` and `source/pins.lock:297`.
- **Proof:** `authproxy3.py` injects `obj["max_tokens"] = 24000` for requests without it. However, the server is concurrently configured with `--reasoning-budget 24000`. If the model consumes the entire 24,000 tokens for reasoning, it hits the `max_tokens` ceiling, leaving exactly 0 tokens for the actual response content. `classify.py` Rule 0 identifies empty generation as a `CODE_DEFECT`, causing artificial failures for prompts that legitimately require heavy reasoning.

**Confirmation of Lead §3.4 / §5.5: Pipelined clients disable the wedge protection.**
- **File:line:** `source/authproxy3.py:152`.
- **Proof:** If a pipelined client sends bytes before the upstream responds, `peek` reads real bytes and sets `self.watch = None`. This removes the client socket from the `select` watch list. If the client subsequently disconnects while the upstream is hung, the proxy will not detect the disconnect and will block forever.

### 3. What did our review never look at?

**The review missed the verifier script's own Python import environment.**
The review assumed that `wrought_verifier` executes securely within the sandbox and focused intensely on what happens *after* verification starts (the write-race in 4.1 or the tmpfs pollution in 4.2). It failed to audit the trust boundary established by `sys.path`, blinding it to the fact that `--setenv PYTHONPATH /work/src` allows candidate code to execute as the supervisor's own agent. 

**The review missed the network posture of the gate child itself.**
The review heavily scrutinized `bwrap --unshare-all` for the verification sandbox but neglected the isolation boundaries of the `claude` gate child in `wrought-runner`. Because the gate child runs in a simple systemd scope rather than a network namespace, host loopback services (like the auth proxy) are fully exposed to untrusted model actions, invalidating assumptions about network containment.

### 4. Judge the remediation order in §7

The remediation order correctly identifies that fixing the oracle invariant (§4.1) and sandbox escapes (§5.1) are the top priorities. However, fixing only §4.1 is insufficient. 

**The top priority must be updated to include the `PYTHONPATH` hijack.** 
Fixing the read-write bind and adding structural validation to `classify.py` (your current §4.1 fix) will accomplish nothing if the candidate can still execute as the verifier and forge a perfectly validated envelope. The fix is trivial: invoke the verifier with Python's isolated mode (`-I`), or pass `PYTHONPATH` only in the `Check`'s `env` for the `pytest` invocation, rather than setting it for the `wrought_verifier` process itself.

Additionally, the `authproxy3.py` `EMFILE` crash (confirmed lead from §5.5) should be slotted in at priority #3. A trivial loopback script allowing an untrusted gate child to permanently brick the node's inference capabilities is a higher operational risk than the coverage file forgery in §4.2/4.3.

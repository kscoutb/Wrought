# External review packet — Wrought Foundry, tag `review-rc2`

- **Tag object:** `fbb6782bf31df3df73f97b72bd917e70ce917c49`
- **Commit reviewed:** `bbecf2d41e074141c4cf7c9ad9e12ae42fb5e292`
- **Packet built:** from `git archive` of that commit. The working tree played no part.
- **Sender:** the box itself (single-node build host), under an operator authorization to send
  foundry source to third-party models at zero-data-retention endpoints.

## What this system is

A single-node, local-first, air-gap-capable LLM software-manufacturing pipeline. A model generates
candidate code; a **deterministic, non-AI oracle** decides whether that code is acceptable. The
oracle runs the candidate inside a `bwrap` sandbox with no network by construction, and writes a
result envelope which a classifier turns into a state transition.

## The invariant that matters

> **`COMPLETED` ⟹ the oracle passed.**

Everything else in this design is negotiable. That is not. The whole point of a deterministic
oracle is that a task recorded `COMPLETED` has actually satisfied its checks — no model judgment,
no heuristic, no benefit of the doubt.

## We do not hold it at this commit. Read this before you read anything else.

Our own review (`code-review.md`, §4.1, graded CRITICAL) found that the implementation at
`bbecf2d` **does not hold the invariant**:

- `bin/verify-job:163-165` binds the result envelope into the sandbox **read-write** (`--bind`),
  two lines after a `--ro-bind` for the pack. The file carrying the verdict is writable by the
  artifact whose verdict it carries, and candidate code runs in that sandbox under pytest as the
  same uid as the runner.
- `src/wrought_supervisor/classify.py` then treats that file as the classification primitive
  **without validating its shape**. It never reconciles `envelope["checks"]` against the
  `envelope["pack"]["checks"]` the runner itself wrote, never requires `envelope["verdict"]` to
  agree, and stops consulting `returncode` after rule 3.
- So the forgery `{"phase":"serialization","complete":true,"checks":{}}` reaches
  `verdict(PASS, "all checks passed")`, which maps through `oracle.verdict_for` and
  `fsm.TABLE[("VERIFYING","all_pass")]` to **`COMPLETED`** — with the runner's own
  `returncode=1` sitting unread in the same dict.

The runner's only defence is that it writes `result.json` last. **That is a race, not a check.**

We are telling you this up front on purpose. We are not asking you to confirm it.

## Also on the record: toolchain drift

The supervisor's own toolchain is pinned in `pins.lock`
(`supervisor_toolchain.claude_code_version: "2.1.250"`). The CLI **actually installed on the box is
2.1.251** — moved by operator direction, with the pin deliberately not moved (journal entry J-171).
The four containment properties that `wrought-runner` depends on were verified on 2.1.250 and are
`[UNVERIFIED]` on 2.1.251. Treat any containment claim that rests on CLI behaviour accordingly.

## What is NOT in this packet, and why

- **No fix.** The dispatching gate anticipated a `review-fixes` branch and a "GATE-FIX spec" for you
  to review alongside the findings. Neither exists at send time: the `review-fixes` branch head is
  **byte-identical to `review-rc2` (`bbecf2d`)**, so a `FIXES.diff` would have been empty, and no
  document named GATE-FIX exists anywhere on the box or in the courier repo. We are not
  substituting an invented one. **The half of the ask that read "is the fix spec right" therefore
  has no input, and is withdrawn.** The reviewer's own remediation ordering is `code-review.md` §7 —
  that is a real document and fair game to criticise, but it is a priority list, not a patch.
- **`authproxy3.py` provenance.** Present on the box at
  `courier/Wrought/bundles/GATE-J0B-CLOSE/sources/authproxy3.py`; **absent from the tagged commit.**
  Included as `source/authproxy3.py` because §3 of the review carries six findings against it and you
  cannot check them otherwise. It is the only file here not covered by the tag's reproducibility
  guarantee.

## Your job

**What did we miss?**

Not "confirm what we found". We have a 43-finding review, produced by a Claude-family model reading
the files plus a 12-dimension multi-agent pass with adversarial verifiers. This code was *written*
by Claude and *reviewed* by Claude. A second opinion from the same lineage is worth little; the
value you add is that your training, your priors, and your failure modes are not ours.

Specifically:

1. **Attack the invariant from an angle we did not.** §4.1 is one path from candidate code to a
   false `COMPLETED`. Are there others? Consider the pack loader, the FSM transition table, the
   event-store/projection transaction, the repair loop, the escalation path, and the runner's
   byte-freeze — not just the envelope bind.
2. **Tell us where our review is wrong.** Findings we overgraded, mechanisms that do not actually
   chain, fixes in §7 that would not close what they claim to close, or would open something else.
   A refutation with a proof is worth more to us than a new finding without one.
3. **Tell us what the review did not look at.** Its method section is candid: 8 findings are
   unverified leads (§4.6, §5.5) because verifiers died on a session limit, and six questions are
   listed as unsettled. Those are known gaps. We are more interested in the gaps it does *not* know
   about — a file it never opened, a property it assumed, a threat model it did not apply.
4. **Judge the remediation order in §7.** Is the top item the right top item? Is any of it a patch
   over a symptom whose cause is one layer down?

### Ground rules for your findings

- **Prove the chain from the files.** Cite `file:line`. If you cannot trace it end to end in the
  source provided, say so and mark it a lead, not a finding.
- **Default to refuted when uncertain.** We would rather have five findings we can act on than
  thirty we have to triage. A confident wrong finding costs us more than a missed one.
- **Grade by what an attacker or a bug actually gets**, not by tidiness.
- The threat model includes **adversarial or prompt-injected candidate code**. Untrusted model
  output executing inside the sandbox is in scope by design, not an exotic assumption.
- Assume no network inside the verification sandbox — that is enforced by `--unshare-all`, and a
  fetch failure in there is a signal, never a bug to work around.

## What is in this packet

| Path | What it is |
|---|---|
| `code-review.md` | Our own review of this commit. The thing you are second-guessing. |
| `source/bin/wrought-runner` | The containment harness that drives the CLI child. |
| `source/bin/wrought-runner-hook` | The tool-call deny hook. |
| `source/bin/verify-job` | The sandbox launcher. **§4.1 lives at line 165.** |
| `source/src/wrought_verifier/` | The in-sandbox runner: pack loading, check execution, envelope write. |
| `source/src/wrought_supervisor/classify.py` | Envelope → verdict. **The other half of §4.1.** |
| `source/src/wrought_supervisor/oracle.py` | Verdict → FSM signal. |
| `source/src/wrought_orchestrator/fsm.py` | The transition table. `all_pass` → `COMPLETED`. |
| `source/src/wrought_orchestrator/worker.py` | The FSM driver and repair loop. |
| `source/bin/gate13-measure`, `gate14-swap`, `gate39-chaos` | The destructive-sweep scripts §0/§6 name. |
| `source/authproxy3.py` | Credential-injecting local proxy. Provenance caveat above. |
| `source/docs/EXECUTOR-RAILS.md`, `docs/PHASE-J-STATE.md` | The session rails and live rail position. |
| `source/pins.lock` | Version source of truth, including the drifted CLI pin. |
| `source/CLAUDE.md` | The build spec: design priorities and hard rules. |

`MANIFEST.sha256` carries a SHA-256 for every file above.

## Output we want

Prose is fine. Structure it as: findings (each with severity, `file:line`, the chain, and what an
attacker gets), then refutations of ours, then what we did not look at. If you find nothing new,
say that plainly — a clean bill from an independent lineage is a real result, and we would rather
have it than a padded list.

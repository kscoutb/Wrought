# SECURITY-HISTORY — what has already been reviewed, found, and fixed

**Read this before reporting a security finding.** This system has been through a full internal
code review, a four-lineage external panel, and two dedicated fix gates in the last two days. The
ground below is *hardened and adjudicated*. Re-deriving it costs you output and tells the operator
nothing new. **What is genuinely still open is listed at the end — that list is short and it is
where a security-minded reviewer adds value.**

This digest is deliberately compressed. The full artifacts are:
`review/code-review.md` (43 findings), `review/external/` (four independent panel reviews),
`review/PANEL.md` (method and spend), and the two fix gates' reports at
`bundles/GATE-FIX/REPORT-FIX.md` and `bundles/GATE-ORACLE-ISOLATION/REPORT-ORACLE-ISOLATION.md`.

---

## 1. The internal review

`review/code-review.md` reviewed tag `review-rc2` (`bbecf2d`) across the four security-critical
paths: the batch runner's containment, the deny hook, the authenticating proxy, and the oracle
invariant with its verification sandbox. **43 findings**, of which the strongest cluster was the
oracle — including one **CRITICAL** against the governing invariant itself.

## 2. The external panel

Four models, **one per distinct non-Anthropic lineage** (google, openai, deepseek, z-ai), each
given the same packet and asked explicitly for *disagreement grounded in the source*, not
corroboration. ZDR was checked two ways and enforced router-side on every call. Total spend
$8.82. Method, roster and per-model accounting: `review/PANEL.md`.

**The panel's most useful output was not a new finding. It was that all four independently said
our own remediation order was wrong** — two of them calling its top item unimplementable as
written. They were right: the proposed `--ro-bind` fix would have broken the verifier's only
output channel, and the fix gate measured exactly that failure (`ruff` exit 2 on a read-only cwd)
when it tried.

**One inter-panel conflict was settled on evidence rather than averaged.** google refuted a
finding about tasks resting in `REPAIRING`/`ESCALATING` without consulting the code; z-ai proved
it from `worker.py`; the box confirmed z-ai independently from `store.py`. **google was wrong.**
Recorded because it is the argument for a panel over a single reviewer, and against averaging one.

## 3. The two fix gates

**`GATE-FIX` (2026-08-31)** landed F-1 (partially), F-2, F-3, F-4, F-5, F-7, F-8 and L1 — one
commit each, each with its test. Highlights: `bin/gate13-measure`'s `pkill -f` was aimed at a
model server and matched the **resident inference service** (hazard proven live at fix time); a
task resting in `REPAIRING`/`ESCALATING` is now refused rather than silently acked; the runner's
push path now runs the secret scan from **outside** the gate child and halts on "could not run"
as well as on "found"; and `oracle.stage_candidate`'s unvalidated `task_id` — which fed a path
straight into `sudo -n rm -rf` — is validated by a rule that now lives once in code.

**`GATE-ORACLE-ISOLATION` (2026-08-31)** was dispatched to close the oracle's remaining face and
**honestly failed to**, which is the more valuable result. See §4.

## 4. The oracle invariant — the one thing worth understanding before you review anything else

The governing invariant is **`COMPLETED ⟹ the oracle passed`**. The threat model explicitly
includes adversarial or prompt-injected candidate code executing inside the verification sandbox.
The invariant has three attack faces:

| Face | What it is | Status |
|---|---|---|
| **A** | Candidate hijacks the oracle's **import namespace** | **CLOSED**, fixture-proven |
| **C** | Candidate replaces the oracle's **decision code** | **CLOSED**, fixture-proven |
| **B** | Candidate **forges its own in-process verdict** | **OPEN — detected, not prevented** |

**The honest statement of the invariant, and the one to quote:**

> `COMPLETED ⟹ the oracle passed` holds against escape and persistence (Faces A, C) but **NOT**
> against an adversarial candidate forging its own in-process verdict (Face B).

**Do not propose a uid boundary for Face B.** It was tried and measured unavailable at three
independent layers — the shipped sandbox has a single-id uid map and zero capabilities
(`setresuid` → EINVAL); a nested `bwrap` is refused by the **pinned seccomp filter**, which
filters `CLONE_NEWUSER` *by argument* and is a load-bearing control that must not be weakened;
and even a rebuilt sandbox with a range-mapped userns **and full capabilities** is denied by host
AppArmor `unpriv_bwrap` (`capname="setuid"` in the kernel audit log), with a no-bwrap control
proving the map and privilege are themselves fine.

**And a uid would not have sufficed even if available.** The oracle's assertions execute *inside
the pytest process*, and pytest is where candidate code runs — **the forger IS the reporter** and
shares whatever uid it holds. Committed proof: fixture `exit0c` hard-codes no path (it reads
`COVERAGE_FILE` and pytest's own `--json-report-file` off the live process) and still reaches
PASS, so **no relocation-based fix can be mistaken for closure**.

**Blast radius, adjudicated:** Face B is contained by the network-less, capability-dropped,
disposable sandbox to **one tool falsely stamped `COMPLETED`** — never escape, never persistence.
A forged verdict is a lie about one artifact, not a foothold.

**Compensating control, in force now:** a `COMPLETED` artifact is **PROVISIONALLY verified** and
must be **re-verified out-of-band** before it is trusted or shipped.

**The real fix, and its real cost:** candidate tests must run **out of the reporting process**.
That closes Face B — and it **eliminates `py.cov.threshold` entirely**, because in-process
coverage measures the process it runs inside, so moving the candidate out leaves the metric with
nothing to name. The oracle can have a coverage threshold *or* an unforgeable verdict, **not both
in one process**. That trade is an open operator/ferry decision, not a settled plan.

## 5. What is genuinely still open — the short list

These are the live items. **A finding here is worth reporting; a finding in §1–4 is not.**

1. **Face B itself** (above) — the redesign is unchosen.
2. **A quiet network attempt by candidate code is never classified as a security finding.** The
   detection is a substring scrape over candidate-influenced stderr, so a candidate that reaches
   the network without printing anything recognisable is never classified at all.
3. **Convention-not-control:** the STOP-33b closed set is prefix-matched, and on the escalation
   path the provenance string is supplied by the very code it audits.
4. **`oracle.staged()` is the third instance of a glob defect** thirty lines below a docstring
   forbidding it.
5. **The pre-call cost bound is unsound for reasoning models** — measured: one model bounded at
   $0.94 cost $7.35, 8× over, because `reasoning.mode: pro` re-bills the prompt across internal
   passes and `max_tokens` does not cap completion billing. A bound that under-reads by 8× is not
   a bound, and it guards the one path that spends real money.
6. **Two `pgrep -f` instances remain in `bin/`** — the class that matches the checking process's
   own command line.
7. **The gate child is not network-isolated**: it launches under a `systemd-run --user --scope`,
   and a scope cannot take `PrivateNetwork`.
8. **The permission allowlist is of unsettled status** — measured fact: `Bash(python3:*)` escapes
   the `--add-dir` workspace boundary with zero denials, because the path lives inside the
   interpreter's `-c` program text where the permission layer never sees it. Whether the allowlist
   is a *security boundary* or a *convenience layer* over the real fences (kernel scope, AppArmor,
   private `$HOME`, and a box with passwordless root) is a design-intent question the operator has
   not yet ruled on.

**One standing fact that bounds every containment claim above:** `sudo -n -l` reports
`(ALL) NOPASSWD: ALL` for the executing user, and gate children inherit it. The permission
allowlist and the systemd scope are the only fences between a gate child and root. There is no
second, credential-shaped one.

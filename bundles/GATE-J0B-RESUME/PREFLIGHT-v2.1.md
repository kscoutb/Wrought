# GATE-J0B-RESUME v2.1 — ATTENDED PRE-FLIGHT

**2026-08-28T21:34:20Z · forge-mini · attended, operator present.**
Raw captures: `bundles/GATE-J0B-RESUME/preflight-v2.1-raw/`. The v2.0 pre-flight that produced
the four blockers this version fixes is `PREFLIGHT.md` beside this file.

## VERDICT

**The batch is RUNNABLE.** All four v2.0 blockers are confirmed fixed, both box pre-flight edits
are applied and verified, and one NEW blocker (B-6) was found and resolved by the box within its
own authority. **Two things are outstanding and both belong to the operator**: launching the
proxy, and setting the QUEUE row `APPROVED`. Nothing else stands between here and the batch.

One finding is larger than this gate and is flagged for a ruling rather than acted on: **the
`--add-dir` workspace boundary does not apply to a bare `Bash` allowlist entry**, which is the
entry every gate so far has declared, including this one.

## The four v2.0 blockers — all CONFIRMED FIXED

| | v2.0 defect | v2.1 | Verified how |
|---|---|---|---|
| **B-1** | header `ADD-DIR:` vs regex `^ADD-DIRS:` — silently ignored | `ADD-DIRS:` | Parsed the archived v2.1 with the runner's own loaded regexes: `add_dirs = ['/home/kalib/courier/Wrought', '/var/lib/wrought/j0b']`. The workdir is reachable. |
| **B-2** | booted egress-LOCKED, then installed Goose from GitHub | two-boot shape restored (OPEN → install → poweroff → LOCKED) | Phase A steps 2–3 now match J0B's measured timestamps (raw/20→21→22→24→30). |
| **B-3** | "the pinned Goose release", but no pin existed | values carried in-prompt | Ratified into `pins.lock` as `virtualization.guest_agent_surface`; every value transcribed from committed J0B evidence with its command (J-95). |
| **B-4** | named `authproxy.py`, the proxy that failed this exact test | `authproxy2.py` | Pre-step 3 now names v2. The file already on the box is byte-identical to the courier copy (`ea2974ce…d99e`), so the `cp` is a no-op — harmless, and it means the operator cannot get the wrong one. |
| **R-1** | dead-man 3600 < runtime_max_sec 5400, silently winning, and it LATCHES | raise to 6000 | Applied. `load_config` on the installed file reports 6000 vs 5400; ordering assert passes. RuntimeMaxSec is the ceiling again. |

## NEW — B-6, and it would have halted the runner before the child ever launched

`bin/wrought-runner` resolves a prompt as `prompts/<GATE>.md`, and **only if that is absent**
globs `<GATE>-v*.md` and requires **exactly one** match. `prompts/GATE-J0B-RESUME-v2.0.md`
already exists. Archiving v2.1 under the same convention makes two candidates and raises
`Halt("prompt-missing")` — whose reason string reads *missing* when the real condition is
*ambiguous*, so the batch would have looked like a runner defect.

**Resolved by the box, within rails §8**, which requires the prompt be archived *verbatim* to
`prompts/` but does not fix the filename: v2.1 is archived as **`prompts/GATE-J0B-RESUME.md`**,
the runner's own exact-name first choice, which short-circuits before the glob. Content is
verbatim (sha256 `88897e44…beb9d`); `-v2.0.md` was not moved, renamed or edited, so the QUEUE
row's reference to it stays valid. Re-checked: exact-name hit, glob never consulted, no halt.

**Carried forward so it does not become a trap:** a future v2.2 **must overwrite**
`prompts/GATE-J0B-RESUME.md`, not merely add a `-v2.2.md` — otherwise the runner silently
re-runs this version.

## NEW — a SAFETY FINDING that outranks this gate: the workspace boundary is CONDITIONAL

v2.1's `ADD-DIRS:` names only `/var/lib/wrought/j0b`. But every command in the proven Phase-A
shape also names **`/var/lib/wrought/j0a`** — `user-data` for `cloud-localds`, the base image
for the hash re-verify and as the overlay's backing file, and **`j0a_key` for every in-guest
`ssh`**. Under the ESTABLISHED FACT in `docs/PHASE-J-STATE.md` — *"A Bash call targeting a path
OUTSIDE the session cwd is denied under `dontAsk` even when explicitly allowlisted"* — that is a
total blocker on Phase A, the same shape as B-1.

**The box measured it instead of reporting it on the strength of that sentence.** The prior
measurements (`runner/raw/14`, `runner-arm/raw/31`) both used `--allowedTools "Bash(touch:*)"`
and a **write**. This gate declares **bare `Bash`**. That cell had never been tested. A 2×2 with
one variable — the allowlist spelling — settles it (`preflight-v2.1-raw/10`):

| Arm | allowedTools | operation | `--add-dir` | denials | ground truth |
|---|---|---|---|---|---|
| **A** | `Read, Edit, Write, Bash` | **read** outside cwd | none | `[]` | correct sha256 returned |
| **B** | `Read, Edit, Write, Bash` | **write** outside cwd | none | `[]` | **canary PRESENT on disk** |
| **C** | `Bash(touch:*)` | **write** outside cwd | none | `['Bash']` | canary ABSENT |

**The boundary is enforced for a SCOPED Bash rule and is NOT enforced for a bare `Bash` entry.**

*Consequence for tonight — good:* the missing `j0a` is **not** a blocker. No prompt edit, no
config widening. The batch runs as dispatched.

*Consequence for the project — a real hole:* three documents state the boundary unconditionally —
`docs/PHASE-J-STATE.md`'s ESTABLISHED FACTS, the VERDICT of `build-evidence/runner-arm/raw/31`,
and `/etc/wrought/runner.conf`'s `_add_dirs_note`. All three generalize a scoped-rule
measurement to every allowlist, and **every gate dispatched so far declares bare `Bash`** — so the
workspace boundary has never once constrained a real gate child's Bash on this box. raw/31's
"CORROBORATION FROM A REAL GATE" does not corroborate: with bare `Bash` that bundle write would
have succeeded without `add_dirs` naming the courier.

Stated plainly and **not repaired here**: together with the recorded fact that `kalib` has
`NOPASSWD: ALL` and gate children inherit it, the real fences around a bare-`Bash` gate child are
the systemd scope, the PreToolUse hook's six-pattern denylist, and the reaper. **The workspace
boundary is not among them.** The fix is a ruling — either require scoped Bash rules in
`ALLOWED-TOOLS:` headers, or correct the three documents to say the boundary is conditional. The
box took neither on its own judgement, and did not weaken or widen anything to make tonight work.

## Applied, verified

- **`pins.lock`** — `virtualization.guest_agent_surface` added beside `guest_base_image`. Tag
  `v1.46.0`, asset sha256 `a1cf4856…5a7b`, installed-binary sha256 `29b3340e…4a89`, marked
  **SELECTED-not-adopted**, **GUEST-ONLY**, **signature NONE-PUBLISHED-UPSTREAM**. YAML still
  parses (30 top-level keys). The key *name* is a structural choice by the box and is flagged as
  such; every *value* came from the prompt or from committed evidence.
- **`/etc/wrought/runner.conf`** — `deadman_no_progress_sec` 3600 → 6000, plus a provenance
  note. **Mechanical leaf-diff: exactly one value changed.** Needed root; the box used its own
  passwordless sudo and says so, departing from GATE-RUNNER-ARM's route-it-through-the-operator
  precedent because v2.1 assigns this edit to the box explicitly and the session is attended.
- **Queue** — `parse_queue()` on the real `QUEUE.md`: **OK, 8 rows, no breaker.** Runnable set is
  currently **empty**, which is correct: the row is still `QUEUED`.
- **§10** — the GATE-RUNNER-ARM adjudication was **already recorded** (2026-08-28T19:51:51Z,
  extracted mechanically from the v2.0 prompt) and the row is already `ADJUDICATED`. Not
  re-recorded: re-extracting the same verdict from a re-worded carrier would replace a mechanical
  extraction with a paraphrase.
- **Environment checked**: base image sha256 **matches its pin exactly**; `cloud-localds`,
  `qemu-img`, `qemu-system-x86_64`, `tmux` present; `kalib` in `kvm(991)`; `/dev/kvm` present;
  **8081 and 2222 free**; `wrought-inference.service` **active** with 8080 listening (the proxy's
  upstream); 1.7 TB free.
- **Byte freeze** — baseline and re-assert both captured; **HELD**, no gate ran.

## OUTSTANDING — both the operator's

1. **Launch the corrected proxy** (prompt pre-step 3, the one privileged action; the key reaches
   it on **stdin** and never enters argv, env, a file or the guest). Launch it **before** the
   runner starts — the reaper snapshots listening sockets per gate, so a proxy that predates the
   run is in the *before* set and is correctly not seen as residue.
2. **Set the QUEUE row `APPROVED`.** Rails §12.1 assigns this to advisor **and** operator, and
   the v2.0 pre-flight explicitly refused to set it alone. v2.1 supplies the advisor half in
   writing; the operator's word is the other half, and the box is waiting for it rather than
   reading an instruction in a prompt as both halves.

## NOT ESTABLISHED by this pre-flight

- Whether the batch fits in `runtime_max_sec` 5400 s. J0B did Phases 0–4 in ~18 min; this gate
  adds three phases, two boots, an 85 MB in-guest download and a full bundle. Untested. If it
  overruns, the child is killed at the deadline (rc −15) and the gate FAILs **without** latching
  (`max_consecutive_failures` is 2), and the guest dies with the scope.
- **Cost.** No `MAX-BUDGET-USD:` header, so the config's `.00` applies — against a measured
  overshoot of 6.94× and 4.6× (two samples, not a trend), implying a worst case near **$55**.
- `apicalls.log` **already holds 19 lines** from J0B. Phase 5 counts model calls; the count must
  be taken as a **delta**, not a total. Not pre-truncated — it is prior evidence (rails §4).
- The reaper's `virsh destroy` branch stays unexercised (this gate uses plain `qemu-system` by
  design), and `terminate_grace_sec` stays unmeasured.

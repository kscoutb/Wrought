# REPORT-RUNNER — GATE-RUNNER, forge-mini, 2026-08-21 (ATTENDED)

**Gate:** GATE-RUNNER v1.0 — build the day-long autonomous batch runner.
**Executor:** Claude Code (Opus 5, ultracode) on forge-mini. **Advisor:** Fable. **Operator:** attended.
**Deliverable:** `bin/wrought-runner` + three companion scripts + `/etc/wrought/runner.conf`,
proven by a dry run against a throwaway courier and a scratch database.

**Byte freeze on `/var/lib/wrought/state/orchestrator.db{,-wal,-shm}` HELD for the whole session**
— `raw/00` baseline, `raw/99` re-assert, `raw/99b` mechanical verdict. No dry run ever opened the
real store; every scenario pointed `freeze_paths` at a scratch trio, which is the reason the
runner takes its paths from config instead of hard-coding them.

---

## 0. Three things surfaced before any work, and not guessed at

1. **This prompt arrived as chat text, not as a file.** `docs/EXECUTOR-RAILS.md` §7 requires
   prompts to travel as files. The content was intact — it was archived verbatim to
   `prompts/GATE-RUNNER-v1.0.md` and the mandated transport check found **exactly three indented
   blocks, none empty, none garbled** (`raw/01`, mechanical block count). The prompt's own STOP
   condition is "if any block is empty or garbled", which was not the case, so the session
   proceeded. **The medium deviation is reported, not absorbed.**
2. **The `PRIOR-ADJUDICATION — GATE-HJ2` block carries no verdict text**, and `GATE-HJ2-HEARTBEAT`
   is `NOT RUN` in the courier with no `bundles/GATE-HJ2*/` directory. There is nothing to record
   and **no verdict was invented.** HJ2's own leftover steps (the rails/README rule text, the HJ1
   `ADJUDICATION.md` write, journal J-158) remain outstanding and outside this gate's scope.
3. **`GATE-J0B-SURFACE` has been `RUNNING` since 2026-08-20 with no bundle** and
   `docs/PHASE-J-STATE.md` was never updated by it. Surfaced — and folded into the design: the
   runner now **refuses** any gate whose row is already `RUNNING` or `BUNDLED`, naming J0B in the
   refusal message as the case that motivated it.

---

## 1. Phase 1 — the RT0 verifications. Which of (a)–(d) hold on THIS build

Measured against **claude 2.1.238**, in an empty scratch cwd with no `.claude/` and no CLAUDE.md,
with this session's `CLAUDE_CODE_*` variables scrubbed. Ground truth is always a file on disk or a
field in the result JSON — never the model's account of itself.

| | Claim | Verdict | Evidence |
|---|---|---|---|
| **(a)** | A fresh non-interactive run clears context | **HOLDS** | `raw/04` |
| **(b)** | `--permission-mode` default-deny blocks an un-allowlisted Bash call | **HOLDS, WITH A CORRECTION THAT MATTERS** | `raw/06` |
| **(c)** | PreToolUse hooks do NOT fire under `claude -p` (RT0 pass-2) | **REFUTED — they DO fire** | `raw/07` |
| **(d)** | The token/output caps and bash-timeout env vars take effect | **HOLDS, WITH TWO LIMITS** | `raw/08` |

### (a) HOLDS — and there is a corollary the claim does not cover

Two `claude -p` invocations in the same cwd, no `--continue`, no `--resume`: distinct
`session_id`s, and the second answered `NONE` when asked for a token planted in the first. Fresh
invocation = cleared history, as assumed.

**The corollary (`raw/05`): "fresh context" is not absolute.** Claude Code maintains a
**per-project auto-memory directory** that is loaded into every later invocation in that cwd — the
foundry project already has a populated one. Nothing in the two-invocation test touches it, so the
test can pass while a real cross-gate channel stays wide open. The runner therefore **fences it**
(§4). Session persistence is left **ON** deliberately: it is the only forensic record if a gate
dies mid-run, and `--no-session-persistence` would trade that away for nothing, since fresh
context is already guaranteed by not passing `-c`/`-r`.

### (b) HOLDS — but three corrections, and one is a trap

1. **There is no permission mode literally named "default-deny".** 2.1.238 offers exactly
   `acceptEdits`, `auto`, `bypassPermissions`, `manual`, `dontAsk`, `plan`. The prompt's
   `<default-deny-mode>` placeholder had to be resolved by measurement.
2. **`dontAsk` and `manual` are default-deny-with-allowlist.** Both refused an un-allowlisted Bash
   call and both honoured an allowlist when given one, down to the granular `Bash(touch:*)` form;
   a granular entry that does not cover the command (`Bash(git *)` against a `touch`) correctly
   refused. **The runner uses `dontAsk`** and refuses to start in any other mode.
3. **THE TRAP: `acceptEdits` and `auto` BOTH RAN the un-allowlisted Bash command.** Under those
   two modes `--allowedTools` is not a containment boundary at all. A runner built on the
   reasonable-sounding assumption that a mode called "acceptEdits" only accepts edits would have
   had no containment whatsoever, and nothing in the output would have said so.

Also measured: `--tools Read` (removing Bash from the built-in set) blocks it even under
`acceptEdits` — a stronger boundary, independent of permission mode; and `--disallowedTools` beats
`--allowedTools`, i.e. deny wins over allow.

**And the classification fact the whole runner rests on: every case exited `rc=0`, including
every denial.** The child's exit status does not distinguish "did the work" from "was refused".
This is the same shape as the project's own rule that bwrap-proxied exit integers are ambiguous
(`CLAUDE.md`, `docs/03` §10.7) — arrived at here for an entirely unrelated reason.

### (c) REFUTED — hooks DO fire, and the way they fail is worse than not firing

A PreToolUse hook installed via `--settings` fired twice (the model retried; the hook denied both)
and its `deny` was **enforced** even though `--allowedTools` would have permitted the exact
command. Hooks also fire from a project `.claude/settings.json`. The payload carries `session_id`,
`cwd`, `permission_mode`, `tool_name` and the full `tool_input` — enough for a real policy hook.

**But a malformed settings file is SILENTLY ignored under `-p`.** `rc=0`, **empty stderr**, no
warning anywhere — and the Bash call ran. A *missing* file is a hard `rc=1` error. **Absence is
loud; corruption is silent.** One stray character in the runner's hook settings would delete the
entire hook layer with no signal. So: the runner `json.load`s its own hook settings **before every
single launch** and refuses to start if they do not parse, and **hooks are defence-in-depth only,
never the boundary.**

*(The `--bare` arm of this test is not evidence about hooks: it exited `rc=1` with
`terminal_reason: "api_error"` and zero tokens, because `--bare` reads Anthropic auth only from
`ANTHROPIC_API_KEY`/`apiKeyHelper` and never from the OAuth credentials this box uses. It died
before any tool call. The help text says `--bare` skips hooks; that documentation, not this run,
is the basis for not load-bearing on them.)*

### (d) HOLDS — with two limits that change the design

- `CLAUDE_CODE_MAX_OUTPUT_TOKENS` takes effect and fails loudly and machine-readably.
- `BASH_DEFAULT_TIMEOUT_MS` takes effect (4 s observed against the 120000 ms default) — **but it
  does not kill anything.** It *backgrounds* the overrunning command, which keeps running. As a
  containment control it bounds only how long the model waits. **A runaway can only be stopped by
  the kernel.**
- `--max-budget-usd` takes effect with the cleanest signature of the three
  (`subtype='error_max_budget_usd'`, `terminal_reason='budget_exhausted'`) — but it is a **soft
  ceiling**: a run capped at `$0.01` spent `$0.0460925`, a **4.6× overshoot**, because the check
  happens between turns and a turn in flight is already paid for.

**Containment conclusion.** Hooks work, so they are used — but the load-bearing layers are the
**kernel scope**, the **`dontAsk` mode with a per-gate allowlist**, and the **env allowlist**. Not
because hooks failed, but because their failure mode is silent and the harness timeout does not kill.

---

## 2. The runner as built

Four scripts in the repo's `bin/`, matching the convention every other gate script follows.
Creating `/opt/wrought/runner/` would have invented a tree; installing to `/opt/wrought/bin` is an
operator step, not this gate's.

| Path | What it is |
|---|---|
| `bin/wrought-runner` | the harness: queue → gate → verify → breakers → pace → status |
| `bin/wrought-runner-hook` | PreToolUse hook. **Deny-or-defer only** — it can narrow a gate's surface, never widen it |
| `bin/wrought-course-check` | outer course-check wrapper: summary on stdin, one token on stdout |
| `bin/wrought-course-post` | the single POST. **Sealed key on stdin only** |
| `/etc/wrought/runner.conf` | strict JSON. **Never sourced.** Every threshold `PROPOSED-UNRATIFIED` |
| `/etc/wrought/runner-hooks.json` | the settings file that installs the hook; validated per launch |

**Python 3 stdlib, not shell.** Phase 1 proved the run must be classified on the result JSON, and
shell cannot do that honestly. The shebang is `#!/usr/bin/env python3` rather than the repo's usual
`/opt/wrought/venv-orch/bin/python`: the runner supervises gates, a gate may legitimately rebuild
that venv, and a supervisor must not depend on the thing it supervises.

### The invocation

    systemd-run --user --scope --quiet --unit=<per-gate unit> \
      -p MemoryMax=<cap> -p MemorySwapMax=0 -p RuntimeMaxSec=<deadline> \
      claude -p "<prompt>" --setting-sources '' --settings /etc/wrought/runner-hooks.json \
        --permission-mode dontAsk --allowedTools "<the gate's own declaration>" \
        --add-dir <minimal> --output-format json --max-budget-usd <cap>   </dev/null

with `CLAUDE_CODE_MAX_OUTPUT_TOKENS` and `BASH_DEFAULT_TIMEOUT_MS` set, in an environment built
from an **allowlist**, in a cwd from config. `--dangerously-skip-permissions` appears nowhere.

Two elements are **not** in the prompt's proposed invocation and are there because measurement put
them there — `MemorySwapMax=0` and `--add-dir` (§5).

**The env is an allowlist, not a blacklist**, for two reasons. A blacklist rots the next time the
CLI adds a variable; and an interactive Claude Code session exports
`CLAUDE_CODE_MESSAGING_SOCKET`/`_TOKEN`, the cross-session steering channel. *(Not inheriting them
turned out to be necessary but not sufficient — see §7.)*

### The verdict is mechanical

The child's own account of itself is **evidence, never proof**. `PASS` requires all of:

- the gate's QUEUE row moved to `BUNDLED`, **and**
- `bundles/<gate>/` exists and is non-empty, **and**
- `sha256sum -c SHA256SUMS` verifies inside it, **and**
- the byte freeze held, **and**
- the child's own disposition was `COMPLETED`.

This is not theoretical: in dry run 1, `GATE-DRYRUN-B` reported `is_error=false`,
`terminal_reason='completed'` — and had produced no manifest and left its own queue row at
`RUNNING`. The mechanical check caught it. A runner that trusted the child would have passed it.

Child dispositions: `COMPLETED`, `ERROR`, `BUDGET`, `RETRYABLE` (API 429/529 → bounded exponential
backoff, then halt), and `SUBSTRATE` — no parseable result JSON, meaning a scope kill, an OOM, or
a crash, with the measured signatures `rc=143` (SIGTERM, RuntimeMaxSec) and `rc=137` (SIGKILL,
memory) named in the detail.

---

## 3. Circuit breakers — and a defect in my own first version

All default to halt-and-wait.

| Breaker | Trips on | Latches? | Proven |
|---|---|---|---|
| byte-freeze tripwire | any change to a frozen path | **yes** | `raw/22` |
| consecutive failures | N non-PASS gates in a row | **yes** | `raw/23` |
| course-check | anything that is not an exact `OK` | **yes** | `raw/24`, `raw/17` |
| dead-man | no runner progress for T | **yes** | `raw/28` (2nd attempt; see §5) |
| stale/ambiguous queue row | row already RUNNING/BUNDLED; duplicate rows; unknown status | **yes** | refusal paths |
| missing `ALLOWED-TOOLS:` | a gate that declares no tool surface | **yes** | refusal paths |
| per-gate kernel limits | `RuntimeMaxSec` / `MemoryMax`+`MemorySwapMax` | via SUBSTRATE | `raw/10`, `raw/11`, `raw/25` |
| gate-count cap | K gates this run | **NO — by design** | — |
| wall-clock budget | ~20 h this run | **NO — by design** | — |

**The defect, found in review and fixed before it shipped.** My first version latched the breaker
on *every* halt, including the gate-count cap and the wall-clock budget. Those two are not faults —
the prompt is explicit that they mean "stop, wait for the daily ferry", while only the
consecutive-failure ledger means "disable further runs, require operator reset". As originally
written, **a batch that simply finished its own quota would have poisoned the next morning's manual
start**, and the operator's day-2 run would have refused with "BREAKER IS LATCHED" on a run that
ended perfectly normally. Now only real faults latch; a cap returns exit 4 and leaves the breaker
clean.

Exit codes: `0` clean, `2` latched breaker, `3` refused because already latched, `4` bounded by
its own cap.

---

## 4. The auto-memory fence — fail-soft, and deliberately so

`raw/05` established that per-project auto-memory is a live cross-invocation channel. The runner
snapshots the directory before each gate and compares after. If it changed, it **copies the delta
aside as evidence, restores the pre-gate state, and records it in the run log — it does not halt**
(`raw/27`).

That is a judgement call, and it is stated rather than assumed. Gates receive memory instructions
from the harness itself, so benign writes will happen; halting a 20-hour batch over a stray note
would be a false positive. Silently leaving it in place would make "fresh context per gate" false.
Copying-then-restoring keeps the claim true and keeps the evidence, which also satisfies
EXECUTOR-RAILS §4's never-overwrite-evidence rule.

---

## 5. The dry run — and the three defects it found

Everything ran against a **local bare git repo standing in for the courier** and a **scratch
`orchestrator.db` trio**. Throwaway bundles never entered the public courier's permanent history,
and the real database was never opened.

| # | Scenario | Result | Evidence |
|---|---|---|---|
| 1 | happy path, two gates | A **PASS**; B **FAIL** (correctly) | `raw/20` |
| 2 | B re-run after the `--add-dir` fix | **PASS** in 41 s | `raw/21` |
| 3 | byte-freeze tripwire | **HALT**, named the exact hash transition, latched, exit 2 | `raw/22` |
| 4 | consecutive-failure breaker | counted to 2, latched; restart **refused**, exit 3 | `raw/23` |
| 5 | stubbed course-check HALT | gate PASSED, then the check **stopped the runner** | `raw/24` |
| 6 | real `claude` child vs `RuntimeMaxSec=30` | killed at **30.3 s**, `rc=143`, 0 bytes, **SUBSTRATE** | `raw/25` |
| 7 | dead-man | **first attempt did not fire** (gate finished in 48 s, inside its 60 s timeout — that run proves nothing and is kept); re-run at 20 s **tripped at 29 s idle**, killed the scope, halted, latched | `raw/28` |

Pacing is exact: gate A ended `02:15:46`, gate B launched `02:16:31` — 45 s, the configured value.

### The three defects, each found by measurement, none by inspection

**(i) `MemoryMax` alone does not cap memory on this box.** Under `-p MemoryMax=256M`, a process
allocating 1 GiB **succeeded and exited 0 in one second**. `memory.max` *was* applied correctly
(268435456) — but `memory.swap.max` defaulted to `max`, so the overrun was paid out of the host's
8 GiB swap file. With `-p MemorySwapMax=0` the identical allocation is OOM-killed immediately
(`rc=137`). **The GATE-RUNNER prompt's own proposed invocation specifies `MemoryMax` without
`MemorySwapMax`.** On this box that combination is not a memory cap, and nothing would have said
so — a memory-runaway gate would have quietly thrashed swap and reported success. (`raw/10`, `raw/11`)

**(ii) A Bash call targeting a path outside the session's cwd is denied under `dontAsk`, even when
explicitly allowlisted.** `GATE-DRYRUN-B` failed reporting "Bash is fully blocked" with an
allowlist that plainly permitted the commands it was refused. Three hypotheses were tested and
two were **refuted before the right one was found**: the `Bash(cmd:*)` versus `Bash(cmd *)`
spelling (both work in isolation, `raw/12`), and an inner space inside `Bash(git *)` corrupting the
space-separated list (it does not, `raw/13`). A 2×2 over {hook present/absent} × {target
inside/outside cwd} isolated it cleanly: **the hook is irrelevant; the workspace boundary is the
discriminator** (`raw/14`). Fixed with a **minimal, explicit, per-gate `--add-dir`** — which widens
the surface, so it is config-driven, logged per gate, and kept as small as possible.

**(iii) My own breaker latched on non-faults.** §3 above.

A fourth, smaller one: the evidence writer redacted the prompt at `cmd.index("-p")`, which finds
`systemd-run`'s `-p`, not `claude`'s — producing a misleading `child-cmd.txt`. Fixed. Evidence that
misrepresents the command that produced it is exactly what J-95 exists to prevent.

---

## 6. The course-check — design, and the ratification it needs

Between gates the runner compiles a compact summary and asks a cloud reviewer **one** question.
The summary is exactly what the prompt specified; here is a real one, from `raw/24`:

    gate=GATE-DRYRUN-I
    verdict=PASS
    queue_status=BUNDLED
    byte_freeze=HOLD — no change to any frozen path
    next_queued=(none)
    gates_this_run=1/6

**`OK` is not approval to proceed.** It means only "no alarm raised"; forward progress is already
gated by the `APPROVED` state the advisor and operator set at the daily ferry. Measured across the
response space (`raw/17`): only an exact `OK` continues — `HALT`, an unparseable sentence, a
non-zero exit, and a missing command **all stop the runner**. Every fail-closed edge of the two
scripts prints `HALT` and exits non-zero (`raw/15`).

**Secret handling.** The key never touches the runner. `wrought-course-check` writes the
(non-secret) summary to a `0600` file and hands the credential work to systemd, which materialises
the sealed key in `$CREDENTIALS_DIRECTORY`; a one-line `cat` pipes it into `wrought-course-post`
**on stdin**. Never in argv, never in an environment variable, never in a file this code writes,
never in the repo — reconciling EXECUTOR-RAILS §5 with the project's existing sealed-credential
mechanism.

**It deliberately does NOT reuse `bin/escalate-once`.** That path calls
`wrought_escalation.escalate()`, which writes the escalation ledger — and the ledger lives inside
`orchestrator.db`, the very file the runner byte-freezes for the whole batch. **Reusing the
production escalation path would have made the runner trip its own tripwire on the first enabled
course-check.** This is a separate stdlib-only path with its own spend log outside the database.

### ⚑ RATIFICATION NEEDED — three items, none of them mine to decide

1. **Pointing the sealed escalation credential at a new purpose.** It is pinned for §13 escalation.
   Using it for a supervisory course-check is a new use. **`course_check.enabled` ships `false`.**
2. **The enabled path needs passwordless `sudo`** for `systemd-run -p LoadCredentialEncrypted=…`.
   That is a real privilege dependency on the autonomous path and is disclosed, not buried.
3. **The prompt's "$50 prepaid backstop" is not the binding number.** `pins.lock` already records
   `provider_side_key_limit_usd: 50`, `provider_side_account_balance_usd: 26.17`, and
   `provider_side_backstop_usd: 26.17` — the effective ceiling is the **minimum** of the two,
   measured 2026-08-03. Further: **the gate children do not spend that credential at all.**
   `claude -p` runs on the box's Claude Code subscription auth; the OpenRouter credential is
   touched only by the course-check. They are two separate budgets and the runner keeps two
   separate caps and two separate ledgers. The shipped course-check cap is `$5.00`.

---

## 7. OTHER SURPRISES

1. **A gate child is discoverable and addressable by any other local Claude Code session, and no
   configuration found this session closes it.** Scrubbing `CLAUDE_CODE_MESSAGING_SOCKET`/`_TOKEN`
   does not: the child is listed by name within seconds anyway. A **private `XDG_RUNTIME_DIR`
   does not either** — the private directory was left completely empty, no socket was created in
   it, and the child was still listed. Discovery is keyed under `$HOME`
   (`~/.claude/daemon/roster.json`), and a private `$HOME` is unavailable because the Claude Code
   credentials live there. **No message content was ever observed to reach a `-p` child** — the
   clean probe ran 7 tool rounds, was explicitly asked to report any out-of-band instruction, and
   answered `NONE`. **The Phase-3 breaker as written is NOT satisfied.** (`raw/16`)

   > **CORRECTION, `raw/18`, received after this bundle was first pushed.** Asynchronous platform
   > notices arrived reporting the fate of all three probe messages: each was **held for the
   > recipient user's approval** and then **not approved before expiry — not delivered.** Two
   > things follow, one better than stated above and one worse.
   > **Better:** the messages were not ignored by the children, they never reached them. Delivery
   > is gated on a human approval that a headless `claude -p` child cannot give, so the path is
   > fail-closed *by construction* rather than by the child happening not to read an inbox. My
   > explanation above — "an observed property of `-p` mode" — was a reasonable inference from
   > what was visible at the time and is **wrong about the mechanism**.
   > **Worse:** `SendMessage` did not "report delivery success", as I wrote; it reported that the
   > **send was accepted**. That is not the same claim, and it is the same trap this gate keeps
   > finding — an interface's optimistic acknowledgement is not evidence the thing happened.
   > **The requirement is still not satisfied**: that approval gate is a platform behaviour this
   > gate neither configured nor pinned, it could change in any CLI update, the children remain
   > discoverable, and **what an *approved* message does was never tested** — which is the case
   > that actually matters, since the operator is the one person who could approve one and the
   > runner is designed to run while they are away.
2. **The full gate prompt is visible in `ps` output** — it is passed as an argv element. Gate
   prompts are public courier documents so nothing is disclosed, but it is a second, independent
   reason a gate prompt must never carry a secret.
3. **`subtype` reads `'success'` on a hard failure.** The output-token-cap failure returned
   `is_error=true` with `subtype='success'`. `subtype` is not a discriminator; `is_error` and
   `terminal_reason` are.
4. **`output_tokens` read 256 against a cap of 64.** The accounting is not the cap. Treat the
   error as the signal and the number as unreliable.
5. **`--bare` waits 3 seconds on stdin** before proceeding. The runner always redirects
   `</dev/null` so no gate can stall on an inherited stdin.
6. **`Linger=no` for `kalib`, and the compiled `KillUserProcesses` default is `no`** (`raw/09`).
   Consequence for the daily loop: the operator should start the runner **inside tmux**, or enable
   lingering, so a closed SSH session cannot take the batch down. **No system configuration was
   changed** — this is a how-to-run note, not an action taken.
7. **The harness this session runs under blocks foreground `sleep`**, which voided the first
   bash-timeout test entirely. The measurement had to be redone with a non-`sleep` long command.
   Recorded because the first attempt looked like a result and was not.

8. **The pre-commit secret scan earned itself, on my own evidence file.** `raw/03` captured this
   session's environment to document the confounds, and my inline redaction in that capture matched
   only `/KEY/` — so it missed `CLAUDE_CODE_MESSAGING_TOKEN`, a **live capability token for the
   local cross-session messaging socket**, and left it in a file bound for a **public** repository.
   `/opt/wrought/bin/gitleaks protect --staged` caught it **before any commit**, which is exactly
   what ST-7's scan-before-commit rule exists for. The value never left the box. The redaction is
   annotated in `raw/03` itself rather than quietly applied, so the record shows the correction.

---

## 8. WHAT THIS DID NOT ESTABLISH

- **The end-to-end path on the real public courier was never exercised.** Every dry run used a
  local bare repo. Pushes were mechanically proven; pushing *to GitHub* under contention was not.
- **The enabled course-check path never ran.** No credential was read, no `sudo systemd-run`
  invoked, no request left the box, `$0.00` spent against the escalation credential. Only the
  fail-closed edges and stubbed reviewers were exercised.
- **`--bare` and hooks** — the `--bare` arm died on auth before any tool call. Untested.
- **`MemoryMax` against `claude` itself.** The memory cap was proven on synthetic processes. Only
  `RuntimeMaxSec` was proven against a real `claude` child.
- **The steering breaker is not satisfied**, per §7.1. What is measured is weaker than what was
  asked for, and is written up as such rather than dressed up. Specifically **untested, and it is
  the case that matters: what happens if a human APPROVES a cross-session message to a running
  gate child** (`raw/18`). All three probe messages expired unapproved, so the approved path has
  never been exercised.
- **Linger under an actual last-session-exit** was not tested; there are eight live sessions.
- **No gate ever legitimately wrote auto-memory.** The fence's changed-path was proven
  functionally (`raw/27`), not by observing a real gate trip it.
- **No multi-day run.** The longest batch was two gates. The 20-hour wall-clock budget and the
  6-gate cap are **untested at scale** and are `PROPOSED` numbers, not measured ones.
- **The API 429/529 backoff path never fired** — no rate limit was encountered.

---

## 9. How to run it — the daily operating loop

1. Operator: `git -C ~/courier/Wrought pull`.
2. Advisor adjudicates the returned bundles and writes the next batch of prompts.
3. Operator commits those prompts to `prompts/`, **each carrying an `ALLOWED-TOOLS:` header**, and
   marks their QUEUE rows `APPROVED`.
4. Operator starts the runner **inside tmux** (see §7.6):

       tmux new -s runner
       /home/kalib/foundry/bin/wrought-runner            # uses /etc/wrought/runner.conf

   and walks away. Useful flags: `--status` (breaker + ledger), `--reset-breaker` (after a latched
   halt), `--max-gates N`.
5. The runner works the batch — fresh context per gate, kernel-contained, default-deny, paced,
   verified mechanically — and halts at batch end or on any breaker, pushing `STATUS.md` at every
   phase so the advisor is never blind.

**No daemon. No timer.** A timer was deliberately not written, not even disabled: the operator
ruling makes the manual daily start the human gate, and a timer would contradict the adjudicated
design.

---

## 10. Adversarial audit

Run against this report before it shipped. **13 claims challenged; 6 changed the text; 0 claims
survived that the evidence does not support.** Challenge 13 arrived after the bundle was first
pushed and is the reason this report has a second revision.

| # | Challenge | Outcome |
|---|---|---|
| 1 | "Fresh context per gate" — is it true given auto-memory? | **CHANGED.** Claim narrowed; the fence and its fail-soft compromise are stated in §4 rather than the claim being left absolute |
| 2 | Is the containment "kernel-level only", as the prompt anticipated? | **CHANGED.** No — hooks *do* fire (c). The report says so and explains why the kernel is still load-bearing anyway, rather than taking the prompt's easier framing |
| 3 | Does the dry run prove the **real** courier works? | **CHANGED.** Demoted to §8; §5 now says explicitly that only a local bare repo was exercised |
| 4 | Probe 1 (gate B) as steering evidence | **CHANGED.** Marked confounded — the message was in flight around its last tool round and that run failed for an unrelated reason. Only probe 2 is relied on |
| 5 | Is `MemorySwapMax=0` a preference or a requirement? | Held: measured both ways, `rc=0` vs `rc=137` |
| 6 | Is the "4.6× budget overshoot" a real measurement? | Held: `$0.0460925` against a `$0.01` cap, in the result JSON |
| 7 | Does `--add-dir` weaken containment? | Held, and disclosed: it does widen the surface; it is minimal, explicit, config-driven and logged per gate |
| 8 | Is the byte-freeze proof circular (the runner checking itself)? | Held: the tripwire was driven by an **external** dirtier synchronised on the runner's own baseline artifact, and the verdict names both hashes |
| 9 | Is "0 spend on the escalation credential" verifiable? | Held: the spend log does not exist; `wrought-course-post` was only ever exec'd with `pin()` reads and empty stdin |
| 10 | Are the config thresholds invented, against CLAUDE.md's first hard rule? | Held: every one is marked `PROPOSED-UNRATIFIED` in the config's own `_README` and listed in `PROPOSED-PINS-DELTA.md` |
| 11 | Does the report claim the Phase-3 steering breaker works? | Held: §7.1 and §8 both say plainly that it does **not** |
| 13 | Why exactly did no probe message reach a child? | **CHANGED, post-push.** Platform notices (`raw/18`) show all three were held for recipient-user approval and expired undelivered — not ignored by the child. §7.1 carries the correction, including that `SendMessage` reported an accepted *send*, not a delivery |
| 12 | Is the evidence itself free of secrets, given the courier is public? | **CHANGED.** It was not — `raw/03` carried a live messaging token. Caught by the staged-diff scan pre-commit, redacted with the redaction annotated in place, and written up as §7.8 rather than silently fixed |

**The claim this report is least able to support** is that the runner is safe to leave unattended
for twenty hours. It has been proven correct over **two gates and seven scenarios in about twenty
minutes**. Every breaker fires, and the failure modes found so far were found by measuring rather
than by reasoning — which is precisely why the remaining confidence should come from a short
supervised batch before a long unsupervised one, not from this report.

---

## 11. Teardown and evidence

**Byte freeze:** baseline `raw/00`, re-assert `raw/99`, mechanical diff `raw/99b` —
**HELD**, all three hashes plus size and mtime identical across the whole session.

**Enumerated teardown** (EXECUTOR-RAILS §3 — deletes are written out one by one, with reasons; no
`rm -r` over a glob). The dry-run tree `/var/lib/wrought/runner/dry/` was removed only after every
log and verdict artifact this report cites had been copied into `raw/`. Each path and its reason is
recorded in `raw/32-teardown.txt`, together with the `sha256sum` of each dry-run log taken **before**
deletion, so the copies in `raw/` can be checked against what was destroyed.

**Nothing else on the box was changed.** No package installed, no unit created, enabled, started or
stopped, no firewall rule touched, no VM work, no `wrought-*` unit read from beyond `systemctl show`
equivalents. The only writes outside this gate's own workdir are the four scripts in the repo's
`bin/`, the two files in `/etc/wrought/`, and the courier commits.

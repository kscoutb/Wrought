# GATE-RUNNER-POLISH — report

**Gate:** `GATE-RUNNER-POLISH` v1.0, ATTENDED-DIRECT (not through the runner: this gate edits
`bin/wrought-runner` and `docs/EXECUTOR-RAILS.md`, and a gate must not run under the thing it is
changing). **Executor:** Claude Code on forge-mini, Opus. **Advisor:** Fable. **Date:** 2026-08-29.
**Workdir:** `/var/lib/wrought/runner-polish/`. **Journal:** J-165. **Foundry commit:** `e3edee8` (operator-authored; pre-commit secret scan run with the tool this gate built — `raw/64`).

## 0. Verdict in one page

All seven phases completed. **Nine defects fixed, of which four were found by this gate's own
proofs rather than by the prompt**, and one of the prompt's stated premises was measured false and
is reported rather than absorbed.

| Phase | Fix | Proof | Result |
|---|---|---|---|
| 2 | Reaper survivor test: command-line substring → **executable identity** | `raw/11` | **PASS** — 3 decoys matched by the old test, 0 by the new; real guest still reaped |
| 2 | Zombies excluded from the survivor scan | `raw/11` step 8 | **PASS** — closing bracket comes back clean |
| 2 | Listener probe takes **every** owning pid, not the first | `raw/12` §B2 | code + shape argument; no multi-owner socket exists on the box right now |
| 2 | `reap()` refuses to signal pid≤1 / itself / its group / its session | `raw/12b`, `raw/12c` | **PASS**, and proven not to neuter the reaper |
| 3 | The staged-diff secret scan gets a **committed home** | `raw/21`, `raw/22b` | **PASS** — old form leaks into 1 argv, new form 0, both detect |
| 4 | Rails §2 split: the freeze is the **runner's** duty under the runner (F-1) | docs | ruled |
| 4 | Rails §13.3: guest RAM budgets against the **scope** (F-2) | docs | ruled |
| 5 | `NOT RUN` documented in all three places | `raw/…` + docs | done; **premise corrected** |
| 5 | `reset_by` false provenance → measured fields | `raw/31`, `raw/32` | **PASS**, code and live state |
| 6 | Workspace boundary **armed**, both halves | `raw/41` | **PASS** — reaches declared tree, denied outside |
| 7 | `breakers.max_batch_cost_usd`, PROVISIONAL and derived | `raw/53b` | **PASS** — 6/6 computed checks |

**Byte freeze: HOLD.** All three frozen paths byte-identical (`raw/00` vs `raw/99`, diffed
mechanically in `raw/99b`). This is a direct session, so rails §2.1 makes the freeze the box's own
duty — which is exactly the distinction Phase 4 wrote down.

**Cost:** four scratch children, read from their own `verdict.json` files —
**$0.1927 + $0.0801 + $0.0808 + $0.0808 = $0.4345.** The two halt arms (`bare-bash`,
`add-dirs-header`) launched no child and cost nothing.

## 1. Transport — TRANSPORT-OK on content, and a rail miss

Exactly **two** indented blocks, both non-empty and intact (`awk` count, `raw/01`). But the
prompt's own integrity line asserts *"this prompt is a FILE"* and **it did not arrive as one** — it
was pasted chat text, so `prompts/GATE-RUNNER-POLISH-v1.0.md` is a **box transcription**, not an
operator-supplied file (rails §7). Tally: chat text for `GATE-RUNNER`, `GATE-RECONCILE`,
`GATE-RUNNER-HARDEN`, `GATE-RUNNER-ARM`; a FILE for `GATE-J0B-RESUME` (the only one); chat text
again here. **5 misses in 6.** The rail should be enforced or amended; it is not being met.

Second observation, and it is this gate's own subject: **this prompt's `ALLOWED-TOOLS:` header
declares bare `Bash`** — the exact spelling Phase 6 exists to retire. No mechanical consequence
here (nothing parses an attended-direct prompt), but **after this gate the runner will refuse a
prompt spelled that way**, so the next dispatched prompt must scope it.

§10 recording done as the first courier action: `bundles/GATE-J0B-RESUME/ADJUDICATION.md`, extracted
by `sed -n` from the archived prompt, never retyped; QUEUE row → `ADJUDICATED`.

## 2. The reaper (Phase 2) — and what the proof found that the prompt did not

`residue_snapshot()` ran `pgrep -a -f "qemu-system"`. `-f` matches the whole **command line**, so it
matched anything that merely *mentioned* a guest. A false positive there is enumerated,
SIGTERM/SIGKILLed, and **latches** a `gate-residue` breaker only `--reset-breaker` clears — so one
unlucky command line kills an innocent process and halts the next morning's good batch.

The test is now the process's **executable**: `/proc/<pid>/exe` basename, `/proc/<pid>/comm` as the
fallback for a process the unprivileged runner cannot stat, matched as a **prefix** because the
kernel truncates `comm` to 15 bytes (`qemu-system-x86_64` → `qemu-system-x86`). `qemu_pattern` is
therefore now an executable-name prefix, and `runner.conf` says so.

**Three decoys, one real guest** (`raw/11`), all with `qemu-system-x86_64` in their command lines:

| | exe | old `pgrep -f` | new test | outcome |
|---|---|---|---|---|
| DECOY-A | `/usr/bin/bash` | **matched** | not matched | alive |
| DECOY-B | `/usr/bin/python3.14` | **matched** | not matched | alive |
| DECOY-C | `/usr/bin/tail` (path argument carries the string) | **matched** | not matched | alive |
| REAL | `/usr/bin/qemu-system-x86_64`, scope descendant | matched | **matched** | **reaped** |

**The proof produced two facts it was not asked for.** (a) The old `pgrep -f` listing includes
`97446 /bin/bash -c source /home/kalib/.claude/shell-snapshots/…` — **the tool-call shell of the
session running the proof**, matched because the harness source mentions qemu. The hazard in its
most literal form, printed unprompted. (b) The reaper's **SIGKILL escalation branch executed for
the first time**: a real `qemu-system-x86_64 -S -machine none` did not die on SIGTERM, the grace
loop ran its full 5 s, and `"SIGTERM ignored for 5s, SIGKILLed"` was logged.
`docs/PHASE-J-STATE` had recorded that branch as untested. **5 s sufficed for that guest shape;
the number stays PROVISIONAL** — one observation of one guest is not a calibration.

**A second false-positive class, found by the proof and also fixed.** The first run failed its own
closing bracket: a just-SIGKILLed guest becomes a **zombie** that keeps its `comm` while losing its
`exe` and cmdline, so the scan matched **the corpse of the process it had just killed**. A zombie
holds no VM, no memory, no port and no key. State `Z` is now excluded (`_proc_state()`).

**Same scrutiny applied to the other two probes** (`raw/12`). Neither shares the substring flaw —
`virsh list --all --name` and `ss -lntpH` are structured output, not patterns. But the listener
probe had a different real defect: `re.search(r"pid=(\d+)")` took only the **first** owner, so a
multi-owner socket would be reaped by one pid with its siblings left holding the port. Now
`re.findall`, with owning process **names** recorded so a reap is enumerated by name.

**Stated, not fixed — the diff window.** Both probes are before/after snapshots, so any listener or
domain appearing between them is attributed to the gate even if an unrelated service created it.
That is inherent to a diff, not a substring bug. It is bounded by the new `_reap_refusals()` floor
(pid≤1, the runner, its process group, its session — `raw/12b`) and by the fact that an
unprivileged runner cannot signal a root-owned service. It remains a way for an innocent listener
to be reaped and to latch a breaker. `raw/12c` verifies the new guard does **not** neuter the
reaper: a gate child is launched `start_new_session=True`, so guests are never in the runner's own
session — and `raw/11`'s real guest was reaped through exactly that shape.

## 3. The secret-scan argv leak (Phase 3)

**Where the scan is defined — and the finding is that the staged-diff form had no home at all.**
`bin/secret-leak-scan` (GATE-30) covers whole **trees** and has been stdin-only since J-92.
`bin/wrought-secret-watch` and `bin/gate30-secrets` both feed it correctly. The **staged diff** —
the surface every gate touches at wind-down — was covered by nothing, so it was re-derived from
memory each time, and the re-derivation is where the leak lived:

| | improvised command | cost |
|---|---|---|
| J-92 | `sudo -n grep -rIal -- "$KEY" …` | `sudo` journals argv → both credentials in the journal ×5; one **rotated**, one is **D24** |
| RECONCILE | `KEY=$(sudo cat …); grep -rlF "$KEY" …` | key in `grep`'s argv |
| J-164 | `KEY=$(sudo -n cat …); git diff --cached \| grep -c -- "$KEY"` | key in `grep`'s argv |

**`bin/wrought-precommit-secret-scan`** is that home (rails **§5.1**). It decrypts **every**
credential in the store (J-75: a hard-coded name keeps printing the same green over a shrinking
fraction) into process memory, compares **in-process**, and prints counts and paths only. The only
credential-shaped thing in any argv is a **path**.

**Proof (`raw/21`) is deterministic, not a race.** An argv exposure lasts one short-lived process;
racing it would make the proof flaky and worthless. Both matchers read the diff from a **FIFO** the
harness does not write until it has finished walking `/proc` — so both are parked with argv already
fixed. A **fake** token is used throughout; testing a secret-scanner with a real secret would be
the same class of mistake it exists to prevent.

- **OLD form:** token found in **1** process argv (`grep -c -- <token> <fifo>`), and it detects.
- **NEW form:** **0** processes, including every descendant, and it detects (exit 1).
- **Control:** clean diff → exit 0. **Refusal:** no usable secret → exit **2**, not a green.

**A defect in this gate's own new tool, caught by its own evidence.** `raw/22`'s probe ran the
unprivileged path and printed a `PermissionError` traceback with **exit 1** — the code for *"a
sealed credential is in the staged diff"*. "Could not look" had collapsed into "found one". Fixed;
`raw/22b` measures all three codes distinct. **`raw/22`'s own closing verdict asserted the exit 2 it
had just failed to observe** — see §8.

The corrected form was then used for real at this gate's own pre-commit (§7).

## 4. F-1 and F-2 (Phase 4)

**F-1 — rails §2 is now two cases.** §2.1: a **direct** session hashes the three paths itself, at
start and before finalizing. §2.2: **under `wrought-runner` the freeze is the runner's duty**,
performed outside the child, and **a gate child must not attempt it**. `bin/wrought-runner-hook`
serialises the whole `tool_input` and denies on `orchestrator\.db`, so any command naming the store
is refused — *including a read-only `sha256sum`*, and including a command that merely quotes the
filename while writing about the denial. **That denial is the control working.** It is also the
better arrangement on its merits: the runner's capture is taken by a process the child cannot
influence, which is a stronger claim than a child attesting about itself.

**F-2 — new rails §13.3.** A guest under the runner is a **descendant of the gate's scope**, so its
memory is charged to the gate's 8 G cgroup and an overrun is an immediate OOM **kill of the gate**
— `MemorySwapMax=0` is exactly what removes the soft landing. J0B's proven `-m 8192` is the whole
scope. **The box had 84 GiB free at the time**, which is why this needed writing down: every
instinct and every `free -g` points the wrong way. Recorded: current scope `memory_max` = **8G**
(PROVISIONAL); `-m 3072` is the only guest size measured to work inside it; **do not exceed
`-m 4096` in an 8 G scope** without raising `memory_max` first, which is a ferry decision.

## 5. `NOT RUN` and `reset_by` (Phase 5)

**`NOT RUN` — documented, and a premise corrected.** The prompt calls it *"ratified-in-use"*. It is
not. `git log -S 'NOT RUN' -- QUEUE.md README.md` over the courier returns **no commit that ever put
it in a row**, and the runner **never writes it** (its two `set_queue_status()` call sites write
`RUNNING` and `HALTED`). So it is **RESERVED, never used**. It is documented in rails §12.1's status
table, the courier `README.md` legend, `QUEUE.md`'s own table and a comment at the definition, with
the minimal meaning the vocabulary needs — *dispatched, then deliberately never started; unlike
`QUEUED` a decision rather than a waiting state, unlike `RESET` nothing executed* — and **the
wording is flagged for the ferry** rather than reconstructed as an intent nobody recorded.
`RUNNABLE_STATUS` untouched.

**`reset_by` — replaced by measurement.** The hardcoded `"operator via --reset-breaker"` was written
when the **box** ran the reset, so the one record of who cleared a safety breaker said something
false, permanently, in the file an operator reads to find out exactly that. `reset_provenance()`
now records `reset_method`, `reset_user`, `reset_uid`, `reset_euid`, `reset_pid`,
`reset_stdin_tty`, `reset_interactive` — and a note saying in as many words that
**`reset_interactive` is evidence, not proof**: uid cannot tell the operator from the box here,
since both are `kalib`. Nothing claims *who*. Both arms measured (`raw/31`): piped stdin → `false`,
a tty → `/dev/pts/4`.

The false record already in **live** `/var/lib/wrought/runner-state/breaker.json` was captured
verbatim as evidence and then replaced (`raw/32`) — safe because the breaker was not latched and
`consecutive_failures` was already 0, and `--reset-breaker` returns before the lock and never
touches the courier. The replacement correctly records that reset as **non-interactive — i.e. the
box**, which is precisely the fact the old string got wrong.

## 6. The workspace boundary, armed (Phase 6) — the careful one

Both halves in one change, because either alone is worse than neither. **Half A:** the runner
refuses a bare `Bash` entry (`validate_allowed_tools()`, halt `bare-bash`) — **unconditional, with
no config key**, because a safety property that can be switched off in a file is one that will
eventually be found switched off, and because CLAUDE.md forbids inventing config keys.
**Half B:** `resolve_add_dirs()` halts on the singular `ADD-DIR:` (which used to be ignored in
silence and cost J0B-RESUME v2.0 its entire workdir — pre-flight BLOCKER B-1) and on any declared
directory that does not exist.

What the runner **cannot** check is whether the declared set is the *right* set. That is stated as a
prompt-author duty in rails §12.2.2 rather than faked as a mechanical check.

**Proof (`raw/41`), through the real runner on a scratch courier with a local bare origin and a
scratch `state_dir`** — necessary because *a `wrought-runner` start is never read-only with respect
to its `courier_dir` on any exit path*. The derived config is diffed against the installed one
mechanically: **104 leaves, 9 changed**, all paths plus the pacing nap; every permission mode,
breaker, limit, `ephemeral_home` and `reaper` setting byte-identical.

- **ARM A** bare `Bash` → `HALT [bare-bash]`, **no child launched**, $0.
- **ARM B** `ADD-DIR:` singular → `HALT [add-dirs-header]`, **no child launched**, $0.
- **ARM C** `Bash(touch:*)` + a correct `ADD-DIRS:` → one real child, $0.193.
  **Ground truth on disk:** `declared/inside.canary` **PRESENT**;
  `undeclared/outside.canary` **ABSENT**; child reports exactly **1** `permission_denial` for the
  outside `touch`. The boundary is a real fence for a scoped rule.

**Closing bracket (`raw/42`):** three runs, two of which halted before launching a child — the
dead-gate shape the teardown lives in a `finally` for — and **zero ephemeral HOMEs survive**, which
is the security question, since they hold live credential copies.

**Corrections to the overbroad ESTABLISHED FACT, in all three places named by the prompt:**
`runner.conf`'s `_add_dirs_note`; a dated **correction file beside**
`build-evidence/runner-arm/raw/31` (the evidence file itself is **not** edited — rails §4);
and `docs/PHASE-J-STATE.md`, where the OPEN ruling is closed. `raw/31`'s "CORROBORATION FROM A REAL
GATE" is specifically retracted: that child's `ALLOWED-TOOLS` was **bare `Bash`** (`tools='Bash'` in
raw/25's own launch line), so its bundle write would have succeeded whether or not `add_dirs` named
the courier.

## 7. The per-batch cost cap (Phase 7)

`breakers.max_batch_cost_usd = 24.0`, **PROVISIONAL and DERIVED** — the derivation is in the config
so the ferry can argue with it: **3 × `max_budget_usd_per_gate`**. The naive product of the two
existing caps (6 gates × $8 = $48) bounds nothing useful, and is optimistic besides, since
GATE-RUNNER-ARM measured the CLI's own `--max-budget-usd` overshooting **4.6×** and **6.94×** —
implying ~$55 worst case for **one** gate. $24 stops a run after roughly three full-cap gates and
leaves the rest for the next day's ferry, which is the same shape as `gate-cap` and `wall-clock`.
**Non-latching**, for that reason: a batch that spent its allowance behaved correctly, and latching
would refuse the next morning's start over a normal ending. A pathological money-burner is still
caught by `consecutive-failures`, which does latch.

Costs are **summed from what the children actually reported**. A child that produced no parseable
JSON reported nothing; its cost is recorded as **unknown** and named in the halt line rather than
guessed at, because a fabricated number would under-count exactly the runs that went wrong.

A config **without** the key now **refuses to start** — same doctrine as `ephemeral_home` and
`reaper`: a run with no cumulative ceiling is not a bounded run.

**RE-CALIBRATION IS OWED, and this is the number that matters most in this report.** The $8 per-gate
cap was calibrated against J0B-RESUME's **$7.53 — the cost of a gate that WEDGED** (goose streaming
with `max_tokens: None`, abandoned generations head-of-line blocking llama-server, turns burned on
recovery). Clean children on this box cost **$0.08–$0.19**; four were measured today. **Calibrating
a cap on a wedged run sets it far too high.** Both `max_budget_usd_per_gate` and
`max_batch_cost_usd` must be re-derived **after F-5 is fixed** in J0B-CLOSE. This is written into
`runner.conf` itself, not only here.

Proven in `raw/53b` with the verdict **computed from the measured values**, 6/6 checks: cap fired,
paid gate in the ledger, second gate never started, breaker did not latch, exit 4 not 2, batch total
over cap.

## 8. What this gate got wrong, and how it was caught

Four defects in this gate's own work, all caught by measurement:

1. **The zombie survivor class** (§2) — caught by the reaper proof's own closing bracket.
2. **The scanner's exit-code collapse** (§3) — "could not scan" reported as "secret found".
3. **The batch-cost check ordering.** It sat **before** `write_ledger()`, so a gate that ran, cost
   money and tripped the cap was **never recorded as having run** — the next morning's start would
   have picked it up again and met it as a `stale-row` halt. Caught by `raw/52`'s own `ran.json`
   dump. Fixed by moving the check after the ledger write **and** after the consecutive-failures
   breaker: the latching fault wants an operator, the cap only says "enough for today", so if both
   are true the fault must win. Re-proved in `raw/53b`.
4. **Three pre-written verdict lines that contradicted the measurement printed directly above
   them** — `raw/22` ("REFUSES (exit 2)" over an observed exit 1), `raw/42` ("no leftover gate
   scopes" over a listing of two), `raw/53` ("the breaker did not latch" over a `HALT
   [consecutive-failures]` and exit 2). Each is corrected by addition, with the wrong sentence left
   standing. **This is a habit, not three accidents**, and it is the same defect class as the
   `reset_by` string this gate was sent to fix: a conclusion no measurement stands behind. The fix
   adopted mid-gate was to **compute the verdict from the measured values inside the harness**,
   which is what `raw/53b` does.

One further self-report: **`raw/52`'s scratch re-run was contaminated by state I failed to clear**
(the scratch breaker's `consecutive_failures`), which is why `raw/53` halted on the wrong breaker.
`raw/53b` resets both ledger and breaker and is the clean run.

And one moment worth naming because it is this gate's own subject matter: while cleaning up a
background harness I ran **`pkill -f "20-secret-scan-argv-harness"`**, which matched **my own Bash
tool wrapper** and killed it — the exact `pgrep -f`/`pkill -f` hazard Phase 2 exists to remove,
committed by the session removing it, an hour after writing the fix.

## 9. Changed and added

| Path | Change |
|---|---|
| `bin/wrought-runner` | 1163 → 1489 lines. New: `_proc_exe_name`, `_proc_state`, `_proc_cgroup`, `qemu_processes`, `_listener_pids`, `_reap_refusals`, `validate_allowed_tools`, `resolve_add_dirs`, `reset_provenance`; `NON_LATCHING` += `batch-cost`; `max_batch_cost_usd` required |
| `bin/wrought-precommit-secret-scan` | **new** — the staged-diff / bundle secret scan |
| `docs/EXECUTOR-RAILS.md` | §2 split into 2.1/2.2 (F-1); §5.1 added; §12.1 status table + `NOT RUN`; §12.2.1/12.2.2 added; §13.2 reaper note; §13.3 added (F-2) |
| `docs/PHASE-J-STATE.md` | six open items closed; this gate's section appended |
| `build-evidence/runner-arm/raw/31-CORRECTION-…txt` | **new** — beside the evidence, never editing it |
| `/etc/wrought/runner.conf` | `max_batch_cost_usd` + derivation + recalibration note; `_add_dirs_note`×4 corrected; reaper `_note3/4/5` |
| courier `README.md`, `QUEUE.md` | status legend incl. `NOT RUN`; scoped-Bash rule |

## 10. Open after this gate

- **Both cost caps need re-calibration after F-5** (§7). The single most actionable item here.
- **J0B-CLOSE owns the two capability items:** **F-5** (proxy must bound `max_tokens` and cancel
  abandoned generations — the pinhole is **not durable** under an agent's retry pattern and is
  **unmitigated for the next gate**) and the **goose 1.46 `extensions` schema**. **F-4 stands as
  doctrine: goose exits 0 on total failure.**
- **`virsh destroy` still unexercised** — today's proof used plain qemu by design.
- **`reaper.terminate_grace_sec`**: branch now exercised, number still PROVISIONAL.
- **The runner has still never run unattended.** Longest real batch: one gate.
- **ST-1 unsatisfied on two triggers**, owed before any manufacturing run.
- **Transport: 5 misses in 6.** And the next prompt must use **scoped** `Bash` entries or the runner
  will refuse it — including a prompt written in this gate's own format.
- **`NOT RUN` wording** is the box's minimal reading; the ferry should confirm or replace it.
- **Stale `failed` scope units** from GATE-RUNNER-HARDEN's dry run (`raw/42b`): no process, no
  cgroup, harmless, **not enumerated by any prompt so not deleted**. Operator's call.
- **A 16-hour peer `claude` session** (pid 87699, started 2026-08-28 17:16) was running throughout
  (`raw/03`). Not touched. It is the maintainability debt PHASE-J-STATE already names.

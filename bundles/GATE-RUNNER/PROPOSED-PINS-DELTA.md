# PROPOSED-PINS-DELTA — candidate `pins.lock` entries from GATE-RUNNER

**PROPOSAL ONLY. `pins.lock` was NOT edited this session.** CLAUDE.md's first hard rule is that a
value not in the docs or `pins.lock` is a gate question, not a blank to fill. Everything below is
that question written down. Until it is ratified, `/etc/wrought/runner.conf` carries these values
with an explicit `PROPOSED-UNRATIFIED` banner in its own `_README`.

---

## 1. The runner's own identity — MEASURED

```
# wrought-runner (GATE-RUNNER, 2026-08-21)
runner_harness            = "bin/wrought-runner"                # repo bin/, per convention
runner_hook               = "bin/wrought-runner-hook"           # PreToolUse, deny-or-defer
runner_course_check       = "bin/wrought-course-check"          # outer wrapper, summary on stdin
runner_course_post        = "bin/wrought-course-post"           # sealed key on stdin, one POST
runner_config             = "/etc/wrought/runner.conf"          # strict JSON, never sourced
runner_hook_settings      = "/etc/wrought/runner-hooks.json"    # strict JSON, validated per launch
runner_state_dir          = "/var/lib/wrought/runner-state"     # ledger, breaker, run evidence
runner_interpreter        = "/usr/bin/python3"                  # Python 3.14.4, stdlib only
```

`runner_interpreter` is **deliberately not** the repo's usual `/opt/wrought/venv-orch/bin/python`.
The runner supervises gates, and a gate may legitimately rebuild that venv; a supervisor must not
depend on the thing it supervises. The script is stdlib-only by rule, so it costs nothing.

## 2. The claude build this containment was measured against — MEASURED

```
claude_code_version       = "2.1.238"                # `claude --version`, raw/02
claude_code_path          = "/home/kalib/.local/bin/claude"
```

**This pin is load-bearing in a way a version pin usually is not.** Every containment claim in
§3 is a behaviour of *this* build, and two of them are behaviours the flag names do not imply
(`acceptEdits` and `auto` silently run un-allowlisted Bash; a malformed settings file silently
discards the hook layer). A version bump re-runs the Phase-1 matrix — the same discipline
CLAUDE.md already applies to llama.cpp/Mesa/kernel/model bumps.

## 3. Containment parameters — MEASURED where marked, PROPOSED where marked

```
runner_permission_mode        = "dontAsk"      # MEASURED default-deny-with-allowlist (raw/06)
runner_memory_swap_max        = "0"            # MEASURED REQUIRED (raw/11) — see below
runner_memory_max             = "8G"           # PROPOSED
runner_runtime_max_sec        = 5400           # PROPOSED (90 min per gate)
runner_max_output_tokens      = 32000          # PROPOSED
runner_bash_default_timeout_ms = 600000        # from the GATE-RUNNER prompt's own block
runner_max_budget_usd_per_gate = 8.0           # PROPOSED — a SOFT ceiling, see below
runner_inter_gate_sleep_sec   = 300            # PROPOSED
runner_max_consecutive_failures = 2            # PROPOSED
runner_max_gates_per_run      = 6              # PROPOSED
runner_max_wall_clock_sec     = 72000          # PROPOSED (~20 h, per the prompt)
runner_deadman_no_progress_sec = 3600          # PROPOSED
runner_api_retry_max          = 4              # PROPOSED
runner_api_backoff_base_sec   = 60             # PROPOSED
runner_api_backoff_cap_sec    = 1800           # PROPOSED
```

**`runner_memory_swap_max = "0"` is not a preference — it is what makes `MemoryMax` a cap at all.**
Measured (`raw/11`): under `-p MemoryMax=256M` alone, a process allocating 1 GiB **succeeded and
exited 0 in one second**. `memory.max` *was* applied correctly (268435456), but `memory.swap.max`
defaulted to `max`, so the overrun was paid for out of the host's 8 GiB swap file. With
`-p MemorySwapMax=0` the identical allocation is OOM-killed immediately (rc=137). The
GATE-RUNNER prompt's own proposed invocation specifies `MemoryMax` without `MemorySwapMax`; on
this box that combination does not bound memory. Removing this line silently un-caps memory.

**`runner_max_budget_usd_per_gate` is a soft ceiling.** Measured (`raw/08`): a run capped at
`--max-budget-usd 0.01` spent `$0.0460925` — a 4.6x overshoot, because the check happens between
turns and a turn already in flight is paid for. Set the cap below what can be afforded, and
reconcile against the child's reported `total_cost_usd` after the fact.

## 4. Two budgets that must not be conflated — RECORDED, one CORRECTION

The GATE-RUNNER prompt asks the course-check to "respect the $50 prepaid backstop (STOP-4)".
Two corrections, neither of them a judgement call:

1. **$50 is not the binding number.** `pins.lock` already records
   `provider_side_key_limit_usd: 50`, `provider_side_account_balance_usd: 26.17`, and
   `provider_side_backstop_usd: 26.17` — the **effective** ceiling is the min of the two, measured
   2026-08-03. The shipped `course_check.spend_cap_usd` is 5.0, far below it.
2. **The gate children do not spend that credential at all.** `claude -p` runs on the box's Claude
   Code subscription auth; the `$50/$26.17` backstop bounds the **OpenRouter** escalation
   credential, which on this rail is touched only by `wrought-course-check`. They are separate
   budgets with separate caps and separate ledgers, and the runner keeps them separate:
   `--max-budget-usd` per gate for the first, `course-check-spend.jsonl` for the second.

## 5. Courier vocabulary — NEW, NEEDS ADVISOR RATIFICATION

`QUEUE.md`'s documented statuses are `QUEUED`, `RUNNING`, `BUNDLED`, `ADJUDICATED`. The runner
needs one more, and one convention:

```
queue_status_approved     = "APPROVED"   # NEW: advisor+operator have cleared this gate to run
                                         # unattended. It is the ONLY status the runner will act on.
prompt_header_allowed_tools = "ALLOWED-TOOLS:"   # NEW, REQUIRED in every runnable gate prompt
prompt_header_max_budget    = "MAX-BUDGET-USD:"  # NEW, optional; falls back to the config cap
```

A prompt with no `ALLOWED-TOOLS:` header is **refused, not defaulted** — an underspecified
requirement is a defect to report, never a blank to fill (CLAUDE.md priority 4). The runner also
refuses any gate whose row is already `RUNNING` or `BUNDLED`; `GATE-J0B-SURFACE` has been sitting
at `RUNNING` with no bundle since 2026-08-20, which is exactly the state that refusal exists for.

## 6. Not proposed, and deliberately so

- **No systemd timer.** The operator ruling makes the manual daily start the human gate; a timer
  would contradict the adjudicated design. None was written, not even disabled.
- **No `/opt/wrought/bin` install.** The scripts live in the repo's `bin/`, matching every other
  gate script. Installing copies to `/opt/wrought/bin` is an operator step, not this gate's.
- **`course_check.enabled` stays `false`.** Pointing the sealed escalation credential at a new
  purpose is a decision the operator has not yet made. §4 above is the disclosure it needs.

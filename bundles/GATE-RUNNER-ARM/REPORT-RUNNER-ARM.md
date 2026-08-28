# REPORT — GATE-RUNNER-ARM (v1.0, ATTENDED-DIRECT)

**Executor:** Claude Code on `forge-mini` (Opus, ultracode). **Advisor:** Fable.
**Date:** 2026-08-28. **Evidence:** `build-evidence/runner-arm/raw/` (34 files).
**Byte freeze: HELD** (`raw/00` vs `raw/99`, mechanical diff at `raw/99b`).

## 0. Verdict in one paragraph

The runner is **ARMED**, and it took **two** fixes to get there, not the one the prompt anticipated.
The CLI is pinned at **2.1.250** with auto-update disabled at **both** surfaces, and **all four
safety properties were re-verified on that build before the pin moved** — so nothing is left
"unverified on the installed build". `DBUS_SESSION_BUS_ADDRESS` is gone from the gate-child
environment, which closed a hole `GATE-RUNNER-HARDEN` had left open rather than merely tightening a
surface. The `PermissionError` is fixed and the runner **starts on the INSTALLED config, rc=0**.
But getting there surfaced a **second, previously unknown hard blocker**: the runner could not
parse the real `QUEUE.md` at all, and would have latched a breaker on every start forever. That was
fixed under an explicit advisor+operator ruling, additively, and regression-proven. One real
`claude` gate then ran end to end through the full armed path and passed.

## 1. Transport — the FOURTH consecutive rails §7 failure

The prompt arrived as **chat text, not a file**, despite its own header asking for a file upload.
Content was intact and the block count was exactly **1** as declared, so it was archived verbatim to
`prompts/GATE-RUNNER-ARM-v1.0.md` and run. **This is now four in a row** (`GATE-RUNNER`,
`GATE-RECONCILE`, `GATE-RUNNER-HARDEN`, `GATE-RUNNER-ARM`). Surfaced, not absorbed. A rail missed
four consecutive times should be enforced or amended.

First courier action per rails §10: the `GATE-RUNNER-HARDEN` adjudication was extracted
**mechanically** (`sed -n '20,27p'`) to `bundles/GATE-RUNNER-HARDEN/ADJUDICATION.md` and that row
set `ADJUDICATED`.

## 2. Phase 1 — the operator action, verified rather than believed

`/var/lib/wrought/runner-state` did not exist; `/var/lib/wrought` is `root:root 0755`. The box has
`(ALL) NOPASSWD: ALL` and **deliberately did not self-authorize** the fix: the prompt routes it
through a human, and capability is not authorization. After the operator ran it, the box **measured
the result** rather than taking it on report — `drwx------ kalib:kalib`, mode `700`, writable,
empty (`raw/02`).

**Unasked security observation, recorded not acted on:** gate children run as `kalib`, and `kalib`
is `NOPASSWD: ALL`. **The `dontAsk` allowlist and the systemd scope are the only fences between a
gate child and root.** There is no second, credential-shaped one.

## 3. Phase 2 — the CLI pin, and the root cause of the self-update

**The headline finding: `autoUpdates: false` was ALREADY SET in `~/.claude.json` and never worked.**
The resolver (`raw/04`, read out of the binary) is:

    if (autoUpdates===false && (installMethod!=="native" || autoUpdatesProtectedForNative!==true))
        return {type:"config"};

This box is `installMethod: native` with `autoUpdatesProtectedForNative: true`, so the config arm is
**void** and the resolver falls through to enabled. Confirmed by direct observation, not just code
reading (`raw/05`): with the preference in place and nothing in the env, `claude doctor` reported
**`Auto-updates: enabled`**. With the env var set it reports
**`Auto-updates: disabled (set by env: DISABLE_AUTOUPDATER)`** — it names the variable.

**On a native install the ENV arm is the only reachable switch.** The config preference is not a
control and must not be recorded as one.

**Two surfaces, both required — and this is the load-bearing part** (`raw/08`). HARDEN's ephemeral
HOME, the fix for the *steering* breaker, had itself **re-opened auto-update for gate children**,
because it moves the child away from the very file the interactive fix lives in. Measured:

| arm | HOME | env | `claude doctor` |
|---|---|---|---|
| A | real | nothing | `disabled (set by env: DISABLE_AUTOUPDATER)` — the settings block works |
| C | **ephemeral** | nothing | **`enabled`** — the settings block cannot reach a gate child |
| D | ephemeral | `DISABLE_AUTOUPDATER=1` | `disabled (set by env: …)` — closed |

Three independent reasons C fails: HOME is the ephemeral dir; the launch passes
`--setting-sources ''`; the child env is an allowlist. So the fix is in **both** places —
`~/.claude/settings.json`'s `env` block, and a hardcoded entry in `build_child_env()`.

`pins.lock` gains `supervisor_toolchain` (2.1.250, commit `2f71b9f41af6`) and a `drift_observed`
entry. **This drift is not an OS-update-policy drift** — `unattended-upgrade` had nothing to do with
it; the tool updates itself out of the user's own home, so `os_update_policy`'s holds could never
have caught it.

## 4. Phase 3 — all four properties HOLD on 2.1.250

Every invocation carried `DISABLE_AUTOUPDATER=1` so the binary could not move mid-matrix; the
opening and closing brackets agree (`raw/15`).

| | property | verdict | evidence |
|---|---|---|---|
| **(b)** | `dontAsk` denies un-allowlisted Bash; honours a granular allowlist; `acceptEdits`/`auto` still silently RUN | **PASS, row for row** | `raw/11` |
| **(c)** | hooks fire under `-p`; malformed settings still **silently** ignored | **PASS** | `raw/12` |
| **(d)** | budget is a soft ceiling; `BASH_DEFAULT_TIMEOUT_MS` backgrounds, does not kill | **PASS** | `raw/13` |
| **(a)** | fresh context per invocation; two-surface isolation | **PASS, and stronger** | `raw/14` |
| **+** | `--add-dir` workspace boundary — *not one of the prompt's four; added because this gate's own audit caught the report overclaiming* | **PASS** | `raw/31` |

**(c) is the one that would have hurt most if it had changed.** A malformed settings file is still
ignored with `rc=0`, `subtype='success'` and **zero bytes of stderr**, and the Bash call runs. The
pre-launch `json.load` guard in `validate_hook_settings()` is **still required**; hooks remain
defence-in-depth only.

**(a) is stronger than HARDEN's result, and the difference is stated rather than papered over.**
HARDEN measured the child's socket *moving* to the private runtime dir. Here, in the runner's real
seed shape (which omits `.claude.json`), the isolated child created **no socket anywhere** — while
a control arm proved the probe could see a non-isolated child. The claim made is the narrow
measured one; the weaker HARDEN result stays the thing to design against, and both surfaces stay.

**Two benign-but-real changes, reported not absorbed.** The model now spontaneously **raises** the
per-call Bash timeout above the env default (it did not on 2.1.238) — which *strengthens* the
existing conclusion that the kernel is the only real stop, and means `BASH_DEFAULT_TIMEOUT_MS` must
never be mistaken for a ceiling. And the budget overshoot measured **6.94x** against 4.6x at
`GATE-RUNNER`: **two single-run samples, not a trend**, but against the provisional
`max_budget_usd_per_gate = 8.0` it implies a worst case near **$55 for one gate**. That belongs in
front of the operator before an unattended batch, not after.

## 5. Phase 4 — DBUS dropped, closing a real hole

Measured at the start of this gate: a gate child was handed `DBUS_SESSION_BUS_ADDRESS=
unix:path=/run/user/1000/bus` — **the real session bus** — despite HARDEN's private runtime dir.
The steering fix moved the `cc-socks` surface and left the bus surface untouched.

The **tighter** of the two allowed options was taken: removed from the allowlist outright rather
than stripped child-only, because `systemd-run --user --scope` was measured to work with no bus
address as long as `XDG_RUNTIME_DIR` is set (sd-bus derives it), while the control with both removed
fails. A real gate child then ran — 3 turns, 0 denials, 0 stderr, `git --version` working — and the
absence was confirmed **from inside the child**, which wrote `DBUS_SESSION_BUS_ADDRESS=[<UNSET>]`,
its private runtime dir, and `DISABLE_AUTOUPDATER=[1]` to a file the box then read (`raw/20`).
Nothing needed re-adding.

## 6. Phase 5 — split, because the prompt asked for two things that cannot both hold in one run

"Starts on the INSTALLED config" and "never the real store" are incompatible in a single run: the
installed `freeze_paths` **are** the real store. So:

### 5(i) — startup on the installed file, verbatim
`--status` proved `load_config()` and the exact `state.mkdir()` line that used to raise now work
(`raw/23`). **The `PermissionError` is gone.** The full start then found the second blocker.

### THE SECOND BLOCKER — the runner could not parse the real `QUEUE.md` (`raw/24`)

    HALT [queue-parse]: QUEUE row 22 for GATE-HJ2-HEARTBEAT has unknown status
    'FOLDED INTO GATE-RECONCILE'  — BREAKER LATCHED

`parse_queue()` rejected **two ratified terminal statuses**: `RESET` (GATE-J0B-SURFACE) and
`FOLDED INTO <gate>` (GATE-HJ2-HEARTBEAT — **parametric**, so it needs a prefix match, and a fix
adding the bare string to the set would still have failed). rails §12.1, the courier `README.md`
legend and `QUEUE.md`'s own table all define both; **only the parser was out of sync.**
`--reset-breaker` could not help: the condition is permanent. Never caught because every prior dry
run used a scratch courier with a synthetic queue — **the same never-exercised-against-production
shape as HARDEN's `state_dir` finding.**

It was **reported, not silently fixed** — the queue parser is outside the prompt's authorized change
set. The advisor endorsed the additive fix, the operator authorized it verbatim (recorded in
`raw/24`), and only then was it applied: `QUEUE_STATUSES += "RESET"`,
`QUEUE_STATUS_PREFIXES = ("FOLDED INTO",)`, **`RUNNABLE_STATUS` untouched**. The `NOT RUN` question
was explicitly **left open** because the ruling did not cover it.

**Re-proof (`raw/28`):** 7/7 real rows parse, **0 runnable** (unchanged); the installed-config start
now gives `no APPROVED gates left to run — exiting cleanly`, **rc=0**, breaker not latched. A
scratch regression carried all three terminal shapes plus one `APPROVED` row: the terminal rows
parsed, and **exactly one gate ran — the approved one**.

### 5(ii) — one real gate, end to end (`raw/25`)

Derived config proven **mechanically**: 8 of 103 leaves changed, all path redirections; every
threshold, mode, breaker, `ephemeral_home` and `reaper` value byte-identical to the installed file.

    session_id      feee78d7-7ea4-4e97-b23a-7650f79a6ae1
    verdict         PASS   (mechanical: QUEUE row BUNDLED + bundle present + SHA256SUMS verifies)
    child           COMPLETED, rc=0, 5 turns, 0 denials, 0 bytes stderr, $0.178, 27.1 s
    byte freeze     HOLD
    orphan sweep    CLEAN — no new guest, domain or listener survived
    teardown        ephemeral HOME removed; no credential files left behind
    the gate's push landed in the scratch origin as its own commit (040a7af)

**Containment caught in the act** during the regression run: the child reached for the `Edit` tool,
which the prompt's `ALLOWED-TOOLS: Bash` does not include; `dontAsk` **denied it**, the denial was
recorded machine-readably, and the child completed the same work through Bash. That is rails §12.2
working on a live gate.

## 7. Two side effects, reported rather than quietly repaired

1. **A `wrought-runner` start is NEVER read-only with respect to the courier — on ANY exit path.**
   Both the halt path and the clean path `push_status()`, which writes, commits and **pushes**
   `STATUS.md`. It clobbered this session's heartbeat twice. A pre-run comment of mine in `raw/23`
   asserted the opposite; **that claim is wrong and is corrected by addition, with the wrong
   sentence left standing**, per rails §4.
2. **The latched breaker was reset** so the operator's state dir carries no probe-induced fault,
   with the reasoning recorded — and noting that resetting the flag does not soften the defect.

## 8. Open items for the advisor

1. **`NOT RUN`** — in `bin/wrought-runner:65`, in no document. Delete from the set, or add to rails
   §12.1? (The runner never writes it; checked.)
2. **`reset_by: "operator via --reset-breaker"` is a hardcoded string** in `breaker.json`, written
   when the **box** ran it. A one-line instance of the false-provenance class this project tracks.
3. **The `$55 worst-case gate cost`** implied by the 6.94x overshoot against the provisional $8 cap.
4. **`NOPASSWD: ALL`** — gate children inherit passwordless root; the allowlist and the scope are
   the only fences.
5. **Transport, four consecutive misses.**

## 9. What this gate did NOT do

No real J0B work. No course-check enablement (untouched, still `false`). No package installs. No VM.
No scale number measured or changed — every `PROVISIONAL` value in `/etc/wrought/runner.conf` is
still for the first supervised batch. The `reaper`'s `virsh destroy` branch and its
SIGTERM→SIGKILL escalation remain **unexercised**, as at HARDEN.

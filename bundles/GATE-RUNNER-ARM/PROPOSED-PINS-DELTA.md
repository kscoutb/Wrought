# PROPOSED-PINS-DELTA — GATE-RUNNER-ARM

**This file is NOT "proposal only". §1 below was APPLIED to `pins.lock` this session, under the
prompt's explicit authorization** ("Authorized changes: pins.lock (CLI pin + drift), ..."). That
is the difference between this delta and its two predecessors, and it is stated here because a
delta file that says "proposal only" while the pin has actually moved is exactly the kind of
false record this project keeps finding. §2 is genuinely still a question.

Predecessors, still current where not superseded:
`build-evidence/runner/PROPOSED-PINS-DELTA.md` (GATE-RUNNER) and
`build-evidence/runner-harden/PROPOSED-PINS-DELTA.md` (GATE-RUNNER-HARDEN).

---

## 1. APPLIED — the supervisor's own toolchain is now pinned

A new top-level `supervisor_toolchain:` section in `pins.lock`, plus one `drift_observed` entry.
The pin moves here because **a pin moves only in the gate that re-measures it**, and this gate
re-verified all four containment properties on the new build first (Phase 3, `raw/11`–`raw/15`).

```
supervisor_toolchain:
  claude_code_version: "2.1.250"                  # `claude --version`, raw/03
  claude_code_commit: "2f71b9f41af6"              # `claude doctor` -> Commit:, raw/05
  claude_code_path: /home/kalib/.local/bin/claude # a SYMLINK — the updater moves it
  claude_code_versions_dir: /home/kalib/.local/share/claude/versions
  claude_code_install_method: native
  claude_code_autoupdate: DISABLED-BY-ENV
  claude_code_autoupdate_switch: "DISABLE_AUTOUPDATER=1"
  claude_code_autoupdate_config_pref_is_void: true
  claude_code_autoupdate_surface_interactive: "~/.claude/settings.json -> env{DISABLE_AUTOUPDATER}"
  claude_code_autoupdate_surface_gate_child: "bin/wrought-runner build_child_env(), hardcoded"
```

`claude_code_autoupdate_config_pref_is_void: true` is the one key here that is not a plain
measurement, and it is the most important. The operator's `autoUpdates: false` **was already set
and did not work**; recording only "autoupdate disabled" without recording that the config arm is
void would leave the next reader believing a control exists that does not.

## 2. STILL OPEN — one ruling this gate deliberately did not take

`bin/wrought-runner:65` carries a queue status **`NOT RUN`** that appears in no document this gate
could find — not `docs/EXECUTOR-RAILS.md` §12.1, not the courier `README.md` legend, not
`QUEUE.md`'s own status table. The operator's ruling this session authorized adding `RESET` and a
`FOLDED INTO` prefix match and said nothing about `NOT RUN`, so it was left in place.

Checked, so the decision is cheap either way: `grep -n 'NOT RUN' bin/wrought-runner` returns only
line 65, and the two `set_queue_status()` call sites write `RUNNING` and `HALTED` only — **the
runner never writes `NOT RUN`**, so deleting it cannot break a round-trip.

```
# OPEN: delete 'NOT RUN' from QUEUE_STATUSES, or add it to the rails §12.1 vocabulary?
```

## 3. Unchanged from the predecessors

Every scale number in `/etc/wrought/runner.conf` remains `PROVISIONAL` and is **for the first
supervised batch to set**. This gate measured none of them and changed none of them.

One datum the batch should carry into that exercise, from `raw/13`: the `--max-budget-usd`
overshoot measured **6.94x** here against 4.6x at GATE-RUNNER. Two single-run samples are not a
trend and must not be pinned as one — but against the provisional
`max_budget_usd_per_gate = 8.0`, a ~7x overshoot implies a worst case near **$55 for one gate**.
That is a number the operator should see before an unattended batch, not after.

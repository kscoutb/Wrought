# PROPOSED-PINS-DELTA — candidate `pins.lock` entries from GATE-RUNNER-HARDEN

**PROPOSAL ONLY. `pins.lock` was NOT edited this session.** This file extends
`build-evidence/runner/PROPOSED-PINS-DELTA.md` (GATE-RUNNER) rather than replacing it; read that
one first. Everything below is a gate question written down, per CLAUDE.md's first hard rule.

---

## 1. THE URGENT ONE — the pinned `claude` build is no longer the installed build

GATE-RUNNER proposed `claude_code_version = "2.1.238"` and said, correctly, that the pin is
**load-bearing in a way a version pin usually is not**: every containment claim the runner rests
on is a behaviour of *that* build.

**It self-updated on 2026-08-28 at 12:56:04Z, hours before this gate ran, with no signal to
anyone** (`raw/02`):

```
/home/kalib/.local/bin/claude --version   ->  2.1.250 (Claude Code)
~/.claude/.last-update-result.json        ->  {"timestamp":"2026-08-28T12:56:04.699Z",
                                               "path":"native","outcome":"success",
                                               "version_from":"2.1.238","version_to":"2.1.250"}
/home/kalib/.local/bin/claude -> /home/kalib/.local/share/claude/versions/2.1.250   (a symlink)
```

Proposed, and this is the substantive question for the operator:

```
claude_code_version       = "2.1.250"            # MEASURED 2026-08-28; was 2.1.238 at GATE-RUNNER
claude_code_versions_dir  = "/home/kalib/.local/share/claude/versions"
claude_code_autoupdate    = "UNPINNED — the CLI updates ITSELF and moves the symlink"
```

**What this invalidates, stated plainly.** GATE-RUNNER's `raw/06` (permission modes), `raw/07`
(hooks under `-p`), `raw/08` (budget overshoot, `BASH_DEFAULT_TIMEOUT_MS` backgrounding), `raw/14`
(the `--add-dir` workspace boundary) and `raw/16`/`raw/18` (cross-session steering) were **all
measured on 2.1.238 and none has been re-measured on 2.1.250.** This gate re-measured only what it
needed: `dontAsk` still default-deny-with-allowlist (every probe), the allowlist spellings from
`raw/12` still behave (probe D vs D2), `RuntimeMaxSec` still kills (`raw/10`), and the steering
surfaces (`raw/06`). **The rest is now UNVERIFIED-ON-THE-INSTALLED-BUILD**, and that is a
statement about the evidence base, not a defect found.

An off-switch exists in the binary — the string `DISABLE_AUTOUPDATER` is present (8 occurrences,
`raw/03`) — but **this gate did not set it and did not test it**, because turning off updates for
the operator's own interactive sessions is not a change a gate should make unilaterally. It is
proposed:

```
# PROPOSED, [UNTESTED] — pin the supervisor's toolchain the way every other tool is pinned
runner_child_disable_autoupdate = "DISABLE_AUTOUPDATER=1"   # env var; string present in the binary
```

The sharpest version of the risk: a 20-hour unattended batch in which gate 3 silently upgrades the
CLI underneath gates 4, 5 and 6, and the run's evidence names one version while three gates ran on
another. That is a reproducibility failure (P3) of exactly the kind `pins.lock` exists to prevent.

## 2. The ephemeral-HOME fence — MEASURED

```
runner_ephemeral_home_root = "/var/lib/wrought/runner-state/ephemeral-homes"   # 0700, per gate
runner_ephemeral_home_seed = [".claude/.credentials.json", ".gitconfig", ".git-credentials"]
runner_cc_socket_path      = "$XDG_RUNTIME_DIR/cc-socks/<pid>.sock"  # MEASURED, raw/06
```

`runner_ephemeral_home_seed` is the **measured minimum**, established by incremental seeding
(`raw/06`): empty HOME → `"Not logged in · Please run /login"`; + `.credentials.json` → completes;
+ the two git files → the gate's own courier push works. `.claude.json` is deliberately excluded.

**These are paths and a measured minimum, not thresholds** — no number here was invented.

## 3. The orphan reaper — one PROVISIONAL number, named as such

```
runner_reaper_qemu_pattern      = "qemu-system"   # the pattern the sweep scans process cmdlines for
runner_reaper_terminate_grace_s = 5               # PROVISIONAL — SIGTERM→SIGKILL grace, UNMEASURED
```

`terminate_grace_sec = 5` is the one number this gate added that nobody measured. It is marked
`PROVISIONAL` in `/etc/wrought/runner.conf` itself and belongs with the other scale numbers the
first supervised batch sets. Every stub in `raw/09` and `raw/12` died on the first SIGTERM, so the
grace path itself is **[UNTESTED]** — a process that ignores SIGTERM has not been exercised.

The proxy port that motivated the listener half of the sweep, for the record — it is **not** a
config key, because the sweep diffs *all* listeners rather than watching a fixed list:

```
# J0B's authenticating proxy, from bundles/GATE-J0B/PARTIAL/authproxy2.py:38
#   LISTEN = ("127.0.0.1", 8081)
```

## 4. Still outstanding from GATE-RUNNER, unchanged by this gate

Every threshold in `build-evidence/runner/PROPOSED-PINS-DELTA.md` §3–§5 remains **PROPOSED**.
This gate ratified the *structure* and the *safety* settings and marked the *scale* numbers
`PROVISIONAL` in the config file itself; it did not measure any of them, and it could not — that
is what the first supervised batch is for.

# Code review — Wrought Foundry, tag `review-rc2` (`bbecf2d`)

Read-only review of a frozen checkout at `/home/kalib/review-rc1`. Nothing was built, started, or
modified; no `wrought-*` unit and no file under `/var/lib/wrought/state/` was touched. System
observation was limited to passive reads (`ss -lntpH`, `ps`, `/proc/<pid>/cmdline`,
`/etc/wrought/*.env|conf`), which touch no unit.

`authproxy3.py` is not in this checkout. It was read at
`/home/kalib/courier/Wrought/bundles/GATE-J0B-CLOSE/sources/authproxy3.py`, verified byte-identical
to the deployed `/var/lib/wrought/j0b/authproxy3.py` (`diff` clean).

Two items were excluded as known-and-assigned per the review brief and are **not** re-reported: the
`Bash(python3:*)` interpreter escape from the allowlist/ADD-DIRS boundary, and the hook content
matcher's document false-positives / `git mv` bypass.

**Headline:** two CRITICAL findings. `bin/verify-job:165` bind-mounts the result envelope
**read-write** into the sandbox while `classify()` validates nothing about its shape, so candidate
code can write its own PASS and reach `COMPLETED` (§4.1) — the one finding here that breaks the
project's central invariant. And `validate_allowed_tools` splits the tool header on commas while the
CLI splits on commas *or spaces*, so a space-separated bare `Bash` passes the guard and reaches the
child unscoped — a spelling one prompt in the courier uses today (§5.1). Method, agent counts and the
verification that did not complete are in the last section.

Standing context that sets severity throughout: `docs/PHASE-J-STATE.md:391` records `sudo -n -l` as
`(ALL) NOPASSWD: ALL` for `kalib`, and gate children run as `kalib`. The systemd scope, the hook,
and the allowlist are therefore the *only* fences — there is no credential-shaped second one. That
is already recorded, so it is framing here, not a finding.

---

## 0. Direct answer — `bin/gate13-measure:43`

```bash
stop_server() { pkill -f "$LLAMA .*--port $PORT" 2>/dev/null; sleep 3; }
```

**Yes. It matches the resident `wrought-inference.service`. This is not inference — I tested the
pattern against the live process's actual command line.**

The chain, each link from a file:

1. `bin/gate13-measure:23-29` sources `/etc/wrought/serving.env`, then sets
   `LLAMA=${LLAMA_SERVER:-/opt/wrought/bin/llama-server}` and `PORT=${WROUGHT_PORT:-8080}`.
   `serving.env` defines no `LLAMA_SERVER` (`grep -c` → 0) and sets `WROUGHT_PORT="8080"`.
   So the pattern resolves to `/opt/wrought/bin/llama-server .*--port 8080`.
2. `config/wrought-inference.service:39` runs `ExecStart=/opt/wrought/bin/serve-model`, and
   `bin/serve-model:151-157` **`exec`s** — so the wrapper is replaced, and the unit's main process
   *is* `llama-server`:
   `exec "$LLAMA_SERVER" "${ARGS[@]}" --device "$TOKEN" --host "$WROUGHT_HOST" --port "$WROUGHT_PORT" ...`
   with the same two defaults, from the same `serving.env`. The match is structural, not coincidental.
3. Live right now: `ps` shows `llama 102501 llama-server`; `ss -lntpH` shows `LISTEN 127.0.0.1:8080`.
   Its `/proc/102501/cmdline` is
   `/opt/wrought/bin/llama-server --model … --device Vulkan0 --host 127.0.0.1 --port 8080 --parallel 1 --metrics --api-key-file …`
   and `grep -cE "/opt/wrought/bin/llama-server .*--port 8080"` against that string returns **1**.

`pkill -f` matches an unanchored ERE against the full command line, so the resident server is a hit.
What happens next splits on who runs the gate, and **both branches are bad**:

**A. Run as root (`sudo bin/gate13-measure` — plausible, since lines 68 and 88 need `sudo` for
`drop_caches` and `dmesg`): production inference is killed silently.**
`pkill` defaults to SIGTERM. systemd treats SIGTERM as one of the four *clean* signals, so
`Restart=on-failure` (`wrought-inference.service:54`) does **not** restart, and
`OnFailure=wrought-alert@%n.service` (line 20) does **not** fire. The unit goes inactive with no
alert and no restart. `stop_server` is called four more times (lines 67, 81, 133), and the script's
last act is `stop_server` — so it leaves the box with no inference server and nothing that noticed.
Between those calls, gate13 runs its own `llama-server` on the same port as the invoking user with
none of the unit's hardening: no `IPAddressDeny=any`, no `ProtectSystem=strict`, no
`NoNewPrivileges`, no `DevicePolicy=closed`, and — stated in the script's own header at lines 15-19
— **no `--api-key-file`**, so the 401 that F-25 was closed on is absent for the duration.
`[UNVERIFIED]` whether `/health` specifically is auth-exempt on this build; either way the
`/completion` endpoint the script POSTs to at line 106 is not.

**B. Run unprivileged (as `kalib`): the kill fails, and the gate's measured value is silently
garbage.** The resident is owned by `llama`, so `kill(2)` returns EPERM. That failure is
double-swallowed: `2>/dev/null` eats the message and the return code is never tested (`set -uo
pipefail` at line 21 — no `-e`). `start_server` (line 44) then cannot bind 8080 and dies into
`$LOG`, but `wait_ready` (lines 46-55) polls `http://127.0.0.1:8080/health` — which **the resident
answers**. Cold-load "measurement" collapses to one poll interval, and `COLD MEDIAN` (line 77) is
recorded as a fraction of a second against a 60 s threshold it can never fail. That number is
destined for `pins.lock`. This is precisely the J-95 failure mode the project ratified a rule
against on 2026-08-04: the recorded value would not reproduce, and nothing in the script would say so.

**Prior evidence does not exonerate it.** `build-evidence/gate-13/gate-13-run.log` shows colds of
14.27/12.78/12.77 s — real loads, so the resident was *not* up during the recorded run. That makes
this a live hazard for the next run, not a past incident, which is what the brief asked.

**Where this sits in what the project already knows.** The class is ruled on and this instance
is logged. `docs/EXECUTOR-RAILS.md:501` is a standing rail — *"Use `pgrep -x` / `pkill -x`, or a pid
captured at launch. Never `pgrep -f` / `pkill -f`"* — written because the pattern recurred three
times in two days (§15 lists them: the reaper's `pgrep -f qemu-system`; `pkill -f stub_model.py`
killing the remote shell; a `pgrep -f "ssh -N -p 2222"` teardown that killed itself, exiting 144).
`docs/PHASE-J-STATE.md:521` carries it as risk-table row 9 — *"THREE LIVE INSTANCES … none edited —
`bin/gate13-measure:43` is the sharp one (a `pkill`)"* — assigned to `GATE-BOUNDARY`.

So the open question was never whether `-f` matching is dangerous in general; it was whether **this**
instance can reach the resident service. **It can, and the match is now demonstrated rather than
argued.** Note also that the reaper — the one instance that *was* fixed — additionally gained
`_reap_refusals` as a floor under it. `gate13-measure:43` has no floor of any kind: no pid check, no
refusal list, no return-code test.

**The prescribed fix is already written and is one line.** Rails §15 says "a pid captured at launch",
and `start_server` (line 44) already ends in `echo $!` — the PID is produced and thrown away. Capture
it and signal that pid; or use `pkill -x` plus a guard that refuses to run while the unit is active.
The `sleep 3` on line 43 is what makes a silently failed kill look like a successful one.

**Fix shape** (not applied — this is a read-only review): record the PID that `start_server`
already echoes (line 44) and signal that PID only; or, at minimum, refuse to run while
`wrought-inference.service` is active and check the kill's return code instead of discarding it.
The `sleep 3` after a silent failure is what converts a hard error into a plausible-looking number.

---

## 1. Containment — `bin/wrought-runner`

All three reviewed files are byte-identical to the deployed copies
(`diff -q bin/wrought-runner bin/wrought-runner-hook bin/gate13-measure` against
`/home/kalib/foundry/bin/`), so every finding below applies to production as it stands today.

### 1.1 [MEDIUM] The deny hook and the supervisor itself are writable by the thing they contain

`/etc/wrought/runner-hooks.json` is `root:root 0644` and points `PreToolUse` (matcher `"*"`) at
`/home/kalib/foundry/bin/wrought-runner-hook`. That file is `kalib:kalib 0775`, and it sits inside
`gate_cwd = /home/kalib/foundry` — the gate child's own working directory, running as `kalib`.
`bin/wrought-runner` itself is likewise `kalib:kalib 0775` in the same tree; it is not deployed to
the root-owned `/opt/wrought/bin` (only `serve-model` is).

The pointer was hardened; the target was not. `validate_hook_settings`
(`bin/wrought-runner:780-792`) parses the *settings JSON* and checks that `hooks.PreToolUse` exists
— it never hashes or verifies the hook script, and nothing else does either. The hook is re-`exec`d
per tool call, so a child that overwrites it neuters the deny layer from its very next tool call
onward, for itself and for every later gate in the batch. Overwriting `bin/wrought-runner` persists
past the batch into the next morning's manual start.

What an attacker or a confused gate does with it: writes six bytes into
`bin/wrought-runner-hook` (`import sys; print('{}')`) and the six catastrophic-action patterns are
gone, with `validate_hook_settings` still reporting the hook layer healthy. Writing to the cwd needs
no `--add-dir`, and it needs no Bash at all — **every gate prompt actually dispatched on this box
declares the unscoped `Write` and `Edit` tools** (`grep -h "^ALLOWED-TOOLS:"
/home/kalib/courier/Wrought/prompts/*.md`: all six carry `Write`/`Edit`, including the ones whose
Bash entries are otherwise carefully scoped). Neither tool has a scoping syntax, so the workspace
boundary is their only constraint — and the hook script is inside the workspace. The bare-`Bash`
refusal added by `GATE-RUNNER-POLISH` does not touch this path. `docs/PHASE-J-STATE.md:126-128` names the hook denylist as one of the three real
fences around a gate child; this removes one of three, silently.

### 1.2 [MEDIUM] The reaper's listener half kills on address novelty, and this box has an ephemeral
tailnet listener

`residue_snapshot` (`bin/wrought-runner:533-559`) keys listeners by the local address string from
`ss -lntpH` field 4. `residue_diff` (562-573) calls a listener NEW when that exact `IP:port` string
was absent from the before-snapshot. `reap` (603-653) then SIGTERMs and, after `terminate_grace_sec`
(5 s), SIGKILLs **every pid owning it** (`_listener_pids`, 520-530), and `run_one_gate:1152-1161`
raises `Halt(..., "gate-residue")` — a **latching** breaker (`NON_LATCHING` at line 113 is
`{gate-cap, wall-clock, batch-cost}` only) — whenever `new["any"]` is true, whether or not the kill
landed.

Nothing in this chain asks whether the gate caused the listener. On this box, `ss -lntpH` currently
shows `100.111.169.112:41875` and `[fd7a:115c:a1e0::c133:a971]:50385` — the Tailscale CGNAT and ULA
addresses, on two independently random high ports. Those are tailscaled's peerapi listeners and the
port is re-chosen by the daemon, not fixed. Any re-selection across a gate boundary presents as a
new address key.

`_reap_refusals` (575-601) is no help: it refuses only pid ≤ 1, the runner itself, its process group
and its session. tailscaled, `sshd`, a `wrought-*` unit, an operator's `ssh -L` forward, a dev
server — none are covered.

Two outcomes, both real:
- **Same-uid target** (anything the operator started as `kalib` during the batch — an `ssh -L`
  local forward binds as the invoking user): SIGTERM then SIGKILL land. The operator loses the
  process, and the batch latches.
- **Other-uid target** (tailscaled as root, `llama-server` as `llama`): `os.kill` raises
  PermissionError, caught at line 626 and recorded as `SIGTERM failed`, but the `gate-residue` Halt
  fires anyway. The next morning's good batch refuses to start until `--reset-breaker`.

This is the same false-positive harm the J-164 fix was written to prevent, arriving through the half
the fix explicitly exempted: `bin/wrought-runner:527` says the listener probe "never had the
`pgrep -f` disease in the first place". It has a different disease with the same symptom — matching
on a coincidence of form rather than on causation. `[UNVERIFIED]` how often tailscaled re-picks its
peerapi port in a 90-minute window; what is certain from the code is that any change presents as
new residue.

**Related, same function:** `wrought-inference.service` restarting during a gate is safe only
because its address key `127.0.0.1:8080` is constant. If it were *down* at the before-snapshot and
up at the after — the exact state §0 above can produce — it is reported as gate residue and reaped.

### 1.3 [MEDIUM] The byte-freeze tripwire is skipped on the two Halt paths that come after the
child has already run

`_run_one_gate_core` takes the baseline at line 1213 (`before = hash_paths(...)`) and re-asserts at
1249-1256. Between them sit two raises:

- line 1239: `raise Halt(f"{gate}: {detail} persisted across {attempts} retries", "api-backoff")`
- lines 1246-1247: `if deadman.tripped: raise Halt(f"dead-man: {deadman.tripped}", "deadman")`

Both fire *after* one or more children have run to completion inside the scope, and both skip the
re-assert entirely. `run_one_gate`'s `finally` (1130) tears down the HOME and re-raises, so the run
stops — but `freeze-after.json` and `freeze-verdict.txt` are never written, and the operator gets a
halt with no answer to the question the freeze exists to answer: *did the gate touch the store?*
Every other pre-child Halt (`stale-row`, `prompt-missing`, `no-allowed-tools`, `bare-bash`,
`add-dirs`, `hook-settings`) is fine, because it precedes the baseline. These two are not.

A gate that modified `orchestrator.db` and then wedged into a dead-man trip is exactly the run where
you most want the tripwire, and it is exactly the run where it does not fire.

### 1.4 [MEDIUM] A gate prompt sets its own cost ceiling, and the prompt comes from a public repo
over the network

`bin/wrought-runner:1192-1193`:

```python
budget = float(MAX_BUDGET_RE.search(text).group("usd")) if MAX_BUDGET_RE.search(text) \
    else float(cfg["limits"]["max_budget_usd_per_gate"])
```

The prompt's own `MAX-BUDGET-USD:` header **replaces** the config ceiling; it is never clamped to
it. `limits.max_budget_usd_per_gate` (8.0) is a default, not a cap. A prompt declaring
`MAX-BUDGET-USD: 500.00` gets 500, and `runner.conf` records the CLI's own cap overshooting 4.6x and
6.94x on top of that. The only backstop is `breakers.max_batch_cost_usd` (24.0), which is evaluated
in `main()` **after** the gate has finished and the money is spent.

The same pattern governs the security-relevant headers: `ALLOWED_TOOLS_RE` (line 87) and
`ADD_DIRS_RE` (line 89) read the gate's tool surface and directory surface from the prompt body.
Those prompts and the `QUEUE.md` that marks them `APPROVED` are fetched by `git_pull(courier, ...)`
at line 1346 from `origin` = `https://github.com/kscoutb/Wrought.git` — a **public** GitHub
repository — with no signature check, no allowlist of gate names, and no local record of what the
operator approved. `resolve_add_dirs` validates only that the named directories *exist*, so
`ADD-DIRS: /` passes.

Nothing on this path runs a secret scan. `bin/wrought-precommit-secret-scan` exists in this repo but
is referenced nowhere in `bin/wrought-runner` (`grep -n "secret\|scan" bin/wrought-runner` returns
only comment text), and the courier checkout has no git hooks installed (`ls .git/hooks` — nothing
but samples). `docs/PHASE-J-STATE.md` row 13 records the scan gap as **structural for gate children**
— a properly fenced gate cannot run it because rails §5.1's scan needs `sudo`. That reasoning does
not extend to the **runner itself**, which is unfenced, runs as `kalib` with `NOPASSWD: ALL`
available, and is the process actually executing `git add -A` and `git push` to the public remote.
It could run the scan; it does not, and no document records that as a decision. The human gate is the operator's manual start plus the word `APPROVED` in a
file pulled from that same remote.

Three regex notes that sharpen this: all three headers use `re.M` and take the **first** match
anywhere in the document, including inside a fenced code block or a quoted example, so a prompt that
*documents* a header above its real one silently uses the documented value; and
`validate_allowed_tools` (709-745) splits on `,`, which means a scoped entry containing a comma is
split into fragments before the bare-`Bash` test ever sees it.

### 1.5 [MEDIUM] `main()` catches only `Halt` and `KeyboardInterrupt`, so any other exception skips
the breaker write and the STATUS push

`bin/wrought-runner:1436-1443`. The epilogue that writes `breaker.json` and pushes `STATUS.md`
(1445-1470) lives *after* the `try/except Halt/except KeyboardInterrupt/finally` — so an exception
of any other type propagates out of `main()`, printing a traceback and leaving `halted: false` on
disk and a stale `STATUS.md` in the courier. For an unattended day-long runner, that is the failure
mode where the operator's only signal is silence.

Reachable raisers on the live path, none of them exotic:
- `residue_snapshot` (533-559): `subprocess.run(["virsh", ...], timeout=30)` raises
  `TimeoutExpired`, which `check=False` does not suppress; a missing `ss`, `virsh` or `systemctl`
  binary raises `FileNotFoundError`.
- `read_breaker`/`read_ledger` (1046-1051, 1098-1101): bare `json.loads(p.read_text())` — a
  truncated file raises `JSONDecodeError` at startup.
- `hash_paths` (287-300): `f.exists()` is true but `f.open("rb")` raises `PermissionError` if the
  frozen store is not readable by `kalib`. `[UNVERIFIED]` — settle with
  `ls -l /var/lib/wrought/state/orchestrator.db`; I did not read that path.

**Compounding it:** `write_breaker` (1053-1057) is a plain `p.write_text(...)` — not atomic, not
fsynced — while `RunLog.log` (188-193) *does* `fsync` every line. The latch, the single most
safety-relevant piece of state the runner owns, is the least durable thing it writes.

### 1.6 [MEDIUM] The ephemeral HOME leaks its credentials on the pre-`try` window, and a teardown
failure is only a log line

`run_one_gate` (1120-1131) calls `make_ephemeral_home` at 1121, then `residue_snapshot` at 1123 and
two `write_text` calls at 1124-1127 — **all before `try:` at 1130**. The `finally:
teardown_ephemeral_home(...)` covers everything inside the try (correctly, including non-`Halt`
exceptions), but not that window. Any of the `residue_snapshot` raisers from §1.5 leaves
`/var/lib/wrought/runner-state/ephemeral-homes/<GATE>-<epoch>/` on disk holding live copies of
`.claude/.credentials.json` and `.git-credentials` — the courier push token for the public repo.

Separately, `teardown_ephemeral_home` (397-409) catches its own failure and downgrades it to
`rlog.say("WARNING …")`. Its own comment reads "Loud: a surviving ephemeral HOME is two secrets left
on disk" — but the consequence is a log line and the batch continues, seeding a fresh HOME for the
next gate while the previous one's credentials remain.

Minor, same function: `make_ephemeral_home` (369-376) does `shutil.copyfile(src, dst)` and *then*
`dst.chmod(0o600)`. Between those two calls the credential file exists at `0666 & ~umask` — 0664 for
a default umask. The parent chain is 0700, which narrows but does not close it.

### 1.7 [LOW] The gate verdict is mechanical, but it is checked against artifacts the child authored

`verify_gate_postconditions` (953-983) requires the QUEUE row to read `BUNDLED`, the bundle directory
to be non-empty, and `sha256sum -c SHA256SUMS` to pass — with `cwd=bdir`. The child writes the
bundle, writes `SHA256SUMS`, and moves the QUEUE row. All three inputs are the child's own. The check
proves internal consistency, not that the work was done. It is described as the point where "the
child's own account of itself is evidence, not proof" — worth stating plainly that it verifies a
self-signed manifest, which is a weaker claim than the docstring implies.

---

## 2. `bin/wrought-runner-hook`

Excluding the two known-and-assigned items (document false-positives, `git mv` bypass).

### 2.1 [MEDIUM] The hook writes its audit line *before* it prints its deny, unguarded — so a failed
log write silently converts a deny into an allow

`bin/wrought-runner-hook:85-107`. The order is:

```python
decision, reason = decide(payload)      # 85
lp = log_path()                         # 86
if lp:
    with lp.open("a") as fh:            # 88  <-- NOT inside a try
        fh.write(json.dumps({...}))     # 89-98
if decision == "deny":
    print(json.dumps({...}))            # 100-103
```

`log_path()` (50-57) is exception-guarded and returns `None` on failure — that branch is safe, the
deny still prints. The dangerous branch is the one where `log_path()` *succeeds* (the config parsed,
`mkdir(parents=True, exist_ok=True)` worked) and the `open`/`write` then fails: ENOSPC, EDQUOT,
EROFS, EIO. The exception propagates out of `main()`, past `sys.exit(main())`, and Python exits **1**
having printed nothing on stdout.

Two links, with their evidence separated. **Certain from the code:** the deny JSON is never emitted,
so the hook contributes no decision at all. **From Claude Code's documented hook contract, not
measured in this repo** (`build-evidence/runner/raw/07` measured that a deny on stdout *is* enforced
and that a malformed settings file is silently ignored; it did not test hook exit codes): exit 2 is
the blocking code, and any other non-zero exit is a non-blocking error that surfaces stderr and lets
the call proceed. The conclusion survives either reading — with no decision on stdout, the outcome
falls back to the permission layer, and for an allowlisted call under `dontAsk` that is *allow*.

So the deny is lost precisely when the disk is full. And the file that fills the disk is
`hook-audit.jsonl` itself: it records **every tool call with its full `tool_input`**, is appended to
forever, and has no rotation, no size cap and no cleanup anywhere in `bin/wrought-runner`. The audit
trail is the mechanism that disables the enforcement.

Fix shape: print the decision first, log second, and wrap the log write in the same `try/except` that
already guards `log_path()`. The hook's own docstring says "Fail CLOSED" (line 79); on this path it
does not.

### 2.2 [LOW] The catastrophic-action patterns are near-miss fragile in ways worth knowing

Not a re-report of the assigned matcher issue — these are specific evasions of specific patterns
(`bin/wrought-runner-hook:34-47`):

- `\bcredstore\.encrypted\b` — a glob defeats it. `sudo cat /etc/credstore*/inference-api-key`
  contains no literal `credstore.encrypted`, and the box has `NOPASSWD: ALL`.
- `\bsystemctl\b.*\b(start|stop|…)\b.*wrought-` — requires the verb *before* the unit name and the
  literal `systemctl`. `systemctl wrought-inference stop` is not matched by any ordering it accepts,
  and `service`, `initctl`, a direct `dbus-send` to systemd, or `kill` on the unit's main pid are not
  the string `systemctl` at all.
- `orchestrator\.db` — matches the name, not the path. `sqlite3 /var/lib/wrought/state/*.db` and
  anything that reaches the store through a wrapper never contains the literal.
- The `rm -rf` alternation matches only the two flag orderings it enumerates; `rm --recursive
  --force`, `find … -delete`, and `shutil.rmtree` are all outside it.

The docstring is honest that the list is "deliberately SHORT" and that the hook is "NOT THE
BOUNDARY", so these are calibration, not surprises — but `docs/PHASE-J-STATE.md:126-128` counts this
denylist as one of the three fences that actually exist, and the gap between those two statements is
worth closing on purpose rather than by accident.

### 2.3 [LOW] The audit log records every `tool_input` verbatim

Line 95: `"input": payload.get("tool_input")`. Anything a gate passes to any tool — a URL with a
token, an inline credential, an env assignment — is written in plaintext to
`<state_dir>/hook-audit.jsonl` and kept indefinitely. Worth a redaction pass of the kind
`src/wrought_orchestrator/redact.py` already implements for prompts, given CLAUDE.md's rule that
prompts and responses are redacted before persistence.

---

## 3. `authproxy3.py` — the sealed key on stdin

Read at `/home/kalib/courier/Wrought/bundles/GATE-J0B-CLOSE/sources/authproxy3.py`, byte-identical
to the deployed `/var/lib/wrought/j0b/authproxy3.py`.

**The core contract holds.** I traced `KEY` from `main()` (490-499) through every use. It is read
from `sys.stdin.readline()`, held in a module global, and reaches exactly two places: the
`Authorization: Bearer` header rebuilt per request (`serve_one`, 380) and the redaction test in
`log_call` (77-78). It never touches `argv`, never enters `os.environ`, is never written to
`PIDPATH` (509-510, pid only) or `LOGPATH`, and the process never forks or execs. **No path puts the
key on argv, in the environment, or into a file.**

Empirically confirmed on the deployed artifacts: `grep -c -iE "bearer|authorization|api[-_]?key"`
returns **0** for both `/var/lib/wrought/j0b/authproxy3.out` (119 lines) and `apicalls.log`. Nothing
has leaked.

The findings below are about the *surface* around that contract, not a breach of it.

### 3.1 [MEDIUM] Every `diag()` is a write to a world-readable file, and one of them formats an
arbitrary exception

`diag` (85-87) writes to stderr. The operator redirects stderr to disk: `authproxy3.out` exists and
its first line is `authproxy3: key read from stdin (64 bytes), held in memory only`. That file is
`-rw-rw-r--` (0664) in `drwxr-xr-x /var/lib/wrought/j0b/` — **world-readable**, as is `apicalls.log`.
So "diagnostics go to stderr, not to the log" is true about `apicalls.log` and misleading about the
disk: every diag line is a permanent, world-readable record.

The one diag that formats data it does not control is `handle`'s catch-all (485-486):

```python
except Exception as e:
    diag("stream %d: unexpected %r" % (sid, e))
```

`%r` on an exception prints its `args`. The specific chain worth naming is `KEY.encode()` at line 380
raising `UnicodeEncodeError`, whose repr embeds **the whole offending string**. That is reachable
only if `KEY` holds surrogates, which requires a non-UTF-8 byte on stdin decoded under
`surrogateescape` — the default for `sys.stdin` in a C/POSIX locale.

**Precondition check, settled rather than asserted:** the deployed key is 64 bytes (the proxy's own
startup line says so) and hex, so it round-trips UTF-8 cleanly and **this path is not reachable with
the current key shape**. Report it as a latent trap for a future binary or base64url key, not as a
live leak. The cheap fix is `%s`-with-type rather than `%r`, or `repr(type(e))`.

### 3.2 [MEDIUM] Port 8081 is an unauthenticated credential-lending oracle for every local process

`LISTEN = ("127.0.0.1", 8081)` (line 61). The proxy authenticates nothing about its caller: `handle`
(464-488) accepts any connection and `serve_one` (380) attaches `Authorization: Bearer <KEY>` to
whatever request arrives. `config/wrought-inference.service:33` exists specifically so that an
unauthenticated POST to `/completion` returns 401 (the F-25 closure). While the proxy runs, any local
process — including a `wrought-runner` gate child, which runs as `kalib` on the same box — reaches
the authenticated model by connecting to 8081 and never sees the key.

Loopback binding bounds this to local processes, which is the right bound; the point is that the
proxy converts "holds the sealed credential" into "grants the credential's authority to anyone who
can open a socket", and nothing in the file narrows that to its intended client. `[UNVERIFIED]`
whether SO_PEERCRED-style caller checking was considered; nothing in the file suggests it.

Currently not live: `ss -lntpH` shows no listener on 8081, so the GATE-J0B-SURFACE seven-day-strand
class is not presently realized.

### 3.3 [MEDIUM] The file written to un-wedge the box has no timeout anywhere, and unbounded threads

The stated purpose (docstring, 10-19) is to stop a wedge in which abandoned generations queue up and
everything appears to hang. But:

- No socket in the file ever gets `settimeout()`. Not the listener (505-508), not the accepted client
  (487), not the upstream (`up = socket.socket(...)`, 366).
- `UpReader.fill` (139-142) calls `select.select(watching, [], [])` — **no timeout argument**, so it
  blocks indefinitely.
- `Reader.fill` (95-106) blocks in `recv` indefinitely.
- `handle` is spawned as an unbounded daemon thread per connection (487) behind `listen(64)`, with no
  cap and no accounting.

Concretely: a client that connects and sends nothing pins a thread in `read_head` → `fill` → `recv`
forever. An upstream that accepts and never responds pins a thread in `select` forever *unless* the
client disconnects. Change (b) closes the specific wedge where the client goes away; it does not
close the wedge where the client stays and the upstream does not answer, which is the shape the
docstring's own §4 describes as "queues behind ~9 abandoned unbounded generations and appears to
hang". The un-wedging file can still be wedged, and it accumulates threads while it is.

### 3.4 [LOW] Once the client's first bytes are peeked, the disconnect watch is dropped for the
lifetime of the request

`UpReader.fill`, 152: `self.watch = None  # real bytes, peeked not consumed; stop spinning`.

The docstring admits the `shutdown(SHUT_WR)` limit. This is a different one: for a **pipelined**
client — one that has already sent request N+1 while N is in flight — the peek returns real bytes
immediately on the first `select`, the watch is dropped on the first iteration, and the
client-disconnect cancellation that change (b) exists to provide is off for the rest of that request.
The wedge protection is silently absent exactly for the client that is fastest to send.

### 3.5 [LOW] `read_body` buffers an entire request body in memory with no cap

`read_body` (170-215) accumulates the whole body before the upstream connect, for every POST to
`chat/completions`. The `length` branch trusts `Content-Length` and the `chunked` branch loops
without any total bound — `HEAD_LIMIT` (68) caps the *head*, not the body. A single client can drive
the proxy's RSS to the size of whatever it claims to send. On a box where `MemoryMax` applies to gate
scopes and not to this manually-started process, that is unbounded.

### 3.6 [LOW] Non-injected requests are relayed with both `Content-Length` and `Transfer-Encoding`
intact

`serve_one` (374-382) rebuilds the head dropping only `authorization`, and — on the non-inject path —
keeps the client's `Content-Length` *and* `Transfer-Encoding` lines verbatim, while `framing`
(255-264) resolves the ambiguity by preferring chunked. That is a classic CL.TE shape. It is bounded
close to harmless here because a **fresh** upstream socket is opened per request (366) and closed in
`finally` (456-460), so there is no shared connection to desync a second party onto. Worth normalising
anyway — the injected path already does the right thing by dropping both and re-framing (384-385).

---

## 4. The oracle invariant and the verification sandbox — the strongest cluster in this review

This is the area where the review found the most, and where the findings bear directly on
`COMPLETED ⟹ the oracle passed`. All three below were independently confirmed by an adversarial
verifier, and I re-checked each against the files myself.

### 4.1 [CRITICAL] The result envelope is bind-mounted **read-write** into the sandbox, and
`classify()` validates nothing about it — so candidate code can write its own PASS

`bin/verify-job:163-165`:

```python
"--ro-bind", pack, "/work/pack.toml",
"--size", str(OUT_TMPFS_BYTES), "--tmpfs", "/work/out",
"--bind", p["envelope"], "/work/out/result.json",
```

Line 163 is `--ro-bind`. Line 165, two lines later, is `--bind` — read-write. The file that carries
the verdict is writable by the artifact whose verdict it carries, and candidate code executes in that
sandbox under pytest as the same uid as the runner.

`src/wrought_supervisor/classify.py` then treats that file as the classification primitive without
validating its shape. Once `complete` is truthy (line 306 handles the negative case), the verdict is
derived purely by scanning `envelope.get("checks") or {}` for bad outcomes (line 309 onward). It:

- never reconciles `envelope["checks"]` against the `envelope["pack"]["checks"]` the runner itself
  writes (`src/wrought_verifier/__main__.py:314-320`);
- never requires `envelope["verdict"]` to agree — line 301 reads that field only to test for
  `PACK_INVALID`;
- stops consulting `returncode` after rule 3, even though the runner sets it to 1 for any non-pass
  (`__main__.py:353`: `return 0 if worst == "pass" else 1`).

So the minimal forgery `{"phase":"serialization","complete":true,"checks":{}}` falls through every
loop and reaches, at line 404:

```python
return verdict(PASS, "all checks passed")
```

`oracle.verdict_for("PASS")` maps that to `all_pass`; `fsm.TABLE[("VERIFYING","all_pass")]` maps
`all_pass` to `COMPLETED`. **A task that passed nothing is recorded COMPLETED, and the `returncode=1`
that contradicts it is sitting unread in the same result dict.**

What candidate code does with it: fork a detached writer during the pytest check that loops writing
that JSON into `/work/out/result.json`. The runner's final `_write_envelope` (O_TRUNC, write, fsync,
`__main__.py:352`) lands, the interpreter shuts down, and the loop keeps writing until bwrap's pid 1
reaps the namespace. Last writer wins. The runner's only defence is its write ordering — "write
`result.json` as its final act" — which is a **race, not a check**. The verifier also noted a
race-free variant: `chmod` the file to 0444 after forging it, which is neither seccomp-denied nor
blocked by the dropped `CAP_DAC_OVERRIDE` (`bin/verify-job:343-348` records the EACCES behaviour as
measured under J-49).

Preconditions: adversarial or prompt-injected candidate code — squarely inside this project's stated
threat model (`docs/03` §10.7 rule 5 exists because candidate code may try to reach the network;
CLAUDE.md treats GGUF loading as untrusted-code execution). No config change; fires on the shipped
`bin/verify-job --sudo` path that `oracle.verify()` invokes and equally on the non-sudo path.

Note what is **not** claimed: `pack.py:112` forecloses a zero-check *pack*, so `complete:true` with
`checks:{}` is not reachable from the shipped runner by accident. This needs forgery. That is the
only thing standing between this and a routine false PASS.

Two independent fixes, either of which closes it: make line 165 an `--ro-bind` over a
runner-private path and have the runner write the envelope outside the sandbox; and/or make
`classify()` refuse an envelope whose `checks` keys do not match `pack.checks` and whose `verdict`
and `returncode` do not corroborate. The second is the one the doctrine already implies — "envelope
absent/invalid = SUBSTRATE" is a rule about *validity*, and validity is currently only tested for
presence and one boolean.

### 4.2 [HIGH] `/work` itself is writable, so state leaks between checks — contradicting the
documented writable set

`bin/verify-job:161-167` binds `/work/tests`, `/work/src`, `/work/pack.toml` and `/work/out` — but
never `/work`. With `--chdir /work` (line 167) and `_run(check, cwd="/work")`
(`__main__.py:332`), the cwd of **every** pack check is a writable directory on bwrap's root tmpfs
that persists from the candidate-executing `py.test.pytest` check into the `py.cov.threshold` check
that judges it.

`docs/03-verification.md:35` states the invariant this breaks, in as many words: *"the only writable
paths are the output dir and /tmp."*

The concrete channel: `pytest --cov` and the separate `coverage json` process (`packs/py.toml:38,47`)
communicate only through `/work/.coverage`, and no `COVERAGE_FILE` is set under `--clearenv`. So
candidate code executing in the pytest check can, after the coverage plugin has saved its data and
before the coverage check starts, delete or corrupt `/work/.coverage`, or drop a `/work/.coveragerc`
or `/work/pyproject.toml` whose `[report] include`/`omit` narrows measurement to a fully-covered
file. The general form is worse than the coverage case: **any later tool that resolves configuration
relative to its cwd is configurable by the artifact it is about to judge.**

### 4.3 [HIGH] The coverage threshold verdict is read from a candidate-writable file, with no
corroboration

`src/wrought_verifier/__main__.py:242-258`. The `py.cov.threshold` pass/fail is decided by the bytes
of `/work/out/coverage.json` — the same writable tmpfs where candidate code has already executed one
check earlier in pack order. The threshold branch of `_judge` checks neither `res["exit"]` nor any
provenance of that file, and `bin/gen-pack:126-134` gives the criterion no `error_exit` to check.

So any run in which `coverage json` fails to overwrite the file scores `pass` from
candidate-controlled bytes. The route: a candidate module imported by the oracle's tests registers an
`atexit` hook; pytest tears down its capture and coverage plugin before interpreter exit, so the hook
runs last inside the pytest check and (a) writes `/work/out/coverage.json` as
`{"totals":{"percent_covered":100.0}}` and (b) destroys coverage's data file, so the subsequent
`coverage json -o /work/out/coverage.json` errors and writes nothing. `_judge` opens the forged file,
gets 1.0 ≥ 0.85, records `outcome="pass"`. With every other check genuinely passing, `classify()`
reaches `verdict(PASS, …)` → `all_pass` → COMPLETED.

§4.1, §4.2 and §4.3 are the same defect seen at three depths: **the sandbox's writable region is
inside the trust boundary of the thing being judged.**

### 4.4 [MEDIUM] Byte-freeze: two confirmed gaps beyond the one in §1.3

- **The inter-gate window is not frozen at all.** The baseline is per-gate (line 1213) and re-asserted
  per-gate (1250), then a **fresh** baseline is taken for the next gate. Everything between —
  the ledger write, the breaker write, the cost accounting, `course_check` (1432), the git pushes and
  the 300 s pacing sleep (lines 1369-1445) — is unmeasured. Any mutation of
  `orchestrator.db{,-wal,-shm}` landing in that window is absorbed into the next gate's baseline and
  never reported. For a runner that halts the batch on a single changed byte inside a gate, the gap
  between gates is a strange place to stop looking.
- **[LOW] `hash_paths` encodes non-existence as the ordinary value `"ABSENT"`** (287-299) and
  `freeze_diff` (302-304) is a plain inequality, so an all-absent path set compares equal to itself.
  A `freeze_paths` list that is mis-pointed, empty, or wrongly typed — `load_config` checks only that
  the key is present — yields `HOLD — no change to any frozen path` while freezing nothing. The
  tripwire reports success most convincingly when it is pointed at nothing.

**One freeze finding was refuted, correctly.** A finder argued the tripwire is wrong to hash the
volatile `-wal`/`-shm` at all; the verifier refuted it against the project's own SOAK-3 ruling. I did
not carry it forward.

### 4.5 [MEDIUM/PLAUSIBLE] The ENOSPC substrate discriminator is a substring scrape of candidate-
reachable stderr

`src/wrought_verifier/__main__.py:127-128, 345-348`. The ENOSPC substrate verdict keys on a substring
match over each check's raw stderr — a stream candidate code can reach in the pytest check's
post-capture window — while the `out_exhausted` discriminator that is supposed to route a
self-inflicted quota exhaustion to `CODE_RESOURCE_DEFECT` is a single `statvfs` sample. CLAUDE.md's
hard rule requires exactly this pair to be *discriminated*, not blanket-classified (J-49 items 4/5);
the discrimination rests on a string in an untrusted stream.

### 4.6 The FSM half of the oracle path — clean where it counts, with four unverified leads

I read this myself as well as tasking it, and the core invariant is defended unusually well.
`worker.process_one` has **no default verdict**: the STOP-33b change replaced
`(verdict_script or {}).get(task_id, "all_pass")` with an indexed lookup, refuses when both a
verdict script and a verifier are supplied, refuses a task the script does not name, and does so
*before any transition and without acking* — so an unsourceable verdict ends in `HUMAN_REVIEW` via
the dead-letter sweep rather than in `COMPLETED`. `store.py` uses `isolation_level=None` with explicit
`BEGIN IMMEDIATE`/`COMMIT` per transition. `oracle.py` records `verdict_source` and asserts staging
so a verdict cannot be attributed to a generation that never happened. I found nothing to add.

**Four leads from the FSM finder could not be verified — their verifier agents died on a session
limit, not on a refutation.** They are recorded here as unverified leads, not as findings, and each
needs the adversarial pass it did not get:

1. `worker.py:329-345, 459-480` — an injected escalation driver's `all_pass` may be accepted as
   terminal with its provenance *defaulted* to `"post-escalation oracle run, attempt 4"`.
2. `worker.py:243-256, 578-581` — no branch for a task resting in `REPAIRING` or `ESCALATING`: the
   message is claimed, nothing transitions, and it is **acked** — the task is silently lost and F-27's
   dead-letter budget never counts it.
3. `bin/manufacture:174-186, 228-235, 255-262` — `manufacture` stages the candidate at its own loop
   counter while `worker.process_one` verifies at `repair_index`; one substrate incident
   desynchronises them permanently.
4. `worker.py:317-345` — STOP-33's closed-world task-identity refusal guards only the
   `verdict_script` branch; the production verifier branch drives whatever task `store.claim()`
   returned.

Lead 2 is the one I would chase first: a silent ack with no transition is the shape that loses work
without leaving a trace, and it is cheap to settle by reading the two cited ranges.

---

## 5. Further containment findings in `bin/wrought-runner`

### 5.1 [CRITICAL] `validate_allowed_tools` splits on commas; `--allowedTools` splits on commas **or
spaces** — and a prompt in the courier today exploits the difference by accident

This is the most important runner finding, and every link is measured in-repo.

1. `bin/wrought-runner:734` tokenises the header on commas only:
   `entries = [e.strip() for e in allowed_tools.split(",") if e.strip()]`, and the bare-`Bash` guard
   at 735 is `re.fullmatch(r"Bash\s*(\(\s*\))?", e)` over those entries.
2. The **raw** header string — not the parsed entries — is what reaches the child
   (`allowed_tools` at 824, from 1203/1231).
3. The CLI splits it differently. This repo captured the CLI's own help text at
   `build-evidence/runner/raw/02-claude-cli-surface.txt:29-31`:
   `--allowedTools, --allowed-tools <tools...>` / *"Comma or space-separated list of tool names to
   allow (e.g. "Bash(git *) Edit")"*.
4. Therefore `ALLOWED-TOOLS: Read Edit Write Bash` is **one** entry to the guard — which does not
   `fullmatch` — and **four** tools to the CLI, the last of which is bare `Bash`.
5. Bare `Bash` "ESCAPES the `--add-dir` workspace boundary entirely", per the runner's own measured
   2×2 quoted at lines 716-717.
6. **That exact spelling is live in the courier right now.** `grep -H "^ALLOWED-TOOLS:"
   /home/kalib/courier/Wrought/prompts/*.md` → `GATE-ST-1-v1.0.md: Read Edit Write Bash`. Of nine
   dispatched prompts, that one is space-separated with a bare `Bash`; the comma-separated bare-`Bash`
   prompts (`GATE-RUNNER-POLISH`, both `GATE-J0B-RESUME`s) trip the guard correctly, which is what
   makes the asymmetry invisible in practice.

So the single control `GATE-RUNNER-POLISH` added to make the documented workspace fence true fails
open on one of the two spellings the CLI documents, and `rlog.log(kind="tool-surface", …)` at 1208
records a **false** single-entry surface while it happens. The child gets unscoped Bash: writes
outside `gate_cwd` with no `--add-dir` at all — `/var/lib/wrought`, `~/.claude` (credentials,
auto-memory), and `/home/kalib/foundry/bin` (the runner and the hook from §1.1).

A second, smaller instance of the same parse mismatch: `GATE-RUNNER-ARM-v1.0.md` reads
`ALLOWED-TOOLS: Read, Edit, Bash   (declared per rails §13; this gate runs attended-direct, not via
the runner)`. Comma-splitting yields entries like `Bash   (declared per rails §13; this gate runs
attended-direct` — no `fullmatch`, so the guard stays silent, and the prose is forwarded to
`--allowedTools` as tool names. The header has no comment syntax and nothing rejects prose in it.

Fix shape: split on `[,\s]+`, and pass the **parsed, re-joined** entry list to `--allowedTools`
rather than the raw header, so the string the guard validated is the string the CLI receives.

### 5.2 [HIGH] Nothing ever signals the gate child: Ctrl-C leaves a fully-permissioned agent running
while the runner tears down its HOME and reports the batch stopped

`run_gate_child` launches with `start_new_session=True` (849) and then blocks in a bare
`rc = proc.wait()` (851). The file imports no `signal` module and installs no handler. So on Ctrl-C
or any non-`Halt` exception:

- the child is **never signalled** — `start_new_session=True` puts it in its own process group, so it
  does not even receive the terminal's SIGINT;
- `run_one_gate`'s `finally` (1137-1138) nevertheless `shutil.rmtree`s the ephemeral HOME **out from
  under the still-running child**, including the credentials it is using;
- the post-gate orphan sweep at 1146-1164 sits **after** the try whose only handler is `except Halt`
  (1135), so it never runs — no after-snapshot, no `residue-after.json`, no reap;
- `main` prints that the batch stopped.

`docs/EXECUTOR-RAILS.md:435-437` and `build-evidence/runner-harden/REPORT-RUNNER-HARDEN.md` §3.3 both
state the sweep "is in the wrapper's `finally`". It is not. The child runs on for up to
`RuntimeMaxSec` (5400 s) with its full tool surface, on a QUEUE row left at `RUNNING`, while the
supervisor that was containing it has exited. `DeadMan.shutdown()` in `main`'s `finally` (1454) stops
the watchdog, so even that lever is gone.

This is the exact requirement `GATE-J0B-SURFACE` produced — "a killed/dead gate must strand none" —
and it holds for a `Halt` and fails for Ctrl-C, which is the more likely way an operator ends a
day-long batch.

### 5.3 Corroborated: the two findings I had reached independently

Both were confirmed at HIGH by the workflow, with detail I did not have:

- **`git add -A` to the public courier** (§1.4). Confirmed, with the frequency pinned: three to four
  pushes *per gate* (1224, 1286, and 1032 via `push_status` at 1365/1436/1468), over a tree every gate
  child holds write access to, and `grep -c` for the mandated pre-push secret scan in
  `bin/wrought-runner` returns **0**.
- **The breaker latch is recorded only for `Halt` and `KeyboardInterrupt`** (§1.5). Confirmed, and the
  verifier named a raiser I had not: `git()`'s own `timeout=` (202-204) raises `TimeoutExpired`, which
  `check=False` does not suppress — a hung `git pull` in the courier is enough to skip the entire
  epilogue.

### 5.4 Confirmed medium cluster

Each of these was confirmed by an adversarial verifier against the file:

- **The retry loop multiplies every per-child bound by five** (1228-1247). Up to five children per
  gate, each in a *fresh* scope carrying the full `RuntimeMaxSec` and the full `--max-budget-usd`,
  with the dead-man window reset at 1234/1244 — while `verdict.json` records `cost_usd` from the
  **last iteration only** (1280). So the cumulative `max_batch_cost_usd` breaker is fed an
  undercount, on top of the self-declared budget of §1.4.
- **`DeadMan` has no authority over the main thread** (872-912). Its only levers are
  `systemctl --user stop self.unit` and `self.proc.kill()` (905-909), and `detach()` (852) nulls both
  the instant the child exits. The watchdog never signals or raises into the main thread. So during
  exactly the runner-side phases its docstring exists to cover — "a git operation that never returns,
  a wedged post-condition check" — it can do nothing. The one unbounded blocking call it should be
  covering is `subprocess.run(["sha256sum","-c","SHA256SUMS"], …)` in
  `verify_gate_postconditions` (1271), which has no `timeout=`. And `self.tripped` is read at exactly
  one site (1246), before that call.
- **The transient scope is never stopped** (802-812, 849-852). `run_gate_child` creates a
  `systemd-run --user --scope` per gate and never stops it; the file's only `systemctl stop` is behind
  `if self.unit:` and `detach()` has already cleared it. A descendant a normally-exiting gate leaves
  behind keeps the scope ACTIVE — which is consistent with risk-row 11's "leftover `failed` transient
  scope units", still present.
- **`extra_child_env` is splatted last, unvalidated and unlogged** (704-705). One undocumented config
  key silently overrides every deliberate child-env control set above it: the ephemeral-HOME override
  (687), `DISABLE_AUTOUPDATER` (699), the output-token and Bash-timeout caps. It predates the fence
  (`raw/07-wrought-runner.BEFORE.py:294`) and both later hardening passes inserted their keys *above*
  it without revisiting the order.
- **The `ADD-DIR:` singular trap is wrong in both directions** (764). The guard is
  `if m_bad and not m_dirs:` — so any line-initial `ADD-DIRS:` suppresses the check entirely, and a
  prompt carrying **both** headers silently discards every directory on its singular line. That
  reinstates the unannounced missing-workdir failure the check was written to end, in the same
  fix-by-addition shape.
- **`reap()` reports failures as successes** (608-652 → 1156-1159). Every per-target outcome is
  appended to the same `killed` list — including `virsh destroy rc=<nonzero>`, `NOT SIGNALLED —
  <refusal>` and `SIGTERM failed: Operation not permitted` — then each is logged as `REAPED` and the
  whole list is interpolated as `Terminated: {killed}` into the latching Halt. An EPERM on another
  user's process reads, in the evidence, as a reaped one. Given §1.2, that is the *normal* case.
- **A skipped libvirt probe is indistinguishable from a measured-empty one** (535, 540-546).
  `snap["domains"]` is left at its `[]` initialiser and the fact of the skip goes into `snap["notes"]`
  — a key no code in the 1489-line file ever reads. So a `libvirtd` inactive→active transition across
  a gate makes every pre-existing domain look new.
- **`ran.json` is permanent and unclearable** (1094-1106, 1351). It keys on gate name alone, never
  consults the verdict it records, and no CLI path clears it — `--reset-breaker` rewrites only
  `breaker.json`. A gate that ran and is later re-approved under the same name is filtered out
  forever, silently.
- **The stale-row refusal is unreachable** (1178-1181). It re-tests the parse-time `status` of a row
  its sole caller already filtered to `APPROVED` (1351/1363), and it reads the snapshot rather than
  re-reading `QUEUE.md`, so it cannot see a concurrent change either. The guard whose docstring cites
  the `GATE-J0B-SURFACE` incident cannot fire.
- **The push-retry loop discards its recovery `git pull --rebase` return code** (226-234) and the file
  contains no rebase-state check and no `git rebase --abort`. A conflicted rebase leaves the shared
  courier clone on a detached HEAD, and the loop then exhausts `push_retry_max` and latches.

### 5.5 `authproxy3.py`, confirmed and refuted

Confirmed at MEDIUM: the unauthenticated credential-lending listener (§3.2) and the total absence of
deadlines (§3.3) — the verifier confirmed there is no `settimeout`, `SO_RCVTIMEO` or `SO_KEEPALIVE`
anywhere in the file and that `select.select(watching, [], [])` at line 147 has no timeout, so an
accepted connection that sends nothing blocks forever in `Reader.fill`'s `recv`.

**Refuted, and I agree:** the `UnicodeEncodeError` → `%r` → disk chain from §3.1. My own empirical
check reached the same place from the other side — the deployed key is 64 bytes of hex and round-trips
UTF-8 cleanly. §3.1 stands only as a latent trap for a future binary key; treat it as a note, not a
finding. A second refutation: `log_call`'s redaction comparing a locale-decoded `KEY` against a
latin-1-decoded path was argued and refuted.

**Not verified** (verifier agents lost to the session limit, not refuted): the pipelined-client watch
disarm (§3.4), the unbounded `read_body` (§3.5, though a second finder reached it independently and
its verifier returned LOW/PLAUSIBLE), `accept()` raising `OSError` and silently killing the whole
proxy, and the observation that the injected `max_tokens=24000` exactly equals the server's
`--reasoning-budget 24000`, leaving zero content budget after reasoning. That last one is worth
settling: it is the kind of off-by-a-whole-budget that would look like a model failure.

---

## 6. The destructive-command sweep beyond `gate13-measure`

### 6.1 [HIGH] `bin/gate39-chaos` honours an inherited `WROUGHT_DB` and can unlink the production
event store

`bin/gate39-chaos:41-47` scopes its destructive state with
`os.environ.setdefault("WROUGHT_DB", …)`. `setdefault` **yields to an inherited value**. Alone among
the six harnesses that re-point the store, this one ships no containment assertion — so an inherited
`WROUGHT_DB` silently overrides the gate-scoped path, and `reset()` (69-75) then unlinks
`orchestrator.db*` and `rmtree`s the effects dir — fourteen times per run — against whatever the
variable points at. That falsifies the file's own line 46 claim, *"never the production literal
(J-80)"*, and reproduces the J-80 destruction its header describes as fixed. The store is the single
spend authority per `pins.lock:1313` and `ledger.py:125-141`.

The fix is the one its five sibling harnesses already have: assert the resolved path is not the
production literal, and fail if it is.

### 6.2 [MEDIUM] `bin/gate14-swap` has no `trap`, and an interrupt leaves the box quietly serving the
wrong model

`grep -n "trap "` over all 80 lines of `bin/gate14-swap` returns nothing. Its restore at line 70 runs
only on the success path. An interrupt or SIGHUP between lines 44 and 56 leaves the box **healthy and
silently serving the 24 B fallback**; between 56 and 70 it leaves `wrought-inference` stopped with
`active-profile` repointed. Neither state announces itself — the first is the more dangerous, because
everything downstream keeps working against the wrong model.

### 6.3 `bin/gate13-measure`, beyond the `pkill` of §0

- **[MEDIUM] It is the only gate that binds the production listener address.** It takes
  `PORT=${WROUGHT_PORT:-8080}` from `serving.env` with no per-gate override — unlike all six peer
  gates — and starts `llama-server` there with no `--api-key-file` and none of the unit's confinement.
  Its last statement is `stop_server`, so on the happy path it exits having left nothing serving.
- **[LOW] It prints a fabricated `COLD MEDIAN` when its own measurements fail.** Lines 72-77 drop
  failed cold repetitions without counting them, so the summary prints a median over whatever survived
  with `n` undisclosed — and with **zero** survivors the empty `awk` result is coerced by
  `printf '%.2f'` into `0.00 s`, which sits inside the `< 60 s` PASS band. The warm path (83-84) has
  no FAIL guard at all. This is the §0 hazard's payload: a number that passes its own gate and would
  not reproduce, which is precisely what J-95 was ratified to prevent.

---

## 7. What to fix first

Ordered by what an attacker or a bug actually gets, not by tidiness:

1. **§4.1** — `bin/verify-job:165` `--bind` → `--ro-bind`, plus structural validation in
   `classify()`. This is the only finding that breaks `COMPLETED ⟹ the oracle passed`.
2. **§5.1** — split `ALLOWED-TOOLS` on `[,\s]+` and pass the parsed list, not the raw header. A
   prompt in the courier exercises this today.
3. **§4.2 / §4.3** — bind `/work` read-only (or make each check's cwd private) and corroborate the
   coverage threshold against `res["exit"]`.
4. **§0** — signal `gate13-measure`'s own captured PID instead of a `pkill -f` pattern; refuse to run
   while `wrought-inference.service` is active.
5. **§6.1** — add the containment assertion `gate39-chaos`'s five siblings already have.
6. **§5.2** — install a signal handler and move the orphan sweep into the `finally` the docs already
   claim it is in.
7. **§2.1** — print the deny before writing the audit line, and guard the write.
8. **§1.1** — hash the hook script at launch, or move it (and the runner) out of `gate_cwd`.

§1.2 (the reaper's address-keyed listener diff) is the one I would think about rather than patch
quickly: the honest fix is an ownership-and-causation test, and `_reap_refusals` is the wrong layer
for it.

## What I could not settle, and how to settle it

Stated as questions rather than findings, per the house convention:

- **Whether `/health` specifically is auth-exempt on this llama.cpp build.** It bears on how bad §0's
  unprivileged branch is. `[UNVERIFIED]` — settle with one unauthenticated `curl` against
  `/health` and against `/completion` on the resident server.
- **How often `tailscaled` re-selects its peerapi port.** §1.2's mechanism is proven from the code;
  the frequency of the tailnet-specific trigger is not. Settle by sampling `ss -lntpH` across a
  restart and across a netmap change.
- **Whether `/var/lib/wrought/state/orchestrator.db` is readable by `kalib`.** Decides whether
  `hash_paths` raises `PermissionError` into §1.5's un-caught path. I did not read that path, per your
  instruction. `ls -l` settles it.
- **Permissions on `<state_dir>/hook-audit.jsonl`.** §2.3's exposure depends on them. `ls -l
  /var/lib/wrought/runner-state/`.
- **The four FSM leads in §4.6.** Their adversarial verification did not run.
- **Four `authproxy3.py` items in §5.5**, same cause.

## Method, and what that means for these findings

I read `bin/gate13-measure`, `bin/wrought-runner-hook`, `bin/serve-model`,
`config/wrought-inference.service`, `/etc/wrought/{serving.env,runner.conf,runner-hooks.json}` and
`authproxy3.py` myself in full, and `bin/wrought-runner` in full across its containment, freeze,
verdict and control-flow sections. §0 and §1–3 are mine, derived and checked directly.

In parallel I ran a 12-dimension multi-agent pass over the same files plus
`src/wrought_{orchestrator,supervisor,verifier}/` and `bin/verify-job`, with each finding handed to a
separate adversarial verifier instructed to refute it and to default to refuted when it could not
prove the chain from the file. 68 agents; 59 completed. **43 findings survived verification, 4 were
refuted, and 9 verifiers died on a session limit — leaving 8 findings unverified**, which are marked
as leads in §4.6 and §5.5 and are *not* counted as findings. I re-checked every CRITICAL and HIGH
against the files myself before writing it here; where a verifier corrected a line range or a
severity, I used the corrected value.

Two of my own findings were corroborated independently at HIGH (§5.3). One of my own — the
`UnicodeEncodeError` key-leak chain — was refuted, and I agree with the refutation on independent
grounds (§5.5); it is downgraded in place rather than removed, because the trap returns the moment
the key stops being hex.

**Where my grade and the verifiers' disagree, both are recorded here rather than averaged.** An
independent verifier reached the same mechanism at one step lower than I did on three findings, and
the headings carry the verifier's lower grade and my dissent is recorded here:

- **§1.1** (hook and runner writable inside `gate_cwd`) — graded MEDIUM by the verifier, on the
  ground that the hook is documented as defence-in-depth rather than the boundary. I would argue HIGH,
  because `docs/PHASE-J-STATE.md:126-128` counts the denylist as one of three fences that actually
  exist and this removes one of them without a trace; but the docstring's own disclaimer is a fair
  reading, so MEDIUM stands in the heading.
- **§1.2** (address-keyed listener reap) — graded MEDIUM, on the ground that the unprivileged runner
  gets EPERM against the interesting targets and the realised harm is a latched batch rather than a
  dead daemon. That is correct as far as it goes; the same-uid targets in §1.2 are the part that keeps
  me closer to HIGH.
- **§2.1** (deny lost on a failed audit write) — graded MEDIUM, because the fail-open step depends on
  harness exit-code semantics this repo has not measured. Stated that way in §2.1 already.

§1.3, §1.6 and §3.2 were graded MEDIUM by both, and the two off-scale "MEDIUM-HIGH" labels I first
wrote for §1.3 and §3.2 are corrected to MEDIUM.

Nothing was executed, built, or modified. `.review/` is gitignored (`.gitignore:19`), so this report
is not a commit candidate.

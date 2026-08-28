# REPORT — GATE-RUNNER-HARDEN (v1.0, ATTENDED)

**Both unattended-run blockers are CLOSED and MEASURED. The config is ratified. One new,
unplanned finding is the most important thing in this report: the `claude` CLI self-updated out
from under its own pin, hours before this gate ran, invalidating part of the evidence base the
runner rests on.**

Date 2026-08-28 · executor Claude Code (Opus) on `forge-mini` · advisor Fable
Workdir `/var/lib/wrought/runner-harden/` · bundle `bundles/GATE-RUNNER-HARDEN/`

---

## 0. Verdicts, up front

| Item | Verdict |
|---|---|
| **BLOCKER 1 — cross-session steering** | **CLOSED, measured.** But **not by the mechanism the prompt named**, and a private HOME *alone* would not have closed it. §2. |
| **BLOCKER 2 — the reaper** | **CLOSED, measured.** Detects, enumerates, terminates, halts latched; proven for a gate that dies as well as one that finishes. §3. |
| **Config ratification** | **DONE.** Six keys added, **zero values changed**, verified by mechanical leaf-diff. §4. |
| **Rails + courier mirrors** | **DONE** — `APPROVED` status, `ALLOWED-TOOLS` header, scope-parenting/teardown rule. §4.2. |
| **Dry-run regression** | **9 of 9 pass**, including a real `claude` gate end-to-end through the hardened runner. §5. |
| **Byte freeze** | **HOLD.** `raw/00` vs `raw/99`, three paths identical. |
| **Course-check** | **UNTOUCHED and still disabled.** No credential read, no sudo configured. |
| **NEW — CLI version drift** | **The pinned build is not the installed build.** §6. Needs an operator ruling. |

Transport deviation, surfaced not absorbed: **the prompt arrived as chat text, not a file — the
third consecutive failure of rails §7**, and this prompt's own header asked for a file upload.
Content was intact and the block count was exactly 2, so it was archived verbatim and run, the
same disposition `GATE-RUNNER` and `GATE-RECONCILE` recorded.

---

## 1. What was done first

Per rails §10, before any work: both carried adjudications were extracted **mechanically**
(`sed -n '17,25p'` and `sed -n '26,31p'` over the archived prompt, never retyped) and written to
`bundles/GATE-RUNNER/ADJUDICATION.md` and `bundles/RECONCILE/ADJUDICATION.md`, with both QUEUE
rows set `ADJUDICATED`.

**Deviation, minor:** the prompt said to write the second file to `bundles/GATE-RECONCILE/`. That
directory does not exist — `GATE-RECONCILE`'s bundle is at `bundles/RECONCILE/`. Creating the
named directory would have split the bundle in two, so the verdict went to the real one. Flagged
rather than silently absorbed.

Health at baseline (`raw/01`): `wrought-inference.service` **active**, `/health` **200**,
`amdgpu runpm` **0**, dGPU `0x744c` at `0000:c7:00.0`, VRAM **19 619 987 456 / 25 753 026 560**.

---

## 2. BLOCKER 1 — the steering breaker, and where the prompt's premise broke

### 2.1 The prompt's stated mechanism is wrong, and following it would have shipped a hole

The prompt says: *"raw/16 established discovery is keyed under `$HOME`
(`~/.claude/daemon/roster.json`)"*, and prescribes a private HOME.

`roster.json` read `{"workers": {}}` with `updatedAt` of **2026-08-20** through **all six probes
this gate ran — including the two in which the gate child WAS discoverable.** It is a stale, empty
registry for a different mechanism and it carries no gate child. Had the fence been built on the
prompt's stated mechanism and validated against that file, it would have "passed" while changing
nothing.

### 2.2 What is actually true: two surfaces, two different keys

Six probes, each in the runner's exact shape, varying only `$HOME` and `$XDG_RUNTIME_DIR`
(`raw/06`, captures in `raw/20`, harnesses in `raw/16`–`raw/18`):

| Probe | `HOME` | `XDG_RUNTIME_DIR` | child socket landed in | listed by a peer session? |
|---|---|---|---|---|
| A, F2 | real | real | `/run/user/1000/cc-socks/<pid>.sock` — **shared** | **YES** |
| E3 | **private** | real | `/run/user/1000/cc-socks/<pid>.sock` — **shared** | **no** |
| D2 | **private** | **private** | `$EPHEMERAL_HOME/xdg-runtime/cc-socks/<pid>.sock` | **no** |

Liveness overlap is established for every row rather than assumed: the polls record the child's
socket present at the wall-clock second each `ListAgents` call was issued.

- **The peer listing is keyed on `$HOME`** — E3 vs F2 isolates it, identical but for HOME.
- **The addressable socket is keyed on `$XDG_RUNTIME_DIR`** — D2 vs E3 isolates it.

**Closing one does not close the other.** A private HOME alone (E3) removes the child from the
listing **while leaving its socket in the shared directory, still addressable by path.** *Not
listed* is not the same claim as *not addressable* — so the runner now does **both**.

### 2.3 The measured minimum HOME is three files, not "the credentials live there, so we can't"

`raw/16` gave two reasons a private HOME was impossible. Both are false on this build:

- *"the Claude Code credentials live there"* — incremental seeding shows the auth minimum is
  **exactly one file**: empty HOME → `is_error=true`, `terminal_reason=api_error`,
  `"Not logged in · Please run /login"`; `+ .claude/.credentials.json` → completes.
  `.claude.json` is **not** required; the CLI writes a fresh one, which is the fence working.
- *"a private `XDG_RUNTIME_DIR` leaves the dir empty and changes nothing"* — on 2.1.250 the
  private dir **does** get a `cc-socks/` and the socket **is** created there. `raw/16` probe 3 was
  still listed because it kept the **real HOME**, not because the runtime dir did nothing.

Shipped seed: `.claude/.credentials.json` (auth), `.gitconfig` + `.git-credentials` (the gate's
own courier push).

### 2.4 Auth and the courier push both survive the isolated shape — verified externally

Probe **D2**, under a private HOME *and* a private runtime dir: **7 turns, 0 permission denials**,
wrote a file into the courier bundle, committed it, and **pushed it to `origin/main`**. Verified
from this session, not from the child's self-report:

```
git branch -r --contains bfe3328   ->  origin/main
git rev-list --count origin/main..HEAD  ->  0
```

The artifact it pushed is `raw/05-probeD-child-push-proof.txt`, carrying the child's **own** view
of both socket directories — which agrees with the external poll.

### 2.5 One mechanical gotcha, measured

The private runtime dir must be applied to the `claude` process **only, inside the scope**.
Overriding it for the whole invocation kills the launcher (probe C1):
`Failed to connect to user scope bus via local transport: No such file or directory`, 0 bytes of
output. `systemd-run --user` needs the real user bus. The working form is
`systemd-run --user --scope … /usr/bin/env XDG_RUNTIME_DIR=<private> claude -p …`.

### 2.6 Residual, stated plainly

- **The isolation is one-directional.** A gate child cannot be seen or addressed by the operator's
  sessions. The reverse is *not* closed: the child's filesystem view still includes
  `/run/user/1000/cc-socks`, and probe D2's own output lists this session's socket. Whether it
  could *use* that is untested and outside this gate's scope. Recorded, because "isolated" without
  a direction is the kind of claim this project keeps having to retract.
- **`DBUS_SESSION_BUS_ADDRESS` is still in the env allowlist**, so a child can still reach the user
  bus by naming the real runtime dir explicitly — which is exactly how the Phase-3 leak stub had to
  be written to leak at all (§3.1). Defence in depth, not a boundary. **Not changed this gate**;
  proposed for the next.
- **Credential rotation** — the ephemeral HOME holds live credential copies. Across all eight
  probe children the real `~/.claude/.credentials.json` was **unchanged** (mtime 08:55, before this
  session) and every copy still hashed identical to it. Whether a *long-running* child would
  refresh a token into its ephemeral copy — and discard it at teardown, leaving the real one
  stale-but-valid — is **[UNTESTED]**.

---

## 3. BLOCKER 2 — the reaper

Two layers, per the prompt. The second is the load-bearing one.

### 3.1 Proof 1 — detect, enumerate, terminate, latch (`raw/09`)

A stub gate leaked a guest-shaped process **and** a listener on `127.0.0.1:8081` — the port J0B's
credential-holding auth proxy actually used (`bundles/GATE-J0B/PARTIAL/authproxy2.py:38`) — and
cleaned up neither, while reporting `is_error=false, terminal_reason=completed`.

```
GATE-LEAKSTUB: REAPED pid 26264 (…/qemu-system-x86_64-STUB): terminated by SIGTERM
GATE-LEAKSTUB: REAPED pid 26267 (listener on 127.0.0.1:8081): terminated by SIGTERM
HALT [gate-residue]: GATE-LEAKSTUB LEFT RESIDUE and was reaped — new qemu pids ['26264'];
                     new domains []; new listeners ['127.0.0.1:8081']
RUNNER-EXIT=2   breaker: halted=true latched=true
```

Post-run: units inactive, **0** listeners on 8081, **0** stub processes.

**An honest note on how this test had to be built.** The first attempt failed to leak *at all*,
because the new private runtime dir stopped the stub's own `systemd-run --user` from reaching the
user bus. That is a real incidental hardening effect — and it is *not* a containment claim, because
the stub then leaked successfully by naming `/run/user/1000` explicitly, which it could do because
`DBUS_SESSION_BUS_ADDRESS` is still inherited. Both runs are in `raw/09`.

### 3.2 Proof 2 — scope-parenting (`raw/10`)

A stub spawned a guest-shaped process as a **plain background child** (a scope descendant, not a
transient unit) and hung past `RuntimeMaxSec=10`:

```
child killed at 10.2s; descendant gone WITHOUT the sweep touching it
sweep: new qemu {} · new domains [] · new listeners {}
disposition = SUBSTRATE
```

This is the evidence behind the new rails §13.1 rule: a gate that must be reapable-by-scope
launches plain `qemu-system` as a scope descendant, never via libvirtd, whose domains re-parent
into `machine.slice` and escape the scope.

### 3.3 Proof 3 — a gate that halts *and* leaks (`raw/12` §I)

The case the sweep's placement exists for. Both faults are reported; neither masks the other:

```
HALT [gate-residue]: GATE-BOTH LEFT RESIDUE and was reaped — new qemu pids ['31428'] …
  | the gate had ALSO already halted: [byte-freeze] GATE-BOTH: BYTE-FREEZE TRIPWIRE — …
```

The sweep is in the wrapper's `finally`, so it runs for a gate that **died** — which is the actual
J0B failure mode — and it also fired on a *pre-flight* halt (`raw/10`, missing prompt file).

### 3.4 A defect this gate found in the runner and fixed

`classify()` mapped the kill signatures as `143`/`137` — the **shell's** 128+signal convention.
The runner does not go through a shell: `Popen.wait()` returns the **negated** signal, so a
`RuntimeMaxSec` kill arrives as **`-15`** and an OOM as **`-9`**. The old map matched neither and
printed **`unknown signal`** for the two signatures it exists to name:

```
before:  rc=-15: unknown signal
after:   rc=-15: SIGTERM — RuntimeMaxSec deadline
```

The *classification* was never wrong — no-parseable-JSON is the discriminator, exactly as in
`docs/03` §10.7 — but the detail line was wrong in the one place an operator would read it.
Found by `raw/10`, fixed, and re-proven on the same scenario in the same file.

---

## 4. Ratification

### 4.1 `/etc/wrought/runner.conf` — six keys added, zero values changed

Verified mechanically (`raw/15`), not asserted: every non-comment leaf of the before and after
files was compared.

```
CHANGED values: NONE      REMOVED keys: NONE
ADDED: ephemeral_home.{enabled,root,seed}   reaper.{enabled,qemu_pattern,terminate_grace_sec}
RATIFIED, re-read from the installed file:
   permission_mode = dontAsk   ·   limits.memory_swap_max = 0
   course_check.enabled = False ·  breakers.missing_allowed_tools = halt
```

Every setting now carries a `_ratified_*` or `_provisional*` marker in the file itself, so the
distinction survives without anyone remembering it. `ephemeral_home` and `reaper` were made
**required** keys: a config predating them would otherwise start **silently unhardened**.

### 4.2 Docs

`docs/EXECUTOR-RAILS.md` gains three sections: **§12** (`APPROVED` is the only runnable status;
`ALLOWED-TOOLS` is a mandatory header), **§13** (scope-parenting, explicit libvirt teardown, and
the sweep as a latching fault), **§14** (the two-key fence, with the "not listed ≠ not addressable"
warning). Courier `README.md` gains one mirror line for each of §12 and §13–14; `QUEUE.md`'s
legend gains the `APPROVED` row.

---

## 5. Dry-run regression — 9 of 9

Scratch courier, scratch DB trio, scratch state dirs. The real store was never referenced by any
dry-run config and its freeze held.

| # | Scenario | Result |
|---|---|---|
| A | missing `ALLOWED-TOOLS` header | `HALT [no-allowed-tools]`, latched |
| B | byte-freeze tripwire | `HALT [byte-freeze]`, latched |
| C | consecutive failures (cap 2) | `HALT [consecutive-failures]`, latched, `consecutive=2` |
| D | latched breaker refuses next start | `BREAKER IS LATCHED`, no gate started |
| E | `--reset-breaker` | `halted=False`, `reset_by=operator` |
| F | unknown QUEUE status *(unplanned)* | `HALT [queue-parse]` — refused an ambiguous queue |
| G | dirty scratch courier *(unplanned)* | `HALT [git]` — refused to run on a dirty tree |
| H | orphan sweep + scope-parenting | §3.1–3.3 |
| I | **real `claude` child, end-to-end** | **`PASS`** |

**I is the one that matters most.** A real gate child, driven by the runner, under the new
ephemeral HOME and private runtime dir, produced a bundle, its `sha256sum -c` verified, the QUEUE
row moved to `BUNDLED`, the **mechanical** verdict was `PASS`, the byte freeze held, the sweep was
clean, and the ephemeral HOME was **torn down** (`raw/11`). Its own report shows
`HOME=…/ephemeral-homes/GATE-HAPPY-…` and only this session's socket in the shared directory.

F and G were unplanned — both were caused by mistakes in *my own* harness (an invalid status
string, an invalid `git add -q`). Both are kept in the evidence rather than edited out, per rails
§4: the runner refused each rather than guessing, which is two more breakers proven for free.

---

## 6. THE FINDING NOBODY ASKED FOR — the CLI moved under its own pin

```
claude --version                    ->  2.1.250        (pins.lock proposal says 2.1.238)
~/.claude/.last-update-result.json  ->  version_from 2.1.238 → version_to 2.1.250
                                        at 2026-08-28T12:56:04Z — hours before this gate ran
```

`GATE-RUNNER` wrote that this pin *"is load-bearing in a way a version pin usually is not"*,
because every containment claim is a behaviour of that specific build. **That build is gone.**

**What is re-measured on 2.1.250** (by this gate, incidentally): `dontAsk` is still
default-deny-with-allowlist; the `raw/12` allowlist spellings still behave; `RuntimeMaxSec` still
kills; and the steering surfaces, in full.

**What is NOT**: `raw/07` (hooks under `-p`), `raw/08` (budget overshoot, `BASH_DEFAULT_TIMEOUT_MS`
backgrounding), `raw/14` (the `--add-dir` workspace boundary), `raw/06`'s full permission-mode
matrix. Those are now **UNVERIFIED-ON-THE-INSTALLED-BUILD** — a statement about the evidence base,
not a defect found.

The sharp version: a 20-hour unattended batch in which gate 3 silently upgrades the CLI underneath
gates 4–6, and the evidence names one version while three gates ran on another. That is a P3
reproducibility failure of exactly the kind `pins.lock` exists to prevent.

An off-switch exists — `DISABLE_AUTOUPDATER` is present in the binary (`raw/03`) — but **this gate
did not set it and did not test it**: disabling updates for the operator's own interactive sessions
is not a change a gate makes unilaterally. Proposed in `PROPOSED-PINS-DELTA.md` §1.

---

## 7. Adversarial audit

Its job is to find the claim this report cannot support. Nine items.

1. **"Blocker 1 is closed" — closed against *whom*?** Against another local Claude Code session
   on the real HOME, which is the stated requirement and the realistic threat. It is **not** closed
   against a process that reads `/var/lib/wrought/runner-state/ephemeral-homes/` — anything running
   as `kalib` or root can find the private socket and the credential copies there. On a single-user
   box that is the same trust boundary as before, but it is not "unreachable".
2. **`ListAgents` is one observer, not a proof of unaddressability.** Every "not listed" row is a
   negative result from one tool. No one tried to address a private-HOME child *by socket path*.
   The socket-location evidence is mechanical and strong; the listing evidence is one instrument.
3. **The still-untested case is still untested.** `raw/18`'s open question — *what an APPROVED
   steering message does to a running gate child* — is **not answered**. It is now *unreachable by
   the ordinary path* rather than *answered*, which is what the prompt asked for and less than
   knowing.
4. **`n=1` for two rows of the matrix.** A/F2 (listed) is n=2; E3 (private HOME, not listed) and
   D2 (both private, not listed) are each **n=1** with confirmed liveness overlap. The socket
   locations are corroborated by the polls and by D2's own internal capture; the *listing* results
   are single observations.
5. **The reaper is proven against stubs, never against a real guest.** By instruction — this gate
   was told not to boot one. A real `qemu-system` with a disk, and a real libvirt domain, are both
   untested. The `virsh destroy` path in particular has **never executed**: `libvirtd` was inactive
   throughout, so the domain probe was skipped every time. **That code path is unexercised.**
6. **`terminate_grace_sec = 5` is unmeasured and its path is untested.** Every stub died on the
   first SIGTERM, so the SIGTERM-ignored → SIGKILL branch never ran. Marked PROVISIONAL.
7. **`pgrep -f qemu-system` will match innocent processes** whose command line merely contains the
   string — my own supervising shell did, repeatedly. It is harmless here because the before/after
   diff cancels anything already running, but a shell that *starts* during a gate and mentions
   `qemu-system` would be killed by the sweep. Loud rather than silent, but a false positive.
8. **The end-to-end PASS ran a 42-second gate, not a 20-hour batch.** Nothing here tests the scale
   numbers, and one gate's ephemeral HOME says nothing about six of them across a day.
9. **This gate changed safety-critical code and graded its own work.** The proofs are mechanical
   and the harnesses are committed so they can be re-run, but the reviewer should re-run them
   rather than take §3 and §5 on trust.

---

## 8. Forward look

The first **supervised** batch is a fresh **GATE-J0B (Phases 5–7 + seed rebuild)** through the
hardened runner, with an `ALLOWED-TOOLS` header, setting the provisional scale numbers while the
operator watches. Then **ST-1** clears the kernel/AppArmor drift before any manufacturing.

Two things the advisor should rule on before that batch:

1. **The CLI auto-update (§6).** Re-pin to 2.1.250? Set `DISABLE_AUTOUPDATER` for gate children,
   or for the box? Re-run GATE-RUNNER's Phase-1 matrix on the installed build?
2. **`DBUS_SESSION_BUS_ADDRESS` in the child env allowlist (§2.6).** Dropping it for the inner
   process would remove a child's remaining handle to the user bus. Cheap, but it is a containment
   change and this gate did not make it unasked.

---

## 9. REVISION 2, same session — a gap this report's own audit missed

**Added after the bundle was first pushed. Nothing above is edited; this is a correction by
addition (rails §4), the same discipline `GATE-RUNNER`'s `raw/18` and `GATE-RECONCILE`'s `raw/20`
followed.** Evidence: `raw/23`.

The advisor asked the question §7 should have asked: **every runner invocation in this session used
a scratch config.** The **installed** `/etc/wrought/runner.conf` and the **modified**
`bin/wrought-runner` had never been loaded together — and Phase 4 made `ephemeral_home` and
`reaper` *required* keys, so a name mismatch would have surfaced for the first time at the
operator's next start. Audit item 9 said "re-run the harnesses"; it did not notice that no harness
touched the installed file.

**Result, in two parts.**

**(a) The change itself is compatible.** The runner's own `load_config` accepts the installed file:
every required key present, `permission_mode` accepted, `ephemeral_home` and `reaper` both found
and well-formed.

**(b) But the runner still cannot start — and this is PRE-EXISTING, not introduced here.**

```
/home/kalib/foundry/bin/wrought-runner --config /etc/wrought/runner.conf --status
  PermissionError: [Errno 13] Permission denied: '/var/lib/wrought/runner-state'
  EXIT=1
```

`/var/lib/wrought` is `root:root 0755`, and `state_dir` has read `/var/lib/wrought/runner-state`
since `GATE-RUNNER` wrote the config on 2026-08-21 — it is in `raw/08`, the BEFORE copy. Every
`GATE-RUNNER` dry run and every run this session used a **scratch** `state_dir` under a directory
`kalib` owns, so **neither gate ever exercised this path.** The operator's first real start would
have met an unhandled traceback rather than a clean refusal.

**Not fixed here, deliberately.** Creating a directory under `/var/lib/wrought` needs root and is
outside this gate's authorized change set (`bin/`, `/etc/wrought/runner.conf`, docs, a scratch
dry-run); rails §1 also says a session creates state only in its own workdir. **Operator action,
recorded rather than taken:**

```
sudo mkdir -p /var/lib/wrought/runner-state
sudo chown kalib:kalib /var/lib/wrought/runner-state
sudo chmod 700 /var/lib/wrought/runner-state
```

The `0700` is not cosmetic: `ephemeral_home.root` defaults to
`/var/lib/wrought/runner-state/ephemeral-homes`, and those directories hold live credential copies.

**A second self-correction, smaller.** The first attempt at the `load_config` check had a bug of my
own — `importlib.machinery` was not imported. The broken attempt is left in `raw/23` above its
correction rather than edited out.

**What this says about the audit.** §7 found nine things and missed the one that would have stopped
the operator's next command. The pattern is the one this project keeps re-learning and which §7
item 9 half-stated: the audit checked what the proofs *concluded*, not which configuration they
*ran against*. Recorded as a finding against this session, not a footnote.

**Also recorded, deliberate residue:** the scratch dry-run harness at
`/var/lib/wrought/runner-harden/dry/` is left in place — stubs, scratch git repos, latched scratch
breakers, and a `fakehome` whose credentials are the literal string `not-a-real-credential`. The
`raw/22` re-scan confirms it holds no real secret. It sits inside this gate's own workdir, which
rails §1 allows, and no prompt enumerated it for deletion. **Operator's call.**

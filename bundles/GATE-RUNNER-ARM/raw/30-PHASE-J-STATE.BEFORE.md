# PHASE-J-STATE — the live rail position for Phase J

**Read this first.** It is the one doc a fresh session needs to know where Phase J stands. It is
updated at every wind-down (`docs/EXECUTOR-RAILS.md` §9); if it disagrees with a prompt's stated
premise, **this file and the box win, and the disagreement is reported, not reconciled by guessing.**

Rails for running a session: `docs/EXECUTOR-RAILS.md`. Versions: `pins.lock`. Narrative and
per-gate detail: `BUILD-JOURNAL.md`.

**Last updated 2026-08-28 by `GATE-RUNNER-HARDEN`** (reconciled the same day by `GATE-RECONCILE`). The same facts, with the full evidence
pointers, are in the courier at `bundles/RECONCILE/SNAPSHOT.md` — that file and this one are
mirrors; if they ever disagree, the raw captures under `bundles/RECONCILE/raw/` decide.

## CLOSED

| Gate | Closed | Evidence | Manifest |
|---|---|---|---|
| **GATE-J0-RECON** | 2026-08-10 | `build-evidence/j0-recon/` | `sha256sum -c SHA256SUMS` |
| **GATE-J0A-SUBSTRATE** | 2026-08-10; **accepted 2026-08-11 (J-155)** | `build-evidence/j0a/` (v1.1, the round that aborted on U-1) and `build-evidence/j0a/round2/` (the round that closed it) | **35/35** and **48/48** verified in the committed copy |
| **GATE-HJ1-HYGIENE** | ran 2026-08-12; **ADJUDICATED — ACCEPTED, CLOSED** (advisor Fable; verdict recorded 2026-08-28 at courier `bundles/GATE-HJ1/ADJUDICATION.md`) | `/var/lib/wrought/hj1/` → courier `bundles/GATE-HJ1/` | J-157 |
| **GATE-RUNNER** | ran 2026-08-21; **ADJUDICATED — ACCEPTED as an attended build** (advisor Fable; verdict recorded 2026-08-28 at courier `bundles/GATE-RUNNER/ADJUDICATION.md`). **Not cleared for unattended use** on three conditions, two of which `GATE-RUNNER-HARDEN` has now closed; the third is a supervised batch | `build-evidence/runner/` → courier `bundles/GATE-RUNNER/` | J-159 |
| **GATE-HJ2-HEARTBEAT** | never ran as its own session; **FOLDED INTO GATE-RECONCILE 2026-08-28** — rails §9/§10, README mirror, HJ1 verdict recorded | `docs/EXECUTOR-RAILS.md` §9–10 | J-158 |
| **GATE-RECONCILE** | ran 2026-08-28; **ADJUDICATED — ACCEPTED, CLOSED** (advisor Fable; verdict at courier `bundles/RECONCILE/ADJUDICATION.md`) | `/var/lib/wrought/reconcile/` → courier `bundles/RECONCILE/` | J-160 |
| **GATE-RUNNER-HARDEN** | ran 2026-08-28; **BUNDLED** — both unattended-run blockers CLOSED and measured, config ratified | `build-evidence/runner-harden/` → courier `bundles/GATE-RUNNER-HARDEN/` | J-161 |

Disposition of the two J0A rounds, and why re-running was mechanically excluded:
`build-evidence/j0a/ACCEPTANCE-2026-08-11.md`. **Round 2 supersedes v1.1 wherever they differ.**

## ESTABLISHED FACTS

- **The seam is QEMU user-mode networking.** A guest reaches a host service bound on `127.0.0.1`
  at **`10.0.2.2`** — SLIRP proxies from host loopback. The **NAT bridge does not** and is refused
  by bind scope: the same service over two transports gives opposite answers. *(The stronger claim
  that this proves the API-key gate resists guest-origin traffic was **retracted by round 2 itself** —
  the 200/200/401 triple is identical from host loopback, i.e. origin-invariant.)*
- **Boot-to-ssh ≈ 15 s** (plain QEMU, user-net) and a **full discard-and-revert cycle ≈ 15 s**
  (`rm` overlay → `qemu-img create` → boot → first ssh). Upper bounds at ±2 s, 2 s poll.
- **The base image is immutable by hash.** Three guest boots wrote through qcow2 overlays and the
  backing file's sha256 never moved — the disposable-guest model's core assumption is *measured*.
  Pin: `pins.lock` `virtualization.guest_base_image`.
- **The daemon model is monolithic and socket-activated.** `libvirtd` starts on first `virsh`
  connect; the modular `virtqemud`/`virtlxcd`/`virtlockd` peers are **not installed** (systemd
  reports them `not-found` — never present, not present-and-off).
- **The dGPU is selected by device id `0x744c`, never by card index.** Same discipline as the
  serving rail's name-based device selection.
- **`kalib` is in `kvm(991)` and `libvirt(972)`.** `usermod -aG kvm,libvirt` added exactly one
  group — `libvirt` was already there, added by `libvirt-daemon-system`'s postinst at install time.
  An unprivileged `kalib` opens `/dev/kvm` read-write (closes recon FINDING V-1).

- **The batch runner exists: `bin/wrought-runner`**, started manually by the operator once a day.
  Config `/etc/wrought/runner.conf` (strict JSON, never sourced; every threshold
  **PROPOSED-UNRATIFIED**). Companions: `bin/wrought-runner-hook` (PreToolUse, deny-or-defer),
  `bin/wrought-course-check` + `bin/wrought-course-post` (halt-only cloud check, **disabled**).
  **No daemon and no timer** — the manual daily start IS the human gate (operator ruling 2026-08-21).
- **Containment is measured, and two of the measurements contradict the obvious reading:**
  - **`acceptEdits` and `auto` SILENTLY RUN un-allowlisted Bash calls.** Only `dontAsk` and
    `manual` are default-deny-with-allowlist on **claude 2.1.238**. The runner refuses to start
    in any other mode.
  - **`MemoryMax` alone does NOT cap memory on this box** — the overrun is paid out of the 8 GiB
    swap file and the process exits 0. **`MemorySwapMax=0` is what makes it a kill** (rc=137).
  - `RuntimeMaxSec` kills a real `claude` child at the deadline (rc=143, measured 30.3 s vs 30 s).
  - **PreToolUse hooks DO fire under `claude -p`** (this refutes the RT0 pass-2 claim) — but a
    **malformed settings file is silently ignored under `-p`**, so hooks are defence-in-depth only
    and the runner json-validates them before every launch.
  - **A Bash call targeting a path OUTSIDE the session cwd is denied under `dontAsk`** even when
    explicitly allowlisted. Gates need a minimal, explicit `--add-dir`.
- **The gate child is now FENCED — and the two surfaces have DIFFERENT keys** (`GATE-RUNNER-HARDEN`,
  `build-evidence/runner-harden/raw/06`). The **peer listing** is keyed on **`$HOME`**; the
  **addressable socket** is `$XDG_RUNTIME_DIR/cc-socks/<pid>.sock` and is keyed on the **runtime
  dir**. Closing one does NOT close the other — a private HOME alone leaves the socket in the
  shared directory, still addressable by path. Each gate now gets **both**, per gate, torn down
  with it. **`~/.claude/daemon/roster.json` is NOT the discovery key**: it read `{"workers": {}}`
  and stale through all six probes, including the two in which the child *was* listed.
  - The **minimal ephemeral HOME is three files** — `.claude/.credentials.json` (auth; without it
    the child reports *"Not logged in · Please run /login"*), `.gitconfig` and `.git-credentials`
    (the gate's own courier push). `.claude.json` is deliberately not seeded.
  - The private runtime dir must be applied to the **claude process only, inside the scope**;
    overriding it for the whole invocation kills `systemd-run --user`, which needs the real bus.
  - A child in the fully isolated shape **authenticated, ran 7 turns with 0 denials, and pushed to
    `origin/main`** — verified externally by `git branch -r --contains`, not from its self-report.
- **Nothing a gate starts may outlive it, and the runner enforces it** (`raw/09`, `raw/10`,
  `raw/12`). A post-gate sweep diffs {qemu processes, libvirt domains, listening sockets}; any NEW
  survivor is enumerated, terminated, and the batch **HALTS with a latching `gate-residue` fault**.
  It runs from the wrapper's `finally`, so it fires for a gate that **died** — the actual J0B
  failure mode — and a halt-plus-leak reports **both** reasons rather than masking one. A plain
  scope **descendant** is reaped by systemd at `RuntimeMaxSec` with no sweep needed; a **libvirt
  domain is not**, which is why rails §13.1 exists.
- **`Popen.wait()` returns NEGATED signals, not the shell's 128+n.** `GATE-RUNNER` recorded the
  kill signatures as `143`/`137`; through the runner they arrive as **`-15`** and **`-9`**.
  `classify()` matched neither and printed `unknown signal` for the two it exists to name — found
  and fixed by `GATE-RUNNER-HARDEN` (`raw/10`). Classification was never affected;
  no-parseable-JSON remains the discriminator.
- **The child's exit integer never classifies a run** — every permission denial exited 0, and
  `subtype` read `success` on a hard failure. Classification is on `is_error` / `terminal_reason`
  / no-parseable-JSON. Same doctrine as the result envelope (`docs/03` §10.7), reached independently.
- **The gate verdict is MECHANICAL**: QUEUE row `BUNDLED` **and** `bundles/<gate>/` present **and**
  `sha256sum -c SHA256SUMS` verifies **and** the byte freeze held. In the dry run this caught a gate
  that reported `is_error=false, terminal_reason=completed` and had produced no manifest at all.
- **Per-project auto-memory is a live cross-invocation channel**, so "fresh context per gate" is not
  free. The runner snapshots it per gate, and on change preserves the delta and restores the baseline.

## RESIDUE — deliberate, operator-accepted

Left in place by J0A round 2 and **attributable to that session, not inherited**:

- libvirt `default` network **active / autostart / persistent**, plus `virbr0`.
- **nftables 91 → 182 lines.** No new table (6 → 6), but **four new base chains registering
  netfilter hooks** and six `LIBVIRT_*` chains; hook registrations 10 → 14.
- **Two permanent host listeners**: `dnsmasq` on `192.168.122.1:53` (tcp+udp) and `0.0.0.0%virbr0:67`.
  The network is autostart+persistent, so these return every boot.
- `libvirt-guests.service` (hooks host shutdown), `qemu-kvm.service`, `machines.target` — all
  enabled by the packaging. **No `systemctl enable/start/stop/restart` was issued by any J0 session.**
- ~~The **dirty boot-2 `overlay.qcow2`** (55 MB) in the round-2 workdir~~ — **DELETED by J0B
  Phase 0** on 2026-08-20, together with `round2/seed.img` (copied and hash-verified first).
  `GATE-RECONCILE` then deleted J0B's own two scratch files on 2026-08-28: `j0b-overlay.qcow2`
  (1.16 GB) and `seed.img`. The base image, `j0a_key` and `user-data` are **kept**.
- **The `GATE-RUNNER-HARDEN` scratch dry-run harness**, `/var/lib/wrought/runner-harden/dry/` —
  stubs, scratch git repos, latched scratch breaker files, and a `fakehome` whose credential is the
  literal string `not-a-real-credential`. Verified to hold **no real secret**
  (`build-evidence/runner-harden/raw/22`). Inside that gate's own workdir, which rails §1 allows;
  no prompt enumerated it. Kept so the proofs can be re-run. **Operator's call.**
  The nine hand-built probe ephemeral HOMEs from the same gate **were deleted** (enumerated, with
  reasons, `raw/22`) because they held real credential copies.
- **Still present, NOT enumerated by any prompt and therefore not deleted:**
  `/home/kalib/overlay.qcow2` (196928 B, 2026-08-11, J0A-era stray), `/var/lib/wrought/j0b/__pycache__/`,
  three stale `*.pid` files, and two untracked prompt files at the foundry root
  (`GATEHJ2HEARTBEATv1.0.md`, `GATEJ0BSURFACEv1.2.md`). Operator's call.

## RULINGS

| Ruling | Where it lives |
|---|---|
| **Hygiene precedes capability** — the biggest risk is becoming too complex for a fresh session to maintain | operator, standing |
| OS substrate **tracks `resolute-security`**; drift **recorded per gate, not fought** (U-1) | `pins.lock` `substrate.os_update_policy` |
| Cloud-image **GPG verification waived** in favour of the hash pin | `pins.lock` `virtualization.guest_base_image.gpg_signature` |
| **C4 relaxed to audited-not-replayable** | operator ruling |
| **Vision is a separate, lower-assurance lane** | operator ruling |
| Foundry commits are **operator-authored** | `docs/EXECUTOR-RAILS.md` §4 |
| Prompts travel as **files**, with a block-count check | `docs/EXECUTOR-RAILS.md` §7 |
| Transport is the **public Wrought courier** | `/home/kalib/courier/Wrought/README.md` |

## OPEN

- **NEXT ON THE RAIL: a SUPERVISED `GATE-J0B` (Phases 5–7 + seed rebuild), run through the hardened
  `wrought-runner` while the operator watches**, setting the PROVISIONAL scale numbers. It is
  gated on **two advisor/operator rulings** (both in `build-evidence/runner-harden/REPORT-RUNNER-HARDEN.md`
  §8): the `claude` CLI auto-update, and whether to drop `DBUS_SESSION_BUS_ADDRESS` from the child
  env allowlist. **After that batch: ST-1**, which is still unsatisfied on two triggers. A gate must
  not be dispatched ahead of this order without saying so.
- **BLOCKER TO THAT BATCH — `wrought-runner` CANNOT START with its installed config.** Measured
  2026-08-28 (`build-evidence/runner-harden/raw/23`):
  `PermissionError: [Errno 13] Permission denied: '/var/lib/wrought/runner-state'`, exit 1.
  `/var/lib/wrought` is `root:root 0755`. **Pre-existing** — `state_dir` has read
  `/var/lib/wrought/runner-state` since `GATE-RUNNER` wrote the config on 2026-08-21, and every dry
  run of both gates used a scratch `state_dir`, so **the path was never exercised**. The change
  itself is fine: the runner's own `load_config` accepts the installed file. **Operator action, not
  taken by the gate that found it** (it needs root, and rails §1 confines a session to its workdir):

      sudo mkdir -p /var/lib/wrought/runner-state
      sudo chown kalib:kalib /var/lib/wrought/runner-state
      sudo chmod 700 /var/lib/wrought/runner-state

  The `0700` matters: `ephemeral_home.root` sits inside `state_dir` and holds live credential copies.

- **`GATE-J0B-SURFACE` is `RESET` — it must be RE-DISPATCHED FRESH.** Resolved 2026-08-28. It ran
  **Phases 0–4 of 8** on 2026-08-20 and stopped mid-Phase-4 with no report, no bundle, no journal
  entry and no update to this file. **Its substantive result stands and is preserved**: the egress
  pinhole is proven — from inside the locked guest, DNS fails (`curl 6`), the SLIRP gateway to the
  host model server is refused (`curl 7`), and only the authenticating proxy answers `200` with the
  real server behind it. **Phases 5 (agent turn), 6 (interception shim) and 7 (wind-down) never
  ran.** Partial evidence: courier `bundles/GATE-J0B/PARTIAL/` (25 raw captures, 4 serial logs,
  both proxy sources); the account is `WHAT-HAPPENED.md` there. **A re-dispatch must rebuild the
  seed** — after this session's enumerated deletes, no cloud-init seed exists on the box; rebuild
  is `cloud-localds` + the surviving `/var/lib/wrought/j0a/user-data`, with no install needed.
- **NEW SAFETY FINDING — a dead gate session does not reap its guest.** J0B's Phase-3c guest ran
  **~7 days**, from 2026-08-20 to the box shutdown on 2026-08-27: three sibling serial logs record
  a `reboot: Power down`, `serial-p3c.log` records none, and the overlay was last written at the
  shutdown. **Strongly supported, not directly observed** — J0B launched QEMU unprivileged, so no
  journal record exists. The authenticating proxy holds the inference API key **in memory** and was
  still bound throughout. **Direct input to the `wrought-runner` ratification**, which is built to
  run 20 hours unattended.
- **`GATE-HJ2-HEARTBEAT` is FOLDED INTO `GATE-RECONCILE` and its debt is PAID** (2026-08-28). The
  heartbeat rule is `docs/EXECUTOR-RAILS.md` **§9**, the adjudication-carrying rule is **§10**, both
  are mirrored in the courier `README.md`, and the HJ1 verdict is recorded. **J-158**, reserved for
  it, is spent on exactly that.
- **Pin drift, measured mechanically 2026-08-28: 36 of HJ1's 51 ratified pins HOLD, 15 DRIFTED, 0
  missing.** All 15 are the libvirt closure, `12.0.0-1ubuntu5.2` → `5.3`, one `unattended-upgrade`
  transaction on 2026-08-20. Recorded in `pins.lock` `drift_observed`; **not re-pinned**. **Open
  question: libvirt is not a declared ST-1 trigger — does a point-release need its own re-measure?**
- **`cloud-image-utils` is load-bearing for this workstream but is ABSENT from `pins.lock`** — a
  pins gap, flagged 2026-08-28, not filled by the gate that found it.
- **Transport has now failed THREE times in a row**: `GATE-RUNNER`, `GATE-RECONCILE` and
  `GATE-RUNNER-HARDEN` all arrived as **chat text, not files** (rails §7) — the last one despite its
  own header asking for a file upload. Both had intact content and correct block counts, so both
  were archived verbatim and run — but the rail is not being met.
- **The runner's SCALE thresholds are still PROVISIONAL** and are what the first supervised batch
  is for; `/etc/wrought/runner.conf` now marks every setting `RATIFIED` or `PROVISIONAL` in the
  file itself. **RATIFIED 2026-08-28:** `permission_mode: dontAsk`, `memory_swap_max: 0`, the
  breaker latch-semantics, `course_check.enabled: false`, the **`APPROVED` QUEUE status** and the
  **required `ALLOWED-TOOLS:` header** (both now `docs/EXECUTOR-RAILS.md` §12).
- **The course-check needs operator ratification before it may be enabled**: it points the sealed
  §13 escalation credential at a new purpose, and its enabled path requires passwordless `sudo`.
- **The steering breaker is CLOSED** (2026-08-28, `GATE-RUNNER-HARDEN`) — see ESTABLISHED FACTS.
  Two residuals are recorded rather than closed: the isolation is **one-directional** (a child can
  still see `/run/user/1000/cc-socks`, though it cannot be seen there), and
  **`DBUS_SESSION_BUS_ADDRESS` is still in the child env allowlist**, so a child can reach the user
  bus by naming the real runtime dir explicitly. **The `raw/18` question — what an APPROVED
  steering message does to a running gate child — is still UNANSWERED**; it is now unreachable by
  the ordinary path rather than understood.
- **NEW AND URGENT — the `claude` CLI SELF-UPDATED out from under its pin.** `2.1.238 → 2.1.250`
  on **2026-08-28 at 12:56:04Z**, hours before `GATE-RUNNER-HARDEN` ran
  (`build-evidence/runner-harden/raw/02`). `GATE-RUNNER` had written that this pin is load-bearing
  in a way a version pin usually is not, because **every containment claim is a behaviour of that
  build**. Re-measured on 2.1.250: `dontAsk` default-deny, allowlist spellings, `RuntimeMaxSec`,
  and the steering surfaces. **NOT re-measured, and therefore UNVERIFIED-ON-THE-INSTALLED-BUILD:**
  hooks under `-p` (`raw/07`), the budget overshoot and `BASH_DEFAULT_TIMEOUT_MS` backgrounding
  (`raw/08`), and the `--add-dir` workspace boundary (`raw/14`). An off-switch exists —
  `DISABLE_AUTOUPDATER` is present in the binary — but was **not set and not tested**.
  **Operator ruling needed before the first supervised batch.**
- **The reaper's `virsh destroy` path has NEVER EXECUTED.** `libvirtd` was inactive throughout, so
  the domain probe was skipped on every run and only the process/listener halves are proven. Same
  for `reaper.terminate_grace_sec` (PROVISIONAL, unmeasured): every stub died on the first SIGTERM,
  so the SIGKILL escalation branch is untested.
- **The runner has never run unattended.** Longest batch: two gates, ~20 minutes. The 20-hour
  wall-clock budget and the 6-gate cap are untested at scale.
- **ST-1 re-run is QUEUED and UNSATISFIED**, now on **two** independent triggers:
  **(a)** AppArmor `5.0.0~beta1` → `5.0.2` moved underneath the oracle's own `bwrap` (J0A SURPRISE
  S-1) — smoke-tested only, **the GATE-23/25 exit-code taxonomy was never re-classified**;
  **(b)** the running kernel is **`7.0.0-30-generic`** against a pinned **`7.0.0-28-generic`**
  (re-measured 2026-08-28; HJ1 had recorded `-29`). The 2026-08-21 `unattended-upgrade` that
  installed `-30` **also removed the pinned kernel's headers**, so `-28` is no longer fully
  rebuildable from what is on the box. `pins.lock` `substrate.os_update_policy.drift_observed`.
- **FINDING B-1** — attended `chown` fix. Latent, not live: no current caller re-stages the same
  `(task, attempt)` after a `--sudo` verify.
- **STOP-44 candidate — unratified, and it has no journal anchor yet.** `grep STOP-44` over
  `BUILD-JOURNAL.md` and `docs/` returns **zero** matches; the highest recorded is STOP-43. Treat
  the number as reserved, not as a reference.
- **V-1 native-login KVM open** — unverified.
- **GPU passthrough — UNTESTED.**
- **Guest egress control — UNTESTED, and the question is live rather than theoretical**: round 2's
  own capture shows generic egress from the libvirt guest **succeeding** (204 from
  `connectivity-check.ubuntu.com`).
- **SOAK-3 `pids.peak` = 112 stands** — `wrought-verify.slice` reading exactly its own `TasksMax`.
- **Escalation rate (P1, the governing metric) is not measured anywhere in Phase J.** No model was
  loaded and no token generated by any J0 session.

## ADVISOR-SIDE NOTE

- The advisor's project doc titled *"…RX 7900 XT.md"* has a **stale title only** — its content
  correctly says **XTX**, and the box docs are clean. Title-only defect; no box action.
- A **day-old idle Claude Code peer session** (`foundry-24`) was observed on the box and is **still
  running as of 2026-08-12**: PID 4756, started Mon 2026-08-10 21:35, elapsed 1d 02:49
  (`ps -o pid,lstart,etime,cmd -p 4756,46628`; bundle `raw/10-peer-session.txt`).
  **RESOLVED 2026-08-28** — the box rebooted that morning (`journalctl --list-boots`), and a
  `comm`-based process listing shows exactly one `claude` process, this session's
  (`bundles/RECONCILE/raw/03`). No action outstanding. The underlying point stands: stale sessions
  are maintainability debt, and a second session holding a stale view of this file is precisely the
  J-156 failure mode.

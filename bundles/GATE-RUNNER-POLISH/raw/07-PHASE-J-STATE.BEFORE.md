# PHASE-J-STATE — the live rail position for Phase J

**Read this first.** It is the one doc a fresh session needs to know where Phase J stands. It is
updated at every wind-down (`docs/EXECUTOR-RAILS.md` §9); if it disagrees with a prompt's stated
premise, **this file and the box win, and the disagreement is reported, not reconciled by guessing.**

Rails for running a session: `docs/EXECUTOR-RAILS.md`. Versions: `pins.lock`. Narrative and
per-gate detail: `BUILD-JOURNAL.md`.

**Last updated 2026-08-28 by the `GATE-J0B-RESUME` LAUNCH ORCHESTRATOR, after the batch closed** (the gate child's own section below is its half; the runner-side verdict is the section after it, which the child could not write because it is produced after the child exits). Earlier that day: the `GATE-J0B-RESUME` pre-flight (same day: `GATE-RECONCILE`, `GATE-RUNNER-HARDEN`, `GATE-RUNNER-ARM`). The same facts, with the full evidence
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
| **GATE-RUNNER-HARDEN** | ran 2026-08-28; **ADJUDICATED — ACCEPTED** (advisor Fable; verdict at courier `bundles/GATE-RUNNER-HARDEN/ADJUDICATION.md`) — both unattended-run blockers CLOSED and measured, config ratified | `build-evidence/runner-harden/` → courier `bundles/GATE-RUNNER-HARDEN/` | J-161 |
| **GATE-RUNNER-ARM** | ran 2026-08-28; **ADJUDICATED — ACCEPTED** (advisor Fable; verdict at courier `bundles/GATE-RUNNER-ARM/ADJUDICATION.md`) — CLI pinned + autoupdate closed at both surfaces, all four safety properties re-verified on 2.1.250, DBUS dropped, **the runner now STARTS on the installed config** | `build-evidence/runner-arm/` → courier `bundles/GATE-RUNNER-ARM/` | J-162 |

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
    `manual` are default-deny-with-allowlist. The runner refuses to start in any other mode.
    **RE-VERIFIED ON THE INSTALLED `claude 2.1.250`** by `GATE-RUNNER-ARM` (`build-evidence/runner-arm/raw/11`):
    the trap still holds, and is still completely silent.
  - **`MemoryMax` alone does NOT cap memory on this box** — the overrun is paid out of the 8 GiB
    swap file and the process exits 0. **`MemorySwapMax=0` is what makes it a kill** (rc=137).
  - `RuntimeMaxSec` kills a real `claude` child at the deadline (rc=143, measured 30.3 s vs 30 s).
  - **PreToolUse hooks DO fire under `claude -p`** (this refutes the RT0 pass-2 claim) — but a
    **malformed settings file is silently ignored under `-p`**, so hooks are defence-in-depth only
    and the runner json-validates them before every launch.
  - **A Bash call targeting a path OUTSIDE the session cwd is denied under `dontAsk`** even when
    explicitly allowlisted. Gates need a minimal, explicit `--add-dir`.
  - **CORRECTION BY ADDITION, MEASURED 2026-08-28 (`GATE-J0B-RESUME` v2.1 pre-flight, courier
    `bundles/GATE-J0B-RESUME/preflight-v2.1-raw/10`): THE BULLET ABOVE IS TRUE ONLY FOR A *SCOPED*
    Bash ALLOWLIST RULE.** The sentence is left standing per rails §4 (corrections are added, never
    edited in), but it is **overbroad and must not be relied on as written**. A 2×2 with one
    variable — the allowlist spelling — and ground truth taken from disk:
    - `--allowedTools "Bash(touch:*)"`, write outside cwd, no `--add-dir` → **denied** (`['Bash']`,
      canary absent). This is what `build-evidence/runner/raw/14` and `runner-arm/raw/31` measured.
    - `--allowedTools "Read, Edit, Write, Bash"` (**bare `Bash`**), the *same* write, no
      `--add-dir` → **ALLOWED. Zero denials. Canary on disk.** A read outside cwd is likewise
      allowed.

    **So a bare `Bash` entry is not constrained by the workspace boundary at all**, and **every gate
    dispatched so far declares bare `Bash`** — the boundary has never once constrained a real gate
    child's Bash on this box. `raw/31`'s "CORROBORATION FROM A REAL GATE" does not corroborate: with
    bare `Bash` that bundle write would have succeeded without `add_dirs` naming the courier.
    Together with `NOPASSWD: ALL` (inherited by gate children), the real fences around a
    bare-`Bash` gate child are the systemd scope, the PreToolUse hook's six-pattern denylist, and
    the reaper. **The workspace boundary is not among them.**

    **OPEN — an advisor/operator RULING, deliberately not taken by the box:** either require scoped
    Bash rules in `ALLOWED-TOOLS:` headers, or correct `runner-arm/raw/31`'s VERDICT and
    `/etc/wrought/runner.conf`'s `_add_dirs_note`, which still state the boundary unconditionally.
    **Do NOT "just scope the Bash rules" as a launch-night tweak:** scoped rules re-arm the
    boundary, and `GATE-J0B-RESUME`'s `ADD-DIRS:` header omits `/var/lib/wrought/j0a` — which every
    Phase-A command names — so scoping without also correcting `ADD-DIRS` converts a non-issue into
    a hard Phase-A denial. Scoped-Bash **plus** corrected `ADD-DIRS` is a v2.2 decision.

    **DIRECTLY FOR A GATE CHILD READING THIS:** if your `ADD-DIRS:` header omits a directory you
    need, check whether your `ALLOWED-TOOLS:` grants bare `Bash` before concluding you are blocked.
    `GATE-J0B-RESUME` does, so **it can read and write `/var/lib/wrought/j0a` — Phase A is not
    blocked, and this is not a premise conflict to refuse on.**
  - **THE PreToolUse HOOK DENIES YOUR OWN BYTE-FREEZE COMMAND, BY DESIGN — do not stall on it**
    (measured 2026-08-28, `preflight-v2.1-raw/11`). `bin/wrought-runner-hook` serialises the whole
    `tool_input` and denies on `orchestrator\.db`, so **any** command naming the orchestrator store
    is refused — including a read-only `sha256sum` of it. Rails §2 asks "a session" to hash all
    three files at start and before finalizing; **a gate child running under `wrought-runner`
    cannot, and does not need to.** The runner owns the freeze for the whole batch: it hashes the
    frozen paths before and after your run and writes `freeze-before.json`, `freeze-after.json` and
    `freeze-verdict.txt` into its run dir, and any drift halts the entire runner. **Log the denial
    as evidence, say in your report that the runner holds the freeze, and proceed.** An attended
    session run outside the runner still does the freeze itself, exactly as §2 says.
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

- **NEXT ON THE RAIL: a SUPERVISED `GATE-J0B` (Phases 5–7 + seed rebuild), run through the armed
  `wrought-runner` while the operator watches**, setting the PROVISIONAL scale numbers.
  **Both rulings that gated it were taken on 2026-08-28 and both are now CLOSED by
  `GATE-RUNNER-ARM`** — the CLI auto-update (§Phase 2) and the `DBUS_SESSION_BUS_ADDRESS` drop
  (§Phase 4). **After that batch: ST-1**, which is still unsatisfied on two triggers. A gate must
  not be dispatched ahead of this order without saying so.

  **BUT THE BATCH IS NOT YET RUNNABLE — `GATE-J0B-RESUME` v2.0 is dispatched and `QUEUED`, NOT
  `APPROVED`.** The box pre-flighted it instead of running it (it is addressed to `wrought-runner`
  as a gate child, so running it attended-direct would defeat its stated purpose of validating the
  runner) and found **4 BLOCKERS + 1 calibration risk** — courier
  `bundles/GATE-J0B-RESUME/PREFLIGHT.md`:
  - **B-1, silent and total:** the prompt's header is `ADD-DIR:`; the runner's regex is
    `^ADD-DIRS:` (`bin/wrought-runner:82`). The line is **silently ignored**, so the child's
    `add_dirs` is only the courier and `/var/lib/wrought/j0b` — the gate's entire workdir — is
    unreachable. Under `dontAsk` that means **Phase A step 1 is denied**.
  - **B-2, ordering:** Phase A boots egress-LOCKED and then installs Goose from GitHub. J0B's own
    timestamps show the proven shape is boot OPEN → install → poweroff → re-boot LOCKED.
  - **B-3, hard rule:** Goose is **not in `pins.lock`** though the prompt says "the pinned Goose
    release". Values exist only as J0B evidence (`v1.46.0`, sha256 `a1cf4856…5a7b`).
  - **B-4:** pre-step 1 names `authproxy.py` — **the proxy that failed this exact pinhole test**
    (J0B raw/32 diagnosis → raw/33 "retry with authproxy2.py (per-request upstream)" → raw/34
    "corrected proxy"). Its own confirmation step passes on the broken proxy, because v1 answers
    the **host** fine and only fails through the guestfwd. **Use `authproxy2.py`.**
  - **R-1, calibration:** `deadman_no_progress_sec` (3600) is tighter than `runtime_max_sec` (5400)
    and **silently wins** — `DeadMan.progress()` is never called while the child runs — so the real
    per-gate ceiling is **60 min, not 90**, and a trip latches the `deadman` breaker.
- **~~BLOCKER — `wrought-runner` cannot start with its installed config~~ — CLOSED 2026-08-28 by
  `GATE-RUNNER-ARM`.** The operator ran the three-command root action; the box verified the result
  rather than taking it on report (`raw/02`): `/var/lib/wrought/runner-state` is
  `drwx------ kalib:kalib`, mode `700`, writable, empty. The `PermissionError` is gone (`raw/23`).

- **~~SECOND BLOCKER, found by closing the first — the runner could not parse the REAL `QUEUE.md`~~
  — CLOSED 2026-08-28 by `GATE-RUNNER-ARM`, under an explicit advisor+operator ruling.** With the
  `state_dir` fixed, the first-ever start against the real courier halted with a **latching
  `queue-parse` breaker**: `parse_queue()` rejected two statuses the vocabulary already blesses —
  `RESET` (used by `GATE-J0B-SURFACE`) and `FOLDED INTO <gate>` (used by `GATE-HJ2-HEARTBEAT`,
  and **parametric**, so it needs a prefix match rather than set membership). rails §12.1, the
  courier `README.md` legend and `QUEUE.md`'s own table all define both; only the parser was out of
  sync, and **`--reset-breaker` could not help because the condition was permanent**. Never caught
  before because every prior dry run used a SCRATCH courier with a synthetic queue — the same
  never-exercised-against-production shape as the `state_dir` bug. Fix was strictly additive
  (`QUEUE_STATUSES += "RESET"`, `QUEUE_STATUS_PREFIXES = ("FOLDED INTO",)`), **`RUNNABLE_STATUS`
  untouched**, so it widens what the parser ACCEPTS and not what the runner RUNS — proven by
  regression (`raw/24`, `raw/28`).

- **MEASURED, and it changes how any future gate may probe the runner: a `wrought-runner` start is
  NEVER read-only with respect to the courier, on ANY exit path.** Both the halt path and the clean
  path call `push_status()`, which **writes, commits and pushes `STATUS.md`**. Two such clobbers of
  this session's own heartbeat are recorded (`raw/23` correction, `raw/28`). A gate that wants to
  exercise the runner without touching the courier **must** point `courier_dir` at a scratch clone.

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
- **Transport has now failed FOUR times in a row**: `GATE-RUNNER`, `GATE-RECONCILE`,
  `GATE-RUNNER-HARDEN` and `GATE-RUNNER-ARM` all arrived as **chat text, not files** (rails §7) —
  the last two despite their own headers asking for a file upload. All had intact content and
  correct block counts, so all were archived verbatim and run — but the rail is not being met, and
  four consecutive misses is a rail that should either be enforced or amended.
- **The runner's SCALE thresholds are still PROVISIONAL** and are what the first supervised batch
  is for; `/etc/wrought/runner.conf` now marks every setting `RATIFIED` or `PROVISIONAL` in the
  file itself. **RATIFIED 2026-08-28:** `permission_mode: dontAsk`, `memory_swap_max: 0`, the
  breaker latch-semantics, `course_check.enabled: false`, the **`APPROVED` QUEUE status** and the
  **required `ALLOWED-TOOLS:` header** (both now `docs/EXECUTOR-RAILS.md` §12).
- **The course-check needs operator ratification before it may be enabled**: it points the sealed
  §13 escalation credential at a new purpose, and its enabled path requires passwordless `sudo`.
- **The steering breaker is CLOSED** (2026-08-28, `GATE-RUNNER-HARDEN`) — see ESTABLISHED FACTS.
  **`DBUS_SESSION_BUS_ADDRESS` was DROPPED from the child env allowlist on 2026-08-28**
  (`GATE-RUNNER-ARM` Phase 4, `build-evidence/runner-arm/raw/20`) — it was a real open hole, not a
  theoretical one: a gate child was still handed `unix:path=/run/user/1000/bus` **despite** its
  private runtime dir. The drop is total (parent and child), because `systemd-run --user --scope`
  was measured to work without it as long as `XDG_RUNTIME_DIR` is set; a real gate child was then
  proven to run, and the absence was confirmed **from inside the child**. Two residuals remain:
  the isolation is **one-directional** (a child can still see `/run/user/1000/cc-socks`, though it
  cannot be seen there), and **the `raw/18` question — what an APPROVED steering message does to a
  running gate child — is still UNANSWERED**; it is unreachable by the ordinary path rather than
  understood.
- **~~URGENT — the `claude` CLI SELF-UPDATED out from under its pin~~ — CLOSED 2026-08-28 by
  `GATE-RUNNER-ARM`, and the ROOT CAUSE is worth carrying.** `2.1.238 → 2.1.250` at 12:56:04Z.
  **The operator's `autoUpdates: false` was ALREADY SET in `~/.claude.json` and did not stop it.**
  The CLI's resolver reads
  `autoUpdates===false && (installMethod!=="native" || autoUpdatesProtectedForNative!==true)`,
  and this box is `installMethod: native` with `autoUpdatesProtectedForNative: true`, so the config
  arm is **VOID** and the resolver falls through to enabled. `claude doctor` confirmed it in as
  many words: with the preference set and nothing in the env it reported `Auto-updates: enabled`
  (`build-evidence/runner-arm/raw/04`, `raw/05`). **On a native install the ENV arm is the only
  reachable switch — the config preference is not a control and must not be recorded as one.**
  Now `DISABLE_AUTOUPDATER=1` at **both** surfaces, and both are load-bearing:
  `~/.claude/settings.json`'s `env` block for interactive sessions, and a hardcoded
  `build_child_env()` entry for gate children. **HARDEN's ephemeral HOME — the STEERING fix — had
  itself RE-OPENED autoupdate for gate children**, measured: ephemeral HOME + nothing in the env
  gives `Auto-updates: enabled`, because the child cannot see the file the interactive fix lives in
  (`raw/08`). Pinned at `pins.lock` `supervisor_toolchain`.
  **All four containment properties were re-verified on 2.1.250 BEFORE the pin moved**
  (`raw/11`–`raw/15`): (b) `dontAsk` + the `acceptEdits`/`auto` trap, (c) hooks under `-p` **and**
  the silent malformed-settings loss, (d) the budget soft ceiling and `BASH_DEFAULT_TIMEOUT_MS`
  backgrounding, (a) fresh context + the two-surface isolation. **Nothing is left
  UNVERIFIED-ON-THE-INSTALLED-BUILD.** Two benign-but-real changes recorded rather than absorbed:
  the model may now RAISE the per-call Bash timeout above the env default (which *strengthens*
  "the kernel is the only real stop"), and the budget overshoot measured **6.94x** vs 4.6x at
  `GATE-RUNNER` — **two single-run samples, not a trend**, but against the provisional
  `max_budget_usd_per_gate = 8.0` it implies a worst case near **$55 for one gate**.
- **The reaper's `virsh destroy` path has NEVER EXECUTED.** `libvirtd` was inactive throughout, so
  the domain probe was skipped on every run and only the process/listener halves are proven. Same
  for `reaper.terminate_grace_sec` (PROVISIONAL, unmeasured): every stub died on the first SIGTERM,
  so the SIGKILL escalation branch is untested.
  - **UPDATE, measured 2026-08-28 at the `GATE-J0B-RESUME` v2.1 pre-flight: `libvirtd` is now
    ACTIVE**, socket-activated at boot (`ActiveEnterTimestamp` = 2026-08-28 08:50:48 EDT,
    `TriggeredBy` libvirtd{,-ro,-admin}.socket). So the **domain probe will execute for the first
    time** during the supervised batch, where every prior run skipped it. `virsh list --all` is
    **empty**, and a pre-batch `residue_snapshot()` reads `domains: []` — so the before-set is
    clean and a domain appearing after the gate would be real residue. **`virsh destroy` itself
    stays unexercised**: this gate launches plain `qemu-system` by design (rails §13.1), so no
    domain should ever exist to destroy. The probe running is not the destroy branch running, and
    the batch must not be read as evidence for the latter.
- **The runner has never run unattended.** Longest batch: two gates, ~20 minutes. The 20-hour
  wall-clock budget and the 6-gate cap are untested at scale.
- **NEW, from `GATE-RUNNER-ARM` — an OPEN RULING the gate deliberately did not take:** the runner
  carries a queue status **`NOT RUN`** (`bin/wrought-runner:65`) that appears in **no document** —
  not rails §12.1, not the courier `README.md`, not `QUEUE.md`'s own table. The 2026-08-28 ruling
  authorized only `RESET` + the `FOLDED INTO` prefix and said nothing about this, so it was left
  alone. Checked so the decision is cheap: the runner **never writes** `NOT RUN` (only line 65; the
  two `set_queue_status()` call sites write `RUNNING` and `HALTED`), so deleting it cannot break a
  round-trip. **Delete it from the set, or add it to the rails vocabulary?**
- **NEW, from `GATE-RUNNER-ARM` — a false-provenance string in the runner.** `breaker.json` records
  `reset_by: "operator via --reset-breaker"`, but the string is **hardcoded**; it was written when
  the BOX ran `--reset-breaker`, not the operator. Small, but it is exactly the class of defect
  this project keeps finding one level up (the ledger docstring, the pack generator header).
- **NEW, from `GATE-RUNNER-ARM` — the box has passwordless root, and gate children inherit it.**
  `sudo -n -l` reports `(ALL) NOPASSWD: ALL` for `kalib` (`raw/02`). Gate children run as `kalib`,
  so **the `dontAsk` allowlist and the systemd scope are the ONLY fences between a gate child and
  root** — there is no second, credential-shaped one. Recorded as an observation, not acted on; the
  gate declined to self-authorize the one root action it needed and routed it through the operator.
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

## 2026-08-28 — GATE-J0B-RESUME v2.1 ran THROUGH the runner (first real-work gate child)

- **Pinhole re-proved** (curl 6 / curl 7 / 200) and **Goose pin reproduces exactly** (size + sha256).
- **Agent turn reached the model** (3 calls, 27 s, rc=0) but **wrote no FORGE.txt** — no filesystem
  tool was attached; `developer` is in-process, and the `extensions:` stdio attach did not load.
- **SEAM: POSITIVE. Decision-1 = BUILD.** `goose mcp {computercontroller,memory,tutorial,autovisualiser}`
  are stdio JSON-RPC servers; a two-line tee shim captured `initialize` / `tools/list` / `tools/call`.
- **F-1 (open, needs a ruling):** the runner hook denies `sha256sum` of the orchestrator store, so
  **EXECUTOR-RAILS §2 is unsatisfiable for any gate child**. The runner's own freeze covers it and is
  better; §2 should say so. The hook also denies quoting the filename in evidence.
- **F-2 (open):** a runner child's scope is `memory_max` 8G and the guest is a scope descendant, so
  J0B's `-m 8192` would OOM the gate. Guests must be sized against the SCOPE, not the box. Used 3G.
- **F-4 (open, important):** **goose exits 0 on total failure.** Never use its rc as a success signal.
- **F-5 (open):** goose streams with `max_tokens: None`; abandoned retries head-of-line block
  llama-server, and the SLIRP guestfwd degrades under that pattern (fixed by a guest reboot).
  No `max_tokens` knob was found — **unmitigated for the next gate**.
- **Cost is the binding constraint:** ~$6.7 of the $8.00 cap; `RuntimeMaxSec`/dead-man never neared.

## 2026-08-28 — the RUNNER-side verdict for that batch (written by the launch orchestrator, after the child exited)

The section above is the gate child's account. It ends where a child must: the child itself filed
*"the runner's own gate verdict and sweep result"* under WHAT THIS DID NOT ESTABLISH. This is that
half. Full evidence with the exact commands: **J-164**. Run dir
`/var/lib/wrought/runner-state/runs/20260828T220144Z/`.

- **MECHANICAL VERDICT: PASS.** `verdict.json`: `rc=0`, `child_disposition=COMPLETED`,
  `terminal_reason='completed'`, `postcondition_failures=[]`, `memory_fence=unchanged`.
  Runner exited cleanly: `run-end wall_sec=2062.0 gates_run=1 halted=false breaker=null`.
- **BYTE FREEZE: HOLD** — "no change to any frozen path", all three paths byte-identical. This is the
  **runner's** artifact, taken by a process the child cannot influence, which is strictly better than
  the child measuring itself. F-1 is why it had to be.
- **ORPHAN SWEEP: CLEAN** — `new.any=false`; no guest, domain or listener survived. Ephemeral HOME
  torn down, lock released, no stray child process.
- **THE LIBVIRT DOMAIN PROBE EXECUTED FOR THE FIRST TIME.** Proof is the *absence* of the skip note:
  `residue_snapshot()` appends `"libvirtd inactive — domain probe skipped"` when it skips, and both
  snapshots carry `notes: []`. Every prior run carried that note. **`virsh destroy` is STILL
  unexercised** — plain-qemu path, no domain ever existed. The probe running is not the destroy
  branch running, and this batch must not be cited as evidence for the latter.
- **SCALE NUMBERS — INPUTS TO A RULING, NOT NEW SETTINGS.** `/etc/wrought/runner.conf` was
  deliberately **not touched**; ratifying a PROVISIONAL number is the ferry's call. Child wall-clock
  **1757.8 s (29.3 min)** vs `runtime_max_sec` 5400; batch **2062 s**; 75 turns; 91,592 output tok;
  **cost $7.5324895 vs the $8.00 cap = 94.2%**. The 6000 s dead-man was never approached.
- **COST IS THE BINDING CONSTRAINT — and it CORRECTS the child's own line above.** The section above
  says "~$6.7 of the $8.00 cap" (the harness's running total; the child's own audit said to prefer
  the runner's number once it landed). **The authoritative figure is $7.5324895 = 94.2%.** Left
  standing above per rails §4; this is the correcting record. Neither time bound came close — **money
  did**, at 94.2% for ONE gate that hit ONE wedge. Against GATE-RUNNER-ARM's 4.6×/6.94× measured
  overshoot, **a ruling on `max_budget_usd_per_gate` is a precondition for any multi-gate unattended
  run.**
- **NEW — the reaper has a live `pgrep -f` FALSE-POSITIVE path, found from both sides.**
  `residue_snapshot()` runs `pgrep -a -f "qemu-system"`, which matches any command line *containing*
  that string — a gate prompt that mentions it, a monitoring command, an editor. Tonight it did not
  fire only because the child had already exited when the after-snapshot was taken. A false positive
  is enumerated, terminated, and **latches** a `gate-residue` breaker. The child found it from the
  inside; the orchestrator independently avoided it from the outside by bracket-quoting every probe
  (`'[q]emu-system'`). **Needs a ruling** — the same `-f` hazard applies to `pkill`.
- **The key-holding proxy is operator-side and must PREDATE the runner start.** Verified as designed:
  `127.0.0.1:8081 -> 89355` appears in `residue-before.json`, so it was in the before-set and could
  never be read as gate residue. Torn down by **recorded PID**, never `pkill -f` (which matches the
  orchestrator's own wrapper shell — observed self-matching in the same session). After teardown
  `:8081` refuses connections, the pre-launch baseline exactly.
  **Precise about what that does and does not mean:** the proxy's **in-memory** copy of the key is
  gone and no unsealed copy exists outside the sealed store. The TPM2-sealed credential and the
  running `wrought-inference.service`'s own copy remain — by design.

**WHAT THE BATCH DID NOT ESTABLISH — the runner has STILL never run unattended.** This was supervised,
with the operator's orchestrator watching and holding the proxy. **One gate, not six; 34 minutes, not
20 hours.** `virsh destroy`, `reaper.terminate_grace_sec`, the consecutive-failure breaker, and the
inter-gate pacing path past a *second* gate all remain unexercised. And note the split result: the
**mechanical PASS is a statement about the runner's postconditions, not a claim that the gate met its
substantive objective** — Phase 5's work-product clause failed (no `FORGE.txt`).

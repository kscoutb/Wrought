# PHASE-J-STATE — the live rail position for Phase J

**Read this first.** It is the one doc a fresh session needs to know where Phase J stands. It is
updated at every wind-down (`docs/EXECUTOR-RAILS.md` §9); if it disagrees with a prompt's stated
premise, **this file and the box win, and the disagreement is reported, not reconciled by guessing.**

Rails for running a session: `docs/EXECUTOR-RAILS.md`. Versions: `pins.lock`. Narrative and
per-gate detail: `BUILD-JOURNAL.md`.

## CLOSED

| Gate | Closed | Evidence | Manifest |
|---|---|---|---|
| **GATE-J0-RECON** | 2026-08-10 | `build-evidence/j0-recon/` | `sha256sum -c SHA256SUMS` |
| **GATE-J0A-SUBSTRATE** | 2026-08-10; **accepted 2026-08-11 (J-155)** | `build-evidence/j0a/` (v1.1, the round that aborted on U-1) and `build-evidence/j0a/round2/` (the round that closed it) | **35/35** and **48/48** verified in the committed copy |
| **GATE-HJ1-HYGIENE** | ran 2026-08-12; **BUNDLED, awaiting advisor adjudication** — not yet closed | `/var/lib/wrought/hj1/` → courier `bundles/GATE-HJ1/` | J-157 |

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

## RESIDUE — deliberate, operator-accepted

Left in place by J0A round 2 and **attributable to that session, not inherited**:

- libvirt `default` network **active / autostart / persistent**, plus `virbr0`.
- **nftables 91 → 182 lines.** No new table (6 → 6), but **four new base chains registering
  netfilter hooks** and six `LIBVIRT_*` chains; hook registrations 10 → 14.
- **Two permanent host listeners**: `dnsmasq` on `192.168.122.1:53` (tcp+udp) and `0.0.0.0%virbr0:67`.
  The network is autostart+persistent, so these return every boot.
- `libvirt-guests.service` (hooks host shutdown), `qemu-kvm.service`, `machines.target` — all
  enabled by the packaging. **No `systemctl enable/start/stop/restart` was issued by any J0 session.**
- The **dirty boot-2 `overlay.qcow2`** (55 MB) in the round-2 workdir — slated for deletion by
  **J0B Phase 0**, under the enumerated-delete rail.

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

- **GATE-J0B is next.** Surface = **Goose** (SELECTED, *not* adopted — `docs/10` §18.7). Design:
  authenticating proxy + `restrict`/`guestfwd` pinhole. Prompt exists advisor-side.
- **ST-1 re-run is QUEUED and UNSATISFIED**, now on **two** independent triggers:
  **(a)** AppArmor `5.0.0~beta1` → `5.0.2` moved underneath the oracle's own `bwrap` (J0A SURPRISE
  S-1) — smoke-tested only, **the GATE-23/25 exit-code taxonomy was never re-classified**;
  **(b)** the running kernel is **`7.0.0-29-generic`** against a pinned **`7.0.0-28-generic`**
  (measured at GATE-HJ1, `pins.lock` `substrate.os_update_policy.drift_observed`).
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
  **Operator to close it.** Stale sessions are maintainability
  debt — a second session holding a stale view of this file is precisely the J-156 failure mode.

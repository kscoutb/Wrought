# SNAPSHOT — forge-mini, 2026-08-28

**The single authoritative current-state document.** Written by `GATE-RECONCILE`, which did no new
capability work: it resolved a tangle of out-of-order gates, paid two recording debts, and measured
what is actually on the box. Mirrored into `docs/PHASE-J-STATE.md` in the foundry repo.

Every fact below names the capture that produced it (`bundles/RECONCILE/raw/NN-*`). Where the
evidence does not reach, it says **UNKNOWN**.

---

## 1. RAIL POSITION — true status of every gate

| Gate | Status | What that means |
|---|---|---|
| `GATE-J0-RECON` | **CLOSED** | 2026-08-10. `build-evidence/j0-recon/`. |
| `GATE-J0A-SUBSTRATE` | **CLOSED** | 2026-08-10, accepted 2026-08-11 (J-155). Round 2 supersedes v1.1. 48/48 verified. |
| `GATE-HJ1-HYGIENE` | **ADJUDICATED — closed** | Advisor verdict ACCEPTED, recorded this session at `bundles/GATE-HJ1/ADJUDICATION.md`, extracted mechanically from the dispatching prompt. |
| `GATE-HJ2-HEARTBEAT` | **FOLDED INTO GATE-RECONCILE** | Never ran as its own session. Its `STATUS.md` bootstrap was done by J0B; **all remaining items completed here** — rails §9 (heartbeat) and §10 (adjudication-carrying), README mirror, HJ1 verdict recorded. Journal **J-158**, reserved for it, is spent on exactly that. |
| `GATE-J0B-SURFACE` | **RESET — must be re-dispatched fresh** | Ran Phases **0–4 of 8**, then stopped with no report and no bundle. Partial evidence preserved at `bundles/GATE-J0B/PARTIAL/`. Full account: `bundles/GATE-J0B/PARTIAL/WHAT-HAPPENED.md`. |
| `GATE-RUNNER` | **BUNDLED — awaiting advisor adjudication** | 40/40 manifest verified. Carries an **unresolved safety finding** (§4 below) and four ratification items. |
| `GATE-RECONCILE` | **BUNDLED** (this session) | `bundles/RECONCILE/`. |

**Physical-presence gates remain DEFERRED per D17** — GATE-01, GATE-03A/03B, GATE-04. Unchanged.

### What J0B actually proved, and what it did not

**Proved** — the egress pinhole, measured from inside the locked guest (`GATE-J0B/PARTIAL/raw/34`):
DNS fails (`curl 6`), the SLIRP gateway to the host model server is refused (`curl 7`), and **only**
the authenticating proxy answers `200`, with the real server behind it (`primary-qwen27b`,
`n_ctx 65536`, `build b10233-0ab9d6fed`). The base image stayed immutable across a write-through
boot. No key material was found anywhere in the guest.

**Not proved** — Phase 5 (the agent turn / first manufactured tokens) and Phase 6 (the Decision-1
interception seam) **never ran**. Nothing was ratified.

---

## 2. BOX SURFACE NOW

### Health — all green
`wrought-inference.service` **active/running**, `NRestarts=0`, started 2026-08-28 08:50:48 EDT ·
`/health` → **200** · `amdgpu.runpm=0` · dGPU by device id **`0x744c`** at `0000:c7:00.0`,
`runtime_status=active`, `runtime_enabled=forbidden`, **VRAM 19.62 / 25.75 GB used**
(`raw/01`). Six `wrought-*` units loaded; **none was touched this session** (`raw/18`).

### Byte freeze — **HELD**
`orchestrator.db{,-wal,-shm}` byte-identical at `raw/00` and `raw/99`; mechanical diff is empty
(`raw/99`). This session wrote nothing under `state/`.

### Kernel — drifted again, and the pinned kernel is no longer fully rebuildable
Running **`7.0.0-30-generic`**; `pins.lock` pins **`7.0.0-28-generic`**. HJ1 recorded `-29`; the
bump to `-30` landed 2026-08-21 06:40 by `unattended-upgrade`, and **the same transaction removed
the pinned kernel's headers** (`Remove: linux-headers-7.0.0-28-generic, linux-headers-7.0.0-28`).
`/boot` now carries `-29` and `-30` only. Recorded in `pins.lock` `drift_observed`; **not re-pinned**
— a pin moves only in the gate that re-measures it, and that gate is ST-1 (`raw/16`).

### Pins — 36 of 51 hold; the 15 that moved are one libvirt security bump
Mechanical, pin-by-pin against `dpkg-query` (`raw/17`):

    pins checked : 51      HOLDING : 36      DRIFTED : 15      NOT INSTALLED : 0

All 15 are the libvirt closure, **`12.0.0-1ubuntu5.2` → `12.0.0-1ubuntu5.3`**, in a single
`unattended-upgrade` transaction on 2026-08-20 06:55. These are **ratified** pins from HJ1, so this
is drift on ratified values. Recorded in `drift_observed`; **not re-pinned**. libvirt is **not** a
declared ST-1 trigger (ST-1 covers llama.cpp / Mesa / kernel / model) — see §3.

72 further upgrades are available and **not applied**.

### Removed this session — nothing. The desktop back-out had already been done.
The prompt's Phase 4 premise ("the failed bridge experiment left GUI packages on the lean box")
**does not hold**. The operator ran the **byte-identical** purge on **2026-08-20 21:12:37**
(`/var/log/apt/history.log`, `raw/04`). Verified package-by-package: **none of the 11 is installed**;
the apt source, the keyring, `~/.config/Claude` and `~/.vnc` are all **already absent**; `apt-get
check` reports no broken dependencies and nothing orphaned; **0 pinned packages were affected**
(`raw/15`). Re-running the purge would have manufactured false history, so it was **not run**.

### Deleted this session — exactly two paths, both J0B scratch (`raw/13`, `raw/14`)

    /var/lib/wrought/j0b/j0b-overlay.qcow2   1160052736 B  sha256 dabad79a…7191e
    /var/lib/wrought/j0b/seed.img               374784 B  sha256 700f6398…848e4

1.16 GB reclaimed. **Kept**, as instructed and verified present: the base image
(`noble-server-cloudimg-amd64.img`, sha256 `0533b065…40ffe`, still matching its pin), `j0a_key`,
and `user-data`. **Left in place because the prompt did not enumerate them**, and therefore
reported instead of deleted: `/home/kalib/overlay.qcow2` (196928 B, 2026-08-11, J0A-era stray),
`/var/lib/wrought/j0b/__pycache__/`, and three stale `*.pid` files.

**Consequence to carry forward: no cloud-init seed image now exists anywhere on the box.** It is
rebuildable with **no install** — `cloud-localds` (`cloud-image-utils 0.33-1build1`, verified
present) plus the surviving `/var/lib/wrought/j0a/user-data` (sha256 `51fbe0df…1ecd5`). **A J0B
re-dispatch must include the rebuild step.** Note `cloud-image-utils` is load-bearing here but is
**absent from `pins.lock`** — a pins gap, flagged not filled.

### libvirt residue — unchanged from J0A, still deliberate and operator-accepted
`default` network **active / autostart / persistent**; `virbr0` present but **DOWN, NO-CARRIER**;
nftables **182 lines, 6 tables, 14 base chains with hooks, 14 `LIBVIRT_*` chains** (6 unique names
across the ip and ip6 families); the two permanent listeners return every boot — `dnsmasq` on
`192.168.122.1:53` (tcp+udp) and `0.0.0.0%virbr0:67`. `libvirtd` and `libvirt-guests` **enabled** by
packaging. **No domains are defined** (`virsh list --all` empty). Nothing here was changed this
session (`raw/18`, `raw/19`).

### Processes and listeners
No `qemu`, `Xvfb`, `x11vnc`, `claude-desktop`, or authproxy is running; nothing listens on `:8081`,
`:5900`, or `:2222` (`raw/03`). Non-loopback listeners are the expected steady state: `sshd:22`,
`tailscaled`, `avahi`, `systemd-resolved`, and the two libvirt `dnsmasq` sockets (`raw/18`).

---

## 3. OPEN DECISIONS — one line each, for the advisor and the operator

1. **`GATE-RUNNER`'s Phase-3 cross-session steering breaker is NOT satisfied** — a gate child stays
   discoverable and addressable by any other local Claude Code session; all three probe messages
   were held for recipient approval and expired undelivered, so delivery is fail-closed **by a
   platform behaviour this project neither configured nor pinned**, and **what an APPROVED message
   does to a running gate child has never been tested**.
2. **Ratify or reject the new `APPROVED` QUEUE status** introduced by `GATE-RUNNER`.
3. **Ratify or reject the required `ALLOWED-TOOLS:` prompt header.**
4. **Ratify every threshold in `/etc/wrought/runner.conf`** — all are `PROPOSED-UNRATIFIED`.
5. **Rule on the course-check credential** — it points the sealed §13 escalation credential at a new
   purpose and its enabled path needs passwordless `sudo`; it **ships disabled**.
6. **ST-1 has two unsatisfied triggers** — kernel (now `-30` vs pinned `-28`) and AppArmor
   (`5.0.0~beta1` → `5.0.2` under the oracle's own `bwrap`); both clear in **one** ST-1 pass, due
   before the next MANUFACTURING run.
7. **NEW — does a libvirt point-release need its own re-measure?** 15 ratified pins moved and
   libvirt is not a declared ST-1 trigger. Recorded, unanswered.
8. **NEW — `cloud-image-utils` is load-bearing but unpinned.** Add to `pins.lock` or rule it out.
9. **NEW — dead sessions do not reap their guests** (§4). Decide whether the runner must own a
   reaper before it runs unattended.
10. **`B-1`** — carried forward from the prior state doc, unchanged and still open.
11. **`STOP-44`** — reserved but unratified, with no anchor; approved as recorded at HJ1.
12. **`GATE-J0B` needs a fresh re-dispatch** — scoped to what remains (Phases 5–7), and it **must**
    rebuild the seed.
13. **Transport has now failed twice in a row.** `GATE-RUNNER` and `GATE-RECONCILE` both arrived as
    **chat text, not files**, against rails §7. Content was intact and block counts checked both
    times, so both were archived verbatim and run — but the rail is not being met.

---

## 4. THE SAFETY FINDING THIS GATE DISCOVERED

**A gate session that dies mid-run leaves its guest and its credential-holding proxy running
indefinitely. There is no reaper.**

J0B's Phase-3c guest was never shut down. It ran from **2026-08-20 until the box went down on
2026-08-27** — roughly seven days. Evidence (`raw/11`):

- `grep -c 'reboot: Power down'` over the four serial logs → **`p2:1`, `p3:1`, `p3b:1`, `p3c:0`**.
  The first three guests logged their power-down; the fourth never did, and its log ends at a login
  prompt.
- `j0b-overlay.qcow2` was last written **2026-08-27 19:58:09 EDT**, inside the shutdown window of a
  single boot spanning 2026-08-10 → 2026-08-27. Nothing else on the box writes that file.
- `authproxy2.out` ends at `stream 2 opened` with no matching close.

**Limit of the evidence, stated plainly:** this is not a direct observation of a live process. J0A
launched QEMU under `sudo` (journal-logged); **J0B launched it as plain `kalib`**, so no journal
record exists and none is recoverable. **Strongly supported, not directly observed.**

**Why it matters:** the authenticating proxy holds the inference API key **in memory** and was, on
the same evidence, still bound to `127.0.0.1:8081` throughout. This is a direct input to the
`wrought-runner` ratification — the runner is designed to run for 20 hours while the operator is
away, and nothing currently reaps a dead gate's guest.

---

## 5. WHAT THE BOX NEEDS NEXT, in priority order

1. **Adjudicate `GATE-RUNNER`** — it is the only gate blocking, and items 1–5 above are all its.
   The steering breaker in particular needs a ruling: accept the platform's approval gate as
   sufficient, or require a real breaker before any unattended run.
2. **Rule on the reaper (§4).** Cheap to specify, and it is a live credential-exposure path.
3. **Re-dispatch `GATE-J0B` fresh**, scoped to Phases 5–7 (the agent turn, the interception shim,
   wind-down), with the seed-rebuild step included. Phases 0–4 do not need redoing, but the guest
   must be rebuilt, which the measured ~15 s revert cycle makes cheap.
4. **Run ST-1 once** to clear both triggers before any MANUFACTURING run. Decide first whether the
   libvirt drift joins it (item 7).
5. **Fix the transport** (item 13) — prompts as files, per rails §7.
6. **Housekeeping, low priority:** pin or rule out `cloud-image-utils`; decide the fate of
   `/home/kalib/overlay.qcow2` and the two untracked prompt files at the foundry root.

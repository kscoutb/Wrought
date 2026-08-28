# REPORT — GATE-RECONCILE, forge-mini, 2026-08-28 (ATTENDED)

**Executor:** Claude Code (Opus, ultracode) on `forge-mini`. **Advisor:** Fable.
**Prompt:** `prompts/GATE-RECONCILE-v1.0.md` (archived verbatim).
**Current state doc:** `SNAPSHOT.md` in this directory — read that for the rail position.
This report is the *narrative of what changed*; the snapshot is *what is true now*.

**Byte freeze: HELD.** `raw/00` vs `raw/99`, mechanical diff `raw/99b` — hashes, sizes and mtimes
identical. Nothing under `/var/lib/wrought/state/` was written.

---

## The headline: three of the prompt's premises did not survive contact with the box

This gate was asked to clean up a tangle. The most useful thing it found is that **the tangle was
partly already untangled**, and that acting on the prompt as written would have made the record
*worse*. Each divergence was reported, not absorbed.

| # | The prompt said | The box said | What was done |
|---|---|---|---|
| 1 | "The failed bridge experiment left GUI packages on the lean box" — purge 11 packages | **The operator already ran the byte-identical purge on 2026-08-20 21:12:37.** None of the 11 is installed; the apt source, keyring, `~/.config/Claude` and `~/.vnc` are all already gone | **Not run.** Verified package-by-package and recorded as PRIOR-COMPLETED (`raw/15`) |
| 2 | Kill the authproxy; `virsh destroy` + `undefine` the j0b guest | **All three PIDs dead; `virsh list --all` empty** — the guest was plain QEMU, never libvirt-defined | Recorded as **evidence-backed no-ops** (`raw/13`) |
| 3 | "Journal J-158 … and J-159" | **J-159 is already spent** by `GATE-RUNNER` (commit `ec593be`) | HJ2 debt → **J-158** (its reservation); reconcile → **J-160**. Collision surfaced, not silently renumbered |

Re-running the purge was the one that mattered. It would have written this session into
`/var/log/apt/history.log` as removing packages that were already absent — **manufactured history**,
which is a worse defect than the residue it was meant to clear. The prompt's own escape hatch
("do NOT purge that one — report it instead") covers the case.

### A methodological note worth keeping

The prompt's inventory line `pgrep -a -f 'authproxy|qemu-system|x11vnc|Xvfb|claude-desktop'`
**matched only the shell that ran it** — the pattern appears in that shell's own command line. Read
naively, it "finds" a running authproxy every time. `raw/02` preserves the raw output and `raw/03`
carries the corrected forms (`comm`-based `ps`; `pgrep` filtered against the snapshot path). The
correction matters: this session's entire cleanup was supposed to be *enumerated from that output*.

---

## Phase-by-phase: what changed

### Phase 1 — baseline and inventory (no changes)
Byte-freeze baseline `raw/00`. Health `raw/01`: service **active**, `NRestarts=0`, `/health` **200**,
`runpm 0`, dGPU by id **`0x744c`**, VRAM 19.62/25.75 GB. Inventory `raw/02`, corrected in `raw/03`.
Kernel observed at **`7.0.0-30-generic`** — drifted since HJ1's `-29`.

### Phase 2 — J0B resolved honestly
**Preserved first, then cleaned.** `bundles/GATE-J0B/PARTIAL/` now holds 25 raw captures, four
serial logs, both proxy sources, `apicalls.log` and `cap.sh` — copied, not moved. Deliberately
excluded: `seed.img`, the overlay, `__pycache__/`, the `.pid` files. The account is
`WHAT-HAPPENED.md` there.

**J0B ran Phases 0–4 of 8 and its result stands** — the egress pinhole is proven from inside the
locked guest (DNS `curl 6`, SLIRP gateway `curl 7`, proxy `200` with the real model server behind
it). Phases 5–7 never ran.

**The two deletes** (`raw/13` preconditions, `raw/14` execution) — each by name, `fuser` clear,
identity hashed first, following J0B's own `04-deletes.txt` pattern:

    /var/lib/wrought/j0b/j0b-overlay.qcow2   1160052736 B  sha256 dabad79affe9f9d8…6937191e
    /var/lib/wrought/j0b/seed.img               374784 B  sha256 700f639818c00788…70f848e4

1.16 GB reclaimed. **Kept:** the base image (sha256 still matching its pin), `j0a_key`, `user-data`.
**Left alone and reported because no prompt enumerated them:** `/home/kalib/overlay.qcow2`,
`/var/lib/wrought/j0b/__pycache__/`, three stale `.pid` files.

**Before removing the last seed on the box, the rebuild path was verified** (`raw/08`):
`cloud-localds` present (`cloud-image-utils 0.33-1build1`) and `/var/lib/wrought/j0a/user-data`
surviving. Checked *before* the delete, not after.

**QUEUE row → `RESET`**, a new terminal status defined in the status table this session, with the
prompt's dictated reason string.

### Phase 3 — the HJ2 recording debt, paid
`docs/EXECUTOR-RAILS.md` gains **§9 Heartbeat** and **§10 Adjudications are carried in**; the old §9
becomes §11. One line of each mirrored into the courier `README.md` (its "two hard rules" are now
four). §10 adds two things HJ2 did not specify, both learned since: extract verdicts **mechanically**
rather than retyping them, and if a prompt names a prior gate with **no verdict text**, record the
absence and invent nothing.

`bundles/GATE-HJ1/ADJUDICATION.md` written — extracted with `sed -n '62,71p'` from the archived
prompt, not retyped — and the HJ1 row set **`ADJUDICATED`**. The verdict's own kernel figure was
already stale when recorded (`-29`; the box runs `-30`) and is **annotated as such**, not quietly
updated. HJ2's row records that it was **folded into this gate**.

### Phase 4 — desktop back-out: PRIOR-COMPLETED, not re-run
See the table above and `raw/15`. Additionally verified that the prior purge **broke nothing**:
`apt-get check` clean, nothing orphaned, **0 pinned packages affected**, and the virtualization
substrate intact (`qemu-system-x86`, `libvirt-daemon-system`, `bubblewrap`, `cloud-image-utils` all
`ii`).

### Phase 5 — the snapshot
`SNAPSHOT.md` written and mirrored into `docs/PHASE-J-STATE.md`.

---

## Two findings this gate was not sent to look for

### 1. A dead gate session does not reap its guest — J0B's ran ~7 days
`grep -c 'reboot: Power down'` over J0B's four serial logs returns **`p2:1`, `p3:1`, `p3b:1`,
`p3c:0`**; the overlay was last written **2026-08-27 19:58:09**, inside the shutdown window of a
single boot spanning 2026-08-10 → 2026-08-27; `authproxy2.out` ends at `stream 2 opened` with no
close (`raw/11`).

**Stated limit:** not a direct observation of a live process, and it cannot become one — J0A
launched QEMU under `sudo` (journal-logged); **J0B launched it as plain `kalib`**, so no record
exists to recover. **Strongly supported, not directly observed.**

**Why it matters:** the authenticating proxy holds the inference API key **in memory** and was, on
the same evidence, bound to `127.0.0.1:8081` throughout — and `wrought-runner` is built to run
twenty hours while the operator is away, with nothing that reaps a dead gate's guest.

### 2. 15 of HJ1's 51 ratified pins have drifted — all of them libvirt
Mechanical, pin-by-pin (`raw/17`): **36 hold, 15 drifted, 0 missing.** The 15 are exactly the
libvirt closure, `12.0.0-1ubuntu5.2` → `5.3`, in one `unattended-upgrade` transaction on 2026-08-20.
The kernel drifted to `-30`, and **the same 2026-08-21 transaction removed the pinned `-28`
headers** — so the pinned kernel is no longer fully rebuildable from what is on the box.

Both appended to `pins.lock` `drift_observed`. **Neither re-pinned** — a pin moves only in the gate
that re-measures it. Two questions go to the advisor: does a libvirt point-release need its own
re-measure (libvirt is not a declared ST-1 trigger), and **`cloud-image-utils` is load-bearing but
absent from `pins.lock`**.

---

## Secret discipline

The courier is **public** and this push ships serial logs and proxy source. Scanned against the
**live sealed credential** (read from `/run/credentials/`, never printed) — `raw/12`:

    files in the PARTIAL bundle containing the literal key : 0
    files in the WHOLE courier tree containing it          : 0

Every long-hex hit is a sha256 digest of a file; every `api_key`/`secret`/`token` hit is a path or a
variable name, never a value. The proxy source reads its key from **stdin** into a variable and
redacts it from its own logs.

> **Correction, same session — the scans that produced these results were themselves defective.**
> They did `KEY=$(sudo cat …)` then `grep -rlF "$KEY"`, which expands the secret into grep's
> **argv** — precisely what rails §5 forbids. The **results above stand and were re-confirmed by
> the correct method** (`sudo cat <cred> | grep -rlFf -`, patterns from stdin): still **0** and
> **0**. Exposure was runtime-only and no secret reached any artifact — the shipped `raw/12` holds
> the *unexpanded* `"$KEY"` text. Recorded by **addition** in `raw/20`, never by overwriting
> `raw/12`. See audit item 9.

---

## Audit counts

| Metric | Count |
|---|---|
| Raw captures produced | **23** (`raw/00`–`raw/20`, `raw/99`, `raw/99b`) |
| Prompt premises checked | 3 |
| Prompt premises that failed against the box | **3** — all reported, none executed |
| Destructive commands the prompt specified | 5 (`pkill`, `apt purge`, 2×`rm -f`, `rm -rf`) |
| …of those actually run | **0** — every target already absent or already done |
| Files deleted | **2**, both enumerated by name, preconditions checked first |
| Bytes reclaimed | 1 160 427 520 (1.16 GB) |
| J0B evidence files preserved to the courier | **35** (25 raw + 4 serial logs + 2 proxy sources + 2 proxy `.out` + `apicalls.log` + `cap.sh`) |
| Ratified pins verified | **51** → 36 hold / 15 drift / 0 missing |
| Secret-scan hits | **0** in the bundle, **0** in the whole courier tree |
| Byte-freeze diff | **empty** |
| `wrought-*` units touched | **0** |
| Packages installed or removed | **0** |
| Foundry files changed | 4 (`docs/EXECUTOR-RAILS.md`, `docs/PHASE-J-STATE.md`, `pins.lock`, `BUILD-JOURNAL.md`) |

---

## Adversarial audit — the claims this report cannot fully support

Run before shipping, per rails §6. Its job is to find what a reviewer would challenge.

1. **"J0B's guest ran seven days" is an inference, not an observation.** Four independent facts
   agree and no competing explanation accounts for the 2026-08-27 overlay write — but no process was
   ever seen. The report says so wherever the claim appears. **A reviewer may reasonably downgrade
   this to "the overlay was written on 2026-08-27 and the p3c guest never logged a power-down."**
2. **The `cause` of the 2026-08-27 unclean shutdown is UNKNOWN.** Boot `-1`'s journal simply stops
   at 19:50:11 with no shutdown sequence. Power loss and a hard poweroff both fit. Not guessed
   (`raw/09`).
3. **"The operator ran the purge" rests on `Requested-By: kalib (1000)`** in the apt log. That is
   the uid, not proof of a human at a keyboard — an automated session running as `kalib` would look
   identical. The conclusion that the packages are *gone* is direct; the attribution is inferential.
4. **This gate did not verify that J0B's preserved evidence is *correct*,** only that it exists, is
   internally consistent, and is faithfully copied. The egress-pinhole result is quoted from J0B's
   own capture and has **not** been independently re-measured — the prompt forbade a J0B re-run.
5. **`raw/18` reported "28 LIBVIRT_ chains" by counting matching lines, which was wrong.** Corrected
   in `raw/19` to **14 chains** (6 unique names across two families) by counting `chain` declarations.
   The error is left in `raw/18` and corrected by **addition**, per rails §4 — never overwritten.
6. **"36/51 pins hold" depends on the extractor** parsing `pins.lock` correctly. It found exactly
   51 entries, matching the recorded `closure_count: 51`, which is a real cross-check — but the
   parser is this session's, not a pinned tool.
7. **The `RESET` status is new and unratified.** This session defined it in the QUEUE status table
   because the prompt dictated the row content and no existing status fit. **It needs the advisor's
   blessing** like `APPROVED` does.
8. **This gate's own secret scans violated rails §5.** They passed the key in `argv`
   (`grep -rlF "$KEY"`) rather than on stdin. The **findings are unaffected** — re-run correctly
   via `grep -rlFf -`, the answer is still 0 files in the bundle and 0 in either tree — and no
   secret reached any artifact. But the report's "Secret discipline" section presented these scans
   as clean practice, and they were not. **Found by the advisor, not by this audit's first pass** —
   which is itself the finding: the audit checked what the scans *concluded* and never checked how
   they *ran*. Corrected by addition in `raw/20`.
9. **Nothing was measured about the model.** No token was generated. **Escalation rate — P1, the
   governing metric — is not measured here**, as in every Phase-J session so far.

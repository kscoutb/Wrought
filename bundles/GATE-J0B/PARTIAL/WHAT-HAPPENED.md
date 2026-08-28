# GATE-J0B-SURFACE — what actually happened, and what did not

*Written by `GATE-RECONCILE` on 2026-08-28, from J0B's own workdir (`/var/lib/wrought/j0b/`)
and the host journal. J0B itself never wrote a report. Every claim below names the file it
came from; where the evidence does not reach, this document says **UNKNOWN** rather than guessing.*

## Summary

J0B was **dispatched 2026-08-20, ran ~18 minutes (00:07–00:25 UTC), completed Phases 0–4 of its
eight phases (0–7), and then stopped mid-Phase-4 without writing a report, a bundle, a journal
entry, or a `PHASE-J-STATE` update.** Its `STATUS.md` was left at `RUNNING P4` and its QUEUE row at
`RUNNING`, which is the stale state this gate resolves.

**The work it did do is real and is preserved here** — 25 capture files under `raw/`, each in the
project's `command → output → [exit=N]` form (J-95). It is *not* a bundle: no report, no
`SHA256SUMS`, no manifest, and no adversarial audit. It is partial evidence, and it is labelled as
such.

## What ran, phase by phase

| Phase | Status | Evidence |
|---|---|---|
| **0 — orient, baseline, deletes** | **COMPLETE** | `raw/00`–`raw/05` |
| **1 — authenticating proxy (host, loopback-only)** | **COMPLETE** | `raw/10`, `raw/11` |
| **2 — install boot (egress open for the fetch only)** | **COMPLETE** | `raw/20`–`raw/24` |
| **3 — locked boot (the air-gap proof)** | **COMPLETE**, after two corrected attempts | `raw/30`–`raw/35` |
| **4 — configure Goose + the C5 exposure map** | **STARTED, NOT FINISHED** | `raw/40`–`raw/42` (last write 00:25 UTC) |
| **5 — the agent turn (first manufactured tokens)** | **NEVER RAN** | no `raw/5x` file exists |
| **6 — the interception shim (Decision-1 seam proof)** | **NEVER RAN** | no `raw/6x` file exists |
| **7 — wind-down (report, bundle, journal, state doc)** | **NEVER RAN** | no report, no `SHA256SUMS` |

## What was proven

**1. The egress pinhole works — this is J0B's substantive result.** A three-way measurement from
*inside* the egress-locked guest, all `--max-time 5` (`raw/34-P3-egress-FINAL.txt`):

    http://connectivity-check.ubuntu.com    000  [curl exit=6]  (could not resolve host)
    http://10.0.2.2:8080/health             000  [curl exit=7]  (could not connect)
    http://10.0.2.100:8081/health           200  [curl exit=0]

The guest cannot resolve DNS, cannot reach the host's model server directly on the SLIRP gateway,
and reaches it **only** through the authenticating proxy at the `guestfwd` address. The body
behind the pinhole is the real server: `model_alias: primary-qwen27b`, `n_ctx: 65536`,
`build_info: b10233-0ab9d6fed`.

**2. The base image stayed immutable across a write-through boot** — re-measured, matching the
`pins.lock` pin `0533b0655c…40ffe` (`raw/24-P2-poweroff.txt`). J0A's core assumption held again.

**3. The two Phase-0 deletes were executed correctly** under the enumerated-delete rail, each with
its precondition checked first and the seed copied-and-hash-verified before its original was
removed (`raw/04-deletes.txt`).

**4. Goose was installed in the guest and did reach the model.** Its own SQLite store showed 3
sessions / 8 messages / 2 `usage_ledger` rows, and its request log confirmed the AAIF system prompt
(`raw/42-P4-c5-exposure-map.txt`). **No key material was found anywhere in the guest** — no
`secrets.yaml`, and no authorization/bearer/api-key string in any goose log on disk
(`raw/35`, `raw/42`).

## What was NOT proven

- **The agent turn never happened as a gate deliverable.** Phase 5 — first manufactured tokens
  through the surface — has no capture file. Goose *did* talk to the model during Phase 4's
  exploration, but that is an exposure-map observation, not the Phase 5 measurement.
- **The Decision-1 interception seam (Phase 6) was never tested at all.**
- Nothing was ratified: J0B proposed no pins and closed no decision.

## A hygiene finding this gate discovered: J0B left a guest running for seven days

**J0B's Phase-3c guest was never shut down. It ran from 2026-08-20 until the box went down on
2026-08-27.** The evidence (`../../RECONCILE/raw/11-guest-lifetime-limit.txt`):

- `grep -c 'reboot: Power down'` over the four serial logs returns **`p2:1`, `p3:1`, `p3b:1`,
  `p3c:0`** — the first three guests logged their power-down; the fourth never did. Its serial log
  ends at a `j0a-probe login:` prompt.
- `j0b-overlay.qcow2` was last written **2026-08-27 19:58:09 EDT** — seven days after the session,
  and inside the shutdown window of a single boot that spanned 2026-08-10 → 2026-08-27
  (`journalctl --list-boots`). Nothing else on the box writes to that file.
- `authproxy2.out`'s last line is `stream 2 opened from 127.0.0.1:54304` with no matching close.

**Limit of this evidence, stated plainly:** it is not a direct observation of a live process. J0A
launched QEMU under `sudo`, so its launches are in the journal; **J0B launched QEMU as plain
`kalib`** (a member of `kvm` since 2026-08-10), so no journal record of the process exists and
none can be recovered. The conclusion rests on the four facts above, which agree, rather than on a
process listing. It is **strongly supported, not directly observed.**

**Why it matters beyond J0B:** the authenticating proxy holds the inference API key in memory and
was, on the same evidence, still bound to `127.0.0.1:8081` for those seven days. A gate session
that dies mid-run currently leaves both its guest and its credential-holding proxy running
indefinitely, with no reaper. That is a live input to the `wrought-runner` ratification discussion.

## Residue, and what this gate did with it

All J0B processes were already dead at reconcile time (the box rebooted 2026-08-28 08:50) and
`virsh list --all` was **empty** — the guest was plain QEMU, never libvirt-defined, so there was no
domain to `destroy` or `undefine`. The scratch overlay and the seed were deleted by name; the base
image and `j0a_key` were kept. See `../../RECONCILE/REPORT-RECONCILE.md` §Phase 2 for the
enumerated list.

**After that delete, no cloud-init seed image exists anywhere on the box.** It is rebuildable
without any install — `cloud-localds` (`cloud-image-utils 0.33-1build1`, verified installed) plus
the surviving source `/var/lib/wrought/j0a/user-data` (sha256 `51fbe0df…1ecd5`) — and **a
re-dispatch prompt must include that rebuild step.** Note also that `cloud-image-utils` is
load-bearing for this workstream but is **absent from `pins.lock`**; that is a pins gap for the
advisor, not something this gate filled in on its own.

# PRE-FLIGHT — GATE-J0B-RESUME v2.0, checked BEFORE the operator starts a supervised batch

**The gate has NOT run.** This prompt is addressed to `wrought-runner` as a `claude -p` gate child,
not to an attended session, so the attended session's job is the courier record and a pre-flight —
not execution. Running it directly would defeat its stated purpose ("*it validates the runner*").

**Status: 3 BLOCKERS and 1 calibration risk. Do not start the runner until B-1 is fixed.**

Every finding below is mechanical — derived from the runner's own regexes and config, or from the
preserved `GATE-J0B` evidence, with the command that produced it.

---

## B-1 (BLOCKER, silent, total) — the prompt writes `ADD-DIR:`; the runner only reads `ADD-DIRS:`

    bin/wrought-runner:82   ADD_DIRS_RE = re.compile(r"^ADD-DIRS:[ \t]*(?P<dirs>.+?)[ \t]*$", re.M)
    prompt line 13          ADD-DIR: /var/lib/wrought/j0b

`ADD_DIRS_RE.search(text)` returns **None**. The line is **silently ignored** — no warning, no halt.

Measured, by parsing the archived prompt with the runner's own loaded regexes:

    ALLOWED-TOOLS : 'Read, Edit, Write, Bash'
    ADD-DIRS      : *** NO MATCH — the prompt's `ADD-DIR:` line is SILENTLY IGNORED ***
    => effective add_dirs for the gate child: ['/home/kalib/courier/Wrought']
    => gate_cwd: /home/kalib/foundry
    => /var/lib/wrought/j0b reachable by the child? *** NO ***

**Why this kills the gate outright.** Under `dontAsk`, a Bash command whose target lies OUTSIDE the
session cwd is DENIED *even when `--allowedTools` permits the command* — measured at `GATE-RUNNER`
`raw/14` and **re-verified on the installed 2.1.250** at `GATE-RUNNER-ARM` `raw/31` (both arms).
`/var/lib/wrought/j0b` is this gate's entire workdir: the seed, the overlay, the serial log, and
`apicalls.log` all live there. **Phase A step 1 — the very first command — would be denied**, and
so would the Phase B step 6 read of `apicalls.log` that the call-count evidence depends on.

**Fix (choose one, operator's call):**
- rename the header to `ADD-DIRS: /var/lib/wrought/j0b` in the dispatched prompt (smallest change,
  no code touched); **or**
- teach the runner to accept both spellings *and* halt loudly on a near-miss header rather than
  ignoring it. The second is the better long-term fix — a mandatory-header mechanism that silently
  drops a misspelled optional header is the same failure shape as rails §12.2's `ALLOWED-TOOLS`
  rule, which *does* halt when absent. **This is a gate question, not a box decision.**

## B-2 (BLOCKER, ordering) — Phase A cannot install Goose in an egress-LOCKED guest

The prompt orders Phase A as: **(2) boot LOCKED → (3) prove the pinhole → (4) install Goose**.
Step 4 fetches an 85 MB release from `github.com`. With `restrict=on` and only a `guestfwd` pinhole
to the proxy, **that fetch cannot succeed** — and it *must not*, because step 3 exists precisely to
prove the guest cannot reach anything else.

The original `GATE-J0B` did it the other way round, and the timestamps prove the sequence:

    raw/20-P2-overlay-and-boot.txt   utc=2026-08-21T00:12:13Z   boot with egress OPEN
    raw/21-P2-goose-release.txt      utc=2026-08-21T00:12:52Z   guest egress precheck -> 204; fetch release
    raw/22-P2-goose-install.txt      utc=2026-08-21T00:13:21Z   download 84957951 bytes, verify, install
    raw/24-P2-poweroff.txt           utc=2026-08-21T00:15:04Z   power OFF
    raw/30-P3-locked-boot.txt        utc=2026-08-21T00:15:53Z   re-boot LOCKED
    raw/31/34                                                    pinhole proven from the locked guest

**Fix:** restore the proven two-boot shape — boot OPEN, install Goose, power off, re-boot LOCKED,
then prove the pinhole and do all of Phase B. This is what "re-establish, don't belabor" should
mean; the prompt's own reference to "the fetch from GATE-J0B PARTIAL raw/21-22 shape" points at
exactly this sequence, so the ordering looks like a drafting slip rather than an intended change.

## B-3 (BLOCKER, hard rule) — Goose is NOT in `pins.lock`

    grep -n -i 'goose' pins.lock   ->  (no matches)

CLAUDE.md's first hard rule: *"Never invent configuration keys, thresholds, or version numbers. If
a value is not in these docs or `pins.lock`, it is a gate question — stop and surface it."*
The prompt says "the **pinned** Goose release" — there is no such pin.

The values exist, but only as `GATE-J0B` evidence, and they carry their commands (J-95):

    tag_name : v1.46.0                                        (raw/21, GitHub releases/latest)
    asset    : goose-x86_64-unknown-linux-gnu.tar.bz2
    size     : 84957951 bytes                                 (raw/22, curl -w size_download)
    sha256   : a1cf4856a765d07d6b95689a53c7bca21fcc6e6d65c0dfd064fc704052b85a7b   (raw/22)
    upstream : github.com/aaif-goose/goose  (successor org to block/goose; artifact ids still
               carry the old io.github.block reverse-DNS name — recorded at J0B, not relied on)

**Fix:** either the operator ratifies these into `pins.lock` before dispatch, or the prompt names
them explicitly as the values to use. **The box will not invent a pin**, and a gate that re-resolves
`releases/latest` would silently install whatever is newest — which is the same class of
reproducibility failure as the `claude` CLI self-update that `GATE-RUNNER-ARM` just closed.

## R-1 (CALIBRATION RISK, not a blocker) — the dead-man is TIGHTER than `RuntimeMaxSec`, and it wins

    runner.conf  limits.runtime_max_sec            = 5400 s  (90 min)  -> the kernel scope bound
    runner.conf  breakers.deadman_no_progress_sec  = 3600 s  (60 min)

`DeadMan.progress()` is **not called while the child runs** — `run_gate_child()` launches, calls
`deadman.attach()`, then blocks in `proc.wait()`. The dead-man thread therefore counts the child's
whole runtime as "no progress", and at 3600 s it stops the scope and kills the child. **The
effective per-gate ceiling is 60 minutes, not 90, and the smaller number wins silently.**

The docstring says the dead-man exists to bound *"a hung RUNNER — a git operation that never
returns"*, explicitly distinguishing it from `RuntimeMaxSec`, which *"already bounds a hung CHILD"*.
As implemented it bounds the child too, and more tightly. Neither number is measured — both are
`PROVISIONAL`, and this gate is meant to *set* them.

**Why it matters for THIS gate specifically:** boot a VM, fetch and install 85 MB, boot again,
run an agent turn against a local model, probe MCP, power off. If that crosses 60 minutes the gate
is killed mid-flight — and a killed gate very likely leaves its **guest running**, which the reaper
then catches as **`gate-residue`, a LATCHING fault**. That is two failures compounding on the first
supervised batch, and the second one requires `--reset-breaker` to clear.

**Suggestion (operator's call, and a good use of a supervised run):** either raise
`deadman_no_progress_sec` above `runtime_max_sec` so the kernel bound is the real one, or leave it
and watch the clock deliberately. Do not change it silently — it is exactly the kind of provisional
number this batch exists to calibrate.

---

## What is READY (checked, no action needed)

| Precondition | State |
|---|---|
| `/var/lib/wrought/j0b` | exists, `kalib:kalib drwxr-xr-x` — **writable without root** |
| base image | `/var/lib/wrought/j0a/noble-server-cloudimg-amd64.img`, sha256 `0533b065…40ffe` — **matches the pin exactly** |
| seed source | `/var/lib/wrought/j0a/user-data` present (1353 B) |
| guest ssh key | `j0a_key` (0600) + `j0a_key.pub` present |
| `cloud-localds` | `/usr/bin/cloud-localds`, `cloud-image-utils 0.33-1build1 install ok installed` |
| KVM | `/dev/kvm` `root:kvm`; `kalib` is in `kvm` **and** `libvirt` — **no root needed** |
| qemu | `/usr/bin/qemu-system-x86_64` present |
| port 2222 | free (ssh hostfwd) |
| `ALLOWED-TOOLS` spelling | `'Read, Edit, Write, Bash'` parses, and comma+space **works** — tested live: canary PRESENT, 0 denials |
| proxy script | `authproxy.py` **and** `authproxy2.py` both preserved; both listen `127.0.0.1:8081` → `127.0.0.1:8080`, both read the key from **stdin** (rails §5-clean), both write the same `apicalls.log`. The prompt's choice of `authproxy.py` is fine for call-counting. `authproxy2.py` is the later revision and is the one whose `.out` shows streams actually served |
| model server | `127.0.0.1:8080` LISTENING |
| proxy `:8081` | **not running** — correctly, it is operator pre-step 1 |

## Notes on the pre-steps themselves

- **Pre-step 2 asks the box to set `APPROVED`. It did not, and must not.** rails §12.1 and the
  courier `README.md` both assign `APPROVED` to **advisor + operator** — *"the gap between the two
  statuses is deliberate: it is where a human still sits on the unattended path."* The row is set to
  `QUEUED`; **the operator sets `APPROVED` at the ferry.**
- **Pre-step 3 (kill the proxy afterwards) is load-bearing beyond hygiene.** The proxy holds the
  inference API key **in memory**. `GATE-J0B-SURFACE` left exactly that running for seven days, and
  it is the incident the whole reaper exists because of. Note its pid when you launch it.
- **Launch the proxy BEFORE starting the runner**, as the prompt says — the reaper snapshots
  listeners *before* the gate and diffs *after*. A proxy started after the runner would appear as a
  **new listener** and be reaped as residue, latching the breaker.
- Transport: file-sourced via the courier, and the "exactly ONE indented block" claim is correct —
  one block, 3 lines, intact.

# GATE-J0B-RESUME — agent turn + interception seam, through the armed runner (v2.1, SUPERVISED)

*(v2.1 fixes the four defects GATE-J0B-RESUME v2.0's pre-flight caught: B-1 header spelling, B-2 the
two-boot ordering, B-3 the unpinned Goose, B-4 the broken proxy — advisor Fable owns B-1/B-2/B-3 as
drafting errors, thanks the box for all four. Executor: run THROUGH `wrought-runner` as a fresh
`claude -p` child. Operator: SUPERVISED — watch it. This is the first real-work runner batch: it
closes J0B's capability question, validates the runner + reaper on a REAL guest, and sets the
provisional scale numbers. The egress pinhole is already proven — re-establish it, don't re-litigate.)*

ALLOWED-TOOLS: Read, Edit, Write, Bash
ADD-DIRS: /var/lib/wrought/j0b
(No sudo in the gate child: qemu runs via the kvm group, the key-holding proxy is operator-launched.
If any step appears to need root, STOP and report — do not request a sudo allowlist entry.)

HEARTBEAT: push STATUS.md=RECEIVED, then keep it current per phase (frequent pushes also keep the
dead-man clear). Run through the runner, so the prompt is file-sourced; transport is a formality (exactly TWO indented blocks).

PRIOR-ADJUDICATION — GATE-RUNNER-ARM: **ACCEPTED (advisor Fable, 2026-08-28)** — the runner is armed
(installed-config start rc=0; a real gate ran the full contained path; four safety properties
re-verified on 2.1.250; CLI pinned + autoupdate closed; DBUS dropped; queue parser taught
RESET/FOLDED). Record per §10 if not already.

## ATTENDED PRE-FLIGHT — three edits before the runner starts (box + operator)
1. **Ratify the Goose pin into `pins.lock`** (B-3), from GATE-J0B evidence (each value carried its
   command, J-95). Add an entry and commit it:

    goose:  tag v1.46.0  |  asset goose-x86_64-unknown-linux-gnu.tar.bz2  |  size 84957951 bytes
            sha256 a1cf4856a765d07d6b95689a53c7bca21fcc6e6d65c0dfd064fc704052b85a7b
            upstream github.com/aaif-goose/goose  (successor to block/goose)

2. **Raise the dead-man above the runtime cap** (R-1): in `/etc/wrought/runner.conf` set
   `breakers.deadman_no_progress_sec` from 3600 to **6000** (still PROVISIONAL — this batch
   calibrates it), so the 90-min `runtime_max_sec` kernel bound is the real ceiling, not a 60-min
   dead-man that would kill a legitimately long first batch and then trip the reaper on its guest.
3. **Operator — launch the CORRECTED proxy** (B-4; the one privileged action, key never seen by the
   child):

    cp /home/kalib/courier/Wrought/bundles/GATE-J0B/PARTIAL/authproxy2.py /var/lib/wrought/j0b/authproxy2.py
    sudo cat /run/credentials/wrought-inference.service/inference-api-key | python3 /var/lib/wrought/j0b/authproxy2.py &
    # liveness only: curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8081/props  → 200
    # (the real proof is the in-guest guestfwd test in Phase A; v1 passed this liveness check and still failed there)

Then set this gate's QUEUE row **APPROVED**, `tmux new -s j0b`, start `wrought-runner`, and watch.
After the batch: kill the proxy, confirm nothing holds `:8081`.

## Rails — by reference
Read docs/EXECUTOR-RAILS.md. Byte freeze on state/. Enumerated deletes. Guests launch as descendants
of the gate's own scope (plain `qemu-system` via the kvm group, NOT libvirt) so the reaper covers them.

## Phase A — rebuild the proven environment, in its PROVEN TWO-BOOT SHAPE (B-2)
1. Rebuild the seed: `cloud-localds /var/lib/wrought/j0b/seed.img /var/lib/wrought/j0a/user-data`.
   Re-verify the base image against its pin (`0533b065…40ffe`) before use. Fresh overlay from it.
2. **Boot #1 — egress OPEN.** Boot the guest as kalib (kvm group, plain qemu, `-accel kvm`) with
   normal user-net. In-guest: fetch Goose **at the pinned tag v1.46.0**, verify the tarball sha256
   equals the pin, install to /usr/local/bin, `goose --version`. Configure it at the pinhole,
   keyless (route from GATE-J0B raw/41). Then **power the guest OFF**.
3. **Boot #2 — egress LOCKED.** Re-boot the SAME overlay with `restrict=on`, `hostfwd` for ssh, and
   `guestfwd tcp:10.0.2.100:8081` → the operator's `127.0.0.1:8081` proxy. Prove the pinhole from
   inside: external DNS fails, `10.0.2.2:8080` refused, `10.0.2.100:8081/health` → 200 (the J0B
   result, re-established). This is the guest all of Phase B runs in.

## Phase B — the three phases J0B never reached
4. **Finish the C5 exposure map** (Phase 4 was cut off): every place Goose asks for or stores a key.
   Feed nothing real; a required dummy is the literal `unused`, and record where it landed.
5. **The agent turn (Phase 5) — first manufactured tokens through the surface:** one bounded headless
   task, `goose run --no-session -t "Create /home/probe/FORGE.txt containing exactly the word FORGE,
   then print it."` with the filesystem builtin. Capture: goose exit 0; the file exists + contains
   FORGE; the host `apicalls.log` model calls (count them); wall-clock; a second-ssh
   `ps -ef --forest` of the guest tree (child-process evidence for the seam).
6. **The interception seam (Phase 6, Decision-1):** probe `goose mcp --help`; if Goose exposes a
   stdio MCP server, wrap it in a tee shim, re-run with the builtin disabled + the shim attached,
   and verify the frame logs carry JSON-RPC `initialize` / `tools/list` / a `tools/call`. If it does
   not, record the NEGATIVE precisely — a full-value result that decides BUILD-vs-VENDOR for the log-tap.
7. **Wind-down (Phase 7):** power the guest OFF (a clean sweep — a leftover guest is a reaper trip you
   do not want to cause). Byte-freeze re-assert + diff. REPORT-J0B.md: pinhole re-proof, C5 map,
   agent-turn result + call counts, seam verdict, **the gate's own wall-clock/token/cost** (these
   calibrate the runner's PROVISIONAL numbers), how the RUNNER behaved (did the scope contain the
   guest, did the mechanical verdict pass on real work, did the reaper stay clean), OTHER SURPRISES,
   WHAT THIS DID NOT ESTABLISH. Ultracode audit with counts. SHA256SUMS last. Set the row BUNDLED,
   push bundles/GATE-J0B-RESUME/, report the sha, STOP.

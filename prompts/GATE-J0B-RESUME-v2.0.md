# GATE-J0B-RESUME — the agent turn + interception seam, through the armed runner (v2.0, SUPERVISED)

*(Executor: run THROUGH `wrought-runner` as a fresh `claude -p` gate child. Advisor: Fable.
Operator: SUPERVISED — watch this batch. GATE-J0B RESET after it ran Phases 0–4 of 8 then stopped;
its environment was torn down by RECONCILE (guest + seed deleted), so this gate REBUILDS the proven
setup fast, then does the three phases J0B never reached: the agent turn, the interception seam,
wind-down. This is the FIRST real-work runner batch — it validates the runner (and the reaper, on a
REAL guest) and sets the provisional scale numbers. Prior proven result: the egress pinhole works
(locked guest reaches the model ONLY through the authenticating proxy); do not re-litigate it,
re-establish it.)*

ALLOWED-TOOLS: Read, Edit, Write, Bash
ADD-DIR: /var/lib/wrought/j0b
(No sudo. The gate child is unprivileged: qemu runs via the kvm group, and the key-holding proxy is
launched by the OPERATOR before the runner starts — see PRE-STEPS. If any step appears to need root,
STOP and report; do not request a sudo allowlist entry.)

HEARTBEAT: push STATUS.md=RECEIVED, then keep it current per phase. (Run through the runner, the
prompt is file-sourced, so the transport check is a formality: it contains exactly ONE indented
block.)

PRIOR-ADJUDICATION — GATE-RUNNER-ARM: **ACCEPTED (advisor Fable, 2026-08-28).** The runner is armed:
installed-config start rc=0, one real gate ran the full contained path (mechanical verdict PASS,
sweep clean, credentials torn down), all four safety properties re-verified on 2.1.250, CLI pinned +
autoupdate closed at both surfaces, DBUS dropped, queue-parser taught RESET/FOLDED. Record per §10.

## OPERATOR PRE-STEPS (before starting the runner — the one privileged action + the ferry)
1. Launch the key-holding proxy yourself (the single sudo; the gate child never sees the key). Reuse
   the preserved script:

    cp /home/kalib/courier/Wrought/bundles/GATE-J0B/PARTIAL/authproxy.py /var/lib/wrought/j0b/authproxy.py
    sudo cat /run/credentials/wrought-inference.service/inference-api-key | python3 /var/lib/wrought/j0b/authproxy.py &
    # confirm: curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8081/props  → 200

2. Commit this prompt to the courier `prompts/`, set its QUEUE row to **APPROVED**, then start the
   runner in tmux and watch:  `tmux new -s j0b ; /home/kalib/foundry/bin/wrought-runner`
3. After the batch: kill the proxy you launched (note its pid), and confirm nothing holds `:8081`.

## Rails — by reference
Read docs/EXECUTOR-RAILS.md. Byte freeze on state/. Enumerated deletes. Evidence never overwritten.
Guests launch as descendants of the gate's own scope (plain `qemu-system` via the kvm group, NOT
libvirt) so the runner's reaper covers them. Bundle returns through the courier at wind-down.

## Phase A — rebuild the proven environment (fast; it is already validated, so re-establish, don't belabor)
1. Rebuild the seed (no install — cloud-image-utils is present): `cloud-localds /var/lib/wrought/j0b/seed.img /var/lib/wrought/j0a/user-data`. Re-verify the base image against its pin (`0533b065…40ffe`) before use.
2. Fresh overlay from the pinned base; boot the guest as kalib (kvm group, plain qemu, `-accel kvm`),
   egress-LOCKED — `restrict=on`, `hostfwd` for ssh, and `guestfwd tcp:10.0.2.100:8081` → the
   operator's `127.0.0.1:8081` proxy. Poll ssh (UserKnownHostsFile=/dev/null, BatchMode, ConnectTimeout=5).
3. Re-prove the pinhole from inside the locked guest (the J0B result, re-established): external DNS
   fails, `10.0.2.2:8080` refused, `10.0.2.100:8081/health` → 200. Record all three.
4. Install the pinned Goose release in the guest (the fetch from GATE-J0B PARTIAL raw/21-22 shape);
   `goose --version`. Configure it at the pinhole, keyless (route from J0B raw/41).

## Phase B — the three phases J0B never reached
5. **The C5 exposure map, finished** (Phase 4 was cut off here): record every place Goose asks for or
   stores a key — env var, config field, keyring attempt, secrets.yaml fallback. Feed nothing real;
   if a dummy is needed use the literal `unused` and record where it landed.
6. **The agent turn — first manufactured tokens through the surface (Phase 5):** one bounded headless
   task, e.g. `goose run --no-session -t "Create /home/probe/FORGE.txt containing exactly the word
   FORGE, then print it."` with the filesystem builtin. Capture: goose exit 0; the file exists and
   contains FORGE; the host `apicalls.log` shows the model calls (count them); wall-clock; and a
   second-ssh `ps -ef --forest` of the guest process tree (child-process evidence for the seam).
7. **The interception seam (Phase 6, Decision-1):** probe `goose mcp --help`; if Goose exposes a
   stdio MCP server, wrap it in a tee shim, re-run the task with the builtin disabled and the shim
   attached, and verify the frame logs carry JSON-RPC `initialize` / `tools/list` / a `tools/call`.
   If it does not, record the NEGATIVE precisely — that is a full-value result that decides
   BUILD-vs-VENDOR for the log-tap.
8. **Wind-down (Phase 7):** power the guest OFF (so the reaper sweep is clean — a leftover guest is a
   reaper test you do NOT want to trigger by accident). Byte-freeze re-assert + diff. REPORT-J0B.md
   with the pinhole re-proof, the C5 map, the agent-turn result + call counts, the seam verdict,
   OTHER SURPRISES, WHAT THIS DID NOT ESTABLISH. **Record the gate's own wall-clock, token usage and
   cost** — these calibrate the runner's PROVISIONAL scale numbers. Ultracode audit with counts.
   SHA256SUMS last. Set the QUEUE row BUNDLED, push bundles/GATE-J0B-RESUME/, report the sha, STOP.

## Note for the report
This gate does double duty: it closes J0B's capability question AND is the runner's first real-work
batch. Say plainly how the runner behaved — did the scope contain the guest, did the mechanical
verdict pass on real work, did the reaper stay clean, what did the gate actually cost — because the
advisor uses that to ratify (or tighten) the provisional runner.conf numbers before any unattended run.

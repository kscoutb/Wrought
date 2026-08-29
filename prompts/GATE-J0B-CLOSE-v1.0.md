# GATE-J0B-CLOSE — finish the agent surface: extensions schema, F-5 proxy fix, work product, real-path seam (v1.0)

*(Executor: run THROUGH `wrought-runner` as a `claude -p` child. Advisor: Fable. Operator: one
mid-gate action (Phase 2, relaunch the proxy). J0B-RESUME proved the agent reaches the model and the
seam is interceptable, but the agent DID NO WORK — no filesystem tool loaded (goose 1.46 `extensions`
schema unknown), and the pinhole WEDGED under goose's unbounded-`max_tokens` retry storm (F-5). This
gate closes both, then proves the work product and goose driving its OWN tool calls through the shim,
and re-measures a CLEAN-gate cost so both cost caps can be re-calibrated. F-4 is doctrine: goose
exits 0 on total failure — assert on work product + host call log, NEVER on goose's exit status.)*

ALLOWED-TOOLS: Read, Edit, Write, Bash(cp:*), Bash(mv:*), Bash(rm:*), Bash(mkdir:*), Bash(chmod:*), Bash(cat:*), Bash(ls:*), Bash(grep:*), Bash(sha256sum:*), Bash(python3:*), Bash(qemu-system-x86_64:*), Bash(qemu-img:*), Bash(cloud-localds:*), Bash(ssh:*), Bash(scp:*), Bash(curl:*), Bash(tar:*), Bash(git:*), Bash(ps:*), Bash(pgrep:*), Bash(kill:*), Bash(timeout:*), Bash(sleep:*), Bash(tee:*), Bash(ss:*)
ADD-DIRS: /var/lib/wrought/j0b, /var/lib/wrought/j0a
(No sudo in the child — qemu via the kvm group; the key-holding proxy is operator-launched. If a
needed command is missing from the scoped list above, STOP and report it — do not work around it.)

HEARTBEAT: push STATUS.md=RECEIVED, then keep current per phase (frequent pushes keep the dead-man
clear). File-sourced by the runner; transport is a formality (no indented blocks — all literals inline).

PRIOR-ADJUDICATION — GATE-RUNNER-POLISH: **ACCEPTED (advisor Fable, 2026-08-29).** 39/39, byte
freeze held, all seven phases; the reaper is now precise (executable identity, zombies excluded,
multi-owner listeners, reap-refusal floor), the staged-diff secret scan has a committed home with
zero argv exposure, F-1/F-2 written into rails §2.1/2.2 and §13.3, `NOT RUN` corrected to
RESERVED-never-used, `reset_by` replaced by measured fields, the workspace boundary ARMED both
halves (bare `Bash` refused unconditionally; scoped-`Bash`+`ADD-DIRS` proven a real fence), and a
PROVISIONAL per-batch cost cap added. Both cost caps owe RE-CALIBRATION after F-5 — which is this
gate. Record per §10.

## Rails — by reference
Read docs/EXECUTOR-RAILS.md; note §2.2 — under the runner the byte freeze is the RUNNER's duty and
the child must NOT attempt it (the hook will deny it; log, don't alarm). §13.3 — a guest under the
runner budgets RAM against the 8 G scope: use `-m 3072`, never exceed `-m 4096`. Guests launch as
plain-qemu scope descendants (kvm group), never libvirt. Enumerated deletes; evidence never
overwritten.

## Phase 1 — DIAGNOSE + BUILD (open-egress guest; no locked pinhole yet, no key)
1. Rebuild seed + fresh overlay from the pinned base (verify `0533b065…40ffe`); boot guest #1 with
   egress OPEN; install Goose at the pinned tag v1.46.0 (verify sha256 `a1cf4856…5a7b`).
2. **Crack the goose 1.46 extensions schema** so the agent gets a working filesystem tool. J0B-RESUME
   found `developer` is in-process, not a stdio server, and the `extensions:` `config.yaml` attach
   silently did nothing. Determine the real schema by measurement — read goose's own config docs
   inside the guest, inspect `goose configure` behaviour, try candidate `config.yaml` shapes, and
   confirm a tool actually loads by having goose LIST its available tools (not by trusting a config
   parse). Deliverable: a goose config that makes a filesystem-write tool available to `goose run`.
   **If the schema cannot be established, STOP and report the negative precisely** — it decides
   whether the surface can manufacture at all, and is a full-value result either way.
3. **Write and UNIT-TEST `authproxy3.py`** (the F-5 fix), in `/var/lib/wrought/j0b/`, WITHOUT the key,
   against a local mock upstream (a trivial python echo server the child runs) — no guest, no sealed
   credential needed for the logic test:
   - it injects a bounded `max_tokens` into any `chat/completions` body that sends `max_tokens` null
     or absent (kills the unbounded-generation storm at the source);
   - it closes the UPSTREAM connection when the client disconnects (cancels the abandoned generation
     so it stops consuming the model), verified by the mock observing the close;
   - it otherwise preserves authproxy2's behaviour (stdin key, Authorization injection, SSE relay,
     per-request upstream, the apicalls log). Prove both new behaviours mechanically against the mock.
4. Power guest #1 off.

## Phase 2 — OPERATOR HANDOFF (the one manual step)
STOP and push STATUS=HALTED: "authproxy3.py written and unit-tested; operator, relaunch the proxy
with it." The operator kills the running proxy and launches the F-5 proxy with the sealed key on
stdin (same pattern as before, authproxy3.py), confirms `:8081` → 200, and resumes the gate. The
child never touches the key.

## Phase 3 — PROVE, in the locked guest, through the F-5 proxy
1. Boot guest #2 egress-LOCKED with the `guestfwd` to the operator's authproxy3 at `:8081`; re-prove
   the pinhole (external FAIL / `10.0.2.2:8080` REFUSED / pinhole 200).
2. **The work product (the actual capability question).** Run the agent turn with the Phase-1
   filesystem tool loaded: `goose run --no-session -t "Create /home/probe/FORGE.txt containing
   exactly the word FORGE, then print it."` Assert PASS on **work product + host call log only**
   (F-4): `FORGE.txt` exists and contains exactly `FORGE`, AND `apicalls.log` shows the model calls.
   Goose's exit status is NOT evidence.
3. **F-5 durability.** Drive the pinhole with goose's real retry/concurrency pattern (the shape that
   wedged J0B-RESUME) and show it does NOT wedge now: the pinhole stays 200 throughout, no
   `HTTP/0.9` empty-response failure, and `apicalls.log` shows generations bounded (the injected
   `max_tokens` took effect). If it still degrades, capture it precisely — F-5 is then not closed.
4. **The real-path seam (the seam's remaining limit).** With the interception `tee` shim on goose's
   OWN stdio-MCP path (using the Phase-1 schema, not a hand-written client), run a task that makes
   goose issue a tool call, and capture `initialize`/`tools/list`/`tools/call` frames driven by
   goose itself. This closes J0B-RESUME's "proven for the transport, not for goose's own loop."
5. Power guest #2 off.

## Phase 4 — CALIBRATE + wind-down
1. **Re-derive both cost caps from THIS clean gate.** Record this gate's actual child cost (from the
   runner's `verdict.json`, authoritative), and propose recalibrated `max_budget_usd_per_gate` and
   `max_batch_cost_usd` as PROVISIONAL values in PROPOSED-PINS-DELTA — do NOT edit runner.conf (a
   ferry decision). A clean gate's cost vs J0B-RESUME's wedged $7.53 is the whole point.
2. REPORT-J0B-CLOSE.md: the extensions schema (or the negative), the F-5 proxy fix + its proof, the
   work product PASS/FAIL, the F-5 durability result, the real-path seam frames, the clean-cost
   recalibration, how the runner/reaper behaved, OTHER SURPRISES, WHAT THIS DID NOT ESTABLISH.
   Ultracode audit with counts (compute verdicts from measured values — the POLISH lesson).
   SHA256SUMS last. Set the row BUNDLED, push bundles/GATE-J0B-CLOSE/, report the sha, STOP.

## Operator post-step
Kill the authproxy3 you launched; confirm `:8081` clear.

# GATE-J0B-CLOSE — finish the agent surface, one direct session (v2.0, ATTENDED-DIRECT)

*(Executor: Claude Code on forge-mini, Opus, ultracode — run as ONE DIRECT session, NOT through
wrought-runner. Advisor: Fable. This replaces the A/B split: a direct session does its own
sequential work — crack the goose schema, write the F-5 proxy, launch it itself, prove the work
product — with no mid-gate resume and no operator hand-off. The operator authorized full delegation,
so YOU (this session) launch the key-holding proxy via sudo; the key passes on stdin ONLY and is
never written, echoed, or placed in argv. Trade-off, stated: this gate does not get the runner's
kernel containment — accepted, the runner is already validated (J0B-RESUME) and this is the
capability gate, not another runner test. F-4 is doctrine: goose exits 0 on total failure — assert
on the work product + host call log, NEVER on goose's exit status.)*

HEARTBEAT: push STATUS.md=RECEIVED, keep current per phase.

## Rails — by reference
Read docs/EXECUTOR-RAILS.md. This is a DIRECT session, so §2.1 applies: hash
/var/lib/wrought/state/orchestrator.db{,-wal,-shm} at start and before finalizing; any change =
STOP EVERYTHING. Do not touch wrought-* units except read-only. Enumerated deletes only. Guests are
plain qemu via the kvm group (no sudo for qemu). The ONLY sudo is reading the sealed inference key
for the proxy, piped on stdin. Byte freeze is your duty here, not the runner's.

## Phase 1 — baseline
Byte-freeze baseline. Health: service active, /health 200, runpm 0, dGPU 0x744c VRAM. Rebuild the
seed (`cloud-localds`, from /var/lib/wrought/j0a/user-data) and a fresh overlay from the pinned base
(verify `0533b065…40ffe`), named /var/lib/wrought/j0b/close-overlay.qcow2.

## Phase 2 — crack the goose 1.46 extensions schema (open-egress guest)
Boot the guest egress OPEN; install Goose at the pinned tag v1.46.0 (verify sha256 `a1cf4856…5a7b`;
extract via python3 `bz2`, no apt). Determine by MEASUREMENT the config that makes a filesystem-write
tool actually available to `goose run` — read goose's in-guest config docs, inspect `goose configure`,
try candidate `config.yaml`/extension shapes, and confirm success by having goose LIST its tools (or
a probe run that writes a file), NEVER by a config parse. Record the exact working config; bake it
into close-overlay.qcow2. **If no config loads a tool, STOP and report the negative** — that decides
whether the surface can manufacture, and is a full-value result. Power the guest off.

## Phase 3 — the F-5 proxy, written and launched by you
Write /var/lib/wrought/j0b/authproxy3.py, extending authproxy2 with: (a) inject a bounded `max_tokens`
into any `chat/completions` body whose `max_tokens` is null/absent; (b) close the UPSTREAM connection
when the client disconnects mid-stream (cancel the abandoned generation); (c) otherwise byte-preserve
authproxy2 (stdin key, Authorization injection, per-request upstream, SSE relay, apicalls log). Diff
against authproxy2 and state what changed. Then LAUNCH it yourself, key on stdin only:
`sudo cat /run/credentials/wrought-inference.service/inference-api-key | python3 /var/lib/wrought/j0b/authproxy3.py &`
Record its PID. Confirm `curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8081/props` → 200.

## Phase 4 — prove it, in the locked guest
Boot close-overlay.qcow2 egress-LOCKED (`restrict=on`, `guestfwd tcp:10.0.2.100:8081` → your
`127.0.0.1:8081`). Prove the pinhole (external FAIL / 10.0.2.2:8080 REFUSED / pinhole 200). Then:
1. **WORK PRODUCT:** `goose run --no-session -t "Create /home/probe/FORGE.txt containing exactly the
   word FORGE, then print it."` with the Phase-2 tool loaded. PASS is asserted ONLY on: FORGE.txt
   exists and contains exactly FORGE, AND apicalls.log shows the model calls. Goose exit is not
   evidence (F-4). File not written = the surface does not manufacture yet; report it plainly.
2. **F-5 DURABILITY:** drive the pinhole with goose's real retry/concurrency pattern (the shape that
   wedged J0B-RESUME). Prove it does NOT wedge: pinhole stays 200, no HTTP/0.9 empty-response, and
   apicalls.log shows generations bounded (the injected max_tokens took effect). Still wedges =
   F-5 not closed, capture it.
3. **REAL-PATH SEAM:** put the interception tee shim on goose's OWN stdio-MCP path (via the Phase-2
   schema, not a hand-written client); run a task that makes goose issue a tool call; capture
   initialize/tools/list/tools/call frames driven BY GOOSE. Closes J0B-RESUME's "proven for the
   transport, not for goose's loop."

## Phase 5 — teardown + wind-down
Power the guest OFF. Kill the proxy by its recorded PID; confirm :8081 is clear (the key dies with
it). Byte-freeze re-assert + mechanical diff. REPORT-J0B-CLOSE.md: the schema (or negative), the
authproxy3 diff, work-product PASS/FAIL, F-5 durability, the real-path seam frames, this session's
own token/cost (note it is not a runner verdict.json, so the cost-cap re-calibration lands at the
first runner-run manufacturing gate — record the number here for it). PROPOSED-PINS-DELTA if
anything is newly pinnable (the goose config shape). Ultracode audit (verdicts from measured values).
Return through the courier: commit bundles/GATE-J0B-CLOSE/ + SHA256SUMS (generated last), set the
QUEUE row BUNDLED, push, report the sha, both trees clean, STOP.

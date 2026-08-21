# GATE-J0B-SURFACE — box session prompt v1.2

*(Executor: Claude Code on forge-mini, Opus, ultracode. Advisor: Fable. Prior state: GATE-HJ1
closed (J-157) — pins ratified, rails and live-state docs now exist ON THE BOX. Read them first,
per Phase 0. This session adopts ONE agent surface — Goose (aaif-goose/goose, Apache-2.0, single
Rust binary) — inside a disposable guest, proves it drives the local model through an
authenticating pinhole with the guest otherwise egress-locked, maps its secret handling (C5),
and locates the tool-dispatch interception seam (C4/Decision 1). v1.2 change from v1.1: the HJ2 heartbeat + adjudication-carrying rules are now standing; this
prompt honors them.)*

HEARTBEAT: the moment you read this file, push STATUS.md=RECEIVED per docs/EXECUTOR-RAILS.md
before the transport verdict, and keep it current at every checkpoint and every operator turn.

PRIOR-ADJUDICATION — GATE-HJ2-HEARTBEAT: to be adjudicated by the advisor before this runs; if
HJ2 is not yet ADJUDICATED on the courier, proceed anyway — J0B does not depend on it beyond the
heartbeat mechanism it installs. Record any PRIOR-ADJUDICATION block per the standing rule.

TRANSPORT INTEGRITY CHECK, FIRST: this prompt travels as a FILE and contains exactly TWELVE
indented command/config blocks (four-space indentation, no fenced code). If any block appears
empty, collapsed, or garbled, STOP and tell the operator. Do not reconstruct.

COURIER: per /home/kalib/courier/Wrought/README.md — before running, copy this prompt verbatim
to prompts/GATE-J0B-SURFACE-v1.1.md, set J0B to RUNNING in QUEUE.md, push. At wind-down the
bundle returns through bundles/GATE-J0B/ (Phase 7).

## Rails — by reference

Read docs/EXECUTOR-RAILS.md and follow it; it is now the canonical copy. The session-specific
points that override or extend it:

- LOCAL TOKENS ARE AUTHORIZED this session (the Phase 5/6 agent turns drive the local model).
  NO cloud call of any kind: the proxy targets 127.0.0.1:8080 only; the guest is egress-locked
  from Phase 3 on. $0 cloud spend, proven by the byte freeze.
- THE SEALED KEY passes on stdin only and never enters the guest, any file, argv, env, or the
  bundle. The guest holds no real key at any point (that is the whole C5 point of Phase 1).
- Authorized state changes: (A) host workdir /var/lib/wrought/j0b/ and a host-side loopback
  proxy process within it; (B) guest work on disposable overlays there; (C) the two enumerated
  deletes in Phase 0. NO host packages, NO unit changes, NO firewall changes, NO commits to the
  foundry repo.

## Executor mode (ultracode)

Subagents read-only (parallel captures + the pre-finalization adversarial audit: 3+ passes over
raw/, candidates to refuter agents, counts in the report). State changes serial in main thread.

## Phase 0 — orient, surface the rails, baseline, deletes

1. Read docs/PHASE-J-STATE.md and docs/EXECUTOR-RAILS.md. Confirm in the report that this
   session's premise matches PHASE-J-STATE's OPEN section (J0B is next; surface = Goose). If it
   contradicts, STOP — that is the J-156 check working.
2. Surface both docs for advisor review: copy them verbatim into the bundle as
   raw/00a-EXECUTOR-RAILS.md and raw/00b-PHASE-J-STATE.md. (The advisor cannot read the foundry
   repo; this is how the canonical docs reach review.)
3. Byte-freeze baseline (raw/00). Workdir /var/lib/wrought/j0b/ + raw/ created.
4. V-1 native closure (fresh login post-usermod, no sudo, no -g):

    id kalib
    python3 -c "import os; os.close(os.open('/dev/kvm', os.O_RDWR)); print('NATIVE KVM OPEN OK')"

   If it fails, record and fall back to sudo -u kalib -g kvm for launches (as round 2 did).
5. Health: service active, /health 200, runpm 0, dGPU by id 0x744c VRAM ~19-20 GB (the round-2
   identity loop).
6. Enumerated deletes, operator-approved: /var/lib/wrought/j0a/round2/overlay.qcow2 (the dirty
   boot-2 overlay); and /var/lib/wrought/j0a/round2/seed.img ONLY AFTER copying it to
   /var/lib/wrought/j0b/seed.img (record sha256 before+after the copy; they must match).
7. Re-verify the base image against its pin before any use:

    sha256sum /var/lib/wrought/j0a/noble-server-cloudimg-amd64.img

   Must equal 0533b0655c32e68b31d792ecd6ccfca95abdbc536c4446874fe0513bd4140ffe.

## Phase 1 — the authenticating proxy (host, loopback-only)

The guest talks to the model WITHOUT holding the key (C5), and every model call is centrally
logged (the Decision-1 log-tap prototype).

1. Write /var/lib/wrought/j0b/authproxy.py, python3 stdlib only:
   - Reads the API key as the FIRST LINE OF STDIN at startup; holds it in memory only.
   - Listens 127.0.0.1:8081. Per connection: parse the request head, inject
     "Authorization: Bearer <key>" (replacing any client Authorization), forward to
     127.0.0.1:8080, then BLIND BIDIRECTIONAL BYTE RELAY for the rest (carries SSE/streaming;
     do not parse bodies).
   - Appends one line per request to /var/lib/wrought/j0b/apicalls.log: ISO-timestamp, method,
     path, response status. No bodies, no headers, no key material.
2. Launch with the key on stdin only (credential path from recon raw/02b):

    sudo cat /run/credentials/wrought-inference.service/inference-api-key | python3 /var/lib/wrought/j0b/authproxy.py &

3. Prove it:

    curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8080/props
    curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8081/props

   Expect 401 then 200. Confirm with ss -lntp that 8081 is bound to 127.0.0.1 only.

## Phase 2 — install boot (guest, egress OPEN for the fetch only)

1. Fresh overlay j0b-overlay.qcow2 backed by the pinned base (round-2 command shape, 20G, full
   path to the base in /var/lib/wrought/j0a/).
2. Boot plain user-net + ssh hostfwd (round-2 launch line with this overlay and
   /var/lib/wrought/j0b/seed.img, serial-p2.log, qemu-p2.pid). Poll ssh with
   UserKnownHostsFile=/dev/null, StrictHostKeyChecking=no, BatchMode=yes, ConnectTimeout=5.
3. In the guest, fetch the latest stable Goose release from GitHub:

    curl -fsSL https://api.github.com/repos/aaif-goose/goose/releases/latest

   Record tag + asset list. Download the linux x86_64 CLI asset (expected shape
   goose-x86_64-unknown-linux-gnu.tar.bz2 — adapt to the real list, record the choice), sha256
   it (this becomes the pin candidate), extract, install to /usr/local/bin, then:

    goose --version

   ABORT this phase if no linux x86_64 asset exists or the binary fails on noble (glibc) — record
   exactly what happened; do NOT pipe any install script to bash.
4. Poweroff. The overlay now carries the installed surface and is the artifact under test.

## Phase 3 — locked boot (the air-gap proof)

1. Boot the SAME overlay egress-locked (round-2 launch line, serial-p3.log/qemu-p3.pid, the
   -netdev replaced by):

    -netdev user,id=n0,restrict=on,hostfwd=tcp:127.0.0.1:2222-:22,guestfwd=tcp:10.0.2.100:8081-tcp:127.0.0.1:8081

   restrict=on isolates the guest except explicitly set forwards — ssh (hostfwd) and the pinhole
   (guestfwd). [Assumption-based from QEMU docs; this phase measures it.] If qemu rejects that
   guestfwd form, fall back to:

    -netdev user,id=n0,restrict=on,hostfwd=tcp:127.0.0.1:2222-:22,guestfwd=tcp:10.0.2.100:8081-cmd:socat STDIO TCP:127.0.0.1:8081

   If both fail: record, continue with the Phase 2 netdev (egress OPEN), and mark every later
   result EGRESS-OPEN with the air-gap proof NOT ESTABLISHED.
2. From inside the guest, the three-way egress measurement (all --max-time 5):

    curl -s -o /dev/null -w '%{http_code}\n' http://connectivity-check.ubuntu.com
    curl -s -o /dev/null -w '%{http_code}\n' http://10.0.2.2:8080/health
    curl -s -o /dev/null -w '%{http_code}\n' http://10.0.2.100:8081/health

   Expect FAIL (external dead), FAIL (raw host endpoint closed under restrict), 200 (only the
   pinhole lives). Record exact failure modes.

## Phase 4 — configure Goose + the C5 exposure map

1. Point the provider at the pinhole. Route (a), config file:

    mkdir -p ~/.config/goose && printf 'GOOSE_PROVIDER: openai\nGOOSE_MODEL: primary-qwen27b\nOPENAI_HOST: http://10.0.2.100:8081\n' > ~/.config/goose/config.yaml

   If the openai route rejects the endpoint, route (b): a custom-provider JSON under
   ~/.config/goose/custom_providers/ with the API URL = the pinhole and "requires an API key" =
   false (Goose docs support keyless endpoints). Record which route worked and every file Goose
   wrote.
2. THE C5 EXPOSURE MAP — record, without feeding anything real: every place Goose asks for or
   stores a key (env var name, config field, keyring attempt, secrets.yaml fallback). If a dummy
   is required to proceed, use the literal string unused and record where it landed. A charter
   input, not pass/fail.

## Phase 5 — the agent turn (first manufactured tokens through the surface)

1. One bounded task, headless:

    goose run --no-session -t "Create /home/probe/hello.txt containing exactly the word FORGE, then print the file contents."

   (Add the filesystem/developer builtin via the flag the installed version expects —
   --with-builtin developer or equivalent; record the exact invocation.)
2. From a second ssh while it runs, capture the guest process tree (ps -ef --forest) — evidence
   for whether tool extensions run as child processes (the seam question).
3. Capture, each: goose exit 0; hello.txt exists and contains FORGE; host apicalls.log shows the
   model calls (count them); wall-clock for the turn.

## Phase 6 — the interception shim (Decision-1 seam proof)

1. Probe first: goose mcp --help (does the binary expose its builtins as a stdio MCP server?).
2. If yes, in the guest write /usr/local/bin/mcp-shim:

    #!/bin/bash
    tee -a /home/probe/frames-in.log | goose mcp developer | tee -a /home/probe/frames-out.log

   Run the same task with the builtin disabled and the shim attached as an external stdio
   extension (--with-extension "/usr/local/bin/mcp-shim" or the installed syntax). Verify
   frames-in/out.log contain JSON-RPC: initialize, tools/list, and at least one tools/call for
   the file write. That is the dispatch-interception seam working — every tool call through a
   point we control and logged.
3. If the shim route fails or goose exposes no stdio MCP, record precisely where the coupling is
   (in-process builtins only?). A NEGATIVE seam finding is full value — it decides BUILD-vs-VENDOR
   for the log-tap in the charter.

## Phase 7 — wind-down

1. Guest poweroff (non-vacuous down-check: round-2 ps comm= + pidof). KEEP j0b-overlay.qcow2 —
   the configured-surface artifact; say so.
2. Stop the proxy (kill its recorded pid); apicalls.log stays; grep it for anything
   secret-shaped as a rail check (expect none).
3. Update PROPOSED-PINS-DELTA.md (in the bundle): goose release tag + tarball sha256; base image
   pin unchanged. Update docs/PHASE-J-STATE.md on the box (wind-down duty): move J0B to its
   result, record the seam verdict and egress result.
4. Byte-freeze re-assert (raw/99) + mechanical diff BEFORE finalizing the report.
5. REPORT-J0B.md: byte-freeze table first; per-phase findings; the C5 exposure map; the seam
   verdict (shimmable or not, with evidence); egress lock results; token/call counts from
   apicalls.log; and — for pacing — the session's /usage at wind-down. OTHER SURPRISES; WHAT
   THIS DID NOT ESTABLISH (at minimum: no C7 policy gating, no hash-pinned tool registry, no
   multi-turn/endurance, no cloud tier, GPU passthrough still untested, ST-1 still queued).
   Run the ultracode adversarial audit with counts.
6. Return through the courier: bundle contents UNZIPPED into bundles/GATE-J0B/, set J0B to
   BUNDLED in QUEUE.md, commit (courier: GATE-J0B bundle) and push. Report the courier push sha
   and confirm both trees clean. STOP.

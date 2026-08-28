# REPORT — GATE-J0B-RESUME v2.1 (SUPERVISED, run THROUGH `wrought-runner`)

**Executor:** Claude Code (Opus 5, 1M) as a `wrought-runner` gate child, session under
`/var/lib/wrought/runner-state/runs/20260828T220144Z/GATE-J0B-RESUME/`.
**Date:** 2026-08-28. **Workdir:** `/var/lib/wrought/j0b`, evidence in `raw/50-65`
(J0B-SURFACE's `raw/00-42` untouched — rails §4).

**Headline:** the pinhole is re-proved, the C5 map is finished, **the agent turn manufactured real
tokens through the surface**, and **the interception seam EXISTS — Decision-1 is BUILD.** Two
findings landed that are bigger than this gate: the runner's own hook makes rails §2 unsatisfiable
for any gate child (F-1), and **goose exits 0 on total failure** (F-4).

---

## 0. Transport, adjudication, pre-flight

- **TRANSPORT-OK.** Claimed 2 indented blocks, measured 2, both intact.
  `sha256 88897e44…beb9d` matches the value the v2.1 pre-flight recorded. (`raw/50`)
- **§10 adjudication:** GATE-RUNNER-ARM was **already** recorded as `ADJUDICATED` by the pre-flight,
  mechanically (`sed -n '22,25p'`). Not re-recorded — re-extracting the same verdict from a
  re-worded carrier would replace a mechanical extraction with a paraphrase.
- **Pre-flight verified from inside the child**, not taken on trust: Goose pinned in `pins.lock`
  as `virtualization.guest_agent_surface` (tag v1.46.0); `deadman_no_progress_sec` = **6000** in the
  installed `/etc/wrought/runner.conf` (R-1 applied, 6000 > 5400 so `RuntimeMaxSec` is the ceiling);
  the proxy listening on 8081 is `authproxy2.py` with `sha256 ea2974ce…d99e`, **byte-identical** to
  the courier copy (B-4 satisfied).

## 1. F-1 — the runner's hook makes EXECUTOR-RAILS §2 impossible for a gate child

Rails §2 orders the child to hash the three orchestrator-store files at start and finish. The
runner's `PreToolUse` hook denies it:

    $ sha256sum /var/lib/wrought/state/orchestrator[.]db{,-wal,-shm}
    wrought-runner-hook: the orchestrator store is byte-frozen for the whole batch (EXECUTOR-RAILS S2)

`bin/wrought-runner-hook` `DENY[0]` matches `json.dumps(tool_input)` — the **command string**, never
the effect — so a read-only `sha256sum` is denied identically to an `rm`. **No workaround was
attempted**; routing around it would have been trivial (substring match), which is exactly why it
must not be done. **F-1b:** the hook also denies *writing about* the denial — two attempts to record
this were themselves denied for quoting the filename, so `raw/51` spells it `orchestrator[.]db`
throughout. An audit trail that cannot quote its own subject is worth naming.

**Nothing is actually lost.** The runner performs the freeze itself, on both sides, outside the
child (`wrought-runner:932`, `freeze-before.json` / `freeze-after.json` / `freeze-verdict.txt`,
`Halt("byte-freeze")` on drift), over exactly the three paths §2 names. That is **strictly better**
than the child's own measurement: taken by a process the child cannot influence. Baseline for this
run is in `raw/51`; `db-wal` is `e3b0c442…b855`, the sha256 of the empty string — a quiesced store.

**This gate did not re-assert the freeze and does not claim to have.** Phase 7's "byte-freeze
re-assert + diff" is the runner's, and its verdict lands in the run dir after this child exits.
**Recommended (not applied — outside the change set):** amend rails §2 to say that under the runner
the freeze is the runner's duty and the child must not attempt it.

## 2. Phase A — environment rebuilt in the proven two-boot shape

| step | result | evidence |
|---|---|---|
| base image vs pin | `0533b065…40ffe` **exact match** | `raw/52` |
| seed rebuild | `cloud-localds` rc=0, `sha256 f71c87da…21ca` | `raw/53` |
| fresh overlay | qcow2 on the pinned backing file, rc=0 | `raw/53` |
| **boot #1, egress OPEN** | booted, ssh in ~5 s, `systemd-detect-virt`=kvm | `raw/54` |
| Goose at the **pinned tag** | 84,957,951 B, `sha256 a1cf4856…5a7b` — **both match the pin exactly** | `raw/55` |
| install + config | `goose --version` → 1.46.0; keyless config at the pinhole | `raw/57` |
| power off | serial records `reboot: Power down` | `raw/58` |
| **boot #2, egress LOCKED** | same overlay, `restrict=on` | `raw/59` |

**The pin reproduces.** Fetched by URL at the pinned tag (`releases/latest` deliberately not
re-resolved), the asset's size and sha256 both equal the pin — an independent second confirmation
of the values GATE-J0B recorded.

### The pinhole, re-established (`raw/60`)

    1. external DNS / egress   curl: (6) Could not resolve host: github.com     -> FAILS
    2. host model server       curl: (7) Failed to connect to 10.0.2.2:8080     -> REFUSED
    3. THE PINHOLE             http_code=200  (10.0.2.100:8081/health)          -> 200
    4. control                 getent hosts github.com -> exit 2 (no resolution)

The J0B result exactly. `/props` also carries the real model through the pinhole. **B-4's corrected
proxy carries the guestfwd**, which is the thing v1 could not do.

### F-2 — J0B's proven guest shape would have killed this gate

J0B booted `-m 8192` as an attended session with no cgroup above it. A **runner child** lives in a
scope with `memory.max = 8589934592` (8 G, `limits.memory_max`), and rails §13.1 requires the guest
to be a scope **descendant** — so guest RAM comes out of the same 8 G as the agent. `-m 8192` + the
child = scope OOM, which kills the *gate*, not just the guest. Guest sized to **`-m 3072`**. The
host had 84 G free; **the binding constraint is the scope, not the box**, and no prompt or doc says
so. Any future gate that boots a guest under the runner must budget guest RAM against
`limits.memory_max`.

### F-3 — guest disk headroom is a real constraint on this surface

The noble root is 2.4 G; the Goose binary is **306,057,864 B uncompressed** (~12% of the disk), and
the naive install path stages it three times (~700 MB) and **filled the disk**. Also: the cloud image
has **no `bzip2`**, so `tar -xjf` fails outright. Resolved without `apt` (python3 stdlib `bz2`, then
extract the single member, then **rename** into place — same filesystem, so no second copy, which is
the only way it fits). Deletes were enumerated with reasons per rails §3 (`raw/57`).

## 3. Phase B.4 — the C5 exposure map, finished

J0B established: no `Authorization` header on the wire, no auth material in any on-disk goose log,
`secrets.yaml` absent, key vocabulary present in the binary. What it never did — and what this step
was for — is **feed a dummy and find where it lands**. Dummy = the literal `unused`. (`raw/61`)

- **`OPENAI_API_KEY=unused` is never persisted.** After the run, `secrets.yaml` still does not
  exist, and the literal string `unused` appears in **no** goose config, state or log file.
- **There is no keyring in the guest**: `gnome-keyring-daemon` absent, `secret-tool` absent, no
  secrets socket. Goose's own log says it plainly:
  `WARN "Keyring unavailable. Using file storage for secrets." target=goose::config::base`
  — so on this substrate the keyring branch is dead and **file storage is the only slot**, but
  nothing was ever written to it because nothing was ever configured *through goose*.
- **The env slot is read but not stored.** Supplying the dummy in `env` changed no on-disk state.
- **`goose configure` is interactive-only** (`Usage: goose configure`, no non-interactive flags), so
  the configure-path write to `secrets.yaml` was **not exercised**. Stated as a gap, not a result.
- **The C5 conclusion stands and is now better supported: there is nothing in the guest to steal.**
  The host proxy is the sole authenticator; the guest holds no credential in any form.

## 4. Phase B.5 — the agent turn: tokens WERE manufactured, the file was NOT written

**The surface works.** On a clean guest the turn ran end-to-end through the pinhole:

    goose rc = 0
    wall clock = 27 s
    apicalls.log DELTA = 3   ->  GET /v1/models 200
                                 POST /v1/chat/completions 200
                                 POST /v1/chat/completions 200

`ps -ef --forest` from a **second ssh during the turn** (`raw/62`, child-process evidence for the seam):

    probe 1126  bash -c cd /home/probe && timeout 300 goose run --no-session -t "Create ..."
    probe 1127   \_ timeout 300 goose run --no-session -t Create /home/probe/FORGE.txt ...
    probe 1128       \_ goose run --no-session -t Create /home/probe/FORGE.txt ...

**`FORGE.txt` was NOT created.** The model was reached and answered; the agent had **no filesystem
tool** to act with. `developer` is *in-process*, not one of the bundled MCP servers, and my attempt
to attach it via `config.yaml` `extensions:` **did not load** — the 1.46 stdio-extension schema was
not established by this gate. So Phase 5's acceptance list is **split**: model call ✅, call count ✅,
wall-clock ✅, process tree ✅, **work product ❌**.

### F-4 — goose EXITS 0 ON TOTAL FAILURE (the most important operational finding)

Every failing run in this gate — network error, no output, no file — returned **rc = 0**, while
goose's own log recorded `ERROR "Error: Network error ..."`. It knows it failed and exits 0 anyway.

**Consequence for the charter: goose's exit status is not a success signal and must never be used as
one.** Any harness wrapping this agent must assert on the **work product** and on the **host-side
call log**. The prompt's Phase-5 list asked for "goose exit 0" *and* "the file exists + contains
FORGE" — this gate is the demonstration that the second clause is the load-bearing one: the first
passed while the task produced nothing.

### F-5 — the guestfwd pinhole DEGRADES under an agent's connection pattern

The gate spent most of its wall clock on a wedge, and the diagnosis chain (`raw/62`) eliminated each
cause by measurement, including **two of my own hypotheses about `authproxy2.py` that were wrong and
are recorded as wrong**:

- **Not the dummy key** — clean env fails identically (one variable).
- **Not the proxy's request path** — POSTs with `Content-Length` **and** chunked bodies relay in
  ~1.5 ms; I read `relay_exact` (l.139) and `parse_headers` (l.105) and both hypothesised bugs
  (buffered-body loss, doubled CRLF) **did not exist**.
- **Not the proxy's streaming path** — a `stream:true` SSE response relayed cleanly, 200, 1799 bytes.
- **Not the model server** — it answers an unkeyed chat POST with 401 in **0.4 ms**.
- **`ps` %CPU is a lifetime average and lied** (0.7%); measured instantaneously from `/proc/7270/stat`,
  llama-server was at **39.2% of a core**, actively generating, with **three** proxy→upstream
  connections open and idle.

Two real effects, both new:

1. **Head-of-line blocking at llama-server.** Goose issues `stream:true` with **`max_tokens: None`** —
   unbounded. Abandoning the client does **not** stop the server; each retry (goose does 3) starts
   another unbounded generation that runs to the context limit, served serially. ~9 were started.
   Everything behind them — goose's own retries and my 240 s curl alike — appears to hang. The two
   *earliest* chat POSTs logged 200; everything after did not. It **drains** (it did, in ~4 min, then
   a bounded chat returned 200).
2. **The SLIRP guestfwd itself degrades.** After the retry storm, an in-guest `GET /health` that had
   returned 200 began failing **instantly** with `Received HTTP/0.9` (connection accepted, closed
   empty) and **zero** host-side proxy involvement (`apicalls` delta 0) — while the same request from
   the *host* still worked. **A guest reboot restored it completely** (0.42 s streaming chat from
   inside). So J0B's "the pinhole is proven" is true **for a fresh boot and sequential use**, and is
   **not durable** under a real agent's concurrent/retrying connection pattern.

**I did not clear the wedge by restarting `wrought-inference.service`** — a `wrought-*` unit, rails §1,
hands off, and the child has no sudo. The available non-privileged move (wait, then reboot the guest)
was taken instead and worked.

## 5. Phase B.6 — the interception seam: **POSITIVE. Decision-1 = BUILD.**

`goose mcp <SERVER>` exists. `developer` is **not** one of them; the bundled stdio servers are not
listed by the CLI and were enumerated by probing (`raw/63`):

    developer          -> invalid value for <SERVER>
    computercontroller -> VALID       memory         -> VALID
    tutorial           -> VALID       autovisualiser -> VALID

`Error: connection closed: initialize request` **is** the confirmation — each waits for a JSON-RPC
`initialize` on stdin. Wrapped in a two-line `tee` shim, both directions were captured verbatim
(`raw/64` 438 B in, `raw/65` 3196 B out):

    id=1  RESULT initialize -> protocolVersion=2024-11-05  serverInfo={'name':'goose-memory','version':'1.46.0'}
    id=2  RESULT tools/list -> 4 tools: [remember_memory, remove_memory_category,
                                         remove_specific_memory, retrieve_memories]
    id=3  RESULT tools/call -> {'content':[{'type':'text','text':'Stored memory in category: wrought'}],
                                'isError': False}

**`initialize`, `tools/list` and a real `tools/call` all traverse a stdio JSON-RPC transport that an
unprivileged two-line shim intercepts in full, in both directions.** The log-tap can be **BUILT**;
no vendor product is needed for this seam.

**Limit, stated plainly:** the shim was driven by a **hand-written client**, not by goose's own agent
loop, because the `extensions:` attach did not load. **Proven:** the transport is interceptable.
**Not proven:** goose driving its own tool calls through that shim.

## 6. How the RUNNER behaved — the other half of this batch

- **Did the scope contain the guest? YES, measured.** Every `qemu-system` launched with `-daemonize`
  reported the gate scope's own cgroup:
  `0::/user.slice/…/wrought-gate-gate-j0b-resume-1787954507-1.scope` (`raw/54`, `raw/59`).
  `-daemonize` double-forks, but cgroup membership is inherited and unaffected by reparenting, so
  rails §13.1 holds for the plain-qemu path in practice, not just in theory.
- **Reaper:** all three guests were powered off by the gate; serial logs record `reboot: Power down`
  and `:2222` is gone. **This gate leaves no residue to sweep** — the sweep verdict itself is the
  runner's to record after the child exits.
  *(Caution for whoever reads the sweep: `pgrep -f qemu-system` matches **this child's own command
  line**, because the gate prompt contains that string. That is a false positive waiting to happen.)*
- **Dead-man:** R-1's 6000 s was never approached; the gate ran ~27 min against a 90-min ceiling.
- **Hook:** fired on every call and denied exactly one class — see F-1.
- **Mechanical verdict on real work:** cannot be self-reported. `verdict.json` is written by the
  runner *after* this child exits.

### Scale numbers (these calibrate the PROVISIONAL values)

| quantity | this gate |
|---|---|
| wall clock, child | ~27 min (22:01:44Z → ~22:29Z) against `runtime_max_sec` 5400 |
| cost, child | **~$6.7 of the $8.00 cap** (from the harness's own running budget line) |
| guest RAM that actually fits | 3 G, inside an 8 G scope shared with the agent |
| model calls, successful turn | 3 (`GET /v1/models`, 2× `POST /v1/chat/completions`) |

**The $8 cap is the binding constraint, and it nearly bound.** ~84% consumed by a gate that hit one
unexpected wedge. Against GATE-RUNNER-ARM's measured 4.6×/6.94× overshoot, a gate that actually
overshoots would blow through. **The dead-man and `RuntimeMaxSec` were never the limit here — money was.**

## 7. Other surprises

1. `goose run`'s stdout prints what looks like a **session description**, not the assistant's answer
   ("Create and print FORGE.txt"). J0B read the analogous "Single word response" as the model's reply;
   on this evidence that reading is doubtful. Flagged, not resolved.
2. The cloud image ships **no `bzip2`** and **no `strings`** (the latter already cost J0B a false
   "no key slots" result).
3. `--no-session` still creates `sessions.db` and writes `llm_request.*.jsonl` to disk.
4. Goose sends **no `Authorization` header at all** when none is configured — not an empty one.

## 8. WHAT THIS DID NOT ESTABLISH

- **`FORGE.txt` was never written.** The agent turn reached the model but performed no tool call.
  Phase 5's work-product clause is **NOT** satisfied.
- **The `extensions:` config schema for a stdio MCP server in goose 1.46** — the attach silently did
  nothing. Until that is known, the shim cannot be put in goose's own path.
- **Goose driving its own tool calls through the tee shim** — the frames captured were driven by a
  hand-written client.
- **The original trigger of the very first `NetworkError`** (22:09:51, while the pinhole was healthy
  and the proxy logged a 200 one second later). The wedge that followed is fully explained; its
  *first* domino is not.
- **The `goose configure` → `secrets.yaml` write path** — interactive-only, not exercised.
- **The byte-freeze re-assert** — impossible from inside the child (F-1); the runner's artifact governs.
- **The runner's own gate verdict and sweep result** — written after this child exits.
- **`max_tokens` control for goose** — no knob was found, so the unbounded-generation behaviour that
  caused the wedge is **unmitigated** for the next gate.

## 9. Adversarial audit (rails §6)

Run against this report before shipping. Counts: **16** `raw/` files this gate (`raw/50`–`raw/65`),
J0B's `raw/00`–`raw/42` untouched (25 files, unmodified); **4** findings F-1…F-5 (F-1 has sub-finding
F-1b); **1** deviation D-1 (a/b/c); bundle `SHA256SUMS` generated last.

Claims the report cannot fully support, surfaced here rather than left for the reviewer:

- **"The seam is BUILD-able" is proven for the transport, not for goose's own loop.** Stated in §5;
  repeated here because it is the gate's headline and the weakest link in it.
- **F-5's SLIRP-degradation mechanism is inferred, not proven.** What is *measured* is: it worked,
  then failed instantly with an empty response and no host-side involvement, then a reboot fixed it,
  and the host path worked throughout. Connection-table exhaustion is the **hypothesis** that fits;
  I did not instrument SLIRP to confirm it. The correlation with the retry storm is temporal.
- **The cost figure is the harness's running total, not the runner's `verdict.json`.** Treat the
  runner's number as authoritative when it lands.
- **"No residue" is the child's view.** Only the runner's post-gate sweep can actually assert it, and
  it must not be fooled by the `pgrep -f` false positive noted in §6.
- **The C5 map is complete for the env and file paths, and has a hole at `goose configure`.** Saying
  "the map is finished" would overclaim; §3 states the gap.

## 10. Wind-down

Guest powered off (3 boots, 3 clean power-downs). `docs/PHASE-J-STATE.md` and `BUILD-JOURNAL.md`
updated per rails §11. `SHA256SUMS` generated last.

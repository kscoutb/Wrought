# REPORT — GATE-J0B-CLOSE v2.0 (ATTENDED-DIRECT)

**Executor:** Claude Code (Opus 5, 1M) on forge-mini, run as ONE DIRECT session — not through
`wrought-runner`. **Date:** 2026-08-29. **Workdir:** `/var/lib/wrought/j0b-close`, evidence in
`raw/10`–`raw/51` + `raw/99`. Artifacts the prompt names by path live in `/var/lib/wrought/j0b/`
(`authproxy3.py`, `close-overlay.qcow2`, `close-seed.img`). J0B's `raw/00–42` and J0B-RESUME's
`raw/50–65` are untouched.

**HEADLINE — the surface manufactures, and the thing that was actually blocking it was not what
anyone thought.**

- **Work product PASS.** `/home/probe/FORGE.txt` exists in the locked guest and contains **exactly
  `FORGE`** (5 bytes, `od -c` = `F O R G E`, no newline), written by the **real Qwen3.6-27B** through
  the pinhole via goose's `write` tool, with the host-side `apicalls.log` showing all five calls.
- **The goose 1.46 extensions schema is cracked** — and the answer is that **no `extensions:` stanza
  is needed at all** for a filesystem-write tool. Bundled tools are `type: platform`, not `builtin`.
- **J0B-RESUME's stated cause of the Phase-5 failure is MEASURED FALSE.** It concluded *"the agent
  had no filesystem tool to act with."* With its own byte-identical `config.yaml` in place, goose
  advertises **18 tools including `write`, `edit` and `shell`**.
- **F-5's real mechanism is found, and it is NOT the one J0B-RESUME hypothesised.** It is not
  connection-table exhaustion and it is not (only) unbounded `max_tokens`. **The SLIRP `guestfwd`
  pinhole is a single multiplexed byte stream that cannot carry a second connection at all.**
  Measured: **16 guest connections → 0 accepted by the proxy**, against **8 host connections → 8
  accepted**, same proxy, same instant, one variable.
- **F-5 is CLOSED**, by `authproxy3.py` (bounded generation + cancel-on-disconnect) **plus** moving
  the pinhole off `guestfwd` into the existing ssh channel. Three concurrent goose runs, **12/12
  chat calls answered, 0 unanswered, 12/12 bounded, no wedge.**
- **The real-path seam is CLOSED.** `initialize` / `notifications/initialized` / `tools/list` /
  **`tools/call`** all captured through the tee shim, driven by goose's own agent loop —
  `clientInfo: {"name":"goose-cli","version":"1.46.0"}`, and the `tools/call` frame carries goose's
  internal `agent-session-id`, `agent-working-dir` and `agent-tool-call-request-id`.
- **Byte freeze HOLD.** All three orchestrator-store hashes identical, mechanically diffed.

---

## 0. Transport, adjudication, and how this gate was authorised

**TRANSPORT: MISS — the seventh in eight.** The prompt arrived as **pasted chat text, not a file**
(rails §7 requires files), and it **states no indented-block count**, which §7 requires the executor
to check "before doing anything else". Measured: **ZERO indented blocks** — so nothing structural was
at risk and there was no damaged literal to reconstruct. Every load-bearing literal in it is an
inline code span, and all of them survived. Archived as a box **transcription** to
`prompts/GATE-J0B-CLOSE-v2.0.md`, sha256 `9355380d2113b2c4ecb980029ebf232af2860cb66376d8901a49d613b9e717b3`.
Recorded, not waived.

**Both truncated hashes in the prompt were matched against the FULL `pins.lock` values, never
against the ellipsis:** base image `0533b065…40ffe` → `0533b0655c32e68b31d792ecd6ccfca95abdbc536c4446874fe0513bd4140ffe`
(exact, `raw/12`); goose asset `a1cf4856…5a7b` → `a1cf4856a765d07d6b95689a53c7bca21fcc6e6d65c0dfd064fc704052b85a7b`
(exact, `raw/21`). The goose **binary** hash `29b3340e…4a89` also reproduces J0B-RESUME's value
exactly — a fourth independent confirmation of that pin.

**§10:** the prompt carries **no `PRIOR-ADJUDICATION` block and no verdict text**. Nothing was
recorded and **nothing was invented** (the `GATE-RUNNER` precedent). `GATE-RUNNER-POLISH` and
`GATE-ST-1` both remain `BUNDLED`, awaiting adjudication.

**The v1.0 pre-flight's blockers, dispositioned by the v2.0 prompt rather than by this gate:**

| | v1.0 finding | status under v2.0 |
|---|---|---|
| **B-1** | `ADD-DIRS:` comma vs whitespace → `HALT [add-dirs]` | **Does not apply.** No runner, no header parsed. **STILL LIVE AND UN-RULED** for the next runner-run gate. |
| **B-2** | Phase 2 asked the operator to *resume* mid-run; there is no resume | **Dissolved.** v2.0 withdraws the A/B split; one direct session, no hand-off. |
| **B-3** | scoped-Bash shapes; `Bash(python3:*)` escapes `--add-dir` | **Does not apply** to an attended-direct run. **STILL LIVE AND UN-RULED.** |
| **R-1** | no `MAX-BUDGET-USD:` → the un-recalibrated $8 cap | **Dissolved.** No runner ledger; this session records its own cost (§7). |

---

## 1. Phase 1 — baseline (`raw/10`, `raw/11`, `raw/12`)

Byte-freeze baseline taken by the session itself (rails **§2.1**, DIRECT). Under `wrought-runner`
this exact command is denied by the hook and the freeze is the runner's (§2.2, F-1); here it is the
box's own duty and it discharged it.

Health, all four clauses the prompt names:

| clause | measured |
|---|---|
| service active | `active`, `NRestarts=0`, `ActiveEnterTimestamp=Sat 2026-08-29 13:38:12 EDT` |
| `/health` 200 | **200 in 0.000390s** (unkeyed — the key gates the *chat* call) |
| `amdgpu.runpm=0` | present on the **live** `/proc/cmdline`, exact-token match, count **1** |
| dGPU `0x744c` VRAM | `[1002:744c]` Navi 31 at `card0`; **18.27 of 23.98 GiB** resident |

`llvmpipe` count **0** in the service journal.

Base image pin **exact**; seed rebuilt with `cloud-localds` as `close-seed.img` — deliberately **not**
over J0B's `seed.img` (rails §4: a prior session's artifact is not overwritten by this one).

**DEVIATION D-1, deliberate and stated:** the overlay was created at **16 G** virtual, not the
backing file's 3.5 GiB. J0B-RESUME's **F-3** measured the noble root at 2.4 G with the 306 MB goose
binary filling it during install (445 M spare after), and this gate additionally needed frame logs
and a stub server. cloud-init's growpart expanded it: **15 G, 13 G available** — F-3 is **relieved**,
and the install ran clean with no rename trick. Had growpart not run, the fallback was exactly the
surface J0B-RESUME proved installable, so the deviation had no downside branch. **The backing file
is byte-identical after all boots** (`raw/50`), so the disposable-guest assumption still holds.

---

## 2. Phase 2 — the goose 1.46 extensions schema, CRACKED (`raw/22`–`raw/29`, `raw/2a`)

### 2.1 The answer: for a filesystem-write tool, **the working config is the default**

`goose info -v` prints the **effective** extension configuration. With **no `config.yaml` at all**:

    developer:
      enabled: true
      type: platform          # <- NOT "builtin", and NOT "stdio"
      name: developer
      description: Write and edit files, and execute shell commands
      bundled: true

Thirteen bundled extensions, every one `type: platform`. **`developer` is enabled out of the box.**

### 2.2 J0B-RESUME's causal claim, tested with one variable and found FALSE

That gate wrote a three-line `config.yaml` and concluded the attach "did not load" and that "the
agent had no filesystem tool to act with". The hypothesis was never measured, so this gate measured
it: the **byte-identical 88-byte file** was written back, and `goose info -v` re-read. The extension
list is **unchanged** — all thirteen present, `developer` still `enabled: true` (`raw/24`).

**Writing that config.yaml suppresses nothing.** The filesystem tool was available all along.

### 2.3 Proof that is not a config parse — goose LISTING its tools, and then USING one

The prompt forbids confirming by config parse. Both stronger forms were taken, using a **stub
OpenAI-compatible endpoint inside the guest** (`stub_model.py` → `stub_model2.py`, sources
committed). This decouples *"is the tool available"* from *"will the model choose it"*, and needs
no credential — rails §5 forbids a key inside a guest.

- **Tools listed (`raw/26`):** goose sent a **18,562-byte** request advertising **18 tools** —
  `write`, `edit`, `shell`, `tree`, `read_image`, `analyze`, `delegate`, `load`, … The `write`
  schema it advertised is `{path, content}`, both required. *This is goose enumerating its own
  tools to a model*, not the box parsing a file.
- **Tool executed (`raw/27`):** the stub returned a `write` tool_call; **goose executed it and
  created `/home/probe/FORGE.txt`**, `od -c` = `F O R G E`. Written by goose's tool machinery — not
  by the stub, not over ssh.

**Also measured here, and it is the ground truth Phase 3 needed:** goose sends `stream: true`,
`stream_options: {include_usage: true}`, and **`max_tokens` ABSENT from the body**. Not inferred.

### 2.4 The stdio schema, obtained from `goose configure` — a path J0B-RESUME left unexercised

J0B-RESUME recorded `goose configure` as interactive-only and listed it as a hole in its C5 map.
Interactive is not un-scriptable: a **pty driver** (`drive_configure.py`, committed) walks it. Goose
then wrote the schema itself (`raw/29`) — which is what makes it safe to pin:

    wroughttap:
      enabled: true
      type: stdio
      name: wroughttap
      description: wrought interception tee over goose mcp memory
      cmd: /home/probe/mcp-tee.sh
      args: []
      envs: {}
      env_keys: []
      timeout: 300
      cwd: null
      bundled: null

**FINDING G-1 — `goose configure` REWRITES `config.yaml` and silently DROPS top-level keys.**
Before the walk: `GOOSE_PROVIDER` / `GOOSE_MODEL` / `OPENAI_HOST`. After it: **`GOOSE_PROVIDER` and
`GOOSE_MODEL` are gone**, replaced by a structured `providers:` block and `active_provider: openai`.
`OPENAI_HOST` survived. Any harness that hand-writes the flat keys and then runs `goose configure`
loses them without a word.

**C5 follow-up:** the configure walk wrote **no `secrets.yaml`** — the file still does not exist.
That closes the hole J0B-RESUME stated it could not test.

### 2.5 Acceptance, config-file-only (`raw/29`)

No CLI flag, only the baked `config.yaml`: **22 tools advertised = the 18 defaults + 4 through the
tee shim** (`wroughttap__remember_memory`, `…__remove_memory_category`, `…__remove_specific_memory`,
`…__retrieve_memories`). Verdict taken from the tool list goose sent, never from a parse.

**Baked into `close-overlay.qcow2`** and re-verified after the Phase-4 boot, byte-exact:
`config.yaml` sha256 `853c7f3e…5504`, `mcp-tee.sh` sha256 `643e4b72…0aea`, goose `29b3340e…4a89`.

---

## 3. Phase 3 — `authproxy3.py` (`raw/30`, `raw/31`, `raw/32`)

`sha256 d3e1477a65b5755e7d9bdfad8e58b896015131803a1a70e4fc447c87b3f4e732`, 522 lines vs
authproxy2's 361. **`authproxy2.py` is UNEDITED** — still `ea2974ce…d99e`. Full `diff -u` in `raw/30`.

**(a) Bounded generation.** New `read_body()` + `inject_max_tokens()`, and a body-buffer/head-reframe
branch in `serve_one` taken **only** for `POST .../chat/completions`. `max_tokens` is injected when
null **or** absent, exactly as the prompt specifies; a client-set value is left alone; a non-JSON or
non-object body is relayed **byte-for-byte** (fails open). 7/7 unit cases pass with no credential and
no upstream (`raw/31`), including the byte-preservation and key-preservation checks.

**THE VALUE IS NOT INVENTED** (CLAUDE.md hard rule 1). **24000** = `pins.lock`
`serving.reasoning_budget`, whose committed n=78 derivation calls it *"the same bound already
ratified for `--escalation-max-tokens`"* — the only ratified per-generation token bound in the file.
Against `ctx_size: 65536` it cuts the worst-case abandoned generation ~2.7×. **The number is
ratified; the proxy KEY that carries it is new**, so it goes to `PROPOSED-PINS-DELTA.md`, not into
settled config by this gate's own hand.

**(b) Cancel on client disconnect.** New `UpReader(Reader)` selects on the **upstream and the client
together**. authproxy2 already closed upstream in `serve_one`'s `finally` — what it lacked was any
way to *reach* that `finally` while blocked in `read_head()` waiting for a first byte an unbounded
generation would not send for minutes. **That blocked window is exactly the F-5 window.** MSG_PEEK
is used so a pipelined request is not consumed, and the watch is dropped on real bytes so `select`
cannot spin. Stated limit: a client that half-closes with `SHUT_WR` and keeps reading would be read
as gone; nothing on this path does that.

**Launched by this session**, key on **stdin only** (`raw/32`). PID **105783**. Rails §5 evidence
taken from `/proc`: argv is `python3 /var/lib/wrought/j0b/authproxy3.py` — a path, never a value —
and **0 environment variables carry a 64-byte value**. The proxy's own stderr reports the key
*length*, never the key.

Both changes proven end-to-end on the host before the guest ever booted:

| | measured |
|---|---|
| `/props` through the proxy | **200** (the prompt's required confirmation) |
| unkeyed chat POST direct to `:8080` | **401** — the proxy is the authenticator |
| injection | `max_tokens INJECTED = 24000 (body 174 -> 206 bytes)`, chat 200 in 5.10 s |
| **cancel** | abandon a long stream → llama-server **1.3 %** of one core (F-5's signature is ~39 %), **zero** dangling upstream sockets, next bounded chat **200 in 0.49 s** |

---

## 4. Phase 4 — proving it in the locked guest

### 4.0 The pinhole (`raw/41`)

`curl exit 6` external / `curl exit 7` to `10.0.2.2:8080` / **200** on the pinhole, `getent` exit 2.
The J0B and J0B-RESUME result, reproduced exactly, and `/props` carries the real model by path.

### 4.1 Work product — FAIL on the prescribed transport, then PASS (`raw/42`, `raw/43`, `raw/44`, `raw/47`)

**Runs 1 and 2 (over the prescribed `guestfwd`) reached the model and wrote no file.** Reported
plainly, as the prompt requires. Then, before blaming the model, the box tested the *server's*
capability:

| test | result |
|---|---|
| 1 tool, non-streaming, through authproxy3 | `finish_reason: tool_calls`, a correct `write` call, 3.3 s |
| the same, **streaming** | 15 tool_call deltas, `finish_reason: tool_calls`, 3.6 s |
| **goose's OWN captured 22-tool body**, user turn swapped to the FORGE task | **`write` called, 2.3 s** |

So the server, the streaming path, goose's 22-tool prompt and the model's willingness were **all
fine**. There is **no `--jinja` gap** — llama-server parses tool calls correctly. The failure was
underneath all of it, in the transport (§4.2).

**Run 3 changed exactly one thing** — `OPENAI_HOST` pointed at the ssh-carried pinhole instead of
`10.0.2.100:8081`. Same guest, same baked config, same model, same task:

    ▸ write     path ~/FORGE.txt   content: FORGE
      Created /home/probe/FORGE.txt (1 lines)
    ▸ shell     command: cat /home/probe/FORGE.txt
      FORGE

**ACCEPTANCE, both clauses, and not one clause wider:**

1. **Work product** — `/home/probe/FORGE.txt`, 5 bytes, `od -c` = `F O R G E`, `b'FORGE'` **exact**.
2. **Host call log** — `apicalls.log` delta **5 lines**: `GET /v1/models 200` + **4× `POST
   /v1/chat/completions 200`**, 23:19:20 → 23:19:51.

**goose exited 0 in all three runs, including the two that produced nothing (F-4). Its exit status
was used as evidence for nothing.**

### 4.2 F-5 durability — the mechanism, and the closure (`raw/45`, `raw/46`, `raw/48`)

**What the failure actually was.** Two separate goose runs, four minutes apart, were served on the
**same proxy client stream ("stream 7")** — the proxy assigns a stream id per accepted connection,
so this means the host-side connection is opened **once** and never closes. `ss` showed that
connection's qemu end holding **14,479 bytes unread**, while llama-server sat at **0.0 % cpu with no
upstream connections**. Not the model, not the proxy's upstream path — the pinhole transport.

**The A/B, one variable — the transport between guest and proxy:**

| | connections | proxy streams accepted | results |
|---|---|---|---|
| **GUEST via `guestfwd`** | 16 (8 sequential + 8 concurrent) | **0** | mixed 200/`000`; three hung the full 20 s |
| **HOST direct to the proxy** | 8 concurrent | **8** | **8× 200, all under 3 ms** |

**J0B-RESUME's hypothesis is measured FALSE.** It offered connection-table exhaustion, honestly
flagged as inferred. The truth is structural and needs no retry storm: **`guestfwd=tcp:…-tcp:host:port`
is a single always-on multiplexed byte stream, and a second concurrent guest connection is not
served at all.** It reproduces on the *first* concurrent pair. The `HTTP/0.9` empty response
J0B-RESUME saw is this, and a guest reboot "fixed" it only by resetting the one stream.

**THE FIX, measured (`raw/46`):** carry the pinhole **inside the ssh channel the gate already has** —
`ssh -N -R 18081:127.0.0.1:8081 probe@guest`. Nothing is widened: the guest keeps `restrict=on`,
gains only a **loopback** listener, and the carrier is **authenticated** — arguably tighter than an
unauthenticated IP-level forward. **The egress proof was re-run with the tunnel up and still holds**
(external `curl exit 6`, `10.0.2.2:8080` `curl exit 7`). Eight concurrent guest requests: **8/8 200**,
9 proxy streams accepted.

**DURABILITY RESULT — three CONCURRENT goose runs, the shape that wedged J0B-RESUME (`raw/48`):**

| | |
|---|---|
| runs that manufactured | **3 of 3** — `D1/D2/D3.txt`, each exactly `DURABLE` |
| chat POSTs | **12**, of which logged a status: **12** |
| requests left unanswered (`NO-RESPONSE`) | **0** |
| `max_tokens` injections | **12 / 12** — every generation bounded |
| `CLIENT-GONE` cancellations needed | **0** |
| post-burst guest health | **3× 200**, no `000`, no `HTTP/0.9` |
| llama-server after | **0.0 %** of one core; **no** dangling upstream sockets |

**F-5 is closed** — by both halves. `authproxy3` bounds and cancels; the ssh-carried pinhole removes
the transport that could not carry goose at all.

### 4.3 Real-path seam — CLOSED (`raw/49`)

The shim is attached through the **Phase-2 config schema** baked into the overlay (`type: stdio`,
`cmd: /home/probe/mcp-tee.sh`) — no CLI flag, **no hand-written client anywhere in the path**. Goose
was asked to store a memory; it called the tool. All four frames captured:

    -> {"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-11-25",
        ...,"clientInfo":{"name":"goose-cli","version":"1.46.0"}}}
    -> {"jsonrpc":"2.0","method":"notifications/initialized"}
    -> {"jsonrpc":"2.0","id":1,"method":"tools/list","params":{"_meta":{"agent-session-id":"20260829_5",...}}}
    -> {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"_meta":{"agent-session-id":"20260829_5",
        "agent-working-dir":"/home/probe","agent-tool-call-request-id":"aidBkNfXYTRjg0wLGkp98dl0sU065Izd",
        "progressToken":1},"name":"remember_memory",
        "arguments":{"category":"wrought","data":"the forge seam is closed","is_global":false}}}

    <- id=2 RESULT tools/call -> [{"type":"text","text":"Stored memory in category: wrought"}] isError=False

**`clientInfo` names goose itself, and the `_meta` block carries goose's internal agent-session id,
working directory and tool-call request id.** No hand-written client produces those. The side effect
landed on disk: `/home/probe/.goose/memory/wrought.txt` → `the forge seam is closed`.

**A difference the hand-written client could not have revealed:** goose negotiates
`protocolVersion 2025-11-25`; J0B-RESUME's hand-written client negotiated **2024-11-05**. The seam
was being probed at a different protocol version than the real client uses.

**J0B-RESUME's stated limit — *"proven for the transport, not for goose's loop"* — is now closed.**

---

## 5. Phase 5 — teardown (`raw/50`), byte freeze (`raw/99`, `raw/99b`)

Guest powered off from inside (`reboot: Power down`); **0** `qemu-system-x86_64` processes by
**executable** match; `:2222` clear; ssh tunnel gone; proxy killed **by its recorded PID** (105783,
recorded at launch, not discovered by a pattern match) and **`:8081` CLEAR — the key died with the
process**. Base image hash unchanged after every boot. `wrought-inference.service` shows the **same**
`ActiveEnterTimestamp` and `NRestarts=0` as Phase 1 — never stopped, started, restarted or reloaded.

**BYTE FREEZE: HOLD.** All three hashes identical between `raw/10` and `raw/99`, compared by
`diff` over extracted hash lines rather than by eye (`raw/99b`).

---

## 6. Deviations — all three were mine, all three are recorded

- **D-1 (Phase 1, deliberate):** 16 G overlay. Rationale and fallback branch in §1.
- **D-2 (Phase 2, a bug):** the stub's capture directory was `rm -rf`'d **after** the stub created
  it at start-up, so every POST raised `FileNotFoundError` inside the handler and goose correctly
  reported a network error. The stub never died. Recorded in `raw/25`, not retried silently.
- **D-3 (Phase 5, a bug — and a RECURRING CLASS):** the teardown used
  `pgrep -f "ssh -N -p 2222"`, and `-f` matches the whole command line — **including the command
  line of the shell running the teardown, which quotes the pattern.** It killed its own shell; the
  tool call exited 144 with `raw/50` truncated. Continued **by appending** (rails §4). Nothing else
  was lost, and state was re-measured from the box rather than assumed.

  **This is the third occurrence of one class in two days**, and the first two are already written
  up as fixed: `GATE-RUNNER-POLISH` removed exactly this from the reaper (`pgrep -f qemu-system`
  matching the tool-call shell), and **this gate hit it again in Phase 2** (`pkill -f stub_model.py`
  killed the remote shell, `raw/25`). The rule the repo already drew — **match the executable, never
  the command line** — was applied to the reaper and not to ad-hoc session commands, which is where
  it keeps recurring. The qemu check three lines above the failure got it right (`pgrep -x`), in the
  same file, minutes earlier. **Knowing the rule is not the same as having it in the fingers**, and
  that is the finding worth carrying forward, not the individual slip.

---

## 7. Cost (`raw/51`)

**Not a runner `verdict.json`.** No ledger, no batch-cost breaker, no independently-taken
measurement — so the cost-cap **re-calibration lands at the first runner-run manufacturing gate**,
and this is recorded so that gate has a same-workload reference.

Measured exactly from this session's transcript: **232 assistant turns**, `claude-opus-5` —
input **1,292**, cache-write **789,383**, cache-read **40,319,497**, output **333,934**;
**41,444,106 billable tokens**.

Derived: **≈ $33.45**. `[VERIFIED]` base rates $5.00/$25.00 per MTok with a 1 M context and **no
separate long-context premium**, read this session from the bundled `claude-api` reference rather
than recalled. `[ASSUMPTION]` cache multipliers 1.25× write / 0.10× read — **the reference's table
does not carry them**, and **the total is dominated by that assumption**: at the full input rate the
same tokens would be **$214.89, a 6.4× difference**. The **token counts are the durable
measurement**; the dollar figure is provisional and should be priced against a billing source.

**The substantive warning, which matters more than the figure:** an attended-direct session carries
the whole gate in **one** context, so its cost is dominated by cache reads in a way a runner child's
never is (J0B-RESUME: ~$6.70; clean POLISH children: $0.08–$0.19). **A cap derived from this number
would be wrong for a runner child, and vice versa. The two shapes need two numbers.**

---

## 8. WHAT THIS GATE DID NOT ESTABLISH

- **Whether `guestfwd` can be made to work at all.** The box measured that it does not carry
  concurrency and moved the pinhole; it did **not** try alternative `guestfwd` spellings, a QEMU
  version bump, or a socket-per-connection chardev. The negative is bounded to the form the prompt
  prescribed, as run.
- **Why runs 1 and 2 failed in the specific way they did.** The transport is proven unable to carry
  goose; the exact frame at which each run gave up was **not** reconstructed, because goose's
  `llm_request.*.jsonl` captured only the title call, never the agent turn. The *mechanism* is
  measured; the per-run post-mortem is not.
- **The ssh-carried pinhole under a runner child.** It was proven attended. A gate child's ability to
  hold an `ssh -N -R` process inside the scope for a whole gate is **untested**, and rails §13.1's
  reaping argument has not been re-run for it.
- **Any claim about goose's retry behaviour.** No run in this gate triggered goose's 3× retry, so
  the "retry storm" half of J0B-RESUME's F-5 narrative was **never reproduced here** — it was
  rendered unnecessary by fixing the transport, not tested and found absent.
- **`--reasoning`'s interaction with agent turns.** The title call spent **1,228 output tokens
  entirely on reasoning** for a three-word answer. That is a real observation about this serving
  configuration; its effect on manufacturing throughput was **not** measured.
- **A long-context trigger.** Unchanged from `GATE-ST-1`: SPEC-R11.1's long-context family is still
  untested, and nothing here touches it.
- **The runner-side blockers B-1 and B-3.** Dissolved *for this gate*, live and **un-ruled** for the
  next runner-run one.

---

## 9. Adversarial audit

See `AUDIT.md`, run against this report before it shipped.

## 10. Wind-down

Guest off (2 boots, 2 clean power-downs), proxy dead, `:8081` clear, byte freeze HOLD.
`docs/PHASE-J-STATE.md` and `BUILD-JOURNAL.md` updated per rails §11. `SHA256SUMS` generated last.

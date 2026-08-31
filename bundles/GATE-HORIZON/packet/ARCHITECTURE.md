# ARCHITECTURE — Wrought Foundry as built, 2026-08-31

A single-node, local-first, air-gap-capable **software-manufacturing pipeline**: a task description
in, a verified tool out, with a deterministic non-AI oracle deciding pass or fail. It is built and
operated almost entirely by AI agents, under a protocol designed around that fact.

**Read this as an honest inventory, not a brochure.** Where something is unproven it says so, and
the qualifiers are load-bearing — this project has twice had a summary drop a qualifier and turn a
narrow result into a broad claim, which is why they are written in the strongest available form.

---

## 1. Substrate

**One box, `forge-mini`.** AMD Ryzen AI 9 HX 370 (12C/24T, single NUMA, AVX-512 incl. VNNI and
BF16), 87 GiB RAM, Ubuntu 26.04, headless, **reachable only over Tailscale**. Inference runs on an
**RX 7900 XTX, 24 GB, over OCuLink PCIe 4.0 ×4** — an external dGPU, deliberately independent of
the iGPU's UMA carve.

**Serving is llama.cpp on Vulkan**, not ROCm. The device is selected **by name**, never by a
`Vulkan0`-style index, `llvmpipe` is excluded by assertion, and a boot-time `ExecStartPre` refuses
to start if the wrong device would be bound. That check exists because a silent fallback to
CPU rasterization produces garbage at plausible-looking speeds.

**The NPU is present and unused.** XDNA2, the in-tree `amdxdna` driver is bound and
`/dev/accel/accel0` is live — **and no userspace stack is installed.** Nothing in this system
offloads anything to it today. Any roadmap item that routes work to the NPU is starting from a
driver node and a kernel driver, not from a working runtime.

**Disposable guests are plain QEMU/KVM**, launched as descendants of a systemd scope so they die
with it. A libvirt domain deliberately is *not* used for gate work: libvirtd is a separate daemon
and the domain re-parents into `machine.slice`, outside the scope entirely — measured, after a
gate died and left a guest running for **seven days** with an API key in a proxy's memory.

**Measured substrate facts:** boot-to-ssh ≈ 15 s; a full discard-and-revert overlay cycle ≈ 15 s;
the base image is **immutable by hash** across guest boots (the disposable-guest model's core
assumption, measured rather than assumed).

## 2. Orchestrator and FSM

An explicit, hand-rolled finite state machine over ten states —
`PENDING → VALIDATING → PLANNING → IMPLEMENTING → VERIFYING → {REPAIRING, ESCALATING} →
{COMPLETED, HUMAN_REVIEW} → ARCHIVED`. It is a **transition table**, `(state, event) → (guard,
target)`, and **an undefined pair raises**. That is the design's central reflex, stated as a hard
rule: *an underspecified requirement is a defect to report, never a blank to fill.* An if-chain's
default branch is precisely the silent-ignore the spec forbids, which is why it is a table.

**Persistence is SQLite + Litestream.** Every state transition is **one transaction** — event
append plus projection update, never two. Delivery is at-least-once, handlers are idempotent, and
acks are **fenced on `received`**. Repair is capped at **3** attempts, enforced.

**Escalation to a cloud model is a rare, budget-capped tier**, reached only through a ledger path
with a pre-call cost bound and an explicit `max_tokens`. It is the only component that spends
money and the only one that leaves the box.

**The governing metric is escalation rate, not tokens/sec** — verification is deterministic and
free, so what matters is how often local generation fails badly enough to need the paid tier. Note
the honest gap: **escalation rate is not currently measured anywhere in the present phase.**

## 3. The deterministic oracle and its sandbox

This is the heart of the system and the thing most worth reviewing.

**The verification oracle is non-AI and read-only.** Tests, manifest, toolchain and candidate
source are read-only binds; only `/work/out` and `/tmp` are writable. The sandbox is `bwrap
--unshare-all` and **has no network by construction** — a fetch failure inside it is not a problem
to work around, *it is the signal*.

**The result envelope is the classification primitive.** The in-sandbox runner writes
`/work/out/result.json` **last**; an absent or invalid envelope is classified `SUBSTRATE`
regardless of exit code, because bwrap proxies child exits and raw integers are ambiguous.
Substrate incidents (126/127/137/139, bwrap errors, pack-tool network attempts) are **never** fed
to the repair loop and never blamed on generated code. Two signatures are deliberately
*discriminated* rather than blanket-classified: ENOSPC is substrate only when the job's own
size-bounded `/work/out` is not itself exhausted, and a network attempt by *candidate* code during
the execution phase is a **security finding**, not substrate.

**Verification packs are generated from `pins.lock` by a pinned generator and content-hashed for
identity.** Hand-editing a shipping pack is a defect: the TOML is a derived artifact, and a version
bump edits the lock and regenerates. Two packs exist today: `py.toml` and `security.toml`.

**The invariant, stated honestly** — this is the single most important line in this document:

> **`COMPLETED ⟹ the oracle passed` holds against escape and persistence (Faces A, C) but NOT
> against an adversarial candidate forging its own in-process verdict (Face B).**

Face B is **detected, not prevented**, and is contained by the network-less, capability-dropped,
disposable sandbox to **one tool falsely stamped `COMPLETED`** — never escape, never persistence.
The compensating control is in force: **a `COMPLETED` artifact is provisionally verified and must
be re-verified out-of-band before it is trusted or shipped.** Full detail, including why a uid
boundary is both unavailable and insufficient, is in `SECURITY-HISTORY.md` §4.

## 4. The autonomous runner and its containment

`bin/wrought-runner` executes queued work unattended. **It is started manually by the operator once
a day — there is no daemon and no timer, and the manual start *is* the human gate.** It walks a
queue and starts only rows marked `APPROVED`, a status that means a human agreed this may run.

Containment is four mechanisms that must be read together, and several of them exist because the
obvious reading was measured wrong:

- **Private ephemeral `$HOME` *and* private `$XDG_RUNTIME_DIR`, per child.** Both are required:
  peer *listing* is keyed on `$HOME`, the addressable *socket* on the runtime dir. Closing one
  leaves the other open — *not listed* is not *not addressable*.
- **`systemd-run --user --scope` with `MemoryMax` and `MemorySwapMax=0`.** The swap cap is not
  belt-and-braces: **`MemoryMax` alone does not cap memory on this box** — the overrun is paid out
  of swap and the process exits 0. Only with swap capped is it an OOM kill.
- **A reaper** that snapshots processes, domains and listening sockets before and after each gate;
  any new survivor is enumerated, terminated, and the batch **halts on a latching fault**. It
  matches on **executable identity** (`/proc/<pid>/exe`), never on command line — because
  `pgrep -f` matches the checking process's own argv, a bug that recurred three times in two days
  and once killed the shell doing the killing.
- **A deny-only PreToolUse hook** that can only ever subtract. It matches against the serialised
  tool input, so it matches file *content*, not just paths.

**Honest limits.** The runner has taken three unattended batches, **all doc-only**. Nothing
establishes that a *manufacturing* batch runs unattended. The reaper's `virsh destroy` branch has
never executed. And the fence list above has a hole worth stating plainly: the box has
**passwordless root** and children inherit it, so the permission allowlist and the systemd scope
are the *only* fences between a gate child and root — with the allowlist itself measured
non-binding for interpreter grants (`Bash(python3:*)` escapes the workspace boundary with zero
denials, because the path lives inside `-c` program text the permission layer never inspects).

## 5. The agent surface

**Goose v1.46.0**, pinned, driving the local model inside a disposable guest, with the host
inference endpoint reached through an **authenticating proxy over an ssh reverse tunnel** — the
guest keeps `restrict=on` and gains only a loopback listener, and the carrier is authenticated,
which is tighter than an IP-level forward.

**What is proven, in the narrowest true form:** the surface **reaches the model and acts on the
filesystem**. The work product that established it is a **five-byte file containing `FORGE`**. It
is **not proven to build software.** That distinction is preserved deliberately — the gate's own
audit is what caught its headline claiming more than the artifact carried.

An earlier transport, `guestfwd`, was replaced after measurement: it is **one always-on
multiplexed byte stream**, not a per-connection forwarder — 16 guest connections yielded **0**
accepted, against 8 concurrent host connections yielding **8**.

## 6. The git-courier gate protocol, and context as an engineering discipline

This is the part with the least precedent elsewhere, and the part most relevant to the question of
whether the approach scales.

The system is built by AI sessions that **do not share memory**. Work is decomposed into **gates**.
Each gate is a self-contained prompt, executed in a fresh context, producing a **bundle** of raw
evidence with a `SHA256SUMS` manifest, returned through a **public git repo (the courier)** that
carries text only — no secrets, no images, no zips. An off-box advisor reviews the bundle and
returns an adjudication, which the *next* prompt carries in, because the advisor cannot push.

The protocol's real subject is **context**, and its rules are all consequences of that:

- **A measured value carries the exact command that produced it, or it is not evidence.** Twice, a
  number whose command was never committed failed to reproduce.
- **Corrections are made by addition, never by editing the record.** The superseded text stays.
- **The two live state files carry a size budget — and the discovered problem is a *rate*, not a
  size.** Every gate must update them, so they have a per-gate growth rate of roughly +7–9 KB, and
  a one-time cut is fully regrown in about seven gates. Narrative was therefore moved to an
  append-only journal that nothing reads by default, leaving only the live position in front of the
  next session.
- **A gate proves work happened by inspecting the artifact, never by reading an exit code.** The
  measured instance: `goose` exits 0 on total failure, having written nothing at all.
- **Prompts travel as files with a block count**, because a paste eats indentation. *This very gate
  is the second instance of that failing:* its two appendices — 8,063 bytes of authoritative
  Python — arrived empty, and the file the operator later supplied carried 57 indented blocks
  against the paste's 0.

**Honest assessment of the protocol's cost:** a clean doc-only unattended gate consumed **99.8 % of
its $8 budget cap**. The cheapest possible gate shape has effectively exhausted the cap. Whatever
else is true, the per-gate overhead of this discipline is not small, and it is currently unmeasured
against a *manufacturing* gate.

## 7. Model tiers

- **Primary: Qwen3.6-27B, UD-Q4_K_XL**, served resident on the dGPU at **65,536 context**,
  `--parallel 1` (one request at a time), reasoning on with a 24,000-token reasoning budget. MTP is
  promotion-gated. SHA-256 verified against `pins.lock` on every pull; a mismatch is treated as
  compromise, and GGUF loading is treated as untrusted-code execution.
- **Fallback: Devstral-Small-2-24B, Q4_K_M.**
- **Escalation: a cloud tier**, budget-capped, ledgered, used rarely and only through the
  escalate-once path.

**A measured caveat that matters for anything built on the local model:** the correctness window
established for it is **96 tokens** — every comparison diff is blind past token 96, so
later-onset corruption is invisible to all of them. Long-context correctness is **untested**.

---

## 8. What actually exists, in one table

| Thing | Status |
|---|---|
| FSM, event store, repair loop, escalation ledger | **Built**, exercised |
| Deterministic oracle + bwrap sandbox + packs | **Built**; invariant holds for Faces A/C, not B |
| Batch runner + containment + reaper | **Built**; 3 unattended batches, all **doc-only** |
| Agent surface (Goose in a guest) | **Reaches the model and writes a file.** Not proven to build software |
| Git-courier gate protocol | **Built and in daily use**; cost per gate is high |
| Manufactured products | **One** (`products/queue-health`) |
| The ten fixture tasks | **Do not exist.** Named in planning, never built |
| NPU offload | **Nothing.** Driver bound, no userspace stack |
| Media generation / vision / computer-use | **Nothing.** No component of any kind |
| Escalation rate (the governing metric) | **Not measured in this phase** |

**The last four rows are the honest distance between this system and the 1.0 vision it is being
reviewed against.**

# Gap analysis: Wrought Foundry vs the 1.0 operator vision

**Distance, stated first.** The box is a serious *software-manufacturing foundry*: FSM, oracle, disposable guests, pins, courier, containment. Against the 1.0 *product* — a free-range local agent that does media, computer-use, identity-adjacent video, and games — **almost none of the surface exists**. Table §8 already says the last four rows *are* the distance. Treat that as load-bearing.

A fair scorecard:

| Layer | vs foundry-as-tool-factory | vs 1.0 vision |
|---|---|---|
| Substrate, pins, serving | Strong | Strong (and the GPU is already spoken for) |
| Deterministic verify + containment | Strong, with Face B open | Necessary, not sufficient |
| Agent that “just goes” | **5-byte write; not proven to build software** | Missing |
| Media / vision / computer-use / NPU | Nothing | Nothing |
| Provenance / likeness / consent | Culture of pins and hashes | No product controls |
| Unattended real work | 3 doc-only batches | Unproven |

Do **not** grow the foundry until it *is* ComfyUI. Keep manufacturing verified tools; put a planner and a compliance kernel in front of them. The failure mode is another quarter of gates that never touch a tiger frame.

---

## (A) Capability-by-capability

### 1. Agentic multi-step planner/executor that maxes GPU + RAM

**Exists.** Ten-state FSM, SQLite+Litestream, repair cap 3, escalate-once ledger, `wrought-runner` with memory/swap fences, Goose in a disposable guest via authenticated ssh reverse tunnel. Workload shape is *one* resident Qwen3.6-27B at **65,536 ctx, `--parallel 1`, ~18.27 GiB VRAM**, 87 GiB RAM, swap disabled for children.

**Missing.** There is no free-range planner. The FSM is `task.md → code → oracle`, not “plain language → tool graph → artifacts.” Goose is proven to **reach the model and write `FORGE`**, not to build software. GATE-41 fixtures **do not exist**. Escalation rate (the governing metric) **is not measured**. Long-context correctness is **untested**; the only established window is **96 tokens**. Unattended **manufacturing** has never run. NPU is a bound driver and an empty userspace.

**Hardest gap.** Not the FSM. **The local model’s unmeasured long-horizon competence, plus a GPU that is already full.** A planner that cannot keep a 20-step media graph coherent past token 96, on a card with ~5.7 GiB headroom, will not “just go.” Everything else is scaffolding around that.

---

### 2. Media generation and editing (image/video, seg, composite, 3D/avatar) on less-filtered local models

**Exists.** Zero components. Operator already ruled vision a **separate, lower-assurance lane**.

**Missing.** Every stage: img gen, video gen, SAM-class segmentation, tracking, ffmpeg/Blender compositing, 3D reconstruction, avatar retarget, a **VRAM scheduler** that can evict the 27B to run a diffusion stack, and a **second lane** so “less-filtered” never means “unlogged / unlicensed.”

**Hardest gap.** **24 GB is one resident LLM, not a studio.** Shipping video models (Wan, Hunyuan, CogVideoX, LTX) and the LLM **cannot sit together**. Without an explicit *swap/queue* (who owns the XTX, for how long, what is checkpointed to the 87 GiB RAM), every media task is a denial-of-service on the planner. Second: “less-filtered” **conflicts with compliance as a hard requirement.** That is a product decision, not a weights decision.

**1.0-honest DoD for the tiger task:** Wikimedia stills → licensed registry → local img2img/img2vid of a few seconds → ffmpeg composite → C2PA on the output. **Not** a cinematic hunt. If the operator needs SOTA video, this box is the wrong substrate.

---

### 3. Asset acquisition with provenance

**Exists.** The *habit*: SHA-256 pins, “mismatch = compromise,” ST-2 integrity-vs-authenticity, generated packs, courier text-only. That is the right religion.

**Missing.** Any media asset store: source URL, retrieval time, license SPDX/CC, author, hash, C2PA, robots/ToS, deny-by-default ingest. Courier **forbids images and zips**, so it cannot be the asset plane.

**Hardest gap.** **The open web is not a public-domain API.** “Sourced from the web” without an allowlist will ingest unlicensed junk and launder it through generation. Wikimedia Commons / Internet Archive / explicit operator drops are the only 1.0-honest sources. General crawl is a lawsuit factory.

---

### 4. VM-hosted computer-use with vision

**Exists.** The right *substrate*: plain QEMU, ~15 s boot and revert, base image **immutable by hash**, Goose in guest, ssh `-R` pinhole (attended only), reaper on exe identity. Libvirt domains deliberately not used for gate work (7-day leftover guest with a key in proxy memory).

**Missing.** Screenshot loop, input injection (evdev/xdotool), a vision/OCR model, a policy on what the agent may click, persistence of the `-R` tunnel **under the runner** (KNOWN-OPEN #4, untested — the shape that already leaked a guest for a week). GPU passthrough **untested**. Guest egress control **untested** (libvirt guest already hit Ubuntu connectivity-check).

**Hardest gap.** **Vision VRAM + an untested in-scope tunnel + passwordless root on the host.** Computer-use is the blast-radius expander. The guest is disposable; the host user is `(ALL) NOPASSWD: ALL` and children inherit it. Until that is not true, “VM-hosted” is a story the host sudo list contradicts.

---

### 5. Tiered routing: local GPU / NPU / cloud

**Exists.** Primary Qwen 27B on XTX/Vulkan, Devstral fallback, cloud escalate-once with ledger, weekly/monthly caps. Device selected **by name**, `llvmpipe` asserted out.

**Missing.** **NPU: driver bound, `/dev/accel/accel0` live, no userspace.** iGPU unused by design. No router that says “OCR/NPU, plan/GPU, refuse/cloud.” Pre-call cost bound is **unsound for reasoning models** (measured 8× overrun). `--parallel 1` — no concurrent local tiers.

**Hardest gap.** **NPU is a kernel node, not a tier.** Any roadmap line that “routes to the NPU” is fiction until ONNX Runtime / Ryzen AI / a llama.cpp backend actually submits work and a pin records the stack. Until then, routing is GPU vs paid cloud, and the GPU is monopolized.

---

### 6. Context as a first-class discipline (system built by AI)

**Exists.** This is the project’s actual invention: gates, fresh context, evidence+SHA256SUMS, corrections-by-addition, measured-command-or-it-isn’t-evidence, live-state size budget, journal nobody reads by default, prompts-as-files with block counts. It caught its own overclaims (FORGE vs “manufactures”).

**Missing.** A **runtime** memory for a days-long media/game task: artifact store (binary), scratch vs live, summarization that is *measured* not hoped, a plane that can hold frames. Courier is **text-only**. Live files grow **+7–9 KB/gate** and a cut regrows in ~7 gates. Clean doc-only gate: **$7.9875 of $8 (99.8%)**.

**Hardest gap.** **The build protocol cannot be the 1.0 runtime.** It is too expensive, forbids the artifacts 1.0 produces, and is tuned for *adjudicated software gates*, not 4-hour video jobs. Keep it for *building* 1.0. Invent a cheaper runtime context (local artifact DB + bounded working set + operator-approved checkpoints).

---

## (B) Critical path — independently useful milestones

Each milestone should be **shippable and usable** before the next. Sizes are calendar on *this* box, one operator + AI gates, not a headcount fantasy.

| # | Milestone | Why it is useful alone | Size |
|---|---|---|---|
| **M0** | **Scope freeze.** 1.0 = (a) PD stills→short licensed video, (b) computer-use in a *game/app VM*, (c) planner over manufactured tools. **Cut** identity clustering of real people and photoreal avatar replacement of real people (1.1 + counsel). Write the three task DoDs in numbers (seconds of video, sources allowlisted, human gates). | Stops the foundry from being aimed at illegal/unshippable work. | 3–5 days |
| **M1** | **Workload scheduler on the XTX.** Exclusive lease: LLM / diffusion / vision. Measured swap (already **5.30 s** LLM primary↔fallback), RAM offload, queue, “who holds `0x744c`.” Refuse concurrent claims. | Without this, no media or vision work is possible. Operator can already run one heavy job at a time without wedging inference. | 2–3 weeks |
| **M2** | **Prove manufacturing.** One unattended **non-doc** gate that produces a real tool; measure **escalation rate**; re-verify COMPLETED out-of-band (Face B compensating control). Ferry decision on Face B vs `py.cov.threshold` recorded, not necessarily closed. | If the factory cannot make tools unattended, it cannot make the media stack. | 2–3 weeks |
| **M3** | **Long-context honesty.** Correctness at 2k / 8k / 32k / 64k on pinned prompts (math+code+plan replay). Pin `--ubatch-size 512` in the harness (KNOWN-OPEN #2). If 32k is garbage, **drop advertised ctx** or force cloud on long plans. | Prevents designing 1.0 around a 65k window you have not measured. | 1–2 weeks |
| **M4** | **Provenance store + allowlisted fetch.** Product `assets`: hash, URL, timestamp, license, SHA, optional C2PA, deny-by-default. **Wikimedia Commons + Internet Archive + operator import only.** No general web scrape. Courier stays text; binaries live under `/var/lib/wrought/assets` with the same pin religion. | Operator can already collect a legal still set for the tiger task. | 2–3 weeks |
| **M5** | **Image lane.** SDXL (or equivalently licensed local) via ComfyUI or a thin pinned pipeline, **inputs only from M4**, C2PA/Content Credentials on outputs, human `APPROVED` before first generate. Swap LLM off (M1). | First visible 1.0 demo: licensed stills in, labeled stills out. | 2–3 weeks |
| **M6** | **Short video lane.** ffmpeg + Blender composite of M4/M5 stills, then **one** local img2vid (LTX-Video or similar that *fits after LLM eviction*). DoD: **N seconds**, not “a hunt film.” | Ships the tiger task at honest quality. | 3–4 weeks |
| **M7** | **Computer-use VM v0 (blind).** Existing guest + screenshot to disk + `ydotool`/`evdev` + allowlisted apps. **No vision model yet.** Operator-written recipes (open game, click New). Measure `ssh -R` under runner + reaper (KNOWN-OPEN #4) **before** any unattended use. Drop inherited NOPASSWD for the guest-control user. | Operator can already script a turn-based game with a human in the loop. | 3–4 weeks |
| **M8** | **Vision cheap.** OCR/UI-parse on **NPU or iGPU**, not the XTX. If NPU userspace fails in a time-box, **ONNX on CPU/iGPU** and say so. Screenshot → structured UI, not “a VLM that sees everything.” | Unblocks M7 from becoming a second 24 GB tenant. | 3–5 weeks, **kill if NPU still empty at 2 weeks** and fall back |
| **M9** | **Planner v0 over tools.** Not a new FSM. Goose (or successor) with a **pinned tool catalog**: asset.fetch, image.gen, video.compose, vm.click, escalate. Bounded steps, artifact log, human approve at network / generate / click-outside-allowlist. | First time “plain language → tiger clip” is a product, not a gate. | 2–3 weeks |
| **M10** | **Turn-based game loop.** M7+M8+M9 on one slow game (chess, a 4X with long turns). Optional cloud only through existing ledger. | Fourth target task, without building a game engine. | 2–3 weeks |
| **1.1** | Face/avatar **only** with enrolled identities, written consent artifacts, separate legal lane. Segmentation (SAM2) can start earlier **on non-person objects** (tiger vs bear) as a 1.0 extra, not as “replace each person.” | — | after counsel |

**Do not** put Face B process-split, Litestream R2, MTP, or libvirt point-release philosophy on this path. They do not move the tiger.

Rough total to a *honest* 1.0: **~4–6 months** if M0 is obeyed and M1/M3 are not failed. If M3 shows the 27B cannot plan, add a **planner-on-cloud / executor-local** split or a stronger local model — that is a fork, not a polish.

---

## (C) Cut / defer vs gold-plate

**Cut from 1.0**

- Organize a library **by the person depicted** (biometric grouping).
- Replace **each real person** with a 3D avatar.
- General web scrape for “PD” images.
- Cinematic video; unattended cyber; “slightly adversarial” beyond a **logged, allowlisted, human-approved VM**.
- NPU as a promised tier before a userspace hello-world.
- GATE-41 ten Python fixtures as a prerequisite to media 1.0 (they measure the *code* oracle, not the product).
- Air-gap *and* “sourced from the web” in the same 1.0 sentence. Air-gap = pre-staged M4 assets.

**Defer (real, later)**

- Face B close that kills `py.cov.threshold` (compensating control is enough for *tools*; media outputs need a different oracle anyway).
- Litestream/R2, snapshots at 500k events, MTP, GPU passthrough, libvirt as guest supervisor.
- Photoreal human avatars, InsightFace-style galleries.

**Do not gold-plate**

- Another four-lineage panel before a single frame exists.
- Perfect Face B.
- Custom diffusion trainer.
- A new agent runtime when Goose already reaches the model.
- Courier support for MP4 (wrong plane).

**Do gold-plate (this is the actual moat)**

- pins.lock + integrity-vs-authenticity for **weights, Comfy graphs, SAM checkpoints, ffmpeg builds**.
- Deny-by-default assets.
- Human `APPROVED` on generate / click / spend.
- Device-by-name, no silent llvmpipe.
- Out-of-band re-verify of COMPLETED **tools**.
- Live-state discipline while *building* 1.0.

---

## (D) Does the git-courier protocol scale to this ambition?

**For building 1.0: yes, with cost control. For being 1.0: no.**

It solves the real problem of AI-built systems: no shared memory, lying exit codes (`goose` exits 0 on total failure), unmeasured numbers, prompt paste eating indentation. Keep gates, evidence, addition-not-edit, block counts.

It does **not** scale as the operator-facing loop because:

1. **99.8% of $8 on the cheapest doc-only shape.** Media planning will blow the cap or starve the work. Recalibrate **now** (dispatcher already said this; KNOWN-OPEN #10 is stale in the other direction).
2. **Text only — no images, no zips.** Tiger frames cannot ride the courier. Forcing them there will smuggle binaries or collapse evidence quality.
3. **+7–9 KB/gate live-state rate.** A media campaign is dozens of steps; the live files will become the product.
4. **Advisor cannot push.** Fine for adjudication; fatal for a tight generate/look/fix loop on video.

**What most improves it**

- **Two planes:** courier = prompts, reports, hashes, licenses, *pointers*. Artifact plane = local content-addressed store (already how models live).
- **Budget by plane:** build gates stay capped; runtime agent uses local tokens (free) and only ledgered cloud.
- **Stop narrating in the live file.** PHASE-J-STATE is the proof the rate problem is real; do not replicate it for media jobs.
- **Mechanical verdicts for runtime** (hash exists, license row exists, C2PA valid, VM reaped) — not advisor-in-the-loop per frame.
- **Enforce prompts-as-files** (8th miss in 9). A protocol the operator bypasses is not a protocol.
- **One manufacturing unattended batch** before claiming the protocol scales off docs.

---

## (E) Compliance and safety — 1.0 controls (hard)

Compliance is not a pack you generate after the demo. If M5 exists without M4, you have already lost.

### Provenance and licensing (every media capability)

**Must have**

- Ingest **deny-by-default**. Allowed sources: Wikimedia Commons, Internet Archive, operator import with a typed license. Parse `license` / `UsageTerms` / SPDX; store **verbatim license + URL + retrieval time + content hash**.
- **No** “looks PD to the model.” The model does not testify.
- Weights and LoRAs pinned with **license of the weight** (Apache/MIT vs OpenRAIL vs Flux non-commercial). Output policy is the **meet** of weight license and asset license.
- Outputs: **C2PA / Content Credentials** (c2pa-rs) stating generated, model id, asset hashes consumed. Keep the unsigned-hash fallback when C2PA tooling is absent — still a pin.
- Training/fine-tune of anything on operator media: **off** in 1.0 (one-way door).

**Current design:** pins religion is excellent and **does not touch media**. Courier cannot hold the evidence. Security pack (gitleaks/syft/osv) is source-code shaped.

### Likeness / consent (person-depicted, avatars, recognition)

**1.0 rule:** **no biometric identification, no face gallery, no replacement of real people.** Segmentation may run on animals/objects. If a face detector fires on a person in a training video, **halt and ask**.

**1.1 (if ever)**

- Enrolled identities only; consent artifact: who, scope (organize / avatar / export), expiry, revocation.
- Separate data store, encrypted, not in courier.
- No “organize the library by person” over random home videos without per-person consent — that is the BIPA/GDPR-class feature.
- Photoreal avatar of a real person = **disclosure + consent + no implicit deepfake of third parties**.

**Current design:** operator ruling “vision is lower-assurance” is correct and **incompatible with shipping those two tasks**. They should not be 1.0 acceptance tests.

### Logging and HITL (cyber-capable agent)

**Must have**

- Every tool call in the existing event-store shape: who (local/NPU/cloud), what, hash of args, outcome. Cloud already ledgered; **generate and click must join that ledger**.
- Human gates: (1) batch/`APPROVED` as today, (2) first network fetch, (3) first image/video generate, (4) any computer-use outside allowlisted window titles/processes, (5) any spend.
- Computer-use **only** in disposable QEMU, egress locked except pinned endpoints, **no host sudo**. Reaper must be proven on the tunnel and on `virsh destroy` if you ever create domains.
- Explicit **legal boundary file** the agent is given: no unauthorized access, no exploit development, no attacking systems you do not own. Matches the system instruction you already want. Log the hash of that file into every session.
- Quiet network in the **oracle** is still OPEN (panel z-ai F3). For computer-use, detection cannot be a stderr substring. Use netns + allowlist + audit (auditd/nft log).

**Current design inadequate**

- Passwordless root inherited by children — **the** containment hole; allowlist is not a boundary (`Bash(python3:*)`).
- Gate child **not network-isolated** (scope cannot take `PrivateNetwork`).
- Face B: COMPLETED is provisional — fine for tools; **do not** let a forged COMPLETED ship a media pipeline that then runs unconstrained.
- Cost bound 8× undershoot on reasoning — the only path that spends money.
- Two remaining `pgrep -f`.
- “Slightly adversarial” without a written, hashed policy is how you get a headline.

**Separate lanes (already implied, make them code)**

| Lane | Assurance | Allowed |
|---|---|---|
| Oracle / manufacturing | Highest | Code, tests, pins |
| Media generate | High, licensed | Animals, landscapes, PD stills |
| Vision / computer-use | Lower, as ruled | VM only, allowlisted apps |
| Identity / likeness | Off in 1.0 | — |

---

## (F) What could sink this — measure first

**Kill shots**

1. **VRAM monopoly.** Planner and video cannot coexist; swap is too slow or unstable (dGPU `runpm` already a known wedge; `amdgpu.runpm=0` is a mitigation).
2. **96-token correctness.** Multi-step media plans rot; operator sees busywork and junk frames.
3. **Courier-as-runtime + $8 cap.** Process eats the product.
4. **Shipping person-ID / avatar** and eating a likeness claim.
5. **Foundry forever.** More invariant prose, no tiger.
6. **Host root + computer-use.** One escaped click is a host compromise. The 7-day guest is the preview.
7. **“Less-filtered” vs compliance.** If the local video model will emit illegal sexual/CSAM-adjacent or celebrity porn, you need an **output filter that is not the generative model**, or you do not ship video. This is non-negotiable and independent of “open” aesthetics.
8. **NPU as vapor** in the 1.0 story.

**Prototype / measure this week, in order**

1. **Lease the XTX:** unload llama, load SDXL or LTX, generate one 512² / one 2s clip, reload llama, compare token-stream canary to GATE-16. Wall clock, VRAM, thermal, `runpm`.
2. **Long-context battery** at 2k/8k/32k (even before a full gate).
3. **Wikimedia fetch + license parse + hash** for 20 tiger/bear stills — no generation. Proves M4.
4. **NPU hello-world time-box (2 days):** install Ryzen AI / ORT, classify one image on `/dev/accel/accel0`. If fail, **write NON-CLAIM** and use iGPU/CPU.
5. **`ssh -R` under `wrought-runner`** for 15 minutes, kill child, confirm reaper — **attended**, before any vision.
6. **Escalation-rate on one multi-step dry plan** (text only, no media) so P1 exists as a number.
7. **Legal memo (operator, not a gate):** 1.0 will not do person-ID. Get that in PHASE-J-STATE as a ruling.

If (1) or (2) fails, **stop designing pipelines** and change the 1.0 DoD (stills-only, or cloud video, or smaller local model).

---

## (G) Public-domain / open components (pin like everything else)

**Planner / executor**

- Keep **Goose** (already pinned v1.46.0, guest-only) + manufactured tools. Do not add LangGraph unless Goose cannot tool-call reliably.
- FSM stays the **factory**; do not fork it into a media DAG. A small **job graph** (existing SQLite) is enough.
- Open-Interpreter / UI-TARS-style stacks: only as *ideas*; they are not pinned, not sandboxed, not your threat model.

**Media**

- **ComfyUI** (GPL) as the graph runtime, graphs hashed in pins; or a thinner **diffusers** (Apache) if Comfy’s surface is too large for the oracle.
- **SDXL 1.0** base (OpenRAIL — *not* PD; treat license as a pin). Prefer **Apache/MIT** stacks where possible: **LTX-Video**, **TripoSR** (MIT), **SAM2** (Apache 2.0) for *non-person* masks.
- **ffmpeg**, **ImageMagick**, **Blender** (GPL) for composite/3D. Blender is the 3D/avatar *engine* when you get to 1.1.
- Avoid: unlicensed Civitai LoRAs, InsightFace for 1.0, closed video APIs as the happy path.

**Assets / provenance**

- Wikimedia Commons API, Internet Archive.
- **c2pa-rs** / `c2patool` for output credentials.
- **Exiv2** / `python-xmp-toolkit` for IPTC.
- SPDX license list as data, not a vibe.

**Computer-use**

- Existing **QEMU/KVM** guests (already measured).
- **Sway/wlroots or Xvfb** in guest + **grim** / `ffmpeg x11grab`.
- **ydotool** / **dotool** / **xdotool** for input (pick one, pin it).
- **PaddleOCR** or **Tesseract** on NPU/CPU for text UI; **OmniParser**-class only if pinned and sandboxed.
- **Stockfish** (or the game’s own engine) for the chess-shaped case — LLM should not play chess by pixels if a PD engine exists. That’s the “framework lifts the local model” idea.

**Routing / NPU**

- **ONNX Runtime** + AMD **Ryzen AI / Vitis AI EP** (the first thing to pin or to NON-CLAIM).
- llama.cpp **stays Vulkan/XTX** for the planner.
- iGPU **RADV** as plan B for vision if XDNA userspace is empty.
- Cloud: keep OpenRouter ledger; do not add a second spend path.

**Context runtime**

- Content-addressed **sqlite + blobs** under `/var/lib/wrought/` (you already live here).
- Append-only job journal (you already invented this).
- **Not** Mem0/Letta as a new brain until the artifact plane exists.

**Compliance filters**

- Output: **NSFW classifiers** you pin (e.g. Falconsai / smaller ONNX on NPU) as a **gate on write**, not a training sermon.
- Robots/ToS: don’t scrape; allowlist.

---

## Architectural recommendation (one paragraph)

Wrought is a **verified tool factory on a single 24 GB GPU**, not a media OS. 1.0 is a **planner with a compliance kernel** that calls manufactured tools: `asset` (Wikimedia/IA only), `image`, `video-short`, `vm-use`, `escalate`. The XTX is a **mutex**. The NPU is **unproven** and must be measured or struck. The courier stays the **build** nervous system. Identity-based video tasks are **not 1.0**. Face B stays open with mandatory out-of-band re-verify for **tools**; media is checked by hashes, licenses, and C2PA, not pytest. The first honest demo is a **licensed tiger/bear animatic** produced under M1+M4+M5+M6 with a human `APPROVED`, not a general agent that “just goes” across all four example tasks.

If you only do three things next: **(1)** M0 scope freeze in PHASE-J-STATE, **(2)** XTX lease prototype, **(3)** Wikimedia provenance store. Everything else is downstream of whether those three are true.
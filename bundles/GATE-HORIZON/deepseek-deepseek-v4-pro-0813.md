# External review (TOP-UP) — deepseek / `deepseek/deepseek-v4-pro-0813`

- Provider: `DigitalOcean` · generation `gen-1788216003-gwxtLswTQIurjDLa6JAF`
- ZDR: pre-checked in `/models?zdr=true`; enforced via `provider.zdr=true` + `provider.data_collection="deny"`
- finish_reason: `stop` · cost $0.1174 · 68223 in / 6902 out

---

# Wrought Foundry vs. the 1.0 Vision — An Honest Assessment

## A. Vision capability by vision capability

### 1. Agentic multi-step task planner/executor maximizing single-node GPU and system RAM

**Exists:** A hand-rolled ten-state FSM with SQLite+Litestream persistence, repair loop capped at 3 attempts, escalation ledger with dual budget caps, and a batch runner with measured containment (private HOME/runtime dir, systemd scope with `MemoryMax` + `MemorySwapMax=0`, residue reaper). The runner has taken three unattended batches, all doc-only.

**Missing:** Any planner that decomposes a free-range plain-language task into gates. There is no task decomposition layer. The FSM executes gates; nothing decides what gates a task needs. The "maximizes GPU and RAM" requirement is unmeasured — the runner is a scheduler with memory caps, not an optimizer. The governing metric (escalation rate) is not measured in the current phase.

**Hardest gap:** Task decomposition and self-repair at the level of "free-range agentic task in plain language" is not merely absent — the entire gate protocol assumes a prompt author already decomposed the work. The system manufactures software from pre-decomposed gates, not from goals. Closing this requires a planner that can reason about the box's actual measured resource envelope (24 GB VRAM, 87 GiB RAM, 65,536 ctx, OCuLink ×4) and subdivide work accordingly — and that planner's output quality must itself be verifiable by the deterministic oracle, or you've just moved the trust problem up one layer.

### 2. Media generation and editing pipelines (image/video generation, segmentation, compositing, 3D/avatar)

**Exists:** Nothing. No component of any kind. The packet says so explicitly.

**Missing:** Everything. No image model, no video model, no segmentation, no compositing, no 3D pipeline. The dGPU (RX 7900 XTX) has 24 GB VRAM — enough for smaller local models but not for video generation at useful resolution without significant work (e.g., diffusion models on ROCm, facing the same driver-availability issues the llama.cpp stack avoided by using Vulkan).

**Hardest gap:** Not "which model" but the entire serving and verification path. The current inference rail is one llama.cpp server, one request at a time (`--parallel 1`), on the only local model. Media generation needs multi-model concurrency (T2I, segmentation, possibly a second LLM for prompt understanding), VRAM orchestration across models with different memory footprints, and a deterministic-oracle story for outputs that are images, not exit codes. The oracle is built around `result.json` envelopes and pytest; extending it to judge "is this a tiger hunting a polar bear" safely needs either a multimodal judge (which is itself a model, breaking the "non-AI, deterministic, free" property of the oracle) or human review (which changes the cost and latency model entirely). The Face B lesson applies with force here: a media oracle that is itself a model is a reporter that shares the defendant's epistemic status.

### 3. Asset acquisition with provenance (public-domain/licensed-source verification)

**Exists:** Nothing in the packet that can fetch or verify media assets. There is a hash-pinning discipline for software artifacts (GGUFs, COTS binaries, guest image) and a `pins.lock` with provenance fields, but no component that can go to the web, find "tiger hunting a polar bear" images, and establish they are public domain or licensed.

**Missing:** Web fetching in a sandbox (the current sandbox has no network "by construction"), license metadata extraction, provenance records that survive to the output artifact, and — hardest — the legal judgment of whether an image is actually public domain or open-licensed. This is not a deterministic oracle problem; it's a search + metadata + human-ratifiable-chain problem.

**Hardest gap:** License verification is a hard legal problem, not a hard engineering problem. A system can collect `CC0` markers and `license` metadata, but it cannot verify the uploader had the rights. The pipeline needs a human-approvable provenance record for every asset — and that means the human-in-the-loop requirement, currently a one-shot `APPROVED` queue status at dispatch time, must extend to per-asset approval, which existing rails don't model.

### 4. VM-hosted computer-use loop with vision (screenshot + vision model)

**Exists:** A VM substrate. QEMU/KVM with disposable guests, measured immutable base image, boot-to-ssh ≈ 15 s, discard-and-revert ≈ 15 s. The guest can reach the host model through an authenticated SSH tunnel (8/8 concurrent, 12/12 chat calls, measured attended). A Goose agent surface in the guest that reaches the model and writes a 5-byte file.

**Missing:** The vision half entirely. No screenshot mechanism, no vision model, no GUI automation, nothing that "drives software like a person." The current guest is headless; the proven agent action is filesystem-level, not GUI-level.

**Hardest gap:** The entire screenshot→vision→action→verify loop is unbuilt, and it is where the cyber-capable adversarial agent's legal boundary problem is sharpest. A VM that can drive software with a screenshot and a vision model can, by construction, take actions with legal consequences (logging into something, clicking something, posting something). The current design's safety story relies on a human approving the queue once and a deny-only hook matching serialized tool input. Neither generalizes to screenshot-driven actions. This subsystem, more than any other, needs a permission model per action, a log of every action with before/after screenshots, and bounded authority — none of which exist.

### 5. Tiered model routing across local GPU, NPU, and cloud

**Exists:** Two tiers: local GPU (llama.cpp/Vulkan, two models, swap measured at 5.30 s) and a rare, budget-capped cloud escalation. The NPU is present and entirely unused — "a driver node and a kernel driver, not a working runtime."

**Missing:** NPU tier entirely, and any routing logic more sophisticated than "primary, fallback, escalate." There is no router that decides per-request which tier to use, no measured cost/quality tradeoff, no NPU userspace stack (XDNA2/`amdxdna` driver bound, nothing on top).

**Hardest gap:** The NPU is not a quick add; it's a from-scratch runtime integration. XDNA2 on Linux in 2026 has no mature open userspace stack that this packet names, and writing a new mlir/onnx runtime for it is a multi-quarter project. But the deeper issue is that routing needs a decision function (escalation rate is supposed to be the governing metric, and is unmeasured), and no decision function is buildable until the local correctness window is measured at scale. The 96-token blind spot means any router deciding "local is fine for this" is making that call on evidence that silently stops at 96 tokens.

### 6. Context management as a first-class engineering discipline

**Exists:** The git-courier gate protocol is the real thing here, and it is the most novel and most developed part of the system. Each gate is a self-contained prompt in a fresh context, producing a bundle with SHA256SUMS, reviewed off-box, with corrections by addition. Live state files carry size budgets, narrative is archived, a measured rate problem (+7-9 KB/gate) was found and addressed.

**Missing:** At 1.0 ambition, the gate protocol's cost is measured as ~99.8 % of an $8 budget for a clean doc-only gate. The protocol handles *recording* context; it does not handle *summarizing, retrieving, or prioritizing* context. There is no mechanism that, for a task requiring hundreds of gates, maintains a working set of relevant prior evidence accessible to each gate without loading it all.

**Hardest gap:** The protocol already measured its own limit: the state file grows per gate and the budget is exhausted by the cheapest possible gate. No retrieval infrastructure, no hierarchy of context, no compression exists. At media-generation scale — where a single task might be dozens of gates — the courier either becomes a monolith no fresh context can load, or the protocol needs a retrieval layer that does not exist and whose quality would itself be unverified.

---

## B. Critical path to a viable 1.0

Each milestone is independently useful and shippable, in order.

1. **Close Face B (oracle verdict separation).** Move candidate tests out of the reporting process. This is an explicitly stated operator decision, not a fix gate. Size: one focused gate, but it kills `py.cov.threshold` and forces re-specification of every pack asserting on it. Estimated 2-4 weeks of AI-gate work. *Why first:* every subsequent media/vision/agentic subsystem needs a verifier it can trust. Building media on a forgeable oracle multiplies risk; this is the foundation.

2. **Measure escalation rate now, on the GATE-41 fixture set, with the current conditions.** The governing metric has never been measured. This is a measurement gate, not a feature. Size: days. *Why:* no routing, no planner, no budget calibration is possible without it.

3. **Build the GATE-41 fixtures (the ten named tasks).** They are named in planning and do not exist. This gives the deterministic oracle a real distribution to measure against, instead of synthetic fixtures. Size: one gate per fixture; operator supplies the task specs. *Why:* the "operator's target tasks" for 1.0 include free-range media; the existing pipeline needs a real fixture set for its own regression before adding new domains.

4. **Runner manufacturing-gate proof.** Run a real manufacturing gate unattended through `wrought-runner`. This is currently untested. Size: one supervised batch with a real (non-doc-only) gate. *Why:* it closes the "three doc-only batches" gap and exercises the reaper's substantive paths.

5. **Multimodal judge as a separate, low-assurance, non-oracle lane.** Wire a small vision-language model (e.g., Qwen2.5-VL-7B or Llama 3.2 11B Vision, both within 24 GB VRAM) behind the existing inference service or a second server. Use it only for tasks the deterministic oracle structurally cannot verify — media outputs, computer-use screenshots. Mark its verdicts PROVISIONAL, always requiring out-of-band re-verification, exactly like Face B artifacts. Size: one gate for model pin, one for integration. *Why:* 1.0's media tasks cannot be verified by pytest; a judge, even a flawed one, starts generating the data needed to calibrate the real oracle later.

6. **Asset provenance service.** A fetch-and-verify component that runs outside the sandbox, fetches candidate assets, records source URLs, license metadata, and hashes into the provenance record. Human approves before the asset enters the pipeline. Size: small, web-enabled, separate from the gate child (the gate child is not network-isolated; this one should be). *Why:* every media task needs it, and it's independently useful for the operator's non-media asset needs.

7. **Computer-use loop, prototype form.** VM guest + screenshot tool (grim or scrot) + vision model from milestone 5 + a bounded action set (click/type/read) logged to a human-reviewable record. Start with a single turn-based game. Size: several gates; this is the largest single milestone and should be split. *Why:* the 1.0 asks for turn-based game play; that's the natural first target for computer use because the turn boundaries give the agent a free thinking pause and the vision loop doesn't need real-time latency.

8. **Media generation pipeline.** Start with image generation, not video. e.g., SDXL-Turbo or a distilled model that fits 24 GB readily, served via a second llama.cpp/ComfyUI instance. Video from public-domain images (the tiger/polar bear task) is image → image composition, not text-to-video; that's a much simpler pipeline: segmentation model + compositing, no video diffusion. Size: one gate for pinning + one for integration. *Why:* the 1.0 target task says "generate an AI video of a tiger hunting a polar bear using public-domain images" — this is compositing from found images, not text-to-video. The operator likely overestimates the difficulty here if they think of full video diffusion.

9. **NPU tier — decide by measurement.** Before any NPU runtime work: measure what the iGPU/XDNA2 can actually do with available tooling. If no usable userspace stack exists (the packet implies none), either write the runtime (multi-quarter, probably not worth it for one box) or delete the NPU tier from the 1.0 vision and document why. Size: one measurement gate; decision after. *Why:* NPU routing is expensive and may add nothing the dGPU doesn't already cover.

Each milestone above is a gate or a small batch of gates in the current protocol — the operator can ship and use each one before the next.

---

## C. Cut or defer versus gold-plate

**Cut entirely:**

- **NPU tier.** Given the packet's evidence (no userspace stack installed), the NPU is a research project, not a 1.0 deliverable. Route everything to the dGPU and cloud. Revisit if a mature XDNA2 runtime appears.

- **Text-to-video generation at 1.0.** The 1.0 target tasks all rely on compositing from existing assets ("using public-domain images sourced from the web") or avatar replacement (segment, composite, 3D model). Text-to-video diffusion at usable quality on 24 GB VRAM is a research problem; it is not needed for the stated tasks and would balloon scope for no user-visible gain.

- **Full 3D avatar pipeline.** "Replace each person with a 3D-modeled avatar" needs segmentation + a 3D model render + compositing. The 3D model can be a prebuilt, rigid, animated model — not a "generate a custom 3D avatar for each person." The hard part is segmentation and compositing, not 3D modeling.

- **Cloud model for routine generation.** The escalation path is deliberately rare and budgeted. Do not make every media generation route through cloud "because it's easier." The 1.0 vision says "leaning on as much public-domain and open software as possible"; the cloud tier should stay a rare escalation.

**Defer:**

- **MTP promotion.** Already declined on measured grounds. Don't reopen.
- **IO bandwidth caps** — packet marks them DEFERRED-HARDENING; fine to leave.
- **Course-check** — disabled; don't enable it until the operator rules on the new purpose for the sealed credential.

**Gold-plated already, and correctly so:**

- The VM substrate, the measurement discipline, the pinning, the honest non-claims. These are not gold-plate; they are the load-bearing floor. But the *protocol overhead* around them is where cost is leaking. The per-gate budget cost (99.8 % of $8 for a clean doc-only gate) means the discipline is consuming the budget that the mission itself needs.

---

## D. Does the git-courier gate protocol scale to 1.0 ambition?

**No, not as currently measured.** The protocol has a rate problem, not a size problem. The two live state files grow +7-9 KB per gate, and a clean gate already costs $7.99 of an $8 cap. The system is designed around a single operator dispatching one gate at a time, with a human in the loop for every dispatch. The 1.0 vision is "the operator loads a local-LLM tool, points it at this box, gives a free-range agentic task in plain language, and it just goes." The current protocol requires prompt authors, dispatchers, off-box advisors, and daily manual runner starts. At a minimum, a free-range task decomposes into N gates; at current cost, N gates × $8 is not viable, and N gates × one-dispatch-per-human-decision is not "it just goes."

**What most improves it:**

1. **Gate budget calibration.** The $8 cap is provisional and measured against doc-only gates. The dispatcher addendum says this explicitly: the re-calibration can no longer wait for a manufacturing gate. Do it now: measure a manufacturing gate, set the budget based on that, and if the number is unacceptable, change the gate shape, not the cap.

2. **Context retrieval.** The state file has a per-gate growth rate but no query mechanism. Add something simple: a small index of which gate produced which finding, so a fresh context can load only the relevant sections instead of the whole live state. This doesn't need an embedding model; a grep-index with gate-level summaries suffices.

3. **A planner that produces gates, not just executes them.** The courier assumes a prompt arrives; nothing generates prompts. The 1.0 needs a component that takes the free-range task, decomposes it into gates, and dispatches them. That planner can itself be a gate — but it's a gate whose output is a queue of further gates, and the courier protocol has no concept of a gate producing work for other gates. This is a protocol extension, not a new subsystem.

4. **Human-in-the-loop at the right rate.** The current human gate is the daily manual runner start. For media and computer-use, the human needs to approve per-asset and per-action, not per-day. The protocol needs to model that without going back to per-gate human review.

---

## E. Compliance and safety as a first-class deliverable

### Provenance

**What the 1.0 must have:**

- **Per-artifact provenance record** that survives from asset acquisition through final output. For every image/video in the pipeline: source URL, license identifier, fetched-at timestamp, sha256, and a human approval marker.
- **Output provenance.** When the pipeline composites or edits an asset, the output carries the provenance of every input. If the tiger image is from Library A (CC0) and the polar bear image from Library B (CC-BY-NC), the output's provenance record must list both, and the pipeline must refuse any license that doesn't permit the intended use.
- **Model provenance.** Which model generated which intermediate result, with the model's own license recorded.

**Current design's inadequacy:** The hash pinning is there, but provenance ends at software artifacts. No component records license terms for non-software assets. The pins.lock has `licence: apache-2.0` for the models, but there is no analogous record for an image fetched from Wikimedia or Flickr.

### Licensing

**What the 1.0 must have:**

- **License allowlist, not metadata display.** A configured set of permitted licenses (e.g., CC0, public domain, CC-BY) that the pipeline checks against before an asset enters. The check must be a gate, not a suggestion.
- **License incompatibility refusal.** If a task asks for commercial use and an asset is CC-BY-NC, refuse or escalate to human, not silently proceed.
- **Training-data license awareness for models.** Any local model used for generation must have its training-data license status recorded, and the pipeline must refuse tasks that would violate it (to the extent knowable).

**Current design's inadequacy:** The system knows how to pin and verify a binary; it does not know how to verify a license grant. The git-courier carries "text only — no secrets, no images, no zips"; there is no legal metadata channel.

### Likeness and consent

**What the 1.0 must have:**

- **Face/likeness detection before any identity-based organization or avatar replacement runs.** The pipeline must not organize a video library by "the person depicted" without an explicit, recorded consent basis for each detected face.
- **Consent record for avatar replacement** — if the training video shows real people, the operator must record consent from those people before replacement can proceed. The system must refuse to replace a face without a consent record.
- **Opt-out for identity recognition.** A configurable deny-list of identities that must not be recognized, matched before any face recognition runs.
- **No persistent face database without data-retention limits.** If the pipeline stores face embeddings for organization, they must be scoped, encrypted, and deletable.

**Current design's inadequacy:** The system has no face capability at all, which is currently honest. But the 1.0 asks for identity-based organization and avatar replacement, which means by construction it will process faces. The current design's only human check is `APPROVED` at dispatch; it has no concept of per-identity consent, no likeness deny-list, and no retention limits.

### Logging and audit

**What the 1.0 must have:**

- **Immutable action log** for everything the cyber-capable agent does: every tool call, every file write, every network attempt, every VM action. Every entry with timestamp, actor, input, output hash, and a pointer to the approval that authorized it.
- **Before/after state for every mutation.** The byte-freeze discipline that currently covers the orchestrator DB must extend to every artifact the agent can touch.
- **Human-approvable log diffs.** The operator must be able to review what the agent did in a bounded, legible form, not a raw event stream.

**Current design's adequacy:** The FSM is transaction-logged, and the runner records before/after process sweeps. But the log covers gate execution, not media or computer-use actions. The hook denies by content, but it doesn't log every allowed action (the "permission allowlist is not a security boundary" problem). For the cyber-capable agent, "logged and human-approved boundaries" means every action is either explicitly allowed or explicitly denied, with the record of both.

### Human-in-the-loop

**What the 1.0 must have:**

- **Per-asset approval for public-domain verification.** The human approves the license check result, not just the fetch.
- **Per-action approval for computer-use actions that have external effects.** For turn-based games, the boundary is simple (the game is the only external effect). For general computer use, the boundary may need to be everything outside the VM.
- **Out-of-band re-verification for all media outputs.** The Face B compensating control applies with extra force: a multimodal judge's verdict is PROVISIONAL, and the operator re-verifies before use.

**Current design's inadequacy:** The one-shot daily `APPROVED` is the only human gate for the runner. The gate-courier has the off-box advisor, but that's for code review, not for legal/constitutional questions. The 1.0 needs a second human gate at the asset and the action level, and it does not exist in any modeled form.

**Where the design is already adequate:** The hash-pinning discipline, the deny-only hook, the disposable sandbox, the "COMPLETED ⟹ oracle passed" with its honest Face B caveat, and the compensating re-verification control. These are foundational; they don't need replacing, only extending.

---

## F. What could sink this, and what to prototype first

**Sink risks, ordered by likelihood × impact:**

1. **The local model's correctness window (96 tokens) is unknown outside 96 tokens.** Every comparison diff is blind past 96 tokens. If the model degrades at 4k/8k/32k contexts, then every long task — media pipeline orchestration, computer-use turn planning, multi-gate task decomposition — is built on a model that cannot be trusted for the work. The 1.0 assumes the local model "can carry work end to end." There is zero evidence for that beyond 96 tokens. *De-risk first:* measure long-context correctness now. This is the single highest-value measurement in the entire packet, and it is explicitly untested.

2. **The gate protocol's cost makes multi-gate tasks infeasible.** $8/gate × N gates. If a media task decomposes into 50 gates, that's $400 before any cloud escalation. The operator may need a different economic model — and the fix is not "reduce context," it's "restructure the gate shape so a single gate does more with less overhead." *De-risk:* run one real manufacturing gate and measure its actual cost.

3. **Face B remains open, and media makes it worse.** A forged verdict on a media output is a lie that could pass a multimodal judge that shares the forge's epistemic status. The compensating control (human re-verification) is cheap for code but expensive for media at scale. *De-risk:* close Face B before any media work goes into production.

4. **The runner has never been proven to run a manufacturing gate unattended.** The reaper's substantive paths, the SSH tunnel under a runner child, and the 20-hour wall-clock are all unproven at the shape the 1.0 requires. *De-risk:* the supervised manufacturing batch (milestone 4) is the prototype.

5. **No planner exists, and the courier protocol has no concept of a gate generating work for other gates.** The 1.0 vision presupposes a free-range task in, multiple gates out. The protocol's core assumption is a prompt author manually decomposing. *De-risk:* prototype a "task decomposition gate" whose output is a queue of further gates, and see if the courier can carry that queue safely.

6. **The Vision/NPU unknowns.** Vision is a separate, lower-assurance lane by operator ruling. The NPU is driver-only. *De-risk:* milestone 9's measurement gate before any NPU investment.

**First prototype:** The long-context correctness measurement. It requires no new subsystems, uses the existing ST-1 harness with longer prompts, and the result determines whether any of the rest of this is buildable on the current local model. If the model is reliable to 32k or 65k, the path is open. If it isn't, the architecture needs a different decomposition level (more, smaller gates) or a different model.

---

## G. Recommended public-domain or open-source components

### Media serving and generation

- **ROCm → Vulkan migration**: The current serving is llama.cpp on Vulkan. For diffusion models, the standard path is PyTorch + ROCm, but ROCm on the RX 7900 XTX has driver maturity risk not measured here. If the box can run ROCm, **ComfyUI** (GPL-3.0) is the natural orchestration layer for image/pipeline generation. If ROCm is unstable, **SHARK/iree-turbine** or **llama.cpp's stable-diffusion** integration (if it has matured by 2026) are alternatives on Vulkan.

- **Image generation**: SDXL-Turbo (Stability, open weights under Stability AI license, not fully open but free for research) or **Stable Diffusion 3 Medium** (open weights, commercial with size caps) — both fit 24 GB VRAM comfortably. **FLUX.1-schnell** (Apache-2.0) is another candidate but is heavier.

- **Segmentation**: **SAM 2** (Meta, Apache-2.0) for segmenting people/objects; **BiRefNet** for background removal; **YOLOv8/11** (AGPL-3.0, choose license-aware) for detection. SAM 2 fits 24 GB VRAM fine.

- **Video editing / compositing**: **FFmpeg** (LGPL/GPL with codec caveats) for all video muxing/filtering; **MoviePy** (MIT) for scripted edits; no heavy video diffusion needed.

- **3D avatar**: For the "replace each person" task, use prebuilt **VRM** models or **Ready Player Me** avatars with a renderer (Blender headless, GPL-2.0), not a custom generation model. If procedural avatars are needed, **MakeHuman** assets are CC0.

### Vision / computer use

- **Vision model**: **Qwen2.5-VL-7B or 11B** (Apache-2.0, GGUF available) — fits 24 GB VRAM alongside the resident LLM if the LLM is swapped out; or **Llama 3.2 11B Vision** (Llama license). Choose based on the same license care as the LLM.

- **Screenshot**: **grim** (MIT) for Wayland, **scrot** or **xwd** (X11) for X11 in the guest; both tiny.

- **Computer-use agent**: **Goose v1.46.0** (already pinned, guest-only) — do not add a second agent framework until proven insufficient. Its MCP tool surface is the natural place to add screenshot/click tools.

- **Automation**: **ydotool** (MIT) for input injection, or **xdotool** (GPL-2.0) in X11. Both give scriptable click/type without needing a full desktop automation stack.

### Asset acquisition and provenance

- **Wikimedia Commons API** — public domain/CC images with machine-readable license metadata; first source for "tiger hunting a polar bear" type tasks.
- **Openverse API** — aggregates CC-licensed images across sources with license filtering built in.
- **Creative Commons license metadata** — parse and check with **license-expression** (Apache-2.0) for SPDX-style license logic.
- **Metadata extraction**: **exiftool** (GPL/Artistic) for embedded metadata; **PIL/Pillow** (HPND) for image reading.

### LLM and serving (already present)

- **llama.cpp** (MIT) on Vulkan — keep this; it's measured and pinned.
- **Qwen3.6-27B-UD-Q4_K_XL** (Apache-2.0) — existing primary; the correctness window remains the governing uncertainty.
- **Devstral-Small-2-24B** (Apache-2.0) — fallback; dense, no reasoning loop.

### Compliance / audit components

- **SPDX license IDs** as the internal license vocabulary; **REUSE** conventions for recording licensing in the pipeline's own outputs.
- **Sealed challenges / attestation**: existing TPM2 sealing already covers credentials; extend to signing provenance records so a forged provenance or a human approval cannot be silently added by a candidate. **cosign** (Apache-2.0) is the natural tool if the Sigstore verification path is completed.

### What not to add

- **A second agent framework.** The current Goose surface is pinned, measured, and adequate for the next milestones. Adding another framework doubles the security review load.
- **A second container orchestrator.** The current bwrap sandbox is deliberately minimal. Don't layer Docker/Podman on top; it would invalidate the security history.
- **A second verification system for media.** The multimodal judge is a stopgap; the honest re-verification human loop is the real control. Don't build an elaborate media oracle until the code oracle is closed (Face B).

---

## Bottom line

The system is not a 1.0 local-AI agent; it is a carefully hardened single-gate code-manufacturing pipeline with an unproven runner, an open forgeability gap in its oracle, and zero media/vision capability. But the floor is unusually solid: the measurement discipline, honest non-claims, pinning, and the "COMPLETED ⟹ oracle passed" caveat are better engineering than most systems with more features have. The 1.0 is reachable if the operator (1) trusts the local model enough to build on (measure long-context correctness first), (2) closes the oracle gap, (3) extends the provenance/human-approval story to media assets before building the media pipeline, and (4) accepts that "it just goes" is a long horizon, not a 1.0 deliverable.

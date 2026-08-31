# Honest Gap Analysis: Wrought Foundry vs. 1.0 Vision

## Top-line verdict

You have built roughly the *spine* of a local-first, AI-built, security-hardened manufacturing pipeline: an FSM with a real event store, a deterministic verification oracle in a network-less sandbox, a disposable-guest agent surface, a runner with measured containment, a pins-locked substrate, and a context-discipline protocol with no real precedent I have seen elsewhere. That spine is **the easy 20% of the 1.0 vision, but it is the 20% that is hardest to do well, and you have done it well.** The remaining 80% — media, vision, computer-use, NPU, asset provenance, compliance — is **essentially absent as code**, and several of its pieces have no clean path on a single 24 GB card. The project's own §8 table says this in three lines; the rest of this review says it concretely.

The most important thing the inventory already admits and I will repeat: **the agent surface has written a five-byte file. That is the proven manufacturing ceiling.** Everything else in the 1.0 vision is downstream of closing that gap, and nothing in the current code establishes that the local Qwen3.6-27B can drive a real tool end-to-end without escalating constantly — which is the project's own governing metric, and it is *unmeasured*.

---

## A. Per-capability assessment

### A1. Agentic multi-step task planner/executor maximizing single-node GPU and RAM

- **Exists:** A 10-state FSM with a real `(state, event) → (guard, target)` transition table that raises on undefined pairs. SQLite + Litestream event store with at-least-once delivery, fenced acks, idempotent handlers, repair cap of 3. Escalation ledger with a dual-cap budget ($15/wk, $40/mo) and a pre-call bound. The runner walks an APPROVED-only queue, with measured containment (private `$HOME` and `$XDG_RUNTIME_DIR`, `MemoryMax` + `MemorySwapMax=0`, a reaper matching on `/proc/<pid>/exe`). Goose v1.46.0 pinned in a disposable guest, reaches the model over an authenticated ssh-reverse-tunnel pinhole.
- **Missing:** No *task decomposition* at the operator level. The "gate" is a single self-contained prompt; there is no planner that takes "generate an AI video of a tiger hunting a polar bear using public-domain images" and decomposes it into a DAG of tool-invoking subtasks the runner can schedule. No co-residency scheduling across the dGPU + iGPU + NPU — the dGPU is loaded only with the LLM, the iGPU is UMA-carved and unused, the NPU is unused. No model registry, no model swap scheduler, no VRAM accountant that decides what fits when. The agent surface is proven to *reach the model and write a file*, not to manufacture.
- **Single hardest gap:** A free-range agentic planner that decomposes arbitrary natural-language work into a graph of tool calls and actually executes them end-to-end on the local model without constant escalation. This is a 0-to-1 capability gap, not a stretch. Until the ten fixture tasks exist and a manufacturing gate runs unattended, you have a controlled experiment in *whether the local model can carry work*, not a demonstration that it does.

### A2. Media generation and editing pipelines on local models

- **Exists:** Nothing. No image model, no video model, no segmentation, no compositing, no 3D, no avatar, no face recognition. The Vulkan stack works; llama.cpp serves the LLM; that is the entire media surface.
- **Missing:** All of it. Specifically: no ComfyUI / diffusers serving lane; no Flux / SDXL / Wan / HunyuanVideo / CogVideoX / Mochi model pin; no SAM2; no OpenCV pipeline; no tripo-sr / Shap-E / gaussian-splatting; no InsightFace / DeepFace / FaceNet; no neural-rendering avatar path. And critically: **no serving architecture that co-resides a media model with the resident 27B LLM.** Qwen3.6-27B at Q4 occupies 18.27 GiB of 24 GiB VRAM; headroom is ~5.7 GiB. A media model that fits in 5.7 GiB at usable quality essentially does not exist above toy-tier. You will be choosing between LLM-resident + media-swapped, or running the LLM at reduced context, or running the LLM on the iGPU (which is UMA-carved and unmeasured for this workload).
- **Single hardest gap:** The 24 GB VRAM ceiling is the structural wall. There is no current mechanism to swap models on the dGPU on demand, no VRAM accountant, no scheduler. Until this is solved, every media capability is blocked at the architecture layer, not the model layer.

### A3. Asset acquisition with provenance

- **Exists:** The pipeline's own COTS provenance is excellent — `pins.lock` carries per-artifact binary + archive hashes, separates integrity from authenticity, records where Sigstore is and isn't available. The courier is public git, text-only, with SHA256SUMS manifests.
- **Missing:** No web-fetching capability. No public-domain source verifier (no Wikimedia Commons / Flickr Commons / Europeana / Smithsonian / MET / LoC lookup). No license parser matching against CC0-1.0 / PDM-1.0 / CC-BY-4.0 / CC-BY-SA-4.0 with explicit "commercial OK + modifications OK" semantics. No per-asset provenance ledger for *acquired* assets (separate from the pipeline's own COTS pins). No C2PA / Content Credentials writer. No defense against prompt-injected false provenance — the same Face-B shape, on a new surface: a candidate that supplies its own license string is the same as a candidate that supplies its own verdict.
- **Single hardest gap:** There is no asset-acquisition subsystem at all, and "is this actually public domain?" is a per-asset legal determination that no ML pipeline solves out of the box. Building a verifier that resists prompt-injected false-provenance is a Face-B-class problem and you have not yet closed Face B itself.

### A4. VM-hosted computer-use loop with vision

- **Exists:** Disposable QEMU/KVM guests, boot-to-ssh ≈ 15 s, immutable base image by hash (measured, not assumed). Goose in a guest with an authenticated ssh-reverse pinhole. Egress control is proven attended for a single sequential connection; the prior `guestfwd` transport was replaced after measurement.
- **Missing:** No vision model. No screenshot loop. No screen parser. No coordinate-into-click mapping. No headless display setup for arbitrary software. No fence for *agent actions in a VM* — the existing containment is for candidate *code* in a sandbox, not for an agent driving real software. Vision is an operator ruling as "a separate, lower-assurance lane" — and that lane has no code in it.
- **Single hardest gap:** Computer-use vision models that fit 24 GB alongside the LLM don't exist at quality; the resident Qwen3.6 is already 18.27 GiB. A vision-capable model (Qwen2.5-VL-7B, InternVL3-8B) is a separate model that must either swap or co-reside with reduced LLM context, and the agent must coordinate across them. The vision model also needs to *act* — clicking, typing, scrolling — and the action surface is unmeasured.

### A5. Tiered local-GPU / NPU / cloud routing

- **Exists:** Local GPU (Qwen3.6-27B Q4, 65k context, reasoning on, 24k budget) and cloud (Claude Opus 5 via OpenRouter, dual-cap budget state, fenced acks, escalate-once path). The escalation ledger has router fields. A pre-call cost bound exists.
- **Missing:** The NPU is **entirely unused** — driver bound, `/dev/accel/accel0` live, no userspace stack. The cost bound is **unsound for reasoning models** (measured 8× under-read; `reasoning.mode: pro` re-bills the prompt across internal passes and `max_tokens` does not cap completion billing). The escalation rate (the project's own governing metric) is **not measured anywhere in Phase J.** No router that places work on NPU vs GPU vs cloud by capability/cost/latency. No model registry for non-LLM models.
- **Single hardest gap:** The NPU starts from a kernel driver and a device node, with no userspace runtime and no identified workload class. Without a runtime, the "tiered" routing is two-tier (GPU + cloud), and the cloud tier has a broken cost bound — so the one path that spends real money is also the one path whose fence is measured unsound. Fix the cost bound first; the NPU can wait.

### A6. Context management as first-class engineering discipline

- **Exists:** The git-courier gate protocol. Per-gate fresh context. Append-only journal. Size-budgeted live state files. Corrections by addition, never editing. Measured values carry their command. Prompts as files with block count. The two-sentence honest invariant. This is the strongest discipline in the project and the part with the least precedent elsewhere.
- **Missing:** Exercised only for doc-only gates and one five-byte write. **A clean doc-only gate consumed 99.8% of the $8 cap** — the cheapest possible gate shape has effectively exhausted the budget. A manufacturing gate has not run; the cost headroom is unknown but expected worse. The discovered problem is a *rate* (per-gate growth ~7–9 KB) rather than a *size*, but the rate is also the *cost* rate, and that is the binding constraint. No context-discipline for multi-hour media agentic tasks.
- **Single hardest gap:** The gate protocol's per-gate cost is high enough that an unattended manufacturing batch has effectively no headroom under the current cap. Either cost must come down (smaller local models for routine sub-tasks, smarter prompting, local-only), the cap must rise, or the protocol must change shape for long-horizon work. As written, it does not scale to a 20-hour media batch.

---

## B. Critical path to a viable 1.0 — ordered, independently-shippable milestones

Each milestone is sized roughly and is useful *before* the next.

1. **M1 — Prove one manufacturing gate runs unattended and ships a tool.** Build the ten fixture tasks (which do not exist). Run them through the runner. Measure the escalation rate (P1, the governing metric). *Size: medium (2–3 gates).* This is the project's actual mission and the cheapest high-information measurement available. If local escalation is >30% on real software, the local-first thesis is in question and the rest of the path changes shape.

2. **M2 — Close Face B of the oracle invariant.** Candidate tests execute out of the reporting process; the parent never imports candidate code; the candidate's only channel back is a serialized result the parent parses as untrusted input. Accept the trade: `py.cov.threshold` dies, replaced by out-of-process coverage instrumentation that is itself candidate-written and therefore untrusted-by-construction. *Size: medium-large (architectural change to the verifier).* Nothing cyber-capable ships before this.

3. **M3 — Fix the escalation cost bound.** Replace the per-token formula with a model-class-aware bound: for reasoning models, bound on `est_input × prompt_price × internal_passes_estimate + max_completion_tokens × completion_price`, with `internal_passes_estimate` measured per model class and recorded in the ledger. Cap completion tokens by a *billing* cap, not a generation cap. *Size: small-medium.* Guards the one path that spends real money.

4. **M4 — Asset acquisition with provenance.** A public-domain source verifier (Wikimedia Commons first; cleanest license metadata). A license parser matching CC0-1.0 / PDM-1.0 / CC-BY-4.0 / CC-BY-SA-4.0 with explicit commercial+modifications-OK semantics. A per-asset provenance ledger, hash-bound to the gate bundle. Any provenance string supplied by candidate code is untrusted — Face-B discipline applied to a new surface. *Size: medium.* No media task is legal without this.

5. **M5 — Model swap / co-residency scheduler on the 24 GB card.** A VRAM accountant that knows what is loaded, what fits, and what must unload. A swap primitive that moves the LLM to a reduced-context or iGPU lane and loads a media model. Measured costs of each swap. *Size: large.* Blocks all media work.

6. **M6 — Image generation pipeline (single-frame).** Flux-schnell (Apache-2.0) served locally via ComfyUI or diffusers, as a tool the agent can call. C2PA / Content Credentials embedded at write time, recording model + version + quant + pin + prompt + seed + timestamp + gate ID + source-asset provenance. Integration test: "generate an image of a tiger using public-domain images." *Size: medium.* Depends on M4, M5.

7. **M7 — Vision model + screenshot loop.** Qwen2.5-VL-7B (mostly open) or InternVL3-8B (MIT) on a separate lane or with reduced LLM context. Headless display in the existing disposable guest. Screenshot → vision model → coordinate → click. Lower-assurance lane per the existing ruling. A fence for *agent actions in a VM* — allowlist of software/URLs, per-action confirmation tier for external-touching actions, latching halt on out-of-scope. *Size: large.* New subsystem, new fence class.

8. **M8 — Segmentation + compositing pipeline.** SAM2 (Apache-2.0) + OpenCV (Apache-2.0). For "replace each person with a 3D avatar" — face detection + tracking + mask + replacement. Real-person detection runs face recognition, which is consent-bounded (see E3). *Size: large.*

9. **M9 — Video generation.** Wan2.1 (Apache-2.0) or Mochi-1 (Apache-2.0), integrated as a tool. Frame-coherent, with the tiger/polar-bear task as the integration test. *Size: very large.* Single 24 GB card may not suffice for quality at length; this is the milestone most likely to force a hardware decision.

10. **M10 — Tiered router + NPU lane.** Only after a userspace NPU stack exists (ONNX Runtime + VitisAI EP) and a workload class is identified (likely: small vision-model prefill, or a small Phi-3-mini for routine sub-tasks). The router places work by capability/cost/latency. *Size: large, exploratory.* Defer past 1.0 if M1 shows the local model is adequate without it.

11. **M11 — 3D / avatar pipeline.** Tripo-SR / Shap-E + OpenSeeFace + SAM2. Real-person likeness is consent-bounded; the safest 1.0 scope is synthetic avatars only (no real-person likeness generation without a recorded consent record). *Size: very large.* Most likely to be cut or scoped down.

I have *not* included "slower turn-based game play" as a milestone. It is a capstone use case, not a load-bearing subsystem. It emerges from M1 + M5 + M7 + a vision model, not as a separate build.

---

## C. Cut or defer vs. gold-plate

**Cut or defer past 1.0:**

- **Real-person 3D-avatar replacement of identifiable individuals.** Legally riskiest, technically hardest, least proven. Defer to post-1.0 or scope to synthetic avatars only. The "replace each person with a 3D-modeled avatar" task should be reframed at 1.0 as "replace each person with a synthetic avatar; no real likeness is generated."
- **Full end-to-end video of a tiger hunting a polar bear.** This is an integration test, not a 1.0 requirement. Ship image-gen + clip-compositing first; the video is the capstone.
- **NPU offload.** No userspace stack, no identified workload class. Defer past 1.0 unless M1 reveals the local model is inadequate without it.
- **Slower turn-based game play.** Capstone, not load-bearing.
- **`py.cov.threshold`.** Already doomed by the M2 trade. Cut now.
- **The libvirt domain probe / `virsh destroy` path.** Plain QEMU is the exercised path; the libvirt reaper branch has never executed and `libvirtd` is now socket-activated, which means the probe will run but the destroy branch still won't. Drop libvirt from the runner, simplify to plain QEMU + systemd scope.
- **65k-context correctness testing.** The 96-token window is fine for sub-gate work. Long-context correctness is real but it is gold-plate past 1.0; the agent surface will need more eventually, but not to ship.

**Gold-plate / keep:**

- The git-courier gate protocol discipline. The strongest part of the project. Keep and adapt, do not abandon. (See D.)
- `pins.lock` as the version source of truth. Excellent. Extend it to acquired assets and media models with the same integrity-vs-authenticity distinction.
- The deterministic oracle. Once Face B is closed, this is a real differentiator.
- The disposable-guest model. Boot-to-ssh in 15 s, immutable-by-hash backing file — measured, not assumed. Reusable for the computer-use loop.
- The deny-only PreToolUse hook and the content-matching discipline.
- The reaper. Matching on `/proc/<pid>/exe` not `pgrep -f` — correct.

---

## D. Does the git-courier gate protocol scale to this ambition?

**In discipline, yes. In cost, no — not as written.**

The discipline scales because it is right: fresh context per gate, append-only records, measured values carry their command, corrections by addition, prompts as files with block counts. None of this becomes wrong at larger scope.

The cost does not scale. The measured fact is decisive: a clean doc-only gate consumed $7.9875 of $8.00, 99.8%, *with no guest, no proxy, no network, nothing started*. The wedge was never the cost driver; the shape of a real gate is. A manufacturing gate has more shape, not less. A multi-hour media agentic task decomposed into many sub-gates would blow the budget by orders of magnitude before producing a single image.

What most improves it:

1. **Local-only manufacturing.** The cloud tier is the cost driver. If the local 27B (or a smaller local model for routine work) becomes competent enough to manufacture without escalating, gate cost approaches the marginal cost of local inference, which is free. This is why M1 (measuring escalation rate) is the highest-information measurement available — it tells you whether the local-first thesis is viable at all.
2. **A small local model for routine sub-tasks.** A Qwen3-4B or Llama-3.2-3B at Q4 (~2–3 GiB) co-resident with the 27B reserved for hard reasoning would do most sub-gate work at near-zero marginal cost. The 27B becomes the escalation tier locally; the cloud becomes the second escalation tier.
3. **Bigger gates, fewer of them.** The per-gate overhead is fixed-cost-high; amortize it. A media-pipeline gate that produces a whole scene in one extended turn is cheaper per artifact than one-shot-per-asset.
4. **Opt-in context re-use.** A pinned, hashed, mutable working tree the agent reads and writes directly (rather than re-establishing from courier text every gate) trades fresh-context discipline for cost. Make it opt-in per gate type; the doc-only and security-critical gates keep fresh context, the long-horizon media gates get a working tree.
5. **Local advisor.** The advisor is currently cloud, paid. Once a second local model is available, adjudication can be local too — at the cost of a smaller, weaker adjudicator, which is the right trade for non-security-critical gates.
6. **Cost-per-artifact accounting, not cost-per-gate.** The governing metric for media work is not "did this gate stay under $8" but "did this artifact cost less than producing it by hand." Re-anchor the budget to the output, not the gate.

The discipline stays. The cost model must change shape, or the protocol will not survive a manufacturing gate, let alone a media batch.

---

## E. Compliance and safety as a first-class deliverable

For the media and cyber capabilities to stay legal and auditable, a 1.0 must have:

### E1. Per-output provenance ledger

Every generated image, video, avatar, and edited asset must carry, in a hash-bound ledger entry *and* embedded in the output file:

- Source assets used, with their per-asset license (CC0, PDM, CC-BY-4.0, CC-BY-SA-4.0, etc.) and source URI.
- Model + version + quant + `pins.lock` hash that generated it.
- Prompt + seed + sampler + step count.
- Timestamp, gate ID, operator approval ID.
- Hash of the output file itself.

The output file should carry C2PA / Content Credentials at write time. **Current design: nothing.** The pipeline pins its own COTS but has no provenance ledger for acquired or generated assets, and no C2PA writer.

### E2. License verifier for acquired assets

A parser that reads the source's license declaration and rejects anything that is not explicitly:

- CC0-1.0 or PDM-1.0 (public-domain-equivalent), or
- CC-BY-4.0 or CC-BY-SA-4.0 (attribution required, commercial OK, modifications OK).

Anything ambiguous is rejected. The verifier must match against SPDX license IDs, not free-text. The license declaration must come from the *source's own metadata* (Wikimedia Commons `License` template, Flickr Commons rights statement, Europeana `rights` field), never from candidate code's self-report. **This is Face-B applied to a new surface, and you have not closed Face B itself.** Current design: nothing.

### E3. Likeness / consent controls

Face recognition on real people is a legal landmine: BIPA (Illinois), CCPA (California), GDPR Article 9 (special category data), state biometric statutes, the right of publicity. A 1.0 must:

- **Refuse to generate a likeness of any identified real person without a recorded, timestamped, signed consent record** stored in a consent registry that the agent checks before any generation step.
- **Block face recognition on acquired assets depicting identifiable people** unless the source explicitly permits it *or* the operator has a documented internal-use exemption (e.g., the operator's own video library, internal-only, not redistributed).
- **For "organize a video library by the person depicted":** this requires face recognition on every frame. At 1.0, scope this to: (a) the operator's own library, (b) internal-only use, (c) a documented exemption, (d) no redistribution of the indexed identity data. Anything broader requires per-subject consent.
- **For "replace each person with a 3D-modeled avatar":** the *replacement* is the privacy-preserving path, but the *detection* of each person still runs face recognition, which is still consent-bounded. At 1.0, scope to: detection is permitted on the operator's own library; the avatar is *synthetic* (no real likeness is generated); the detection results are not redistributed.

**Current design: no consent registry, no likeness controls, no face-recognition boundary.** The "organize a video library by the person depicted" task as stated is, in most jurisdictions, illegal to ship without per-subject consent. Reframe it at 1.0 as "organize the operator's own video library by the person depicted, internal-only."

### E4. Logged, human-approved boundaries for the cyber-capable agent

The runner already has the right shape: APPROVED status = human gate, manual start = human gate. For computer-use on real software or the web, this must extend to:

- An explicit allowlist of software the agent may drive and URLs it may visit.
- A per-action confirmation tier for actions that touch external systems (login, payment, communication, file deletion outside the workspace).
- A latching halt on any out-of-scope action.
- The action log is append-only, hash-bound to the gate bundle, and reviewable post-hoc.

**Current design: the containment is for candidate *code* in a sandbox, not for agent *actions* in a VM.** The computer-use loop needs its own fence equivalent, and it does not exist.

### E5. Audit log that is itself provenance-bound

Every action the agent takes, every model call, every asset fetch, every output write must be in an append-only log hashed against the gate bundle. The current courier is text-only and public — good for transparency, but it excludes binary artifacts. Media outputs need a parallel binary provenance store with the same hash discipline: a per-gate `assets/` directory with its own `SHA256SUMS`, pushable to a separate (possibly private) courier, with the text courier carrying only the manifest pointer.

**Current design: the courier explicitly excludes binary. Media work needs a parallel binary courier, or the provenance chain is broken at the output.**

### Where the current design is inadequate (summary)

- No asset provenance ledger.
- No license verifier.
- No consent registry.
- No likeness controls.
- No fence for agent actions in a VM (only for candidate code in a sandbox).
- Face B is open; a forged COMPLETED verdict on a media or cyber gate is the same shape as on a code gate, and the compensating control ("re-verify out-of-band before shipping") does not extend to media assets that have already been published or to cyber actions that have already been taken.
- The escalation cost bound is unsound; any compliance review depending on "the cloud tier was used only when needed and within budget" cannot be supported.
- No C2PA / Content Credentials output writer.
- The courier excludes binary artifacts, breaking the provenance chain at the output for media work.

---

## F. What could sink this, and what to prototype or measure first

### What could sink this

1. **The 24 GB VRAM ceiling.** Qwen3.6-27B (18.27 GiB) + a media model + a vision model cannot co-reside at usable quality. If the box cannot run LLM + vision + media model in some scheduled fashion, the "single node does everything" thesis fails. This is the structural risk and the one most likely to force a hardware decision.
2. **The agent surface's manufacturing competence.** A five-byte write is not software. If the local 27B cannot drive a real tool end-to-end without escalating constantly, the cloud tier becomes the actual manufacturer and the local-first thesis fails. The escalation rate is the governing metric and it is unmeasured.
3. **The per-gate cost ceiling.** At $8/gate and 99.8% consumption on doc-only, a manufacturing gate has no headroom. The protocol does not currently scale to multi-hour agentic media tasks.
4. **Legal exposure from real-person likeness.** If "organize a video library by the person depicted" or "replace each person with a 3D-modeled avatar" ships without consent infrastructure, the legal risk is real and severe. This could sink the project by litigation, not by technology.
5. **Face B on a media or cyber gate.** A forged COMPLETED verdict on a cyber-capable agent's action is worse than on a code tool — it could mean an out-of-bounds action was "approved." The compensating control (re-verify out-of-band) is survivable for code that has not shipped; it is not survivable for an action that has already been taken.

### What to prototype or measure first (cheapest, highest-information)

1. **Measure the escalation rate on a real manufacturing task.** Build the ten fixture tasks. Run them. If local escalation is >30% on real software, the local-first thesis is in question and the rest of the path changes shape. *Cheapest measurement available; highest information.*
2. **Prototype the model swap / co-residency on the 24 GB card.** Load Qwen3.6-27B + Qwen2.5-VL-7B-Q4 (~4–5 GiB) and measure: can they co-reside? At what context cost? At what latency? If not, what does swap cost? *This is the structural-risk measurement.*
3. **Prototype a single image-generation gate with Content Credentials.** Flux-schnell (Apache-2.0), served locally via ComfyUI or diffusers, with a C2PA writer. This proves the media-provenance loop end-to-end on the cheapest media surface and exercises the asset-verifier surface against Wikimedia Commons.
4. **Build the public-domain asset verifier.** Prototype against Wikimedia Commons first (cleanest license metadata). It is the legal gate for every media task. Treat it as Face-B-shaped: any provenance string from candidate code is untrusted.
5. **Close Face B before shipping anything cyber-capable.** The fix is known (candidate tests out of reporting process); the cost is known (`py.cov.threshold` dies). Make the trade.

If measurements 1 and 2 come back bad, the path changes shape: a second GPU (or a different substrate) becomes a 1.0 requirement, not a stretch goal. Better to know that now than after building media pipelines on a box that cannot run them.

---

## G. Recommended public-domain / open-source components

### Agentic task planner/executor
- **Keep the hand-rolled FSM.** It is more disciplined than LangGraph defaults and you already understand it.
- For richer planning: **LangGraph** (MIT) if you want graph-based orchestration, but only as a layer above your FSM, not a replacement.
- Tool calling: **Goose** is already the surface. Keep.

### Image generation
- **Flux.1-schnell** (Apache-2.0) — fastest, decent quality, fully open.
- SDXL-turbo / SDXL-base (CreativeML Open RAIL++-M — **license-risky**, not fully open).
- Stable Diffusion 3.5 (Stability Community License — **non-commercial constraints; risky**).
- Flux.1-dev (non-commercial; **risky**).
- Serving: **ComfyUI** (GPL-3.0, fine for local use) or **diffusers** (Apache-2.0) for programmatic.

### Video generation
- **Wan2.1** (Apache-2.0) — current state of the art for open video.
- **Mochi-1** (Apache-2.0).
- HunyuanVideo (Tencent custom non-commercial — **risky**).
- CogVideoX (Apache-2.0 base, some variants restricted — check per-variant).

### Segmentation
- **SAM2** (Apache-2.0) — Meta's Segment Anything 2. Best choice.
- FastSAM (AGPL-3.0 — **risky for combination with non-AGPL code**).

### Compositing
- **OpenCV** (Apache-2.0).
- **Pillow** (HPND-Copyright).
- For node-based: **Natron** (GPL-2.0) — heavier, only if you want a GUI compositor.
- For in-pipeline: a ComfyUI custom node.

### 3D / avatar
- **Shap-E** (MIT) — OpenAI's text/image-to-3D.
- **Tripo-SR** (check license; was research-only) — single-image-to-3D.
- 3D Gaussian Splatting (research code, license varies — **check before use**).
- For head pose: **OpenSeeFace** (MIT).
- For synthetic avatar: **SadTalker** / **RigFace** (some are non-commercial — **check**).

### Face recognition (consent-bounded)
- **facenet-pytorch** (MIT) — FaceNet via PyTorch. Fully open.
- **DeepFace** (MIT) — wraps multiple models.
- InsightFace (non-commercial research; **production use requires permission — risky**).
- Best for a consent-bound 1.0: DeepFace or facenet-pytorch + your own consent registry.

### Computer-use vision
- **Qwen2.5-VL-7B** (Qwen license, mostly open) — strong computer-use vision, fits in ~5 GiB at Q4.
- **InternVL3-8B** (MIT) — fully open.
- Llama-3.2-Vision (Llama license — **check restrictions**).
- Best fully-open: InternVL3 or Qwen2.5-VL.

### Asset acquisition with provenance
- **Wikimedia Commons API** (CC0 metadata, cleanest) — first source.
- **Flickr Commons API** (institutional, no known copyright).
- **Europeana API** (rights statements, standardized).
- **Smithsonian Open Access** (CC0).
- **MET Open Access** (CC0).
- **Library of Congress** (mixed; per-asset).
- License parser: **SPDX license list** (CC0-1.0, PDM-1.0, CC-BY-4.0, CC-BY-SA-4.0).

### Provenance embedding
- **C2PA / Content Credentials** (c2pa.org — open spec).
- **libvips** — can write C2PA manifests.
- **ffmpeg** — carries metadata; C2PA via plugin for video.

### NPU runtime (when addressed)
- **ONNX Runtime + VitisAI EP** for the NPU.
- **Riallto / Ryzen AI Software** (AMD's Python stack for XDNA2) — check Ubuntu 26.04 packaging.
- A small model that fits the NPU's SRAM budget: **Phi-3-mini** or smaller.

### Tiered routing
- **LiteLLM** (MIT) for routing across providers/models.
- Or a hand-rolled router (the project's style is hand-rolled; that is fine and probably better here).

---

## Bottom line

The spine is strong. The body is unbuilt. The honest distance is: you have ~20% of the 1.0 vision, but it is the *hard* 20% and it is done with a discipline most projects never achieve. The next step is not to build more spine — it is to prove the spine can carry weight, by building the ten fixture tasks and measuring the escalation rate. If that measurement is bad, the path changes shape. If it is good, the rest of the milestones follow in order, and the project's own discipline (pins, gates, oracle, courier) extends naturally to acquired assets, media models, and provenance-bound outputs — *if* the 24 GB VRAM ceiling and the per-gate cost ceiling are solved first, and *if* the compliance surface (provenance, licensing, likeness, consent, audit) is treated as a 1.0 deliverable from the first media gate, not a post-1.0 add-on.

The single most important thing to do next is **measure the escalation rate on real software**. Everything else follows from that number.
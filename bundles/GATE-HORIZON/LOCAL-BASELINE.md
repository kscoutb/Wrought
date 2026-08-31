### (A) Gap Analysis: Vision Capability vs. Current State

| Capability | What Exists | What Is Missing | Single Hardest Gap |
|---|---|---|---|
| **Agentic multi-step planner/executor** (max GPU/RAM) | Deterministic FSM, SQLite+Litestream event store, bwrap sandbox, cloud escalation path, containment/reaper, doc-only unattended batches. | Multi-step agentic loop for complex tasks, proven end-to-end manufacturing, dynamic token budgeting, automated context pruning, escalation-rate telemetry. | **Context/token explosion across steps.** Doc-only gates already consume 99.8% of budget caps. Without automated pruning/RAG, multi-step tasks will exhaust context or budget before completion. |
| **Media generation & editing** (image/video/seg/3D/avatar) | **Nothing.** Zero media models, pipelines, or tooling. | Diffusion/SDXL/ControlNet, video generation (SVD/AnimateDiff), segmentation (SAM2), 3D/avatar tools, pipeline orchestrator, VRAM/RAM management for concurrent LLM+media. | **VRAM/RAM contention.** 24GB VRAM leaves ~5.7GB headroom after Qwen-27B Q4 loads. High-res video/3D pipelines will OOM unless heavily quantized, CPU-offloaded, or streamed. |
| **Asset acquisition with provenance** | SHA-256 pinning, git-courier for code artifacts, strict `pins.lock` discipline. | Web scraper/crawler, license classifier, media metadata extractor, C2PA/provenance stamping, automated rights verification. | **Automated license/provenance verification at scale.** Public-domain filtering requires deterministic classification + human override; false negatives carry legal risk. |
| **VM-hosted computer-use loop with vision** | Disposable QEMU/KVM guests, bwrap sandbox, Goose agent surface (proven to write files). | Vision model (CLIP/LLaVA), headless UI automation (xvfb/python-xlib), screen capture pipeline, accessibility tree reading, low-latency interaction loop. | **Round-trip latency & visual grounding.** Headless screenshot → vision inference → action → new screenshot must stay <2s per step. Requires tight integration, not bolt-on. |
| **Tiered model routing** (GPU/NPU/cloud) | GPU serving (llama.cpp/Vulkan), cloud escalation (Anthropic/OpenRouter, budget-capped). | NPU userspace stack, model converters, routing/health-check logic, fallback heuristics. | **NPU runtime maturity.** AMD XDNA2 has kernel driver but zero production userspace inference stack on Linux. Routing logic is blocked on hardware/firmware availability. |
| **AI-managed context discipline** | Git-courier protocol, append-only journals, measured-evidence rules, size budgets, manual adjudication. | Hierarchical memory, vector retrieval, automated summarization, delta encoding, dynamic token budgeting per step. | **Manual adjudication cost.** Current protocol requires human review of every gate bundle. Does not scale to 10+ step agentic horizons without AI-assisted pruning that preserves the "command carries value" invariant. |

---

### (B) Critical Path to Viable 1.0 (Ordered Milestones)

Each milestone ships independently usable value. Sizes are rough effort estimates assuming 1-2 engineers + operator oversight.

1. **M1: Proven Agentic Loop & Context Scaling** (~3 wks)
   - Implement hierarchical memory (short-term scratchpad + long-term vector store).
   - Add automated summarization/pruning of past gates (preserve commands, drop narrative).
   - Instrument escalation rate, token spend, and context growth as first-class metrics.
   - *Ship:* Multi-step code generation task completes unattended with <5% escalation.

2. **M2: Vision & Computer-Use VM Loop** (~4 wks)
   - Deploy headless UI stack (`xvfb` + `python-xlib`/`xdotool` + `OpenCV`).
   - Integrate lightweight vision model (e.g., `SmolVLM` or `SigLIP`-based) for screen grounding.
   - Build screenshot → inference → action → verification loop. Benchmark latency.
   - *Ship:* Agent drives a simple desktop app or turn-based game end-to-end.

3. **M3: Media Pipeline Foundation & Provenance** (~5 wks)
   - Integrate quantized SDXL/ControlNet + SAM2 via ComfyUI backend or DiffSynth.
   - Build asset scraper + license classifier + C2PA stamping pipeline.
   - Enforce provenance tagging on every generated/ingested media asset.
   - *Ship:* "Generate AI video from public-domain assets" task runs with auditable provenance chain.

4. **M4: NPU Runtime & Tiered Routing** (~3-4 wks, deferred if blocked)
   - Install AMD XDNA userspace stack (or Intel OpenVINO as reference if AMD lags).
   - Benchmark vision/segmentation offload to NPU vs GPU/CPU.
   - Implement routing logic with health checks and fallback heuristics.
   - *Ship:* Vision/seg tasks route to NPU when available; GPU remains primary for LLM/media gen.

5. **M5: 3D/Avatar & Compliance Hardening** (~5-6 wks)
   - Integrate open 3D/avatar tools (MakeHuman, MediaPipe, Blender Python API).
   - Implement likeness detection, consent registry, and hard gating.
   - Build immutable audit trail + human-in-the-loop approval workflow.
   - *Ship:* Avatar replacement pipeline runs with consent checks, provenance, and audit logs. 1.0 is legally auditable.

---

### (C) Cut/Defer vs. Gold-Plate

**Cut or Defer:**
- NPU offload for 1.0 (GPU handles workloads; NPU Linux stack is immature. Defer to post-1.0 or use only for background tasks if runtime matures).
- MTP promotion (already declined; greedy divergence risk outweighs speed gain).
- Perfect Face B prevention (compensating control of out-of-band re-verification is sufficient for 1.0; chase structural fix post-1.0).
- Exhaustive exit-code taxonomy (focus on practical failure modes; narrow scope).
- Libvirt (raw QEMU/KVM + systemd scopes is proven and lean; stick with it).

**Gold-Plate:**
- Deterministic oracle + bwrap sandbox (core trust primitive; keep strict).
- Git-courier context protocol (differentiator; must scale with automation).
- Provenance/Licensing enforcement (hard compliance requirement; non-negotiable).
- Escalation rate measurement & budget caps (financial/safety rail; instrument early).
- Human-in-the-loop gates for media/likeness (legal requirement; architect as first-class state in FSM).

---

### (D) Git-Courier Protocol: Scaling Assessment & Improvements

**Assessment:** The protocol's discipline is excellent, but its current cost profile is unsustainable for agentic horizons. Doc-only gates already exhaust budget caps. Multi-step tasks will multiply context waste, token spend, and manual adjudication overhead. It will choke on long-horizon tasks without structural changes.

**What Most Improves It:**
1. **Hierarchical Memory:** Separate volatile scratchpad (current step) from persistent long-term memory (vector store). Only commit deltas to the courier.
2. **Automated Pruning & Summarization:** AI-assisted compression of past gate evidence. Preserve the "measured value carries exact command" rule; discard narrative, drop resolved KNOWN-OPEN items, keep only active state.
3. **Delta Encoding:** Push only changes between gates, not full journal appends. Use git tree deltas or structured JSON patches.
4. **Token Budgeting per Step:** Hard cap per gate with automatic truncation/summarization when approaching limit. Fail fast on budget exhaustion rather than silent degradation.
5. **AI-Assisted Adjudication:** Pre-filter bundles with a lightweight reviewer model to flag obvious issues before human review. Reduces manual load by 60-70%.

These changes preserve the protocol's evidentiary rigor while slashing token waste and manual overhead to sub-10% per gate.

---

### (E) Compliance & Safety: First-Class Deliverable Architecture

Compliance is not a feature; it is a gate in the FSM. Every media/cyber capability must pass these controls before `COMPLETED`.

| Control | Specification | Current Inadequacy |
|---|---|---|
| **Provenance** | C2PA-compliant metadata embedded in every asset. Source URL, license, transformation history, model version, prompt hash. Immutable WORM storage. | None. No metadata extraction, no stamping, no WORM store. |
| **Licensing** | Automated classifier (Pype/ExifTool) + rule engine. Hard block on non-public-domain/commercial-restricted assets. Human override logged. | None. Web scraping and license verification absent. |
| **Likeness/Consent** | Face detection (RetinaFace/MTCNN) → 1:1 verification against consented registry. Hard block on unauthorized likeness. Avatar replacement logs original→replacement mapping. | None. No face detection, no consent registry, no gating. |
| **Logging/Audit** | Immutable event log of every agent action, model call, asset used, compliance check. Append-only, cryptographically signed. Tamper-evident. | Event store exists but lacks media/cyber event schemas, signature verification, and tamper evidence. |
| **Human-in-the-Loop** | Mandatory approval gates in FSM for: asset ingestion, likeness match, video/avatar generation, cloud escalation, final media output. Operator signs off before `COMPLETED`. | FSM has `HUMAN_REVIEW` state but lacks structured approval forms, timeout escalation, and audit linkage. |

**Architectural Change:** Introduce a **Compliance Oracle** alongside the code oracle. Runs in a separate bwrap sandbox. Validates provenance, licenses, likeness checks, and audit logs. Must pass before artifact transitions to `COMPLETED`. Face B mitigation applies equally here.

---

### (F) What Could Sink This & De-Risking Prototypes

**Primary Risks:**
1. **VRAM/RAM exhaustion** on concurrent LLM + media pipeline → OOM kills, unstable generation.
2. **Context/token explosion** across agentic steps → budget burn, silent degradation, escalation dependency.
3. **NPU runtime instability** → blocked routing, wasted engineering cycles.
4. **Compliance false negatives** → legal exposure, platform takedowns, reputational damage.
5. **Face B oracle bypasses** → systemic trust erosion if forged verdicts multiply.

**De-Risking Prototypes (Measure Before Building):**
1. **VRAM Stress Test:** Load Qwen-27B Q4, run SDXL + ControlNet + vision model concurrently. Measure swap/OOM behavior, swap latency, and fallback heuristics. Define streaming/CPU-offload thresholds.
2. **Context Scaling Test:** Run 10-step agentic task. Measure token growth vs budget, test automated summarization, validate delta encoding. Prove <5% overhead per step.
3. **Computer-Use Latency Benchmark:** Headless VM screenshot → vision inference → action → new screenshot. Measure round-trip time. Target <2s. Optimize if >3s.
4. **License/Provenance Accuracy:** Scrape 200 public-domain images, run classifier, measure precision/recall. Define false-negative tolerance. Build human override workflow.
5. **Compliance Oracle Load Test:** Run 50 media generation tasks through compliance checks. Measure verification time, false positives, and FSM gate throughput.

Prototype these in 1-2 weeks. Cut or pivot based on data before committing to full pipelines.

---

### (G) Public-Domain / Open-Source Component Recommendations

| Subsystem | Recommended Components | Rationale |
|---|---|---|
| **Agentic Planner/Executor** | LangGraph, LlamaIndex, or custom FSM (keep current), CrewAI for multi-agent if needed | LangGraph/LlamaIndex provide state management, tool routing, and memory primitives. Custom FSM is already proven; extend, don't replace. |
| **Media Generation/Editing** | ComfyUI (backend), Stable Diffusion XL/3, ControlNet, IP-Adapter, SAM2, AnimateDiff/SVD, DiffSynth-Studio | ComfyUI provides node-based pipeline orchestration, quantization, and CPU offloading. DiffSynth offers unified media pipeline. |
| **3D/Avatar** | MakeHuman, OpenFace, MediaPipe Face Mesh, Blender Python API, Gaussian Splatting (nerfstudio) | Open, scriptable, no licensing traps. Blender API enables programmatic compositing. MediaPipe handles real-time face/body tracking. |
| **Asset Acquisition/Provenance** | Scrapy/Crawler4j, Pype (license detection), C2PA Python SDK, ExifTool, OpenCue/Tractor | Pype classifies licenses accurately. C2PA SDK stamps provenance. ExifTool handles metadata. OpenCue tracks pipeline jobs. |
| **Computer-Use/Vision** | `xvfb`, `python-xlib`/`xdotool`, OpenCV, CLIP/SigLIP, LLaVA/SmolVLM, Open-WebUI | Lightweight, headless-friendly. SmolVLM/CLIP for fast vision grounding. python-xlib for deterministic UI interaction. |
| **NPU Runtime** | AMD Vitis AI (legacy/reference), ROCm (if applicable), OpenVINO (cross-vendor reference) | AMD XDNA Linux stack is immature. Use OpenVINO as reference for routing logic; defer NPU offload until stable runtime ships. |
| **Compliance/Audit** | C2PA SDK, ExifTool, Retriev, OpenLineage, Marquez, custom WORM store | C2PA for provenance. OpenLineage/Marquez for pipeline tracking. WORM store for immutable audit logs. |

**Final Note:** The current system is a rigorously engineered code-manufacturing pipeline with excellent containment, deterministic verification, and disciplined context management. The 1.0 vision requires extending it into media, vision, and compliance domains. The path is clear: instrument metrics, prototype constraints, automate context, harden compliance gates, and defer NPU until runtime maturity. Ship iteratively. Measure aggressively. Cut ruthlessly.
Below is a gap analysis and a concrete, staged path to a viable 1.0, grounded in the facts of the current system (Wrought Foundry as of 2026-08-31). I will be direct about what exists, what does not, and what must be proven to reach the operator’s vision.

A) Vision capabilities: what exists, what’s missing, hardest gap

1) Agentic multi‑step task planner/executor maximizing a single node’s GPU and RAM
- What exists
  - Deterministic orchestration: an explicit FSM across PENDING→…→COMPLETED with idempotent handlers and an escalation ledger; batch runner with containment; a non-AI deterministic oracle in a bwrap sandbox, per-attempt tmpfs output with strict envelope rules; pinned model serving (llama.cpp/Vulkan) on a 24 GB RX 7900 XTX; budget-capped, ledgered cloud tier; rigorous pins with content hashing.
  - An “agent surface” (Goose) proven only to the level of creating a file through a guest; not yet proven to build software end to end.
  - Resource controls measured in practice (systemd scope + MemorySwapMax=0, RuntimeMaxSec); VRAM/memory budgets pinned; reasoning budget pinned; accurate device selection by name; long context loaded (65k), though long-context correctness is untested.
- What’s missing
  - A real, stable, multi-step planning/execution agent that consistently manufactures software or media artifacts on the node, uses the GPU/NPU consciously, and closes the loop against the oracle. Today’s runner has only taken doc-only unattended batches; manufacturing gates were attended and the “agent surface manufactures” proof is a 5-byte write.
  - Escalation rate (the governing metric) isn’t measured, so there is no evidence the local stack can carry end-to-end without frequent cloud spends.
  - The oracle’s governing invariant is open on Face B: an adversarial candidate can forge its own in-process verdict (detected-not-prevented). That forces human re-verification for anything marked COMPLETED.
  - No NPU runtime exists in userspace; nothing schedules work across GPU/NPU.
- Single hardest gap
  - Closing the oracle’s Face B (unforgeable verdicts) without compromising determinism or safety, and proving unattended manufacturing gates run end-to-end with measured escalation rate. This is foundational; without it, an agent that “just goes” cannot be trusted to close the loop safely.

2) Media generation and editing on less‑filtered local models (images, video, segmentation, compositing, 3D/avatar)
- What exists
  - Nothing. No component for media generation, segmentation, video, or 3D exists in this system today.
- What’s missing
  - Local pipelines for image synthesis, video synthesis/editing, segmentation/tracking, matting, optical flow, body/face pose, and 3D rig retargeting; GPU scheduling/integration; deterministic packaging and provenance stamping of outputs; compliance enforcement (see E).
- Single hardest gap
  - A compliant, reproducible end-to-end media pipeline that is both local-first and legally enforceable (provenance/licensing/consent baked in), especially for identity/likeness tasks. Technically, the tracking/segmentation/retarget stack and its orchestration stability on one GPU is the biggest engineering effort; legally, consent/provenance enforcement is the gating risk.

3) Asset acquisition with provenance and licensing verification (public‑domain/licensed)
- What exists
  - A rigorous pinning/provenance posture for software artifacts (models, binaries, wheels, secpack), and secret scanning; but nothing tailored to media asset acquisition.
- What’s missing
  - An acquisition crawler/ingestor tied to license metadata (SPDX/C2PA), site policies, robots.txt, content hashing, and a durable provenance ledger; a compliance engine that refuses assets lacking acceptable license/consent; output signing/credentialing; cross-artifact manifesting of all inputs used in render outputs.
- Single hardest gap
  - Automated, defensible licensing and consent verification at scale with legally meaningful proofs (e.g., C2PA credentials, SPDX manifests) and deny-by-default behavior.

4) VM-hosted computer‑use loop with vision (agent drives software like a person)
- What exists
  - QEMU/KVM disposable guests, proven immutable backing image; a secured reverse SSH tunnel approach to get guest → host connection; containment/reaper scaffolding on host. No vision loop or interaction loop yet. No measured guest egress control; network isolation for gate child is not set (scope cannot take PrivateNetwork).
- What’s missing
  - A resilient “computer-use” controller: periodic screenshots, OCR/vision model inferences, action planning and input synthesis (mouse/keyboard), failure recovery, and safety/egress controls; standardized per-app recipes; deterministic recording/playback; human-in-the-loop gating and logs.
- Single hardest gap
  - A safe, network-contained, and logged computer-use loop that can run unattended without leaving residue or leaking secrets, while operating within explicit human-approved boundaries.

5) Tiered model routing across local GPU, NPU, and cloud
- What exists
  - Local GPU tier (qwen 27B quant) served via llama.cpp on the dGPU; fallback model; budgeted cloud escalation via OpenRouter; careful pricing bounds (but proven unsound for reasoning models); request-time reasoning budgeting; no NPU userspace.
- What’s missing
  - Runtime router that schedules tasks by cost/perf/latency/assurance; measured escalation rate; NPU EP/runtime and placement; end-to-end correctness/quality metrics per tier for media/vision tasks; model context-length correctness beyond 96 tokens.
- Single hardest gap
  - No NPU runtime and no measured escalation rate. Practically, without measured performance and correctness per task type, routing policies are guesses.

6) Context management as a first-class discipline (AI builds/operates the system)
- What exists
  - Git-courier gate protocol, strict pins, result envelopes, bundle manifests, append-only journals; discipline around repeating measured commands; careful treatment of context budgets; a robust hygiene/security posture.
- What’s missing
  - The cost of gates is high even for doc-only runs (~$6–$8). A consistent live manufacturing context still is not proven (manufacturing gates unattended); structural measurements like escalation rate and wall-clock budgets for real manufacturing flows are incomplete; content-matching denylist blocks some doc gates from writing their own docs.
- Single hardest gap
  - Throughput and cost scalability of the gate discipline to handle complex, multi-artifact media tasks. Without reducing per-gate overhead and instrumenting real manufacturing metrics, the system risks becoming too expensive/slow for practical use.

B) Critical path to a viable 1.0 (ordered, independently useful milestones)

Each milestone is shippable on its own and reduces risk for the next. Sizes are rough and assume a single engineer + this automation; callouts indicate hard dependencies.

1) Close the oracle Face B and make manufacturing gates unattended-viable
- Deliverables
  - Redesign verification to run candidate tests out of the reporting process (separate child process; parent only parses untrusted JSON); drop or replace in-process coverage threshold; enforce provisional→verified recheck until this ships; instrument escalation rate.
  - Runner: supervised manufacturing batch end-to-end; measure and log escalation rate; enforce human gate and reaper correctness.
- Size
  - Medium–large (changes to verifier harness, packs, and classification; measured manufacturing runbook).
- Why first
  - Nothing agentic or media-related is trustworthy until the oracle can’t be forged in-process and unattended manufacturing is proven.

2) Introduce a minimal asset-provenance/consent subsystem (deny by default)
- Deliverables
  - Asset store with: ingestion manifesting (SPDX tag/value), license filter (CC0/PD/explicitly licensed), robots compliance, hash-based provenance, and C2PA signing of stored assets; a consent registry for likeness (allowlist/denylist entries with evidence); provenance ledger per build.
  - Hard-fail if asset lacks acceptable license or consent token. This governs future media pipelines.
- Size
  - Medium; mostly glue + policy + store + simple web scrapers/APIs (Openverse, Wikimedia).
- Why now
  - Compliance is a hard requirement and this subsystem is the gate; build it before any media pipeline.

3) Computer-use loop MVP in the VM (vision+actions with hard boundaries)
- Deliverables
  - Guest automation harness: screenshot capture, OCR/vision inference (local), action planner/executor with strictly bounded action library, logging, and replay; headless browser recipe and one desktop app recipe; human-in-the-loop approval per high-risk action; safe reverse tunnel shape tested under runner; reaper asserts guest teardown; no-network execution path verified.
- Size
  - Medium; integration of existing pieces with careful safety.
- Why now
  - Enables later pipelines that require driving apps, and validates the VM containment and logging story.

4) Media pipeline A: “public-domain montage video” end-to-end
- Target task
  - “Generate an AI video of a tiger hunting a polar bear using public-domain images sourced from the web.”
- Deliverables
  - Governed asset acquisition (from PD sources only) → image dedupe/fingerprint → segmentation/matting → motion/optical flow or pan/zoom generation → compositing → FFmpeg output → C2PA-stamped output with full asset manifest.
  - Deterministic recipe; one-button re-run; GPU aware; cloud escalation optional; enforce provenance in outputs.
- Size
  - Large; but bounded to still imagery + simple motion/compositing first (no text-to-video model required initially).
- Why now
  - Demonstrates the full compliance-governed, local-first media pipeline with a concrete, shippable output.

5) Media pipeline B: “organize a video library by person depicted” (consent-gated)
- Deliverables
  - Offline face detection/embedding, face index build, consent registry check; buckets: “consented-identified”, “declined-identified” (no outputs), “unknown”; write-only hashed embeddings with salted hashes; HIL review workflow and export; jurisdictional switch to disable identification where prohibited.
- Size
  - Medium–large; careful legal gating and UX.
- Why now
  - Exercises the likeness/consent engine and demonstrates a compliance-first identity task.

6) Media pipeline C: “replace each person with a 3D-modeled avatar” MVP
- Deliverables
  - MVP focuses on tracked 2D-to-2.5D overlay via pose/segmentation/tracking + Blender render; optional parametric 3D (SMPL/SMPL-X) retargeting as a second step; explicit consent gating; deterministic recipes; full provenance stamping.
- Size
  - Large; highest technical risk; start with 2D retargeting overlay to derisk.
- Why now
  - Core to the 1.0 vision; do it after A/B so asset/consent/VM/compute infrastructure exists.

7) Tiered router with measured escalation and optional NPU offload
- Deliverables
  - Instrument and enforce local→NPU→cloud placement policies; per-task metrics (quality/perf/cost); measured escalation rate target with dashboards; integrate ONNX Runtime EP for AMD XDNA if feasible on this host; hard cap for reasoning cost on cloud path reworked for the measured model billing shape.
- Size
  - Medium–large; depends on having tasks and metrics from prior milestones.
- Why now
  - Optimizes costs/throughput and unlocks optional cloud improvements safely.

8) Slow turn-based game agent (local LLM + GPU + optional cloud)
- Deliverables
  - Game environment harness; step policy; tiered routing; log and safety gating; deterministic replay; minimally playable on local tier; optional cloud reasoning.
- Size
  - Medium; now feasible once agent containment and router are proven.

C) What to cut or defer versus gold‑plate

- Defer NPU until an ONNX/XDNA userspace EP is running on this exact host; do not burn time integrating a phantom accelerator.
- Start avatar replacement as 2D retargeting (pose+overlay) before attempting full 3D rigs and physics; ship the 2D MVP with consent policies and logs.
- Avoid implementing long-context correctness testing beyond today’s 96-token harness for a media-focused 1.0; record the gap and bound risk by task types that do not need 100k tokens correctness guarantees.
- Skip “general computer use of arbitrary desktop apps” in favor of two nailed-down recipes (headless browser + one specific app); document scope.
- Do not build an elaborate multi-agent planner up-front; a single-agent + deterministic recipes + FSM is sufficient for 1.0. Add LangGraph/autonomous planners later.

D) Does the git‑courier AI‑managed gate protocol scale? What improves it most

- Today’s realities
  - The protocol is rigorous but expensive: doc-only gates consumed ~76–99.8% of an $8 cap; manufacturing gates are unproven unattended. Courier pushes always write status; denylist blocks some doc operations due to content matching; unresolved metrics (escalation rate) are absent.
- Will it scale?
  - Not as-is for media workflows with many artifacts and iterations. The per-gate overhead will dominate small content changes; manufacturing gates with heavy binary artifacts (images/videos) are incompatible with “text-only courier” unless you introduce a signed artifact repository.
- Improvements that pay off most
  - Split gate classes with different budget/tooling: doc gates (text-only, strict denylist), manufacturing gates (artifact repo allowed, with enforced secret scan and size quotas). Move heavy artifacts to a signed artifact store (e.g., object storage + manifest with SHA256 + C2PA), referenced in courier by hash.
  - Make the runner responsible for required compliance scans (already partially done) and for byte-freeze; keep gates unprivileged.
  - Introduce a per-gate cost/latency budget in the queue and measure escalation rate and wall-clock consistently; refuse gates that will exceed budgets under observed distributions.
  - Add a context cache for recurring measurements/artifacts within a batch (still hash-verified), to avoid re-measuring identical steps across gates.
  - Provide a “manufacturing bundle” format: immutable manifest + signatures + provenance JSON; prohibit ad-hoc zips.

E) Compliance and safety deliverables for 1.0 and current inadequacies

1) Provenance and licensing
- Requirements
  - Deny-by-default for assets; only PD/CC0/explicitly licensed sources allowed without human waiver. Enforce SPDX license expressions per asset; store full source URL, timestamp, hash, license text snapshot; maintain a provenance ledger (W3C PROV or similar).
  - Use C2PA to embed credentials in outputs, including a manifest of all inputs (hashes and licenses); sign outputs with a project key; include pipeline steps metadata.
  - Ensure robots.txt and site-specific terms compliance; record proof.
- Current gaps
  - No media asset ingestion or license verification exists; no C2PA signing; no provenance ledger for media.

2) Likeness/consent
- Requirements
  - Likeness registry with explicit “consent tokens” linked to face embeddings (salted/hardened); default is deny; jurisdictional policy toggles (e.g., disable identification in prohibited regions); minors prohibited; category-based sensitivity (e.g., medical, sexual) flagged and blocked.
  - Face recognition tasks must operate offline and only on assets with documented consent; outputs must annotate consent ids and include opt-out logs; provide an HIL approval flow.
- Current gaps
  - No likeness/consent system; current design does not enforce consent; no policy engine.

3) Logging and audit
- Requirements
  - Immutable, signed logs for: asset intake, consent checks, pipeline steps, human approvals, and outputs; per-run IDs linking inputs→outputs; tamper-evident store (e.g., append-only with hash chains).
  - Red/green “compliance gate” in the FSM; task cannot pass without compliance checks.
- Current gaps
  - Logs exist for code-manufacturing, but no media compliance logs or compliance gates are implemented.

4) Human-in-the-loop controls and boundaries
- Requirements
  - Explicit approval steps for: cloud cost spends over a threshold, likeness identification, avatar replacement, and any computer-use actions outside pre-approved recipes; clearly defined deny lists; disable network by default in verification/computer-use contexts; require “operator-approved boundary lists”.
- Current gaps
  - Runner children inherit passwordless sudo; gate child is not network-isolated (scope cannot take PrivateNetwork); the PreToolUse denylist is content-based and not sufficient boundary control for interpreters; HIL approvals for the new media/cyber domains do not exist.

5) Cyber-safe adversarial agent operation
- Requirements
  - Strict sandboxing and network isolation for verification and computer-use flows; no secrets in process address space beyond necessity; sealed credential handling; mandatory reaping; forbidden syscall classes; per-run budget/timeouts enforced.
- Current gaps
  - Known open items: oracle Face B; quiet network attempts by candidate code not classified as security findings; gate child not network-isolated; permission allowlist semantics unresolved (boundary vs convenience).

F) What could sink this and what to prototype/measure first

- Potential sinkers
  - Oracle Face B not closed, leading to false “COMPLETED” media tools and unsafe automation.
  - Compliance gaps (licensing/consent) causing legal exposure; facial recognition without consent enforcement.
  - Gate protocol cost/latency overwhelming practical usage; manufacturing gates not running unattended; escalation rate high and unmeasured.
  - NPU hopes consuming time with no usable runtime; “computer-use” leaking secrets or leaving residue; cloud cost bounds unsound for reasoning models (already measured 8× underestimation).
- De-risking prototypes (do these first)
  - Prototype out-of-process oracle: refactor pytest runner to spawn a child for candidate code; verify fixtures; explicitly drop in-process coverage metric; show forged verdict no longer passes; re-run a supervised manufacturing gate end-to-end.
  - Build the asset store + provenance/consent MVP; ingest PD assets end-to-end; stamp outputs with C2PA; fail assets missing license; wire a compliance gate in FSM. This immediately makes media experiments legal/auditable.
  - Computer-use MVP harness in the guest: screenshot+vision+actions with strict recipes; measure that it starts/tears down clean under the runner; prove no egress; capture logs; run under RuntimeMaxSec with reaper.
  - Measure escalation rate and wall-clock on a real manufacturing gate and the media pipeline A; record escalation and costs; enforce budgets accordingly.
  - Validate a minimal NPU path only if an ONNX Runtime EP for AMD XDNA is actually running here; otherwise explicitly defer.

G) Specific public‑domain/open‑source components per subsystem

- Task planner/executor and orchestration
  - Keep the current FSM and deterministic oracle. For agent workflows, layer LangGraph (local) for multi-step planning; adopt structured tool calling through llama.cpp with strictly bounded tool sets; retain the existing escalation ledger.
  - For code fabrication, keep pytest/coverage/basedpyright/ruff; for out-of-process test running, use Python’s subprocess + JSON report plugins (pytest-json-report) with strict JSON parsing only.

- Media generation/editing
  - Image/Video synthesis: Stable Diffusion (InvokeAI or ComfyUI headless pipelines), AnimateDiff/Deforum, Stable Video Diffusion for local text-to-video (quality caveats apply).
  - Segmentation/matting: Segment Anything (SAM), Rembg/U²Net for matting; Grounding DINO for phrase grounding; DeepLab variants; MediaPipe for landmarks.
  - Tracking/optical flow: RAFT; DeepSORT/ByteTrack for tracking; OpenCV for classical flow/compositing operations; FFmpeg for encoding.
  - 3D/avatar: Blender as the render backbone; SMPL/SMPL-X/Body models via mmhuman3d for parametric fits; OpenPose/MediaPipe for 2D/3D pose; PIFuHD or Neural Body as optional; start with 2D overlay pipelines.
  - Provenance stamping: c2pa (c2pa-rs) to embed content credentials; exiftool and pHash for metadata/fingerprints.

- Asset acquisition/provenance
  - Sources/APIs: Openverse, Wikimedia Commons, Internet Archive (with license filters).
  - Licensing/provenance: SPDX tools (spdx-tools), C2PA; W3C PROV JSON for a simple provenance ledger; Robots and site-policy compliance via standard robots parsers; hash/hardening with SHA-256 + timestamps.

- Face identification and consent
  - Detection/embeddings: InsightFace or FaceNet variants; store salted, keyed hashes of embeddings; provide local-only matching.
  - Policy engine: Open Policy Agent (OPA) with Rego policies for consent/licensing decisions; enforce deny-by-default.

- Computer-use loop
  - GUI automation: Playwright (browser), X11 automation via xdotool/xdg tools; PyAutoGUI for fallback; headless window capture through Xvfb/Xpra/noVNC for screenshots; OCR via Tesseract or PaddleOCR; simple on-screen object detection via CLIP/OWLv2.
  - Strict recipes per target app; record/replay with deterministic scripts.

- Tiered routing and NPU
  - Router: small policy engine (local-first with quality/cost thresholds); metric collection via Prometheus exporters; dashboards via Grafana (optional).
  - NPU: ONNX Runtime with AMD’s XDNA execution provider if/when available for this kernel/driver; otherwise explicitly label NPU “not in use” and disable code paths.

- Compliance logging/audit
  - Immutable logs: append-only log with SHA chaining; sign bundles with project key; store manifests and logs together; expose a human-readable audit report per output.

Closing judgement

- Distance to vision: The system is strong on deterministic manufacturing hygiene and pinned reproducibility, but it has built none of the media/vision/computer-use subsystems and has not demonstrated unattended manufacturing gates for real outputs. The NPU is unused. Compliance in media is nonexistent today and must be built before any identity/media feature is shipped.
- Path to 1.0: Achievable with the sequence above. The first two milestones (oracle redesign and compliance/provenance subsystem) are non-negotiable. The next two (computer-use MVP and media pipeline A) provide the first tangible “it just goes” experience while staying legal and local-first. From there, identity and avatar tasks become tractable. Throughout, measure escalation rate and keep the cloud tier rare and budget-capped.
- Reality check: If oracle Face B, compliance gating, and gate cost/latency aren’t addressed early, the project will stall under its own weight or ship unsafe features. Conversely, if you land those three, the rest is engineering effort with known open-source components and well-understood risks.
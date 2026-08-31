# External review (TOP-UP) — google / `google/gemini-3.1-pro-preview`

- Provider: `Google` · generation `gen-1788215912-BOcMJTkW2G7w9MCQtYPu`
- ZDR: pre-checked in `/models?zdr=true`; enforced via `provider.zdr=true` + `provider.data_collection="deny"`
- finish_reason: `stop` · cost $0.1961 · 73481 in / 4095 out

---

As an independent staff-level software architect, I have reviewed the Wrought Foundry packet against your 1.0 vision. 

My assessment is grounded strictly in the provided live state and security history. To be blunt: you have built an exceptionally rigorous, heavily audited, and philosophically pure foundation for *text-based* software manufacturing. However, the system is fundamentally a text/code engine today. It is structurally, operationally, and architecturally at 0% progress toward the multimodal media, NPU offloading, and cyber-capable 1.0 vision you outlined.

Here is the concrete assessment of your existing pipeline versus the 1.0 target.

### A. Current Capabilities vs. 1.0 Vision

*   **Agentic task planner/executor maximizing GPU and RAM:** 
    *   *Exists:* The FSM, event store (SQLite/Litestream), repair loop, and batch runner exist. The Qwen3.6-27B model is resident on the dGPU. 
    *   *Missing:* The agent is **not proven to build software**. The agent surface (Goose in a QEMU guest) is currently only proven to write a 5-byte file. The ten baseline fixture tasks do not exist. Long-context correctness is unverified past 96 tokens.
*   **Media generation and editing (image/video/segmentation/3D-avatar):**
    *   *Exists:* Nothing. No component of any kind.
    *   *Missing:* The entire multimodal generation stack.
*   **Asset acquisition with provenance:**
    *   *Exists:* Nothing. 
    *   *Missing:* Network-isolated fetchers, provenance tracking, and cryptographic metadata attribution.
*   **VM-hosted computer-use with vision:**
    *   *Exists:* Disposable QEMU guests exist. A text-based agent (`goose`) executes inside.
    *   *Missing:* Multimodal vision routing, screenshot loops, and UI-actuation frameworks.
*   **Tiered local-GPU/NPU/cloud routing:**
    *   *Exists:* GPU (Qwen3.6) and Cloud (budget-capped Anthropics via OpenRouter) exist. 
    *   *Missing:* NPU offload. The XDNA2 NPU has a bound driver but **no userspace stack**. It does absolutely nothing today.
*   **AI-managed context discipline:**
    *   *Exists:* The Git-courier gate protocol is built and in daily use.
    *   *Missing:* Cost efficiency. It currently exhausts ~99.8% of an $8 budget on a *doc-only* run due to strict append-only rules and reasoning overhead.
*   **The Single Hardest Gap:** Bridging the chasm between a text-only deterministic test oracle (pytest/ruff/etc.) and the inherently non-deterministic evaluation of multimodal media. Your system relies heavily on a deterministic read-only bwrap sandbox to verify output. You cannot `pytest` an AI video of a tiger hunting a polar bear. A fundamentally new, non-deterministic or human-in-the-loop oracle architecture is required for media.

### B. Critical Path to a Viable 1.0 (Milestones)

This path defers the hardest items to ensure you ship stable, useful increments.

1.  **M1: True Software Manufacturing (Small):** Clear the 10 unbuilt fixture tasks. Prove the Goose agent can reliably generate, test, and repair software in the QEMU guest, rather than just writing a 5-byte file.
2.  **M2: Secure the Foundation (Medium):** Fix Face B of the oracle invariant. The reporting process must be separated from the candidate code, even if it costs you `py.cov.threshold`. Eliminate passwordless root (`NOPASSWD: ALL`) for the gate children and move the runner to a proper systemd service so `PrivateNetwork=yes` actually functions.
3.  **M3: Web-Acquisition & Provenance Sandbox (Medium):** Build a new, strict fetch-only agent role. It fetches public domain assets, applies C2PA/provenance hashes, and checks licenses, outputting *only* verified assets into a secure asset store.
4.  **M4: Vision & Computer Use (Large):** Integrate a multimodal model into the GPU stack. Expand the QEMU guest with a UI-actuation loop (screenshots to vision model to keyboard/mouse events).
5.  **M5: Media Generation Pipeline (Large):** Integrate headless media models (Stable Diffusion/ComfyUI). Map the existing orchestrator to media tasks. Implement human-in-the-loop review queues, since the deterministic oracle cannot evaluate video quality.

### C. What to Cut, Defer, and Gold-Plate

*   **Cut:** In-process coverage thresholds (`py.cov.threshold`). You must make the trade outlined in the packet: you can have coverage, or you can have an unforgeable verdict (closing Face B). Choose the unforgeable verdict.
*   **Defer:** NPU offload. Linux XDNA2 userspace is incredibly raw. For 1.0, run everything on the RX 7900 XTX.
*   **Defer:** 3D-modeled avatar replacement. Deepfake/likeness mapping requires robust alignment and fine-tuning pipelines that are far too complex until basic generation is solved.
*   **Gold-Plate:** The FSM, the containment sandbox, and the git-courier discipline. Your architectural rigidity here is your only lifeline for keeping autonomous agents from destroying the host. 

### D. Git-Courier Assessment

**It does not scale to this ambition.**
The git-courier protocol relies on appending text to track state. A clean, doc-only run burned $7.98 of an $8.00 budget and consumed nearly 22,000 reasoning tokens. As you add media tasks, UI coordinates, and complex agentic plans, the context window will choke and the API/local reasoning budgets will bankrupt you. 

**What most improves it:** You must implement *lossy summarization* and *state compaction*. The protocol mandates that corrections are made by addition, never editing the record. This creates an O(N) context growth rate (~7-9 KB per gate). You need a gate specifically designed to safely compact history into semantic state without losing the causal chain.

### E. Compliance and Safety (First-Class Deliverable)

Your 1.0 targets (avatar replacement, web scraping, computer use) introduce massive legal and ethical risks. Your current controls are inadequate for this.

*   **Provenance & Licensing:** You need a mandatory pre-processing oracle. Any asset fetched from the web must pass through a strict filter that cryptographically signs the file with its source URL and license. 
*   **Likeness & Consent:** Avatar replacement triggers deepfake and consent liabilities. You must enforce a **Hard Human Gate** (similar to your `APPROVED` queue status) before any job involving facial segmentation or identity mapping executes.
*   **Logging & Cyber Controls (Where current design fails):**
    *   Your packet explicitly states: *"A quiet network attempt by candidate code is never classified as a security finding."* This is a critical failure for a cyber-capable agent. You must employ eBPF or strict network namespace logging to catch *all* network calls, not just those printed to stderr.
    *   Gate children inherit `NOPASSWD: ALL` root access, and the systemd scope fails network isolation (`PrivateNetwork=yes` returns unknown assignment). This means a slightly adversarial agent currently has a trivial path to root and the broader network. You must run the agent in a network-isolated service namespace with dropped capabilities.

### F. Sink Risks & De-Risking

*   **Sink Risk 1: The Reasoning Model Budget Blowout.** Item 15 clearly states that OpenAI/Cloud reasoning models bypassed the `$0.94` budget and spent `$7.35` (8x over) because `max_tokens` does not cap internal reasoning passes. You must fix your cost-bound math immediately, or your escalation tier will bankrupt the project.
*   **Sink Risk 2: Long-Context Blindness.** You noted the local model's correctness window is only proven to 96 tokens. Your primary model is operating at a 65,536 context with a 24,000 reasoning budget. **De-risk this first:** Run the `GATE-16` correctness harness on long-context payloads immediately. If the model is silently corrupting context at 10k tokens, the entire system is hallucinating.

### G. Recommended Open Source/Public Domain Components

*   **Computer Use / Vision:** Look at *OSWorld* or the *Anthropic Computer Use Demo* reference implementations for driving UI within QEMU/KVM.
*   **Media Generation & Compositing:** *ComfyUI* (runs headless via API, highly deterministic graph execution, maximizes the RX 7900 XTX via Vulkan/ROCm). Use *Stable Diffusion* or *Flux* base models for open-weights image generation.
*   **Video/Segmentation:** *SVD (Stable Video Diffusion)* or *CogVideoX* for video. *Segment Anything (SAM 2)* for precise masking and replacement.
*   **Asset Provenance:** Implement *C2PA (Coalition for Content Provenance and Authenticity)* open-source CLI tools to cryptographically sign metadata, ensuring the origin of web-scraped content is verifiable through your pipeline.

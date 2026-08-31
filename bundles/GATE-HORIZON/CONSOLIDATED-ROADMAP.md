# CONSOLIDATED-ROADMAP — a CANDIDATE synthesis toward 1.0

> **THIS IS A CANDIDATE SYNTHESIS FOR THE ADVISOR. IT IS NOT A VERDICT, NOT AN ADJUDICATION, AND
> NOT A PLAN THE BOX HAS AUTHORITY TO ADOPT.** It consolidates what independent reviewers said and
> marks where they agreed and where they did not. The advisor produces the final gap map and
> milestoned roadmap, weighted by cross-lineage agreement; the operator tags `review-rc3`.
> Where this file records a *decision*, it is recording that a decision is **owed**, not taken.

**Inputs.** Five independent non-Anthropic lineages, each given the identical packet and ask, plus
the resident local model as a free air-gapped baseline. Method, roster, ZDR handling and per-model
spend are in `PANEL.md` and `panel-results.json` / `panel-topup-results.json`.

| Lineage | Model | Weight in this synthesis |
|---|---|---|
| openai | `gpt-5` | full |
| z-ai | `glm-5` | full |
| x-ai | `grok-4.6` | full |
| google | `gemini-3.1-pro-preview` | full |
| deepseek | `deepseek-v4-pro-0813` | full |
| google | `gemma-3-4b-it` | **EXCLUDED — see below** |
| *local* | Qwen3.6-27B (resident) | baseline, **not a peer vote** |

**One panelist is excluded and the reason is evidence, not taste.** `google/gemma-3-4b-it` was
selected by a defect in the sending script (it sorts candidates by *shortest slug*, so
"prefer non-`-pro`" selected a 4B model). Its review reports that media generation, library
organisation, avatar replacement and a screenshot-plus-vision loop are all **working**. The packet
it was given states: *"Media generation / vision / computer-use — **Nothing. No component of any
kind**."* It read the VISION wish-list as the as-built inventory. **A confabulated review averaged
into a roadmap would corrupt it**, so it is excluded and named rather than quietly dropped.

**The local baseline is reported, never counted as a vote.** It is one model, on the box, reading
a trimmed packet. It is included because this gate exists partly to measure whether the local
model can do real work — and it did: it correctly reported "Nothing. Zero media models" where
nothing exists, and it independently identified the VRAM co-residency blocker that a paid frontier
lineage also raised. That is a genuine result and it is recorded as one.

---

## 1. Per-capability gap map

Agreement is marked **5/5** where every full-weight lineage said the same thing independently.
Where they diverged, the divergence is preserved rather than averaged.

### 1.1 Agentic multi-step planner/executor maximizing local GPU and RAM

- **As built.** The deterministic spine: explicit 10-state FSM with an event store, repair loop
  capped at 3, escalation ledger, containment, reaper, pins. A resident 27B on the dGPU.
- **Missing.** An agent that actually manufactures. **5/5 independently anchored on the same
  fact:** the agent surface's proven work product is a **five-byte file**. Every lineage quoted it
  back; none of them softened it.
- **THE GAP NOBODY ELSE NAMED THIS PRECISELY, and it reframes the whole capability — deepseek:**
  *"The entire gate protocol assumes a prompt author already decomposed the work. The system
  manufactures software from pre-decomposed gates, not from goals."* **There is no task
  decomposition layer at all.** The vision's premise is a free-range task in plain language; the
  system's premise is a gate someone already wrote. That is not a missing feature inside the
  architecture — **it is a layer above everything that exists**, and it is currently performed by
  the advisor and the operator, by hand, every single gate. Worse, deepseek names the trap in
  closing it: the planner's output *"must itself be verifiable by the deterministic oracle, or
  you've just moved the trust problem up one layer."*
- **Hardest gap — and here the panel SPLIT, which is the most useful disagreement in this review.**
  - **openai, google:** the oracle's Face B is first. Nothing agentic is trustworthy while a
    candidate can forge its own verdict.
  - **z-ai, x-ai:** *prove one manufacturing gate unattended and measure escalation rate* is first,
    because if local escalation is high the local-first thesis itself changes shape — and Face B
    has a working compensating control in the meantime.
  - **This is a real fork and the advisor should rule on it rather than split the difference.**
    The disagreement is about sequencing under uncertainty, and both readings are defensible from
    the same packet. z-ai's argument is the sharper one: **Face B is contained today; the
    escalation rate is not even measured**, and it is the project's own declared governing metric.

### 1.2 Media generation and editing

- **As built. Nothing.** 5/5, unambiguous.
- **Hardest gap — TWO were named, and they are different problems.**
  1. **VRAM co-residency.** Raised independently by **z-ai, x-ai and the local baseline**: 24 GB
     holds a 16.7 GB model plus KV, leaving ~5.8 GB (this gate measured **5,842 MiB free**). A
     media model and the resident LLM **cannot both be loaded**. That makes model residency a
     *scheduling* problem the orchestrator does not currently model at all. x-ai puts a workload
     scheduler at **M1, before everything else**, on the grounds that no media work is possible
     without it.
  2. **THE ORACLE HAS NO MEDIA ANALOGUE.** Stated most sharply by **google**: *"You cannot
     `pytest` an AI video of a tiger hunting a polar bear."* The deterministic, non-AI oracle is
     this project's crown jewel and its entire assurance argument — **and it does not transfer to
     media at all.** Media needs a different oracle: human-in-the-loop, or non-deterministic, or
     both. **No panelist proposed a way to keep determinism here.** This is, in the judgement of
     this synthesis, the single most under-appreciated finding in the whole review, because it
     means 1.0 is not "the foundry plus media tools" — it is a second assurance model.

     **AND THE OBVIOUS FIX REPRODUCES FACE B EXACTLY. deepseek closes the loop that google
     opened**, and this is the most important sentence returned by the entire panel: a media
     oracle that is itself a model is *"a reporter that shares the defendant's epistemic
     status."* Reach for a multimodal judge and you have rebuilt, in a new subsystem and from
     scratch, the precise defect this project has spent two gates measuring and failing to close
     — a verdict rendered by something with no independence from the thing it judges. **The
     project's hardest-won lesson transfers to media before any media code is written.** Whatever
     the media oracle is, its independence has to be argued from the start, not retrofitted.

### 1.3 Asset acquisition with provenance

- **As built.** Nothing for media assets. A strong *culture* of pins and hashes for software.
- **5/5 agreement on sequencing, and it is the strongest unanimity in the entire review:
  provenance must be built BEFORE any media pipeline, deny-by-default.** Every lineage said it
  independently and unprompted. No panelist proposed building media first and adding compliance
  later.
- **Hardest gap.** Defensible licence verification at scale, where the normal case is that
  machine-readable licence metadata is **absent or wrong**.
- **x-ai alone caught a contradiction in the vision statement itself**, and it is worth surfacing
  to the operator directly: **"air-gapped" and "sourced from the web" cannot both hold in the same
  1.0 sentence.** Its resolution — air-gap means *pre-staged, allowlisted assets*, with fetching a
  separate, human-gated, non-air-gapped step — is the only one offered.

### 1.4 VM-hosted computer-use with vision

- **As built.** The substrate half, and it is genuinely good: disposable QEMU guests, ~15 s
  boot-to-ssh, backing image immutable by hash, reaper, scope teardown. **No vision loop, no
  actuation, nothing.**
- **Hardest gap.** A loop that fails *silently and confidently* — an agent misreading a screen does
  not error, it acts wrongly. Detection here collides with the project's own rule that an exit code
  is never a success signal.
- **x-ai's staging is the most practical proposal on the table:** ship a **blind** computer-use
  loop first (screenshot to disk, allowlisted apps, operator-written recipes, human in the loop),
  and add the vision model only afterwards — so the containment story is proven before a second
  24 GB tenant is introduced.

### 1.5 Tiered local-GPU / NPU / cloud routing

- **As built.** GPU tier and a budget-capped cloud tier. **The NPU does nothing.**
- **5/5: DEFER THE NPU.** Unanimous, and unusually blunt — openai: *"do not burn time integrating
  a phantom accelerator"*; google: *"Linux XDNA2 userspace is incredibly raw"*; x-ai adds the only
  concrete discipline offered anywhere in the review: **time-box it at two weeks and fall back to
  CPU/iGPU ONNX if userspace is still empty.**
- **Second unanimous point:** routing policy without measured per-tier cost and quality is
  guesswork, so **escalation-rate measurement precedes router design.**

### 1.6 AI-managed context discipline

- **As built.** The git-courier gate protocol, and every lineage rated the *discipline* highly —
  z-ai called it *"with no real precedent I have seen elsewhere."*
- **5/5 on the split verdict: the discipline scales; the COST does not.** All five anchored on the
  same measured number — a clean **doc-only** gate consumed **99.8 % of its $8 cap**.
- **google names the mechanism precisely:** correction-by-addition creates **O(N) context growth**,
  and the fix is a compaction gate that can losslessly-enough compact history *without breaking the
  causal chain* — which is exactly the property the addition rule exists to protect. **That tension
  is unresolved and no panelist resolved it.**
- **This gate contributed its own measurement to this row:** the packet is **70,810 real tokens**
  against a **65,536** served window. **The system's live state documentation does not fit its own
  resident model**, before leaving any room to answer.

---

## 2. Candidate critical path

Synthesized from five orderings. **Where the panel split on what comes first (§1.1), that split is
preserved as a fork at M2/M3 rather than resolved here.** Sizes are the panel's rough consensus and
are calendar-on-this-box, not headcount estimates.

| # | Milestone | Independently useful because | Size | Agreement |
|---|---|---|---|---|
| **M0** | **Scope freeze, in numbers.** Write the target tasks as DoDs with numbers (seconds of video, allowlisted sources, human gates). **Cut real-person identity clustering and photoreal likeness replacement from 1.0.** Resolve the air-gap-vs-web contradiction explicitly. | Stops the foundry being aimed at work that cannot ship legally. | 3–5 d | x-ai proposed; **z-ai, openai, google concur on the legal cut** |
| **M1** | **Workload scheduler / VRAM accountant on the XTX.** Exclusive lease: LLM ∥ diffusion ∥ vision. Measured swap cost. Refuse concurrent claims. | Operator can run one heavy job without wedging resident inference. | 2–3 w | **x-ai, z-ai, local baseline** — blocks all media work |
| **M2** | **Prove manufacturing + measure escalation rate.** One unattended non-doc gate that ships a real tool. Build the ten fixture tasks (they do not exist). | The project's actual mission, and the cheapest high-information measurement available. | 2–3 w | **z-ai, x-ai first; google M1**; openai folds it into its #1 |
| **M3** | **Close oracle Face B**, accepting that `py.cov.threshold` dies. | Nothing cyber-capable or unattended ships on a forgeable verdict. | med–large | **openai and google put this FIRST**; z-ai M2; x-ai defers it |
| **M4** | **Fix the escalation cost bound** for reasoning models. | Guards the one path that spends real money; measured 8× under once already. | small–med | z-ai explicit; openai and x-ai concur |
| **M5** | **Long-context honesty.** Correctness at 2k/8k/32k/64k. Pin `--ubatch-size 512` in the harness. | Prevents designing 1.0 around a 65k window nobody has measured. | 1–2 w | **x-ai only** — but it is the precondition for C-1 and this gate agrees it is undercounted |
| **M6** | **Provenance store + allowlisted fetch**, deny-by-default. Wikimedia Commons / Internet Archive / operator import. **No general web scrape.** | Operator can legally collect a still set for the tiger task. | 2–3 w | **5/5 — the strongest agreement in the review** |
| **M7** | **Image lane.** Local image generation, inputs only from M6, content credentials on outputs, human approval before first generate. | First visible 1.0 demo: licensed stills in, labelled stills out. | 2–3 w | 5/5 as the right first media lane |
| **M8** | **Short video lane.** Composite M6/M7 stills; one local img2vid that fits after LLM eviction. DoD in seconds, not "a hunt film." | Ships the tiger task at honest quality. | 3–4 w | 5/5, all explicitly scoping it down |
| **M9** | **Computer-use v0, BLIND.** Existing guest, screenshot to disk, allowlisted apps, operator recipes. Measure `ssh -R` under the runner and the reaper **before** any unattended use. | Operator can script a turn-based game with a human in the loop. | 3–4 w | x-ai's staging; openai and z-ai concur on hard boundaries |
| **M10** | **Vision, cheaply.** OCR/UI-parse off the XTX if possible. **Kill-switch: if NPU userspace is still empty at 2 weeks, fall back and say so.** | Unblocks M9 without a second 24 GB tenant. | 3–5 w | x-ai's time-box; **5/5 on deferring the NPU itself** |
| **M11** | **Planner over a pinned tool catalog.** Not a new FSM. Bounded steps, artifact log, human approval at network / generate / click-outside-allowlist. | First time plain language → clip is a product, not a gate. | 2–3 w | 5/5 — **all five say do NOT build an elaborate multi-agent planner** |
| **1.1+** | Likeness work, only with enrolled identities and written consent artifacts, in a separate legal lane. | — | after counsel | 5/5 |

**Rough total to an honest 1.0: ~4–6 months**, the one end-to-end estimate offered (x-ai), and
consistent with the others' sizes. **It assumes M0 is obeyed and M1/M5 do not fail.** If M5 shows
the 27B cannot plan reliably, the panel's stated fallback is a **planner-on-cloud /
executor-local** split — *"that is a fork, not a polish."*

---

## 3. Cut / defer

**Cut from 1.0 — 5/5 or near, and the legal items are the firmest agreement in the review:**

- **Organizing a library by the person depicted** (biometric grouping of real people).
- **Photoreal avatar replacement of real people.** Reframe as *synthetic avatars only; no real
  likeness generated*.
- **General web scrape for "public domain."** Allowlisted sources only.
- **The NPU as a promised tier**, before a userspace hello-world exists.
- **`py.cov.threshold`** — already doomed by the Face B trade; cut it deliberately rather than
  letting it die by accident.
- **Unattended cyber capability.** Logged, allowlisted, human-approved VM only.

**Defer:** long-context correctness beyond what M5 measures; Litestream/R2 and snapshot work; MTP;
GPU passthrough; libvirt as guest supervisor (**z-ai: drop libvirt entirely — plain QEMU is the
only exercised path and the `virsh destroy` branch has never once executed**).

**Do NOT gold-plate** — named explicitly, and this gate is an instance of the first one:
another multi-lineage panel before a single frame exists; a perfect Face B; a custom diffusion
trainer; a new agent runtime when Goose already reaches the model; courier support for binary
media (wrong plane — binaries belong in a hash-pinned asset store, not a text courier).

**DO gold-plate — the actual moat:** `pins.lock` discipline extended to weights, graphs and
checkpoints; deny-by-default assets; human approval on generate / click / spend; device-by-name
with no silent `llvmpipe`; out-of-band re-verification of every `COMPLETED` tool; and the live-state
discipline itself while 1.0 is being built.

---

## 4. The compliance and safety control set a 1.0 must carry

**Every lineage treated this as a gating requirement rather than a feature, and none of it exists
today.** Presented as a control set because that is how all five framed it.

1. **Provenance, deny-by-default.** Per-asset record: source URL, timestamp, content hash, licence
   identifier, and a snapshot of the licence text. An asset whose provenance cannot be established
   is **refused, not used with a caveat** — which is the project's own fail-loudly reflex applied to
   a new surface.
2. **Output credentialing.** Every generated artifact carries a manifest of every input (hash +
   licence), the model, its pin, the prompt and seed, and the gate id — embedded as content
   credentials and signed.
3. **Likeness and consent, separate from licence and stricter.** A consent registry keyed to
   enrolled identities with recorded evidence; **default deny**; minors categorically excluded;
   jurisdictional switch to disable identification entirely. **No real-person likeness output
   without a consent artifact on file.**
4. **A compliance gate in the FSM itself**, not a checklist beside it — a task cannot reach a
   terminal success state without passing it. This is the single most important structural
   recommendation in this section: it makes compliance a *transition guard*, which is the one
   mechanism this codebase already enforces rigorously.
5. **Tamper-evident audit log** — hash-chained, append-only, linking inputs → approvals → outputs.
6. **Human-in-the-loop at named boundaries:** cloud spend over a threshold, any likeness operation,
   any generate, and any action outside an allowlist.
7. **Provenance strings from candidate code are UNTRUSTED.** z-ai's sharpest point: this is Face-B
   discipline applied to a new surface. A provenance claim supplied by the thing being audited is a
   convention, not a control — **and this project already has that exact defect recorded twice.**

**Where the current design is inadequate, stated plainly:** none of the above exists; gate children
inherit **passwordless root**; the gate child is **not network-isolated** (a systemd *scope* cannot
take `PrivateNetwork`); and the permission allowlist is measured non-binding for interpreter grants.
**google and openai both flagged the NOPASSWD inheritance as a 1.0 blocker**, not a known-issue.

---

## 5. Top risks, each with a first de-risking experiment

| # | Risk | First experiment | Cost |
|---|---|---|---|
| 1 | **The local 27B cannot actually drive end-to-end work**, making the local-first thesis unsound. Everything downstream assumes it can, and the proven ceiling is a 5-byte file. | **Build the ten fixture tasks and run one unattended manufacturing gate. Measure escalation rate.** 5/5 named this the cheapest high-information measurement available. | 2–3 gates |
| 2 | **Media has no oracle.** Determinism does not transfer; the assurance argument does not survive the move to media. | Take **one** media output and write down what "verified" means for it. If the answer is "a human looks at it", that is the finding, and the FSM needs a human-review terminal state that is not `HUMAN_REVIEW`-as-failure. | days |
| 3 | **VRAM contention blocks all media work.** | Measure the swap: evict the LLM, load a media model, generate, restore. **Record the wall-clock cost of one swap cycle.** That number decides whether co-residency scheduling is a feature or the architecture. | days |
| 4 | **Gate-protocol cost dominates.** A doc-only gate ate 99.8 % of its cap; media gates are strictly larger. | Instrument cost per gate class and set a per-class budget. Then run **one** media-shaped gate and see what it actually costs. | 1 gate |
| 5 | **Legal exposure on likeness and provenance** — the only risk here that is not recoverable by engineering. | Do M0 and M6 **before** any media pipeline. Get counsel on the identity lane before building it, not after. | 1 gate + counsel |
| 6 | **Escalation cost bound is unsound**, measured 8× under on the one path that spends money. | Re-derive the bound per model class; cap on **billing**, not generation. Replay the measured 8× case against the new bound. | small |
| 7 | **Face B stays open longer than expected** and something ships on a forged verdict. | The compensating control is already in force — **out-of-band re-verification of every `COMPLETED` artifact.** Verify it is actually being applied, since a control nobody performs is not a control. | days |

---

## 6. What this synthesis will not claim

- **It does not rule on the M2-vs-M3 fork.** Two lineages put manufacturing proof first, two put the
  oracle first. Both are defensible from the same packet; the advisor should rule.
- **It does not verify a single panel finding against the code.** The panel read a curated packet,
  not the tree. Every finding here is a **candidate**, exactly as an escalation reply is a candidate
  and not a PASS — the standard this project applied to its last panel and must apply to this one.
- **Sizes are the panel's, not measured.** No milestone here has been costed on this box.
- **The strongest agreements are the most reliable content in this file, and the exclusions are
  part of the evidence.** Where five independent lineages converged unprompted — provenance before
  media, defer the NPU, discipline-scales-cost-does-not, cut real-person likeness, no elaborate
  planner — that convergence is the signal the advisor asked to be weighted by. Where they split,
  the split is preserved.

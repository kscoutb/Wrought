# RESEARCH-QUESTIONS — the open questions this review surfaced

**What this file is.** Each section below is a **crisp research prompt a future research gate could
run as-is**. They are questions, not answers. Nothing here proposes a version number, a model slug,
a threshold or a configuration key — **naming one would be inventing a pin**, which is a hard-rule
violation in this project and the exact failure these questions exist to avoid. Where a value is
needed to answer a question, the question says so and says who must ratify it.

**Method note that applies to every section.** This project's standing rule is that *a measured
value carries the exact command that produced it, or it is not evidence*. A research gate answering
any of these must return commands and captures, not a literature summary. Where the answer is a
recommendation to adopt something, the deliverable is a **`pins.lock` delta proposed for operator
authorship**, never a pin written by the gate itself.

---

## R-1. The out-of-process oracle redesign for Face B

**This is the highest-value question in this file**, because it is the only one that touches the
system's governing invariant.

**Background, settled and not to be re-derived.** `COMPLETED ⟹ the oracle passed` holds against
escape and persistence (Faces A, C) but not against a candidate forging its own in-process verdict
(Face B). A uid boundary was measured **unavailable** at three layers *and* **insufficient in
principle** — the oracle's assertions run inside the pytest process, so the forger *is* the
reporter. Fixture `exit0c` is committed proof that no relocation-based fix can be mistaken for
closure.

**The question.** Design a verification architecture in which the process that renders the verdict
never executes, imports, or links candidate code — and cost it honestly.

Specifically:

1. **What is the minimum trusted computing base for a verdict?** The parent parses a serialised
   result from an untrusted child, exactly as `docs/03` §10.7 already treats the result envelope.
   What must the parent do to make that parse safe, and what is the complete list of things the
   child can still lie about?
2. **`py.cov.threshold` dies. What, if anything, replaces it?** In-process coverage measures the
   process it runs inside; move the candidate out and the metric has no referent. Any out-of-process
   coverage instrumentation produces output that is *also* candidate-written and therefore *also*
   untrusted. **Is a coverage number that the candidate can influence worth having at all, or is
   the honest move to delete the check rather than reimplement it weaker?** Answer this before
   answering (1) — it may be that the right design has no coverage gate.
3. **What breaks downstream?** Every pack, fixture and gate asserting on `py.cov.threshold` is
   downstream. The number does not merely change — **it changes meaning**, which is worse. Enumerate
   the blast radius before proposing the change.
4. **What does it cost per verification?** A second process per check, on a box where verification
   is meant to be deterministic and free. Measure the wall-clock delta on the existing fixture set.

**Deliverable:** a design with the coverage trade stated explicitly as a trade, for a **ferry
decision**. Not an implementation.

## R-2. What genuinely offloads to the Strix NPU

**Background.** XDNA2 is present, the in-tree `amdxdna` driver is bound, `/dev/accel/accel0` is
live — and **no userspace stack is installed**. Nothing in this system uses it. Every roadmap item
that routes work to the NPU is starting from a kernel driver and a device node.

**The question, in the order a gate should answer it:**

1. **What userspace stack is actually required**, and is it installable from the offline hashed
   wheel set this project mandates — or does it require network installs that the air-gap
   requirement forbids? *A stack that cannot be installed offline is disqualified regardless of its
   performance.*
2. **What operations does it actually accelerate on this silicon?** Not "AI inference" — which
   specific operator classes, at which precisions, with what memory constraints.
3. **Is LLM inference among them at useful sizes, or is the honest answer that the NPU is for
   small vision/audio models and not for a 27B?** The project should know this before any tiered
   routing design assumes an NPU tier exists.
4. **What is the measured power and thermal profile** relative to running the same work on the
   dGPU, on a box whose dGPU sits on an external OCuLink link?

**Why this is high priority despite being unglamorous:** the vision's tiered-routing capability
names local-GPU / NPU / cloud as three tiers. **If the NPU tier cannot carry real work, the design
is two tiers and should say so from the start** rather than discovering it during implementation.

## R-3. Local video generation and 3D-avatar stacks under Vulkan on an RX 7900 XTX

**Background and the binding constraint.** This box serves inference through **llama.cpp on
Vulkan, not ROCm** — a deliberate choice, load-bearing, with a name-based device assertion at boot.
**Most of the open media-generation ecosystem assumes CUDA, and its second-class path is ROCm, not
Vulkan.** This is the single hardest constraint on the media half of the vision and it should be
confronted first, not discovered late.

**The question:**

1. **Is there a credible Vulkan path for image and video generation at all**, or does the media
   workstream require introducing ROCm alongside Vulkan on the same GPU? **If it requires ROCm,
   that is a substrate decision with consequences for the serving rail's reproducibility, and it is
   the operator's, not a gate's.** Cost both branches.
2. **What fits in 24 GB alongside a resident 27B — or must the LLM be evicted for media work?**
   Measured right now: 16.7 GB of model plus KV leaves ~5.8 GB free. **The likely honest answer is
   that media generation and resident LLM serving cannot coexist on this GPU**, which makes model
   residency a scheduling problem the orchestrator does not currently have. Confirm or refute it
   with a measurement.
3. **Segmentation, compositing, and 3D/avatar are separate stacks with separate constraints** —
   answer them separately rather than as one "media pipeline". Which have Vulkan-viable
   implementations, which are CPU-viable at acceptable latency, and which are neither?
4. **What is the licence status of each candidate's weights**, not just its code? The vision makes
   compliance a hard requirement, and a permissively-licensed inference engine wrapping
   restrictively-licensed weights satisfies nothing.

## R-4. The strongest open computer-use / vision loop drivable by a ~27B local model

**Background.** The vision wants a VM-hosted computer-use loop — screenshot plus vision model — so
the agent drives software like a person. The box already has the hard part of the substrate: a
disposable-guest model with a measured ~15 s boot-to-ssh and a hash-immutable base image.

**The question:**

1. **Which open computer-use harnesses are drivable by a ~27B local model rather than a frontier
   model?** Most published results assume a frontier model. **The honest sub-question: is there a
   measured floor of model capability below which the loop does not close at all**, and is a 27B
   above or below it? A negative answer is a valuable answer.
2. **What vision model runs alongside**, given the 24 GB constraint and R-3's residency problem?
3. **What is the failure mode when the loop breaks?** An agent driving a GUI that misreads a screen
   does not error — it acts wrongly and confidently. What is the detection mechanism, and how does
   it fit this project's rule that an exit code is never a success signal?
4. **How does the existing containment carry over?** The disposable guest, the reaper, the
   scope-based teardown and the "nothing a gate starts may outlive it" rule are all built. Does a
   long-lived interactive guest break any of them? *Note the specific precedent: a gate once left a
   guest running for seven days with an API key in a proxy's memory, which is why §13 exists.*

## R-5. Provenance checking for web-sourced public-domain assets

**Background.** The vision names asset acquisition with provenance — public-domain and licensed
source verification — and makes compliance a **hard requirement, not a feature**. The concrete
target task ("generate an AI video of a tiger hunting a polar bear using public-domain images
sourced from the web") requires fetching third-party media and being able to defend its licence
status afterwards.

**The question, and it is more legal-shaped than technical:**

1. **What does "verified public domain" actually mean operationally?** A source site's assertion is
   not provenance. What is the minimum evidence chain this project would accept, given that its own
   standard elsewhere is *a measured value carries the command that produced it*?
2. **What machine-readable licence metadata exists in practice** across the plausible sources, how
   often is it present, and how often is it wrong? **Assume it is frequently absent** and design for
   that case, because that case is the normal one.
3. **Where does the evidence live, and for how long?** If a licence claim is challenged a year
   later, what does the system produce? This is an audit-trail design question and it should reuse
   the event store and manifest discipline the project already has rather than invent a second one.
4. **What is the refusal path?** The system's governing reflex is *fail loudly; an underspecified
   requirement is a defect to report, never a blank to fill.* Applied here: an asset whose
   provenance cannot be established must be **refused, not used with a caveat.** Confirm that is
   the intended policy before building anything that assumes it.
5. **Likeness and consent are a separate question from licence, and harder.** Identity-based
   organisation, face recognition, and avatar replacement of real people carry constraints that no
   licence tag addresses. **What controls must exist before any of those capabilities is built** —
   not retrofitted after. Treat this as the gating question for that whole capability class.

## R-6. Serving-window and model-residency economics

**Raised by the operator during this gate**, and worth a gate of its own because the intuitive
answer is measurably wrong.

**Background.** The 65,536-token served context is **not** a model ceiling and **not** a VRAM
ceiling. It is decision **D5**, taken deliberately: the 128K headroom is real, but mid-context
reliability decays from 32K, fill-the-window retrieval is evidenced harmful, and **a window size
that raises escalation rate is negative value** under P1. Revisit is gated on **C-1**. Measured
during this gate: ~5.8 GB VRAM free, so a larger window is affordable — and this gate's own packet
came to **70,810 real tokens, exceeding the served window before leaving any room to answer.**

**The question:**

1. **Does anything in the 1.0 vision actually require a >64K single-pass window**, or does
   decomposition serve every case? *This gate's own evidence is that decomposition worked: the
   packet went to 34,032 tokens by dropping whole blocks, at no quality cost that was detectable.*
   **The default answer should be "decompose", and the burden of proof is on the window.**
2. **Is there a smaller-expert or otherwise-cheaper model that holds output quality while freeing
   enough VRAM for a materially larger KV cache?** The two models on this box are a 27B (16.7 GB)
   and a dense 24B fallback (13.3 GB). **Answering this requires naming a candidate, which requires
   a `pins.lock` entry, which is operator-authored** — so the deliverable is a proposed pins delta
   with measurements, never an adopted pin.
3. **C-1's own precondition is unmet and should be stated:** it requires that retrieval
   demonstrably needs >64K **and** that ≥85%-of-32K quality holds. **The second half cannot
   currently be evaluated at all** — long-context correctness is `KNOWN-OPEN` item 1, untested, and
   the measured correctness window is **96 tokens**. **So C-1 cannot be satisfied until a
   long-context correctness harness exists.** That harness, not the window, is the real
   prerequisite, and it is a gate.
4. **Does media work force eviction of the resident model?** See R-3.2. If so, model residency
   becomes a scheduling concern the orchestrator does not currently model.

## R-7. Whether the gate protocol survives the scale the vision implies

**Background.** The git-courier gate protocol is the mechanism by which this system is built by
agents that do not share memory. It works. It is also **expensive**: a clean, doc-only, unattended
gate consumed **99.8 % of its $8 cap**, and the cheapest possible gate shape has effectively
exhausted it. The two live state files have a measured **per-gate growth rate of +7–9 KB**, so a
one-time cut is regrown in about seven gates.

**The question:**

1. **What is the cost of a *manufacturing* gate?** Every cost datapoint so far is doc-only. The
   re-calibration debt is `KNOWN-OPEN` item 10 and it has been deferred twice.
2. **Does the protocol's per-gate overhead scale sub-linearly, linearly, or worse** with the number
   of gates? The growth-rate measurement suggests the live-file read cost grows linearly with gate
   count, which would make the protocol's cost quadratic in total gates. **Two observations are not
   a trend — this needs a third and fourth.**
3. **What is the minimum viable gate?** If the floor is ~$8, the vision's scope implies a cost that
   should be estimated now rather than discovered.
4. **Where does the human actually sit?** Today: the operator starts the runner manually once a
   day, and `APPROVED` is set by a human. Both are load-bearing and neither scales with gate count.
   **What replaces them, and does anything survive that removes the human from the loop?** Note the
   standing constraint that makes this sharp: the box has passwordless root and gate children
   inherit it.

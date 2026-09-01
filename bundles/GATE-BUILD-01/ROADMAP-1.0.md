# ROADMAP-1.0 — the locked milestone sequence toward 1.0

**Locked 2026-09-01 by `GATE-BUILD-01` PHASE 1**, the first BUILD gate. This file supersedes the
candidate synthesis as *the project's plan*; it does not supersede it as *evidence*.

**Provenance, and the distinction matters.** The content below has two sources and they carry
different authority:

| Source | Authority | Where it is |
|---|---|---|
| `bundles/GATE-HORIZON/CONSOLIDATED-ROADMAP.md` | **CANDIDATE.** Five non-Anthropic lineages against a curated packet. **Not one finding was verified against the code.** | courier, unmodified |
| **The operator's eight rulings** | **DECIDED.** They ARE the M0 scope-freeze. | reproduced verbatim in §1 below |
| **The advisor's fork ruling** | **DECIDED.** It settles the panel's 2-vs-2 sequencing split. | §2 |

Where the two disagree, **the rulings win and the disagreement is written down rather than
smoothed over** — §1 rulings 5 and 6 each overturn a 5/5 panel position, and both say so in place.
Where this file states a size, it is **the panel's rough size and was NOT costed on this box**;
that qualifier travels with every number here and is not repeated on each row.

---

## 1. M0 — SCOPE FREEZE. The operator's eight rulings.

**These eight rulings ARE M0.** M0 is not a milestone to be *done*; it is the frame every later
milestone is built inside. A gate that finds itself arguing with one of these is arguing with a
decision that has been taken.

### Ruling 1 — task decomposition is TWO-TIER

Big projects are decomposed into project docs and gates **by the operator and the advisor — the
human trust anchor**. WITHIN a bounded task the agent may call tools and dynamically solve
problems.

**1.0 does NOT build a full autonomous project planner. It builds a bounded within-task tool-use
loop whose scope is AUTHORED, not INVENTED.**

*What this settles.* deepseek's finding — *"the entire gate protocol assumes a prompt author
already decomposed the work; the system manufactures software from pre-decomposed gates, not from
goals"* — is **correct as a description and is not a defect to be fixed in 1.0.** The missing layer
is missing on purpose, and the humans are it. This also disposes of deepseek's trap in closing it
(*"the planner's output must itself be verifiable by the deterministic oracle, or you've just moved
the trust problem up one layer"*): a planner whose output is human-authored does not move the trust
problem, because the trust anchor never left.

### Ruling 2 — media assurance is AUTOMATED SCAN + HUMAN-IN-THE-LOOP

**NOT a deterministic oracle, and NOT an AI-judge-as-verdict.** Cheap automated checks — format,
resolution, safety/quality, provenance — plus operator feedback. **The human is the media verdict
authority.**

*What this settles, and it is the panel's single most important finding.* google: *"You cannot
`pytest` an AI video of a tiger hunting a polar bear."* deepseek closed the loop: an AI judge is
*"a reporter that shares the defendant's epistemic status"* — **it reproduces Face B exactly, in a
new subsystem, from scratch.** The ruling refuses both horns. The deterministic oracle is not
stretched to cover media (it cannot), and no model is given verdict authority over another model's
output (that is Face B rebuilt). **The human takes the verdict, and the automated checks are
filters that reduce what the human must look at — never a substitute for looking.**

**A consequence that must not be lost:** the FSM needs a human-review terminal state that is a
**success**, not `HUMAN_REVIEW`-as-failure. Panel risk 2 named this and it is real work, not a
labelling change.

### Ruling 3 — the CONTEXT SCOPING TOOL is elevated to the first build milestone

The cloud orchestrator holds the big picture; **the local model gets scoped slices.** The project
need not fit the local model — **only the current task's slice must.**

*What this settles.* `GATE-HORIZON` measured the live state docs at **70,810 real tokens against a
served `n_ctx` of 65,536** — the system's own documentation does not fit its own model, before
leaving any room to answer. The reflex fix is a bigger window; **D5 already declined that**, and
`KNOWN-OPEN` item 22 records why (mid-context reliability decays from 32K, and *"a window size that
raises escalation rate is negative value"* under P1). The ruling takes the other branch: **stop
trying to fit the project into the window and start selecting what goes in it.** This is
`M-scope` in §2 and it is what `GATE-BUILD-01` PHASE 2 builds.

### Ruling 4 — MEASURE-FIRST STANDS, hands-off

The manufacturing and escalation measurement runs **unattended**. **The operator launches; the
operator does not babysit.**

### Ruling 5 — compliance is RIGHT-SIZED TO PERSONAL USE

**KEEP, as good engineering:**

- provenance / asset tracking
- a **light** audit log
- **human approval on cloud spend and on destructive operations**

**DROP, as corporate scaffolding this project does not need:**

- the consent registry
- jurisdictional switches
- biometric prohibitions

**AND the "compliance gate in the FSM" becomes a POLICY GATE enforcing the operator's OWN rules** —
air-gap mode, spend caps, protected paths.

*This overturns a panel position, and the overturning is deliberate.* The panel's §4 control set
was framed by every lineage as *gating*, and items 3 (consent registry, jurisdictional switch,
categorical minor exclusion) and the biometric prohibition are dropped here. **The reason is
scope, not disagreement about the engineering:** this is a single-operator personal system, not a
product with third-party subjects. The panel's structural insight is KEPT and is the better half of
the finding — **a transition guard is stronger than a checklist beside the FSM**, and it is exactly
the mechanism this codebase already enforces rigorously. What changes is *whose rules it enforces*.

**One item from panel §4 is KEPT IN FULL and must not be read as dropped with the rest:** item 7 —
**provenance strings supplied by candidate code are UNTRUSTED.** That is Face-B discipline on a new
surface, this project has recorded the exact defect twice, and it is not a compliance item at all;
it is an assurance one.

### Ruling 6 — AVATAR REPLACEMENT and LIBRARY-SORTING-BY-CAST are IN SCOPE

For **personal use**: legally-acquired media, **no distribution of real-person deepfakes assumed**.

*This overturns the panel's firmest agreement, and it is recorded as an overturn rather than
absorbed quietly.* The panel cut both at 5/5 — *"organizing a library by the person depicted
(biometric grouping of real people)"* and *"photoreal avatar replacement of real people"* — and
put likeness work behind counsel in a 1.1+ legal lane. **The operator rules them in**, on the
ground that the panel costed a distribution risk this deployment does not carry. **The assumption
is stated so it can be re-examined if it stops holding: no distribution.** If that changes, this
ruling is the first thing to revisit.

### Ruling 7 — AIR-GAP MODE

A **per-task and global switch** restricting work to **local GPU/NPU plus pre-staged assets**: no
network egress, no cloud tier. It is a **privacy and resource choice, NOT a security boundary**,
and it is **the natural default for media work.**

*What this settles.* x-ai alone caught the contradiction in the 1.0 vision statement —
**"air-gapped" and "sourced from the web" cannot both hold in the same sentence.** The resolution
is two modes with the operator selecting, not one mode with an asterisk.

**The "not a security boundary" clause is load-bearing and is the reason this ruling is safe to
state so simply.** This project has measured, repeatedly, what happens when a convenience layer is
described as a fence: `KNOWN-OPEN` item 8 is that exact question, still open, about the permission
allowlist. Air-gap mode is declared a *mode* from its first line so nobody has to discover later
that it was never a boundary. The real fences stay where they are — the netless bwrap sandbox by
construction, nftables egress, the sealed credentials.

### Ruling 8 — the NPU is DEFERRED, TIME-BOXED

**Do not build 1.0 around it.** Two weeks, then **fall back to CPU/iGPU and say so.**

*This was the panel's other unanimity* — openai: *"do not burn time integrating a phantom
accelerator"*; google: *"Linux XDNA2 userspace is incredibly raw"*. x-ai supplied the only concrete
discipline offered anywhere in the review and the ruling adopts it: **a time-box with a stated
fallback and an obligation to announce the fallback.** Note what the ruling does NOT do — it does
not remove the NPU from the tier list. It removes it from the critical path.

---

## 2. The milestone sequence

**M0 is §1 above.** `M-scope` is `GATE-BUILD-01` itself. The rest run in the order given.

| # | Milestone | Why it is independently useful | Panel size (NOT costed here) |
|---|---|---|---|
| **M0** | **Scope freeze** — the eight rulings in §1. | Every later milestone is built inside this frame. | done, this gate |
| **M-scope** | **Context scoping tool — `bin/wrought-scope`.** A committed index over `bin/`, `src/`, `docs/`; ranked minimal file set per task with honest `/tokenize` costs. | **Ruling 3.** Every gate after this one loads a slice instead of the tree. It is the only milestone that makes the ones after it cheaper. | this gate |
| **M1** | **VRAM scheduler / workload accountant on the XTX.** Exclusive lease: LLM ∥ diffusion ∥ vision. Measured swap cost. Refuse concurrent claims. | The operator can run one heavy job without wedging resident inference. **Blocks all media work.** | 2–3 w |
| **M2** | **PROVE MANUFACTURING + MEASURE ESCALATION RATE.** One **unattended** non-doc gate that ships a real tool. Build the ten fixture tasks — they do not exist. | The project's actual mission, and **escalation rate is the governing metric** (P1). The cheapest high-information measurement available. Ruling 4 makes it hands-off. | 2–3 w |
| **M3** | **Close oracle Face B**, accepting that **`py.cov.threshold` dies.** | **Nothing adversarial and nothing unattended-in-production ships on a forgeable verdict.** See §2.1. | med–large |
| **M4** | **Provenance store + allowlisted fetch, deny-by-default.** Operator import; allowlisted sources; no general web scrape. | **The panel's strongest unanimity — 5/5, unprompted: provenance BEFORE any media pipeline.** Right-sized per ruling 5: asset tracking and a light audit log, not a consent registry. | 2–3 w |
| **M5** | **Image lane.** Local image generation, inputs only from M4, output credentialing, human approval before first generate. | First visible 1.0 demo: licensed stills in, labelled stills out. Media verdict is the human's (ruling 2). | 2–3 w |
| **M6** | **Short video lane.** Composite M4/M5 stills; one local img2vid that fits after LLM eviction. **DoD in seconds, not "a hunt film."** | Ships the tiger task at honest quality. | 3–4 w |
| **M7** | **Computer-use v0, BLIND.** Existing disposable guest, screenshot to disk, allowlisted apps, operator-written recipes, human in the loop. | Containment proven **before** a second 24 GB tenant exists. **Precondition: measure `ssh -R` under the runner and the reaper** — `KNOWN-OPEN` item 4, currently UNTESTED and NOT AUTHORIZED. | 3–4 w |
| **M8** | **Vision, cheaply.** OCR / UI-parse. **Ruling 8's kill-switch applies: two weeks, then CPU/iGPU, and say so.** | Unblocks M7 without a second heavy tenant. | 3–5 w |
| **M9** | **Bounded within-task planner over a pinned tool catalog.** Not a new FSM. Bounded steps, artifact log, human approval at network / generate / click-outside-allowlist. | **Ruling 1's second tier.** Plain language → clip becomes a product. **All five lineages said do NOT build an elaborate multi-agent planner**, and ruling 1 agrees. | 2–3 w |

### 2.1 THE FORK RULING — recorded because it is the one thing the panel refused to decide

The panel split **2-vs-2** on what comes first and **preserved the split rather than averaging
it** — openai and google put closing oracle Face B first; z-ai and x-ai put *prove one unattended
manufacturing gate and measure escalation rate* first. The synthesis explicitly declined to rule
and referred it up.

> **THE ADVISOR'S RULING: measure manufacturing and escalation (M2) BEFORE the Face B redesign
> (M3) — BUT nothing adversarial and nothing unattended-in-production ships until Face B is
> closed.**

**Why this is not simply picking one side.** It takes z-ai/x-ai's ordering and openai/google's
constraint, and the two are compatible because they were never actually about the same thing. The
*measurement* is safe under an open Face B: `GATE-BUILD-01`'s own PHASE 3 probe is a
non-adversarial, operator-authored task whose forged-verdict blast radius is exactly what the
`GATE-ORACLE-ISOLATION` adjudication bounded — **one tool falsely stamped `COMPLETED`, never escape,
never persistence** — and the compensating control catches it: **a `COMPLETED` artifact is
PROVISIONALLY verified and must be re-verified out-of-band before it is trusted.** What is *not*
safe under an open Face B is shipping. So the ordering is measurement-first and the gate is on
**production and adversarial exposure**, not on measurement.

**The word "adversarial" is doing real work in that sentence and is not decoration.** Face B is a
claim about a candidate that is *trying* to forge a verdict. An operator-authored task is not that.
A cyber-capability task, an unattended production pipeline, or anything taking untrusted task text
**is**, and none of it ships before M3.

**A dependency M3 carries that must not be discovered late:** closing Face B **kills
`py.cov.threshold`** — it does not degrade it, it removes its referent. Every pack, fixture and
gate asserting on it is downstream and must be **re-specified, not merely re-run**. The full trade
is `KNOWN-OPEN` item 16 and it is a ferry decision.

### 2.2 CARRIED, NOT DROPPED — two panel milestones the spine above does not name

Neither is cut. Both already have a home in `KNOWN-OPEN`, and naming that home here is the point:
a milestone that exists in two places under two numbers is a milestone that will be done twice or
not at all.

- **The escalation cost bound is UNSOUND for reasoning models** (panel M4; `KNOWN-OPEN` item 15).
  Measured **8× under** — `openai/gpt-5.6-sol-pro` bounded at `$0.94`, cost `$7.35` — because
  `reasoning.mode: pro` re-bills the prompt across internal passes and **`max_tokens` does not cap
  completion billing.** **This is a PRECONDITION OF M2 BEING TRUSTWORTHY, not a successor to it:**
  M2 measures escalation rate on the path this defect misprices, and a bound that under-reads by 8×
  is not a bound. It is small work and it should land inside M2's window.
- **Long-context correctness is UNTESTED** (panel M5; `KNOWN-OPEN` items 1 and 2). Correctness at
  2k/8k/32k/64k, and **pin `--ubatch-size 512` in the harness** — production pins it explicitly and
  the test harness relies on the default, so **the instrument that decides corruption is the weaker
  of the two surfaces.** It is the precondition for `C-1`, and `KNOWN-OPEN` item 22 records that
  C-1's second precondition **cannot currently be evaluated at all**: the measured correctness
  window is **96 tokens**. **A long-context correctness harness, not a bigger window, is the real
  prerequisite** — and M-scope is what makes the small window survivable in the meantime.

---

## 3. Cut, and deferred

**CUT from 1.0** — the panel's list, **amended by ruling 6**, which removes two items from it:

- ~~Organizing a library by the person depicted.~~ **IN SCOPE per ruling 6** (personal use, legally
  acquired, no distribution).
- ~~Photoreal avatar replacement.~~ **IN SCOPE per ruling 6**, same conditions.
- **General web scrape for "public domain."** Allowlisted sources only. **CUT stands** — it is what
  makes M4's deny-by-default provenance store meaningful.
- **The NPU as a promised tier**, before a userspace hello-world exists. **CUT stands** (ruling 8).
- **`py.cov.threshold`.** Already doomed by the M3 trade — **cut it deliberately rather than letting
  it die by accident.**
- **Unattended cyber capability.** Logged, allowlisted, human-approved VM only. **CUT stands, and
  §2.1's ruling reinforces it**: adversarial capability is precisely what waits for Face B.

**DEFERRED:** long-context correctness beyond what §2.2 measures; Litestream/R2 and snapshot work;
MTP; GPU passthrough; **libvirt as guest supervisor** — z-ai's observation that plain QEMU is the
only exercised path and the `virsh destroy` branch **has never once executed** is corroborated by
rails §13.1, which already tells a gate to launch plain `qemu-system` rather than via libvirtd.

**DO NOT GOLD-PLATE**, named explicitly by the panel, and the first item is a judgement on the gate
that produced this roadmap: another multi-lineage panel before a single frame exists; a *perfect*
Face B; a custom diffusion trainer; a new agent runtime when Goose already reaches the model;
courier support for binary media — **wrong plane: binaries belong in a hash-pinned asset store, not
a text courier.**

**DO gold-plate — the actual moat:** `pins.lock` discipline extended to weights, graphs and
checkpoints; deny-by-default assets; human approval on generate / click / spend; device-by-name
with no silent `llvmpipe`; **out-of-band re-verification of every `COMPLETED` artifact**; and the
live-state discipline itself while 1.0 is being built.

---

## 4. What this roadmap does NOT establish

**Written first, not last, because it is the part most likely to be dropped when this file is
quoted.**

- **NOT ONE PANEL FINDING WAS VERIFIED AGAINST THE CODE.** The panel read a **curated packet**, not
  the tree, and the packet's `ARCHITECTURE.md` and `SECURITY-HISTORY.md` are `GATE-HORIZON`'s own
  prose — **so panel agreement is partly agreement with that gate's framing.** Adopting the
  sequence does not promote any finding inside it from candidate to fact.
- **NO SIZE HERE WAS COSTED ON THIS BOX.** Every duration is the panel's rough consensus. The one
  end-to-end estimate — **~4–6 months to an honest 1.0** — is x-ai's, assumes M0 is obeyed, and
  assumes M1 and the long-context work do not fail. **If the 27B cannot plan reliably, the panel's
  stated fallback is a planner-on-cloud / executor-local split, and that is a FORK, not a polish.**
- **THE MEDIA ORACLE IS A RULING, NOT A DESIGN.** Ruling 2 says what media assurance *is not* — not
  deterministic, not an AI judge — and names the human as the verdict authority. **What the
  automated scan actually checks, and what the human is shown, is unwritten.** Panel risk 2's
  experiment stands and is cheap: take **one** media output and write down what "verified" means
  for it.
- **RULING 6'S ASSUMPTION IS AN ASSUMPTION.** *"No distribution of real-person deepfakes"* is the
  premise the in-scope decision rests on, and it is stated as a premise so that it can be
  re-examined, not buried so that it cannot.
- **M2 HAS NOT RUN.** `GATE-BUILD-01` PHASE 3 is a **time-boxed probe**, not M2. Whatever it
  measures is a first reading against one small task, and **N=1 licenses no rate** — the error
  `products/queue-health/MANIFEST.json` already names as STOP-27's.

---

## 5. Where this file sits

- It is **not** on any default read path. `docs/PHASE-J-STATE.md` remains the live rail position;
  this is the plan that position is walking.
- It is superseded only by an operator ruling or an advisor adjudication, recorded here **by
  addition** (rails §4) — a plan is corrected the same way a measurement is.
- Its candidate source stays where it is, unmodified, at courier
  `bundles/GATE-HORIZON/CONSOLIDATED-ROADMAP.md`. **This file is not a replacement for reading it**
  where the question is *what did the panel actually say*.

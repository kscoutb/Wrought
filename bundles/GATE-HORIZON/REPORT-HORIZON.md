# REPORT-HORIZON — GATE-HORIZON, 2026-08-31, ATTENDED-DIRECT

Worktree `/home/kalib/review-rc1`, branch `review-fixes`, base `54f7786`. A **review gate**: no
`bin/` or `src/` code written, no system behaviour changed, no unit restarted.

**Headline.** Both review streams came back and are published. The oracle-invariant wording is
stabilized. **But the most transferable thing this gate produced is not the roadmap — it is that
SIX of its own instruments were defective, and every one was caught by RUNNING it rather than
reading it.** Three came in with the prompt (§3); **three more were in tooling this gate wrote
itself** (§4) — including a groundedness checker that **penalized the correct answer** and a
negative control that **could not fail**. That is rails §18 six times in one session, in a gate that
had read §18 before it started.

**The uncomfortable part, stated plainly because it is the finding:** every one of the six printed
success. Not one announced itself. The appendix reported `summarized 3/3 files` over three empty
files; the checker reported a clean green from a control that tested an absent token; the packet
sizing looked fine until a real tokenizer was asked. **A gate that had trusted any exit code, any
"N/N", or any green would have shipped all six.**

---

## 1. What was stabilized (PHASE 1)

`docs/PHASE-J-STATE.md`'s `NON-CLAIMS` now opens with the honest one-sentence invariant, by
addition above everything it does not replace:

> **`COMPLETED ⟹ the oracle passed` holds against escape and persistence (Faces A, C) but NOT
> against an adversarial candidate forging its own in-process verdict (Face B).**

With it, the **compensating control** — *a `COMPLETED` artifact is PROVISIONALLY verified and must
be re-verified out-of-band before it is trusted or shipped* — and `KNOWN-OPEN` item 16's real fix
and real cost: candidate tests must run **out of the reporting process**, which **eliminates
`py.cov.threshold` entirely**, because in-process coverage measures the process it runs inside.
**The oracle can have a coverage threshold or an unforgeable verdict, not both in one process.**
Referred to the ferry as a stated trade; this gate takes no position on it.

`DO NOT TAG review-rc3` still stands. Nothing here lifts it.

**PHASE 0** recorded `GATE-ORACLE-ISOLATION` as **ACCEPTED** — extracted mechanically (`sed -n
'41p'`), `diff` empty, negative control run, bundle re-verified **17/17**, base confirmed as
`54f7786^1`. The prompt's *"manifest begins 33291886"* is the **sha256 of `SHA256SUMS` itself**,
not its first entry (`1343ee10`); recorded so a later session does not read a drift that is not
there. **A defect in this gate's own proof:** the first negative control tested a token absent from
the row, so it was a no-op returning a meaningless green. Re-run with a token that is present.
**A control that cannot fail is not a control** — and that one could not, for about ninety seconds.

## 2. Transport — the 13th miss in 14, and the second actually damaged

The paste lost **8,063 bytes**: both appendices, the full source of the two scripts the prompt
itself calls authoritative. The prompt **declared no block count** and carried **zero indented
blocks**; the operator's file carries **57**. Rails §7 prescribes precisely the countermeasure that
would have caught this — literals in indented blocks, a declared count checked first — and it has
now paid for itself twice in four days.

Both copies archived under their own names (rails §4 — evidence is never overwritten, and a
repaired prompt does not erase the record of having been broken):

| file | bytes | sha256 |
|---|---|---|
| `prompts/GATE-HORIZON-v1.0.md` (authoritative) | 21,817 | `f99a11ba…9cc9259` |
| `prompts/GATE-HORIZON-AS-PASTED-DAMAGED.md` | 13,754 | `a5d735ae…8bd4b389` |

Negative control discriminates: prior archived prompts still return their own declared counts
(25 / 48 / 42).

## 3. The three defective instruments THAT CAME WITH THE PROMPT

**Every one printed success.** This is the section worth carrying forward. The other three — all in
tooling this gate wrote itself — are in §4.

**(1) Appendix B returns EMPTY summaries and exits 0.** The served profile is `--reasoning on
--reasoning-budget 24000`; the appendix passes `max_tokens=512`. The model spends the entire budget
on reasoning and returns **zero content** — while printing `summarized 3/3 files` and exiting 0.
Run as written: **3 files, 3 empty.**

| `max_tokens` | `finish_reason` | completion tokens | reasoning | **content** |
|---|---|---|---|---|
| 512 | `length` | 512 | 2,069 B | **0 B** |
| 2048 | `length` | 2,048 | 8,256 B | **0 B** |
| 25000 | `stop` | 2,254 | 8,230 B | **637 B** |

Three minimal deviations applied, documented in the file's own docstring; **Appendix B is kept
verbatim alongside** as `run-local.py.appendix-verbatim`.

**(2) The packet does not fit the box's own model.** Measured with the served tokenizer
(`POST /tokenize`), and `n_ctx` read from `GET /v1/models` — neither estimated:

| artifact | chars | **real tokens** | fits 65,536? |
|---|---|---|---|
| `PACKET.txt` | 233,003 | **70,810** | **NO** — before any room to answer |
| `PACKET-LOCAL.txt` | 107,423 | **34,032** | yes, ~31,100 left for output |

**The system's own live state documentation exceeds what its resident model can read in one pass.**
A usable packet was built by dropping **whole blocks** — never rewriting — with every cut recorded
in `packet/PACKET-PROVENANCE.md`. Also measured: `pins.lock`'s
`input_token_estimator_chars_per_token: 3.0` is a **cost estimator, not a tokenizer** (real: 3.16
and 3.29), so it **under-reads** and a gate sizing a prompt with it will overshoot the window. Now
`KNOWN-OPEN` item 22.

**(3) Appendix A selects panelists by SHORTEST SLUG.** `pick_models()` sorts by
`("pro" in s or "thinking" in s or "reasoning" in s, len(s))` — so *"prefer non-`-pro` variants"* is
implemented as *"prefer the shortest slug"*. For google it selected **`gemma-3-4b-it`, a 4B model**,
to perform a staff-level architecture review. Its output is **confabulated**: it reports media
generation, library organisation, avatar replacement and a screenshot-plus-vision loop as
**working**, against a packet stating *"Media generation / vision / computer-use — **Nothing. No
component of any kind**."* **It read the VISION wish-list as the as-built inventory.** Excluded from
the synthesis and **named**, with the contradiction quoted. Separately `deepseek/deepseek-r1`
**hard-failed 400** — 64,000-token endpoint, ~99,760-token request. **Neither loss was a bad review:
one was a bad pick, one a bad fit, and the script caused both.**

## 4. The local stream — REPO-MAP timing and reliability

**PHASE 2 ran the resident 27B over every script under `bin/` and every module under `src/` —
127 files, air-gapped, sequential (`--parallel 1`), reasoning ON, at zero marginal cost.**

| | |
|---|---|
| Files summarized | **127 / 127** |
| Wall clock | **132 minutes** |
| Rate | **~64 s/file** overall; ~67 s/file steady-state |
| Marginal cost | **$0.00** |

The rate was depressed mid-run because PHASE 4b's baseline call contended for the single serving
slot — the server is `--parallel 1`, so the two jobs interleaved rather than ran in parallel. **The
thinking-ON choice is what makes this 132 minutes rather than ~21**: measured on one file, thinking
OFF took 3.4 s and thinking ON took 61.5 s. That was the operator's explicit trade and it is
recorded as one.

**Groundedness — and the number moved three times, because the INSTRUMENT was wrong twice more.**
All three readings are kept (rails §4: corrected by addition, never overwritten):

| reading | RELIABLE | UNRELIABLE | NO-SOURCE | % of checkable | identifiers grounded |
|---|---|---|---|---|---|
| **v1** as first run | 110 | 5 | 3 | 95.7 % | 1115/1202 = 92.8 % |
| **v2** two fixes | 112 | 1 | 0 | 99.1 % | 1110/1151 = 96.4 % |
| **v3** final | **113** | **0** | **0** | **100.0 %** | **1102/1135 = 97.1 %** |

**The two further defects, both in this gate's own tool, both found by reading what it accused:**

1. **The path decoder was lossy and silently mislabelled three real modules `NO-SOURCE`.** The
   encoding `"/" → "__"` collides with every dunder filename:
   `src/wrought_verifier/__init__.py` encodes to `src__wrought_verifier____init__.py`, which decodes
   back to `src/wrought_verifier//init/.py` — not a file. Fixed by **not inverting a non-invertible
   encoding**: encode each path forward from the original file list and match. Exact by
   construction.
2. **THE CHECKER PENALIZED THE CORRECT ANSWER.** For a shell script with no functions, the honest
   summary is *"Key functions: None; operates as a linear bash script without named functions"* —
   and the extractor read `operates`, `linear`, `without`, `named` as **claimed identifiers**, found
   them absent, and marked the summary UNRELIABLE for fabrication. It did this to 5 summaries and
   **every one of them was right.** The clinching case was `bin/make-review-bundle-20`, scored 0.56:
   every identifier it actually claimed is in the file (`ZIP` 7 hits, `STAGE` 18, `BASE` 6, `trap`
   1), while all four "invented" tokens are English prose with **0 hits each**. **A groundedness
   check that punishes "there are none here" measures fluency, not honesty.**

**THE CAVEAT THAT TRAVELS WITH THE 100 %, and it is not a small one.** That figure is
**post-correction**, and the instrument was corrected **three times, every time in the direction
that raised the score.** That is the exact shape of an instrument fitted to its data, and it should
be read with suspicion even though each fix was forced by a demonstrated false positive with
evidence rather than by the number being unsatisfying. **The defensible claim is the narrow one:
after correction, no summary falls below the 60 % threshold — but 33 individual identifiers out of
1,135 are still ungrounded, so the check is not reporting a clean sweep at the identifier level.**
14 summaries remain `UNCHECKABLE` (too few citable names for a ratio to mean anything); they are
carried with that label, since excluding honest summaries over an instrument limit would bias the
map toward whatever the checker parses well.

`REPO-MAP.md` is **89,099 B**, carrying 113 RELIABLE and 14 UNCHECKABLE summaries, 0 excluded.

The groundedness check is **fabrication-only** and says so in its own output: identifiers a summary
cites are grepped against the file summarized. **`RELIABLE` means *not obviously fabricated*, never
*correct*** — a summary can cite exclusively real names and still describe them wrongly.

**A defect in the checker, corrected by measurement rather than left standing.** Its first version
extracted only backticked identifiers, leaving 8 of the first 14 summaries `UNCHECKABLE` — it would
have reported a rate over a **biased half** of the sample. Widened to the labelled `Key functions`
line, which is the sharpest fabrication test available; deliberately still **not** parsing the
imports line, whose generic tool names and sysfs paths prove nothing by their absence. `UNCHECKABLE`
is also kept **distinct** from `UNRELIABLE`: one is an instrument limit, the other a finding, and
merging them would bias the map toward whatever the checker happens to parse well.

## 5. Packet

| member | bytes | provenance |
|---|---|---|
| `VISION.md` | 1,891 | verbatim from the prompt, `sed`-extracted, `diff`-proven byte-identical |
| `ARCHITECTURE.md` | 13,192 | **written by this gate**, curating the repo-map |
| `SECURITY-HISTORY.md` | 8,302 | **written by this gate** |
| live state + `pins.lock` | 210,387 | verbatim |
| `PACKET.txt` | **233,003 (70,810 tokens)** | concatenation, sent to the panel |
| `PACKET-LOCAL.txt` | 107,423 (34,032 tokens) | trimmed for the resident model, cuts recorded |

No raw local-model summary was shipped to any reader, as the prompt requires.

## 6. Panel roster, ZDR, and spend

**ZDR was checked two ways on every call** — pre-flight membership in `GET /models?zdr=true`, and
router-side enforcement via `provider.zdr=true` + `provider.data_collection="deny"`, so a non-ZDR
endpoint is refused rather than silently substituted. **The key existed only inside the HTTP
`Authorization` header**, read from the service-private `$CREDENTIALS_DIRECTORY` tmpfs — never an
argv, never an env value, never written, never printed.

| lineage | model | ZDR | in / out | cost | carried? |
|---|---|---|---|---|---|
| openai | `gpt-5` | ✅ | 65,994 / 7,177 | $0.1543 | **yes** |
| z-ai | `glm-5` | ✅ | 66,449 / 13,549 | $0.1098 | **yes** |
| x-ai | `grok-4.6` | ✅ | 67,292 / 9,847 | $0.1935 | **yes** |
| google | `gemini-3.1-pro-preview` | ✅ | 73,481 / 4,095 | $0.1961 | **yes** (top-up) |
| deepseek | `deepseek-v4-pro-0813` | ✅ | 68,223 / 6,902 | $0.1174 | **yes** (top-up) |
| google | `gemma-3-4b-it` | ✅ | 73,415 / 1,788 | $0.0038 | **NO — confabulated** |
| deepseek | `deepseek-r1` | ✅ | — | $0.0000 | **NO — HTTP 400, 64k endpoint** |

**GRAND TOTAL `$0.7749` of the `$15.00` the operator authorized — 5.2 %.** Key
`limit_remaining` was $21.18 at the first run's start. The top-up ran under its own **$5.00**
ceiling and used slugs taken from the **live ZDR listing** — nothing invented — both with ≥1M
context, so the full packet fit and no trimming was needed.

**A note on the cost bound, because `KNOWN-OPEN` item 15 predicted trouble here.** Every pre-call
bound held this time (google bounded $0.36, actual $0.1961; deepseek bounded $0.08, actual $0.1174
— *over* its bound, in the same direction item 15 warns about, though trivially). Item 15's measured
8× failure was on a `-pro` reasoning model at much larger output. **This run does not vindicate the
bound; it did not stress it.**

## 7. The local baseline's gist

The resident 27B, air-gapped and free, produced a **13,215 B** structured gap analysis on the
trimmed packet. **It is not counted as a peer vote** — it is one model on the box reading a smaller
packet. But it did real work, and two things are worth recording:

- **It correctly reported "Nothing. Zero media models, pipelines, or tooling"** where nothing
  exists — the exact distinction the 4B panelist failed to hold.
- **It independently identified the VRAM co-residency blocker**, citing ~5.7 GB headroom after the
  27B loads, against this gate's own measurement of **5,842 MiB free** — converging with a paid
  frontier lineage that raised the same point.

Its own hardest-gap picks were coherent: context/token explosion across multi-step tasks, VRAM
contention, automated licence verification at scale, round-trip latency in a vision loop, NPU
userspace immaturity, and the manual adjudication cost of the gate protocol.

**For the gate's stated purpose — proving the local model can carry real work — this is a pass.**
It summarized 127 files and wrote a coherent architecture review, for $0.00, with no network.

## 8. My own cost — the context-scaling datapoint

**Approximate, and the approximation is stated rather than hidden.** This session's context
window rolled over once, so the figure is the sum of two windows and the per-phase split is derived
from observed checkpoints and turn counts, not from an authoritative meter. **The box cannot read
its own `verdict.json` here — there isn't one; this is an attended session, not a runner child.**

| Phase | ~turns | ~tokens | note |
|---|---|---|---|
| Orientation (rails, state doc, QUEUE, courier) | 8 | ~120 k | reading 43 KB of rails + 80 KB of state doc dominates |
| 0 — adjudication, QUEUE surgery | 8 | ~90 k | |
| 1 — invariant restatement | 4 | ~35 k | |
| 2 — tooling, smoke tests, groundedness, assembly | 16 | ~110 k | includes 3 rounds of instrument correction |
| 3 — packet assembly and measurement | 7 | ~70 k | |
| 4 / 4b — panel, top-up, baseline | 12 | ~140 k | reading 5 external reviews is most of this |
| 5 — consolidation | 6 | ~85 k | |
| 6 — research questions | 2 | ~25 k | |
| 7 — wind-down, bundle, report | 12 | ~75 k | |
| **TOTAL** | **~75** | **~750 k** | across two context windows |

**What this number is not.** It is the *whole session*, including reading the rails
(43 KB), the state doc (80 KB), the queue, five external reviews and the local baseline. **It is not
comparable to a runner gate's `verdict.json` cost**, which is a fenced child with a fresh context;
this session is attended, long-lived, and read far more than a gate child ever would. It is offered
as a datapoint about **this shape** — one long-lived agent orchestrating two model streams — which
is the shape the 1.0 vision proposes, and which is why the prompt asked for it.

**The honest observation for the 1.0 question:** the expensive part was not the delegation. The two
model streams cost **$0.77 and $0.00**. The expensive part was **me** — reading state, checking
instruments, and writing prose. Any 1.0 that puts an agent in this seat inherits that cost, and
`KNOWN-OPEN` item 22 says the state it must read already exceeds the local model's window.

## 9. Strongest cross-lineage agreement — data for the advisor, not an adjudication

**Five of five, independently and unprompted**, converged on: **provenance and licensing must be
built BEFORE any media pipeline, deny-by-default**; **defer the NPU** (no userspace stack exists);
**the gate protocol's discipline scales but its cost does not** (all five anchored on the same
measured 99.8 %-of-cap doc-only gate); **cut real-person likeness work from 1.0**; and **do not
build an elaborate multi-agent planner** — a single agent over a pinned tool catalog is enough.

**But the strongest agreement is not the most important finding, and the advisor should weight this
accordingly.** The finding that reshapes the project's understanding of itself arrived from **two
lineages independently**, and neither is a majority vote: **google** — *"You cannot `pytest` an AI
video of a tiger hunting a polar bear"* — the deterministic oracle, this project's entire assurance
argument, **has no media analogue**; and **deepseek**, closing that loop — a media oracle that is
itself a model is *"a reporter that shares the defendant's epistemic status."* **The obvious fix
reproduces Face B exactly**, in a new subsystem, before a line of media code is written. Together
they say **1.0 is not the foundry plus media tools; it is a second assurance model.** `deepseek`
separately named the layer nobody else did: **there is no task decomposition layer** — the gate
protocol assumes a prompt author already decomposed the work, which the advisor and operator do by
hand, every gate, and which the vision hands to the agent.

**A 2-vs-2 split is PRESERVED, not averaged:** `openai`/`google` put closing the oracle first;
`z-ai`/`x-ai` put *prove one manufacturing gate unattended and measure escalation rate* first,
because **Face B is contained today while the governing metric is not measured at all.** Both are
defensible from the same packet. **The advisor should rule; this gate deliberately does not.**

## 10. Rails compliance and housekeeping

- **Byte freeze:** `raw/00` vs `raw/99` — see §11. `raw/00` was **identical to
  `GATE-ORACLE-ISOLATION`'s `raw/00`**, so the store had not moved since that gate closed.
- **Rails §5.1:** the committed scan was run before **every** commit and **every** push, and over
  the whole courier tree before the bundle push. **PASS exit 0 every time.** Exit 2 was never
  treated as a pass and none was manufactured.
- **Rails §13/§15 — a leak, recorded not glossed.** A tool-call timeout killed my shell while a
  `systemd-run` **service** was running; the service **survived**, exactly as §13.1 describes for
  anything that is not a scope descendant. Torn down **by unit name** — an identity, never a
  pattern. All subsequent long jobs were launched as **named** units for that reason.
- **Rails §17 — BOTH LIVE FILES ARE OVER BUDGET, and the rail requires saying so:**

| file | now | budget | over by |
|---|---|---|---|
| `QUEUE.md` | 29,208 B | ~11,013 | **+18,195** |
| `docs/PHASE-J-STATE.md` | 83,563 B | ~76,072 | **+7,491** |
| **live total** | **112,771 B** | ~87,085 | **+25,686** |

- **§17.1 rule 1 — this gate's own deltas, because a size is unattributable and a delta names its
  author:** `docs/PHASE-J-STATE.md` **+9,243 B**, `docs/GATE-JOURNAL.md` **+11,391 B**,
  `BUILD-JOURNAL.md` **+5,577 B**. The state-doc delta is large for a review gate; it is two live
  blocks (`KNOWN-OPEN` 22 and the `NON-CLAIMS` panel qualifier) plus the invariant restatement the
  prompt mandated. **The narrative went to the journal, not the state doc**, per §11.1.
- **Uncommitted and left alone:** a `.gitignore` line adding `.review/`, pre-existing at session
  start. Not this gate's, not discarded, noted.

## 11. NOT ESTABLISHED — these travel with every result above

- **Not one panel finding was verified against the code.** They read a **packet**, not the tree.
  Every finding is a **candidate**, the same standard this project applied to its own last panel —
  where one lineage was later proven simply wrong on the evidence.
- **The packet is this gate's own prose.** `ARCHITECTURE.md` and `SECURITY-HISTORY.md` were written
  here, so panel *agreement* is partly agreement with this gate's framing. The one panelist that
  disagreed with the packet did so **by confabulating**, which is not the kind of independence that
  helps.
- **Roadmap milestone sizes are the panel's and were not costed on this box.**
- **The local summaries are checked for FABRICATION ONLY.**
- **Nothing here was unattended and nothing exercised the reaper.** A clean run is still not a clean
  reap.
- **The consolidated roadmap is a CANDIDATE for adjudication, not a plan this project has adopted**,
  and no gate should cite it as one.

# REPORT — GATE-NARRATIVE

**Runner-run gate child, UNATTENDED. The THIRD unattended batch and the FIRST gate authorised to
edit prose in the two live state files.** Doc-only: no code edited, no `pins.lock` committed, no
`state/` or `wrought-*` unit touched, no interpreter granted. Byte freeze not attempted — under the
runner it is the runner's duty (rails §2.2). Prompt archived at `prompts/GATE-NARRATIVE-v1.0.md`,
sha256 `bfb29aa0c577f67d7d7d53996c1a5e7941fcac7bdaabd880f46ab5c13b30fe91`.

**TRANSPORT CHECK: PASS, FIRST RUN.** `grep -cE '^    [^ ]' prompts/GATE-NARRATIVE-v1.0.md` → **48**,
expected 48. The tool the check needs was granted, so the child ran the check itself — ruling (4)
honoured end-to-end for the second gate running. All 48 blocks decompose as one contiguous span:
the `PRIOR-ADJUDICATION` block is lines 41–94 and contains **all 48** of them, which is a stronger
result than a bare count — the structure is not merely 48 blocks, it is the *one* block the prompt
says it is.

---

## THE HEADLINE, AND ITS QUALIFIER ATTACHED

**All five phases completed. ZERO hook content denials, including two payloads of roughly 25 KB
each. ONE denial of a different kind, recorded below and not worked around.** The dated closed-gate
narrative is out of the live file: **`docs/PHASE-J-STATE.md` 79,960 B → 59,588 B, −20,372 B,
−25.5 %.**

**The qualifier, stated first because it is the one that matters:** this is a **relocation, not a
saving**. `docs/PHASE-J-HISTORY.md` grew by more than the live file shrank. Nothing was deleted and
nothing was compressed. The only sense in which anything was *saved* is that ~25 KB left the path a
fresh gate must read before it can act.

---

## PHASE 0 — the prior verdict, and the first denial

`bundles/GATE-TRIM/ADJUDICATION.md`, 5,718 B. `QUEUE.md` row flipped to `ADJUDICATED` as the first
courier action, rails §10.

**An attempted improvement on `GATE-TRIM`'s method, DENIED, reported rather than buried.**
`GATE-TRIM`'s finding was that `git mv` keeps archived bytes out of any tool payload, so byte
fidelity becomes a property of the move rather than a claim about transcription. The same principle
applies to a *range inside* a file if the shell can do the copy, so this gate tried:

    grep -A 53 -F "<anchor line>" prompts/GATE-NARRATIVE-v1.0.md >> bundles/GATE-TRIM/ADJUDICATION.md

**DENIED.** Retried once with the trailing `; wc -l` compound removed, to isolate the cause.
**DENIED again.** So the cause is the **shell redirect**, not the compound: `Bash(grep:*)` scopes
the *command*, and a redirect is not part of it.

**This is a PERMISSION-LAYER denial, not a hook content denial, and the two must not be conflated.**
It independently re-measures, on a different binary, what `GATE-J0B-CLOSE` recorded and what is now
archived in `docs/PHASE-J-HISTORY.md`: *a scoped allowlist permits only bare single-command
invocations — every redirect, pipe, `&&` and `;` was denied even when every constituent command was
allowlisted.* That was measured on `sha256sum … > SHA256SUMS`; it is now measured on `grep … >> …`
too. **The rule generalises. The zero-transcription route is closed to any gate fenced this way, and
`git mv` remains the only measured way to move bytes without a payload — which is exactly why
`GATE-TRIM`'s adjudication was right to make it a PATTERN rather than a permission.**

**Fallback, and its proof.** `Read` → `Write` → a **PREDICTED-COUNT** check stated before it ran:
`grep -c -Fxvf prompts/GATE-NARRATIVE-v1.0.md bundles/GATE-TRIM/ADJUDICATION.md` counts lines of the
record appearing nowhere in the carrier. Predicted **18** — the authored header lines, counted in
advance and written into the file before the command ran. **Measured 18. First run.** All 54 verdict
lines are byte-faithful. **Negative control on the same command form against the WRONG carrier
(`prompts/GATE-TRIM-v1.0.md`): 110.** The check is sensitive; 18 is a match, not a silent no-op.

---

## PHASE 1 — the three orphans, all three re-homed and verified

Precondition for PHASE 4, and it really was one: the dispatcher's `raw/03` confirmed items 1 and 2
lived at **exactly one line each, both inside the cut, with no live copy anywhere else**.

1. **Leftover `failed` transient scope units** (`GATE-RUNNER-HARDEN` dry run) → **`KNOWN-OPEN`
   item 11**, owner **operator**. Never enumerated by any prompt, so never cleared; clearing them is
   a deliberate operator action, not a gate's.
2. **`P-2`** — may a key carry the escalation-ratified `24000` into the guest-agent path → **`KNOWN-OPEN`
   item 12**, owner **operator**, **with the ruling attached**: ACCEPTED IN PRINCIPLE, and the
   `pins.lock` commit that carries it **stays operator-authored**.
3. **`F-4` as doctrine** → **`docs/EXECUTOR-RAILS.md` §18 — "An exit code is not a success signal —
   verify the WORK PRODUCT"**, citing `GATE-J0B-CLOSE` as instructed. Written as the general rail
   with goose as its measured instance, because that is what makes it a rail rather than a note
   about one binary.

**All three verified readable in their new homes before PHASE 4 moved anything.** No re-home was
denied, so the HALT condition never armed.

---

## PHASE 2 — two stale passages struck BY ADDITION (rails §4), originals preserved

1. **`DIRECTLY FOR A GATE CHILD READING THIS`** — struck. Stale on fact (`GATE-RUNNER-POLISH` made a
   bare `Bash` entry halt the runner **unconditionally**, so the escape hatch it points at cannot
   exist), and **backwards on doctrine**, which is the worse half: it teaches a fenced child to go
   looking for a way around its fence. **Replacement, in substance as the prompt specifies it: if a
   gate needs a tree its `ADD-DIRS:` does not name, it HALTS AND REPORTS — a child never widens its
   own grant.** Original text preserved immediately below the strike.
2. **`NEXT ON THE RAIL` / the `GATE-J0B-RESUME` v2.0 blocker block** — struck as stale. It called an
   adjudicated gate `QUEUED, NOT APPROVED`. Replacement points at the archive and at the courier
   rows, and explicitly keeps the B-1/B-3 pre-flight findings as **evidence**, since rails §12/§16
   and `KNOWN-OPEN` item 8 still cite them — they are a record of a pre-flight, not a live blocker
   list. Original text preserved.

---

## PHASE 3 — the phase that matters: the growth rate

1. **`docs/GATE-JOURNAL.md` created** — append-only, one section per gate, **read by nothing by
   default**.
2. **Rails §11.1 — WHERE the wind-down writes.** Narrative → the journal; `docs/PHASE-J-STATE.md`
   updated **only in its live blocks** (rail position, `KNOWN-OPEN`, `REVIEW-READINESS`,
   `NON-CLAIMS`). Where it is genuinely ambiguous the state doc gets **one line and a pointer** and
   the journal gets the full text — deliberately narrower than §17's keep-live rule, because what
   must stay in front of the next session is *that something is there*, not the paragraph that
   establishes it. **PROVISIONAL pending a ferry ruling**, as §17 is.
3. **Rails §17.1 — the budget is a SIZE; the problem is a RATE.** No threshold invented. What this
   gate measured, stated as two observations and labelled as two observations:

   | Event | `QUEUE.md` | `docs/PHASE-J-STATE.md` | Live total |
   |---|---|---|---|
   | `GATE-TRIM` post-split — the §17 budget | 11,013 B | 76,072 B | 87,085 B |
   | after the whole `GATE-TRIM` cycle closed | 16,436 B (+5,423) | 79,960 B (+3,888) | 96,396 B (+9,311) |
   | after the `GATE-NARRATIVE` dispatch row alone, before this gate ran | 23,467 B (+7,031) | 79,960 B (+0) | 103,427 B (+7,031) |

   **The rate: roughly +7 KB to +9 KB of live bytes per gate, dominated by the `QUEUE.md` row, not
   by the state doc.** At that rate `GATE-TRIM`'s −60,729 B cut is **fully regrown in about seven
   gates**. Two observations are not a trend; they are enough to show a size budget is the wrong
   instrument. The rule added is a rate rule: **report the DELTA you added**, narrative goes to the
   journal, and a terminal `QUEUE.md` row is one line.
4. **This gate's own wind-down uses the new rule** — see below.

**A FERRY QUESTION THIS GATE STATES AND DOES NOT RESOLVE, flagged by the dispatcher and confirmed
from disk.** `BUILD-JOURNAL.md` is **already** an append-only journal — 670,300 B, and already off
the Phase-J default read path, since CLAUDE.md points Phase J at `docs/PHASE-J-STATE.md`. Whether
this project wants **two** append-only journals or one is a ferry decision. **This gate created
`docs/GATE-JOURNAL.md` as instructed, recorded the overlap in the file itself and in rails §11.1,
and did NOT merge them.** Until there is a ruling, rails §11 step 2 and §11.1 step 1a both stand and
a gate appends to both.

---

## PHASE 4 — the narrative cut

**THE PROMPT'S OWN ~40 KB FIGURE IS STALE, AND THE PROMPT SAYS SO AND ASKS FOR A RE-MEASURE.**
Both numbers, as instructed:

- **`GATE-TRIM`'s estimate: ~40 KB.**
- **Measured here: the six dated closed-gate sections and their subsections are 324 lines and
  ~25.4 KB** — corroborating the dispatcher's independent `raw/03` measurement of **25,331 B** for
  the same range almost exactly. **The ~40 KB figure overstates it by about 58 % and must not be
  quoted forward.**

**Destination checked, not assumed:** `docs/PHASE-J-HISTORY.md` **already existed** (11,783 B,
`GATE-TRIM` created it), so this gate **appended**.

**Method, and it carries two independent proofs.**

1. **Append first**, so nothing was ever at risk, then a **PREDICTED-COUNT** check stated in advance:
   baseline `grep -c -Fxvf docs/PHASE-J-STATE.md docs/PHASE-J-HISTORY.md` = **129** before the
   append; the header authored for the archive is **12** non-blank lines that appear nowhere in the
   state doc; **predicted 141. Measured 141. First run.** Every one of the 324 moved lines is
   byte-identical to a line still standing in the live file at that moment.
2. **Then the cut, as a single exact-match `Edit`.** This is a second and independent proof and it
   is free: `Edit` applies only on an exact byte match, so **a single wrong byte anywhere in 25 KB
   and the cut would not have applied.** It applied.

   Line-count arithmetic closes the loop: the archive went 164 → 508 lines, **+344 = 324 moved +
   20 authored**, exactly as predicted.

**A pointer stub replaced the cut**, per §17 constraint 3, saying in terms that it is a pointer and
not evidence, naming where the material went, naming the three re-homes, and saying why this cut
differs from `GATE-TRIM`'s.

### THE REFUSED-BLOCK LIST — and it has one entry, which is not the kind that was expected

**ZERO hook content denials across the whole gate.** Every `Edit` and `Write` in PHASES 0–4 was
allowed, including the two ~25 KB payloads that carry the whole moved range. The dispatcher's `raw/02`
predicted exactly this for the cut range — that all 13 sections DEFER on both the cut and the append
— and **the prediction held.**

The single denial is PHASE 0's shell redirect, above. It is a **permission-layer** denial, not a
content denial, and it is listed here because the prompt asked for refusals as a first-class result
and this is the honest content of that list.

### WHAT WAS DELIBERATELY NOT MOVED, and why — this is a scope decision, not a denial

**The two `DISPATCHER ADDENDUM` sections were NOT moved.** They are now at
`docs/PHASE-J-STATE.md` **L566–627** (`GATE-CONSOLIDATE`, ~5.0 KB) and **L628–677** (`GATE-TRIM`,
~4.0 KB) — the dispatcher measured the pair at **8,909 B**, which is the difference between the
"core" reading of dated narrative (25.3 KB) and the "widest" reading (34.2 KB).

**They are in scope on a reasonable reading and were left for budget, stated plainly rather than
quietly dropped.** Moving each costs three turns and two payloads; with the mandated wind-down still
to fund, this gate chose to protect the deliverables. **The decision is the advisor's to reverse and
it is cheap for the next gate to finish** — the method is proven and the range is identified.

**One prediction therefore remains UNTESTED, and it must not be reported as measured:** the
dispatcher predicts the `GATE-CONSOLIDATE` addendum will be **DENIED in both directions** on
pattern 4. That prediction was derived by importing the patterns from the hook source itself and
simulating, which is strong — but **this gate did not attempt the payload, so the prediction is
corroborated by simulation and not by a live denial.** The `GATE-TRIM` addendum is predicted clean.

---

## THE BYTE TABLE, BEFORE AND AFTER

| File | At dispatch | At wind-down | Change |
|---|---|---|---|
| `docs/PHASE-J-STATE.md` | 79,960 B | **59,588 B** | **−20,372 B, −25.5 %** |
| `docs/PHASE-J-HISTORY.md` | 11,783 B | **38,168 B** | +26,385 B |
| `docs/EXECUTOR-RAILS.md` | 38,569 B | **44,486 B** | +5,917 B (§11.1, §17.1, §18) |
| `docs/GATE-JOURNAL.md` | — (did not exist) | **2,390 B + this gate's section** | new |
| `QUEUE.md` | 23,467 B | 23,695 B + a deliberately short `BUNDLED` row | + |
| **LIVE TOTAL a fresh gate must read** | **103,427 B** | **83,283 B** + that row | **−20,144 B, −19.5 %** |

**The within-gate movement is worth stating because it is not monotonic.** PHASES 1 and 2 *grew*
the state doc by **+3,191 B** — re-homes are additions and rails §4 strikes preserve their originals
— taking it 79,960 → 83,151 B. PHASE 4 then removed **23,563 B net** of the pointer stub. **A gate
that corrects a record honestly pays bytes for the correction.** That is the cost of §4 and it is
worth paying, but it should be visible rather than netted away.

### §17 BUDGET CHECK, which §17 requires be said out loud

| File | §17 provisional budget | Now | Verdict |
|---|---|---|---|
| `QUEUE.md` | ~11,013 B | 23,695 B | **OVER by ~12,682 B** |
| `docs/PHASE-J-STATE.md` | ~76,072 B | 59,588 B | **UNDER by ~16,484 B** |
| Live total | ~87,085 B | 83,283 B | **UNDER by ~3,802 B** — and the `BUNDLED` row eats into that |

**`QUEUE.md` is now the whole problem and the state doc is not.** That inverts the position
`GATE-TRIM` closed on, and it is the reason §17.1's rule 3 singles out the QUEUE row. **This gate
applied its own new rule to itself: its `BUNDLED` row is deliberately short.** For contrast,
`GATE-TRIM`'s `BUNDLED` row and this gate's own dispatch row are each **several kilobytes of a file
every gate must read**, and the dispatch row was written *before the gate had run*.

---

## THE OPEN QUESTION `GATE-TRIM` LEFT: did the split measurably reduce cost?

**NOT ESTABLISHED — and the more useful finding is that THIS GATE COULD NOT HAVE ESTABLISHED IT.**
The adjudication designates this gate as the measurement. It is the wrong instrument, for three
reasons, all measured rather than argued:

1. **This gate never read `QUEUE.md` whole.** Not once. It located the two rows it needed with a
   single `grep -n` and edited them in place. The split's benefit is only realised by a gate that
   reads the live files whole — **the saving that actually occurred here came from targeted `grep`
   instead of whole-file reads, which is a technique, not the split.**
2. **The "split" state was not the state `GATE-TRIM` left.** `QUEUE.md` had already regrown from
   11,013 B to 23,467 B before this gate started, so even a gate that *did* read it whole would have
   been measuring something 2.1× the size of what was handed over.
3. **This gate's cost is dominated by a one-time 25 KB relocation** — reading the range once and
   emitting it twice, as an append payload and as an exact-match cut payload. **No ordinary gate
   incurs that.** Comparing it to `GATE-CONSOLIDATE` or `GATE-TRIM` compares three different shapes
   of work.

**The measurement that is actually needed is an ORDINARY gate — one that reads the live files to
orient itself and then does unrelated work — not a third consecutive trim gate.** Until one runs,
"41 % fewer bytes on disk is not 41 % less cost" stands exactly where `GATE-TRIM` left it.

---

## COST AND TURNS — with the limit on what a child can report

**≈54 tool calls** to the start of wind-down; **≈$4.58 of the $8.00 cap** on the harness's running
total at that point, final figure in the manifest turn below.

**The child cannot report tokens, and the cost figure it *can* report is not the authoritative one.**
`verdict.json` sits outside this gate's `ADD-DIRS` by design. **The dispatcher must take the real
numbers from the runner** — this recurs from `GATE-TRIM` and is a property of the fence, not an
oversight.

Two of the ≈54 calls were the denied redirect and one was a wrong-path `grep` — the child's own
error: `cd` is granted but the working directory is the courier, and a `docs/` path was passed
unqualified. Cheap, self-corrected in one turn, recorded because the turn count includes it.

---

## OTHER SURPRISES

- **The transport check decomposes better than it was asked to.** All 48 indented lines are inside
  the single `PRIOR-ADJUDICATION` block (prompt lines 41–94: 48 non-blank + 6 blank = 54). A block
  *count* authenticates structure; a block *span* is a stronger statement, and it was free.
- **The predicted-count method transfers cleanly from `GATE-TRIM`'s use to a much larger range.** It
  proved 54 lines in PHASE 0 and 324 lines in PHASE 4, in one command each, with **nothing read
  back**. Paired with `Edit`'s exact-match property it gives two independent proofs of a 25 KB move
  for the price of one `grep`.
- **`Edit`'s exact-match requirement is an under-used verification instrument.** A cut that applies
  *is* a proof that the text was transcribed byte-perfectly. It costs nothing and it fails safe: a
  wrong byte produces a refused edit, never a corrupted file.
- **`git mv` was NOT available to this gate and the reason is worth recording.** The material moved
  is a *range inside* a file, not a whole file, so the pattern `GATE-TRIM` found — and which its
  adjudication correctly made a pattern rather than a permission — does not reach this case. The
  shell substitute for it is a redirect, and the redirect is denied. **A fenced gate has no
  payload-free way to move a range.**
- **The state doc's problem migrated to the QUEUE.** See the §17 table above.

---

## WHAT THIS GATE DID NOT ESTABLISH

- **Nothing about the byte freeze.** Not attempted, no workaround sought (rails §2.2).
- **Nothing about the reaper.** A clean run is not a clean reap. This is the **third** consecutive
  clean unattended run, and three of them do not add up to one exercised reaper. `virsh destroy` and
  the SIGTERM→SIGKILL escalation remain unexercised in production.
- **Nothing about a MANUFACTURING gate unattended.** Doc-only again, so `KNOWN-OPEN` item 10
  (cost-cap RE-CALIBRATION) is **NOT discharged** and still lands at the first runner-run
  manufacturing gate.
- **Whether the split reduces cost.** See above — not established, and not establishable here.
- **Whether the `GATE-CONSOLIDATE` addendum is really hook-denied.** Predicted by simulation from
  the hook's own source; **not attempted, so not measured.**
- **Rails §5.1 is UNDISCHARGED on this push, for the THIRD gate running.** No `Bash(sudo:*)` and no
  `python3` are granted, so the staged-diff secret scan cannot run inside the child. **Exit 2 is
  "could not run", which is not a pass, and none was manufactured.** **No foundry commit was made:
  all `docs/` edits are left UNCOMMITTED in the working tree** for the operator to commit behind a
  real scan, exactly as the last two gates did. The obligation on the courier push falls to the
  dispatcher afterwards. **This is the structural gap the `GATE-TRIM` adjudication proposes moving
  to the runner, and it recurred here unfixed by design — a gate cannot be both fenced and able to
  run its own mandated scan.**

---

## ON THE PROMPT ITSELF

The prompt invited the child to say plainly if any instruction was impossible, self-contradictory,
or asked for a tool it did not grant. **None was.** `Bash(date:*)` was granted this time, so the
heartbeat carries real UTC stamps rather than `GATE-TRIM`'s `(approx)` — ruling (4) applied to the
advisor, and it took.

Two instructions were **correct but not fully executable as scoped**, and both were handled by doing
the lawful thing and reporting it: the ~40 KB figure the prompt itself flagged as possibly stale
(re-measured at ~25.4 KB, both reported), and the two dispatcher addenda, left for budget with the
range and method recorded so the next gate can finish them cheaply.

**One instruction the child could not satisfy in the form it would have preferred**, which is the
PHASE 0 redirect. It was not rephrased to evade the denial. It was recorded with what it refused,
and the fallback was proven instead.

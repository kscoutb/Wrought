# GATE-BUILD-01 — REPORT

**The first BUILD gate.** ATTENDED-DIRECT, worktree `/home/kalib/review-rc1`, branch
`review-fixes`, base `22a0ceb`. 2026-09-01.

**The deliverable is `bin/wrought-scope`**, and the number it exists to produce is this:

> Over 23 committed fixture queries, at the tool's own default cap, a session loads **12.0 files of
> 156** and **66,356 tokens of 624,093** — **13.0× fewer files and 9.4× fewer tokens** than reading
> the indexed tree. Every token count is **measured** by the served `/tokenize` endpoint, never
> estimated.

**TWO READINGS OF THAT NUMBER EXIST AND BOTH ARE KEPT, because the tree moved underneath it.** The
figure above is the tree **as shipped** (`raw/31`), after wind-down committed `bin/wrought-scope`,
`bin/test-wrought-scope` and the edited state docs — 156 indexed files, 624,093 measured tokens
(`raw/32`, the final rebuild after §4.5's failure).
Phase 2 measured **12.8× / 9.3×** on the tree as it stood then (`raw/13`), 154 files and 604,102
tokens. **Neither supersedes the other and neither was edited to match**; each has its own raw
capture with the command that produced it, which is J-95's whole point. The difference is that the
tool now indexes itself.

**Every headline below is followed by what it does not establish.** §7 collects the rest.

---

## 1. What each phase did

| Phase | Outcome | Evidence |
|---|---|---|
| **0** | `GATE-HORIZON` recorded `ADJUDICATED` — **and re-verified against its own bundle rather than believed.** Its terminal `QUEUE.md` row collapsed to one line, full text moved byte-for-byte to `QUEUE-ARCHIVE.md`. | `raw/01`, `raw/02`, `bundles/GATE-HORIZON/ADJUDICATION.md` |
| **1** | `docs/ROADMAP-1.0.md` LOCKED (20,018 B). The operator's eight rulings reproduced as M0; the advisor's M2-before-M3 fork ruling recorded. | foundry `ef0aa8a`, `ROADMAP-1.0.md` in this bundle |
| **2** | **`bin/wrought-scope` built, tested, committed.** Five test arms, all pass. Two defects found in its own ranker by running it. | `raw/10`–`raw/15`, foundry `ae11902` |
| **3** | The M2 probe: `COMPLETED`/`all_pass` **attempt 0, 191 s, `$0.00`** — and **no escalation rate measured**, see §4. | `raw/20`–`raw/25`, foundry `c0a2b6a` |
| **4** | Wind-down: doc edits → index rebuild → test re-run → freeze re-assert → manifest. | `raw/30`, `raw/31`, `raw/99` |

**Sequencing note for Phase 4, because it is a trap this gate walked into deliberately rather than
accidentally:** the wind-down edits `docs/PHASE-J-STATE.md`, `docs/GATE-JOURNAL.md` and
`BUILD-JOURNAL.md`, and the first two are **indexed**. Editing them stales the committed index, so
this gate's own `bin/test-wrought-scope` arm D would fail on the tree as shipped. The order is
therefore **doc edits → `wrought-scope rebuild` → re-run the test → one commit → `raw/99`**. A gate
that ships a tool which validates the repository has to leave the repository valid.

---

## 2. PHASE 0 — the verdict was re-verified, and one result nobody asked for

The prompt said *"re-verify against `bundles/GATE-HORIZON/`"*, so every load-bearing number in the
verdict was checked against the bundle mechanically (`raw/02`):

| Claim | Command | Result |
|---|---|---|
| 168-entry manifest verifies | `sha256sum -c SHA256SUMS` | **exit 0, 168 OK, 0 FAILED** |
| byte freeze HOLDS | `diff` of the 64-hex lines, `raw/00` vs `raw/99` | **exit 0, zero bytes** |
| 127 files summarized | `ls repo-map \| wc -l` vs `wc -l tools/file-list.txt` | **127 and 127** |
| 113 RELIABLE / 14 uncheckable | `groundedness.json` `counts` | **exact match, 127 results** |
| `$0.7749` spend | sum of `usage.cost` over six `*.raw.json` | **`0.7749` exactly** |

**The free result.** `GATE-HORIZON`'s `raw/00` is **byte-identical to this gate's own `raw/00`**,
taken independently a day later. Neither gate can say that alone; together they say the production
store has not moved across two gates and the interval between them.

**Rails §17 applied.** The 4,969-byte `GATE-HORIZON` row moved byte-for-byte to `QUEUE-ARCHIVE.md`
— **proven by `cmp` against `git show HEAD:QUEUE.md`, identical**, not asserted — and `QUEUE.md`
kept a one-line pointer. **QUEUE.md 33,728 → 29,255 B, −4,473.**

---

## 3. PHASE 2 — the deliverable

### 3.1 The load-reduction ratio, which is what this tool buys every future gate

Measured by the committed `bin/test-wrought-scope` over the 23 fixture queries (`raw/13`):

| tree | | files | tokens | vs. the tree |
|---|---|---|---|---|
| **at Phase 2** (`raw/13`) | whole indexed tree | 154 | **604,102** | — |
| | at the test's uniform cap (25) | 22.7 avg | 115,594 avg | 19.1 % |
| | **at `query`'s own default (12)** | **12.0 avg** | **64,779 avg** | **10.7 %** → **12.8× / 9.3×** |
| **as shipped** (`raw/31`) | whole indexed tree | 156 | **623,884** | — |
| | at the test's uniform cap (25) | 22.8 avg | 118,840 avg | 19.0 % |
| | **at `query`'s own default (12)** | **12.0 avg** | **66,329 avg** | **10.6 %** → **13.0× / 9.4×** |

> **13.0× fewer files. 9.4× fewer tokens**, on the tree this gate ships.

The comparand is the summed `/tokenize` cost of every indexed file, and it is **stored in the index
itself** so no ratio here is against an unnamed denominator.

**Sections make it better again where the answer is in a document.** On *"courier transport
rules"*, four files cost 58,343 tokens whole; the named sections inside them cost **25,601**
(`raw/14`). `docs/EXECUTOR-RAILS.md` is 12,293 tokens; the three sections that answer that query
are §7 *Prompt transport* (195), §8 *Courier* (159) and §9 *Heartbeat* (442).

### 3.2 Token costs are MEASURED, and `rebuild` refuses to guess

`rebuild` **will not run** without the served tokenizer; it exits 1 with the reason (`raw/14`).
Measured on this corpus (`raw/15`):

| | bytes | measured tokens | chars/token |
|---|---|---|---|
| whole corpus | 2,185,638 | 604,102 | **3.618** |
| python (95) | 1,350,313 | 366,098 | 3.688 |
| shell (32) | 173,930 | 55,641 | 3.126 |
| markdown (26) | 657,134 | 180,954 | 3.631 |

**`pins.lock`'s `input_token_estimator_chars_per_token: 3.0` OVER-READS this corpus by 20.6 %** —
728,546 estimated against 604,102 measured. It is a **cost** estimator, deliberately conservative
about money, and not a tokenizer. `GATE-HORIZON` measured 3.16 and 3.29 on its packet payloads;
this gate measures 3.62 on 154 code and doc files. **Both are above 3.0 — the same direction, a
different magnitude, because the payloads differ.** Neither reading licenses changing the pin.

### 3.3 TWO DEFECTS IN THIS GATE'S OWN RANKER, BOTH FOUND BY RUNNING IT

This is the part worth reading.

**(a) Markdown headings were scored as code symbols**, at the full `W_SYMBOL` weight. A
40-heading journal that merely *says* "oracle" in a heading outranked the module that *implements*
the oracle's verdict. Headings are a real signal, so they now have a field of their own at a lower
weight — and `wrought-scope symbol` searches code symbols only, which is what it always claimed.

**(b) THE ANSWER MOVED BETWEEN RUNS.** `expand()` iterated a **set** of vocabulary terms and
truncated the result at 12, so which expansions survived depended on the process's string hash
seed; the second graph round then seeded differently among tied scores. **Measured before the fix:
the same query, the same index, the same tree returned between 61,431 and 82,262 tokens across
eight `PYTHONHASHSEED` values.** Every such iteration is now sorted, and **arm E** of the committed
test asserts the property across four seeds rather than leaving it to a comment.

It was found because a fixture line printed 141,157 tokens on one run and 156,433 on the next, in
the same session, and that was read rather than shrugged at.

### 3.4 The ranking was tuned by measurement, and the losing variants are recorded in the code

| variant | worst must-include rank | mean rank | in top 10 |
|---|---|---|---|
| text only (BM25 + coordination + test demotion) | 32 | 4.15 | 30/34 |
| **+ import graph, 2 rounds, `src`-restricted refs (SHIPPED)** | **22** | **3.21** | **33/34** |
| + unrestricted "file names another file" edge | 40 | 5.75 | 17/20 |
| + package-sibling edges | 36 | — | pushed `bin/escalate-once` from rank 2 → 7 |

**The unrestricted reference edge and the package-sibling edge were both built, both measured, and
both removed** — a document most of the tree mentions becomes everything's "dependency", and
sibling edges pull whole packages in ahead of real answers. The chosen parameters sit in the
**middle of a stable plateau** (rounds=2, seeds 4–6, discount 0.20–0.30 all give worst 21–26) rather
than at the argmax (rounds=3 touched worst=13 but swung to 26 on a one-step parameter change).
**23 hand-made fixtures do not justify a knife edge.**

### 3.5 One fixture was wrong, and the tool was right

*"offline wheel install and supply chain"* named `bin/secpack-fetch`, which pins security **tools**.
`bin/secpack-freeze` is the file that freezes the offline **wheel set**. The tool ranked the right
file **5th** and the wrong one **24th**. The fixture is corrected and **the original error is on the
record in `index/scope-fixtures.json`**, not quietly repaired.

### 3.6 The test

`bin/test-wrought-scope`, five arms, **all pass** (`raw/13`): retrieval (34/34 must-includes inside
a uniform cap; **33/34 inside the default 12**), symbol (12/12), rebuild stability (two rebuilds
**byte-identical**, *and* the committed index matches a fresh rebuild), index/tree sync (0/0/0),
hash-seed determinism (4 queries × 4 seeds). **A skipped arm prints, and `--require-all` turns it
into exit 2** — an arm that did not run has proven nothing, which is rails §5.1's rule wearing a
different hat.

---

## 4. PHASE 3 — the M2 manufacturing probe

### 4.1 The probe ran with escalation STRUCTURALLY OFF, and the reason is a rails §2 collision

**Found by reading the code before launching, not by tripping it** (`raw/20`):
`ledger.authority()` resolves the spend authority to `pins.lock`'s `db_path`, which is
**`/var/lib/wrought/state/orchestrator.db` — the byte-frozen production store.**
`bin/manufacture`'s own docstring calls the ledger row *"the one production write this run is
allowed to make"*. For a normal manufacturing run that is correct and intended. **For this gate it
would have moved `raw/99` and turned the gate's own byte freeze into a rails §2 STOP EVERYTHING.**

So the probe ran `--no-escalation`: `esc_key` is `None`, `escalate.read_credential` is never called,
no OpenRouter credential was loaded, and **no cloud call was made. What is measured is escalation
PRESSURE — attempts used against the repair cap — and not escalation SPEND.** Said plainly here
rather than reported as a comfortable "0 escalations".

### 4.2 What the probe measured

**`COMPLETED`, `all_pass`, ON THE FIRST ATTEMPT, IN 191 SECONDS, FOR `$0.00`.** The verdict was
**sourced by the worker from its own oracle** — `worker.run(verifier=oracle.oracle_verdict)`, no
`verdict_script` supplied and none possible. That is STOP-33b's production path.

| | |
|---|---|
| final state | **`COMPLETED`** |
| oracle verdict | **`all_pass`** |
| attempts used | **1** of a repair cap of **3** |
| escalated | **False** — and the tier was off, see §4.1 |
| wall clock | **191.0 s** (generation 190.09 s, verification 0.86 s) |
| checks | ruff **PASS**, basedpyright **PASS**, pytest **29/29**, coverage **0.9825** vs a pinned 0.85 |
| tokens | 1,593 in / 6,917 out at **36.4 t/s**, `finish_reason=stop`, 21,468 reasoning chars |
| spend | **`$0.00`**, 0 ledger rows, 0 substrate incidents |
| unit | `Result=success`, `ExecMainStatus=0` — read from systemd, not inferred from a log tail |

**DID IT PRODUCE REAL MULTI-LINE CODE, OR A STUB?** Real code: **145 lines, 5,132 bytes**, a module
docstring and a full Args/Returns/Raises docstring on the public function, structural validation
cleanly separated from drift detection, and the `bool`-is-not-an-`int` boundary handled correctly.
**The module ships verbatim in `raw/23` and in this bundle** so a reader can judge it rather than
take this paragraph for it.

**AND ON ITS FIRST CONTACT WITH REAL DATA IT FOUND REAL DRIFT.** Pointed at the actual index and the
actual tree — data neither its spec nor its all-synthetic test suite ever mentioned — it reported
**2 × `MISSING_FROM_INDEX`**, correctly: `bin/wrought-scope` and `bin/test-wrought-scope` had been
committed *after* the index was last built, and the index is derived from `git ls-files`. **The tool
manufactured to check the index found the index stale, in the same session that built both.** A
planted-drift arm then confirmed it is not a function that always says "clean": four planted drifts,
four kinds detected, correctly ordered, inputs unmutated.

**OUT-OF-BAND RE-VERIFIED (the Face B compensating control).** The graded envelope says all four
checks passed — and that envelope is written by the process being judged, which the envelope itself
admits, carrying `evidence_provenance: "self_reported -- candidate code executes in the reporting
process (F-1 Face B, OPEN)"`. So all four were re-run in a **different process, from a different
directory, driven by this session**: pytest **29/29**, ruff **clean**, basedpyright **0 errors under
the pack's own `typeCheckingMode=standard`**, coverage **98 %**. The staging receipt `9e2200f8…`
agrees on **all three surfaces** — the `TRANSITION:all_pass` event payload, the job's `staged.json`,
and `sha256sum` of the file.

**One discrepancy appeared and it is a config mismatch, not a forged verdict — recorded because the
flattering reading would have been to omit it.** The first out-of-band `basedpyright` run supplied
**no config** and reported **3 errors and 35 warnings**; the pack generates
`{"typeCheckingMode": "standard"}` (`packs/py.toml:32`) and basedpyright's own default is stricter.
Re-run with the pack's config: **0 errors, 0 warnings**, matching the envelope's `metric_value: 0`.
**Both readings are on the record.** The stricter one is a fact about the module's typing, not about
the verdict, and the pinned gate is `standard` by pack design.

**PRODUCTION UNTOUCHED, PROVED RATHER THAN PROMISED** (`raw/24`). The probe's own freeze bracket —
`raw/20` before, `raw/24` after — **diffs to zero bytes**, and the production store holds **0 rows
matching this task on three separate predicates**. **Nothing the gate started outlived it**
(`raw/25`): the transient unit was stopped and unloaded by name, and a `/proc/<pid>/exe` scan finds
no survivor.

The artifact is registered at **`products/scope-lint/`**, which it earns under
`products/README.md`'s single admission rule.

### 4.3 THREE OF THIS GATE'S OWN VERIFICATION CHECKS WERE DEFECTIVE

Corrected **by addition**, never edited out (rails §4):

1. **A planted-drift arm crashed** with `KeyError: 'bin/wrought-scope'` — and **the crash was the
   finding**, because the key it could not find was one of the two files the index was missing.
2. **Two SQL queries named a column and a table that do not exist** (`events.task_id`, `ledger`;
   the real names are `events.stream_id` and `escalation_ledger`). They returned **error strings
   where a reader scanning the column would see zeros.** An error string is not a zero, and a check
   that could not run has proven nothing — rails §5.1's exit-2 rule wearing a different hat.
3. **A survivor scan used `pgrep -x`** on `qemu-system-x86_64`, which is longer than the kernel's
   15-byte `comm` (pgrep printed its own refusal), and on `manufacture`, whose process `comm` is
   `python3` because of its shebang — **that one would have said "none" with the process running.**
   Redone by resolving `/proc/<pid>/exe`, the identity match rails §13's reaper was rewritten to use.

---

## 4.5 THE LAST CHECK BEFORE DECLARING DONE FAILED, AND KEEPING IT IS THE POINT

`raw/31` ran `bin/test-wrought-scope` after the wind-down rebuild and it **passed**. This session
then appended a correction-by-addition to `docs/GATE-JOURNAL.md` and `BUILD-JOURNAL.md` — recording
that the headline number had moved — and committed. **`docs/GATE-JOURNAL.md` is indexed.** A final
re-run before declaring the gate done therefore failed:

    D. SYNC — the index describes the tree it claims to
      FAIL  1 indexed with a stale hash: ['docs/GATE-JOURNAL.md']

**This is the exact trap §1 of this report describes, in the sentence *"a gate that ships a tool
which validates the repository has to leave the repository valid"*, written about an hour before it
was sprung.** The rule was known, written down, and sequenced for — and then broken by one more
honest edit made after the last rebuild. Rails §15 says this about a different rule and it
generalizes without alteration: **knowing the rule is not the same as having it in the fingers.**

**It is also the deliverable's own half-life, demonstrated twice in one session by two different
instruments** — first by the manufactured `scope_lint` module on its first contact with real data
(§4.2), then by `wrought-scope`'s own arm D here. The index is **derived**; any commit touching
`bin/`, `src/` or `docs/` stales it; **nothing rebuilds it automatically and this gate added no
hook.** Both instruments *detect* the staleness. Neither *prevents* it, and §7 says so.

**Fixed in the prescribed order** — rebuild, re-run, commit (`raw/32`). **All five arms pass on the
tree finally shipped.**

**AND ONE SMALLER THING THE FAILING RUN TAUGHT, recorded because the flattering move is to omit
it:** that run printed `EXIT=0` beneath a verdict line reading `wrought-scope: FAIL (2 failing
check(s))`. The `0` was `tail`'s, not the test's — a pipeline's `$?` is its **last** stage's. The
verdict line is the work product; the exit code was not. **Rails §18 in miniature, produced by this
gate's own reporting shell while it was writing about rails §18.**

## 4.4 The byte freeze, and the live-file deltas

**BYTE FREEZE HOLDS.** `raw/00` (session start) vs `raw/99` (wind-down), mechanical `diff` of the
64-hex lines: **exit 0, zero bytes of output.** The probe's own inner bracket — `raw/20` before it,
`raw/24` after it — likewise **zero bytes**, so the "nothing moved" claim is attributable to the
probe specifically and not only to the session as a whole.

**The deltas this gate added to the two live files** (rails §17.1 rule 1 — a size is unattributable
after the fact; a delta names its author):

| file | at session start | at wind-down | delta |
|---|---|---|---|
| `QUEUE.md` | 32,980 B | 29,255 B → plus this gate's `BUNDLED` row | **−3,725 B net**, after collapsing the terminal `GATE-HORIZON` row (−4,473) and adding this gate's own |
| `docs/PHASE-J-STATE.md` | 83,563 B | **89,301 B** | **+5,738 B** |

**Both files remain over the §17 budget** (~11,013 B and ~76,072 B), and §6 item 4 names the two
terminal rows that §17 says should already be one line each. **This gate did not fix them** —
§17 does not require it to — but it does not pass over them silently either.

## 5. Cost

| Phase | turns (approx.) | wall | notes |
|---|---|---|---|
| ORIENT + 0 | ~30 | ~25 min | rails, state doc, QUEUE, and re-verifying the HORIZON bundle |
| 1 | ~8 | ~12 min | the roadmap |
| 2 | ~50 | ~65 min | the build, four parameter sweeps, two defect fixes, five test arms |
| 3 | ~25 | ~35 min | pre-flight, the 191 s run, harvest, out-of-band re-verify, teardown |
| 4 | ~20 | ~30 min | wind-down |
| **total** | **~130** | **~2 h 45 min** | against a 16-hour budget; Phases 0–3 done inside the first ~2 h 15 min against a 6-hour target |

**External spend: `$0.00`.** No cloud tier was reached at any point, by design in Phase 3 and by
absence of need elsewhere. **Local model: 5 calls in Phase 2** (fresh purpose lines, `max_tokens`
28000, every one non-empty) plus the Phase 3 manufacturing run — all `$0.00`, resident GPU.

**Token/turn cost is APPROXIMATE and is labelled so.** An attended-direct session produces no
`verdict.json`, so these are turn counts and a session-level estimate, not an instrument reading.
That is the same limitation `GATE-HORIZON` recorded and it has not improved.

---

## 6. OTHER SURPRISES

1. **THE PROMPT'S FIRST INSTRUCTION WAS WRONG ON THE BOX.** It says `cd /home/kalib/foundry` and
   confirm branch `review-fixes`. `/home/kalib/foundry` is on **`main`**; `review-fixes` is checked
   out in the worktree `/home/kalib/review-rc1` — and `git` would have refused to check it out in
   foundry, because a branch cannot be checked out in two worktrees at once. Worked in the worktree,
   which is also where `GATE-HORIZON` ran. **This mattered more than a `cd`:** session 21's proven
   launch command hardcodes `/home/kalib/foundry` three times, and copied verbatim the Phase 3
   probe would have run against a tree that does not contain the task.

2. **THE FOUNDRY HAS NO GIT REMOTE.** `git remote -v` is empty. The prompt says "push" after
   Phases 1 and 2; the only push that exists is the courier's. The deliverable's sources and all
   evidence are therefore published into this bundle so the advisor can read them without a
   foundry checkout.

3. **THIS GATE'S OWN TASK SPEC FAILED THE PROJECT'S OWN VALIDATOR ON FIRST PASS.**
   `validate.validate()` returned `ok=False, defects=1`: `threshold_without_number` on REQ-007,
   which said *"SHALL carry at least the keys"*. It is an enumeration and not a threshold, and the
   lint cannot tell them apart from one line — but the lint is right to fire, because an
   unquantified *"at least"* in a requirement is exactly the shape that reaches a candidate as a
   blank to fill. Fixed in the spec. **It was caught only because session 21's input-validation
   check was reproduced clause for clause instead of re-derived.**

4. **`docs/PHASE-J-STATE.md` IS OVER THE §17 BUDGET AND SO IS `QUEUE.md`, and this gate says so
   without fixing them** (rails §17's own instruction). At session start: `QUEUE.md` 32,980 B
   against a ~11,013 B budget; `docs/PHASE-J-STATE.md` 83,563 B against ~76,072 B. **Two
   `ADJUDICATED` rows — `GATE-TRIM` and `GATE-REVIEW` — are terminal and still carry multi-KB text
   that §17 says should be one line each.** Collapsing them is a dispatched gate's work, not this
   one's, but a silent pass would make the cost invisible, which is the failure §17.1 exists to name.

5. **RAILS §15 RECURRED, IN THIS GATE, AT THE CONSOLE.** Checking whether a background rebuild was
   still alive, this session ran `pgrep -af 'wrought-scope'` — and the output's first line is the
   tool-call shell whose own command line contains the pattern. Nothing was signalled and no harm
   was done, but §15's whole point is that *knowing the rule is not the same as having it in the
   fingers*, and it has now recurred a fourth time. Recorded rather than omitted.

6. **A HEREDOC ATE A BACKTICK AND GARBLED AN EVIDENCE LINE** (`raw/15`). Corrected **by addition**
   per rails §4 — the garbled line stands, with the correction beneath it and the cause named.

7. **THE PROBE'S ARTIFACT FOUND THIS GATE'S OWN INDEX STALE, WITHIN AN HOUR OF THE INDEX BEING
   BUILT.** `bin/wrought-scope` and `bin/test-wrought-scope` were committed *after* the last
   rebuild, and the index is derived from `git ls-files`, so it did not know about them. **This is
   the deliverable's own half-life, demonstrated by the tool manufactured to detect it**, and it is
   now a `KNOWN-OPEN` line rather than a discovery waiting for a later gate: nothing rebuilds the
   index automatically and this gate added no hook.

8. **AN `ExecMainStatus=0` AND A `Result=success` WERE READ FROM SYSTEMD RATHER THAN FROM THE LOG,
   AND ONE OF THEM STILL NEEDED IGNORING.** `systemctl reset-failed` exited **1** during teardown —
   because `stop` had already fully unloaded the transient unit. The measurement that matters is the
   empty `list-units` immediately after it, not the exit code of the command before it. Rails §18
   applied to this gate's own cleanup.

---

## 7. WHAT THIS DID NOT ESTABLISH

- **THE TUNING SET AND THE GRADING SET ARE THE SAME 23 QUERIES.** `bin/wrought-scope`'s ranking
  parameters were chosen by sweeping against `index/scope-fixtures.json`, and that same file is what
  `bin/test-wrought-scope` grades against. **Generalization beyond these queries is UNMEASURED.**
  Three of the 23 are the dispatching prompt's and were not chosen here; ten were written from the
  repo-map before any measurement existed; **ten more were added part-way through the sweep**
  because thirteen were too few to choose between configurations without fitting them. They were
  written to widen the target rather than to hit it, and none was altered after seeing its score —
  but that is still weaker than a held-out set, and the fixture file now says so.

- **9.3× IS AN AVERAGE OVER THOSE QUERIES, NOT A GUARANTEE.** One fixture (*"byte freeze the
  orchestrator store"*) costs 30.4 % of the tree at the test cap. A query whose answer is genuinely
  spread across the tree will scope badly, and the tool has no way to tell the caller that in
  advance.

- **THE INDEX IS A DERIVED ARTIFACT WITH A HALF-LIFE.** It is correct for the tree it was built
  from and `bin/test-wrought-scope` arm D asserts that, but **any commit that touches `bin/`,
  `src/` or `docs/` stales it** until `rebuild` runs. Nothing runs `rebuild` automatically; there
  is no hook and this gate did not add one.

- **THE PURPOSE LINES ARE NOT VERIFIED CORRECT.** 113 come from `GATE-HORIZON`'s repo-map with a
  groundedness verdict of `RELIABLE`, which means *not obviously fabricated* and **never**
  *correct*; 14 more are `UNCHECKABLE` and are carried with that flag rather than regenerated,
  because a fresh summary of an uncheckable file is no more checkable. 22 come from `CLAUDE.md`'s
  document map and 5 from a fresh local-model call. **`purpose_source` is recorded per file so a
  reader can weigh each one; none of them was checked against the file's behaviour.**

- **THE PHASE 3 ORACLE IS MACHINE-AUTHORED.** Its tests and the spec they grade were both written
  by this session. What it is *not* is authored by the thing it grades — the candidate is written
  by the resident 27B, in another process, from `TASK.md` alone. That is the separation the probe
  needs and the one it has; **it is not operator ratification, and D11 makes ratification the
  operator's.** The same question is already open against `products/queue-health/MANIFEST.json`.

- **N=1 LICENSES NO RATE — AND NOW n=2 DOES NOT EITHER, WHICH IS THE MORE TEMPTING CLAIM.**
  `products/queue-health` and `products/scope-lint` both reached `COMPLETED` at attempt 0. **Both
  are pure functions over plain dicts, with no concurrency and no cross-file scope** — the easy end
  of the GATE-41 distribution, twice. What two data points license is exactly what one licensed:
  that the production path runs end to end and that the worker sources its own verdict. **Nothing
  about how often it will.** `products/README.md` now says so in the table itself, so the next
  reader meets the warning beside the number rather than in a report they may not open.

- **NO ESCALATION RATE WAS MEASURED AT ALL.** The cloud tier was structurally off (§4.1). M2 —
  *prove manufacturing and measure escalation rate* — **remains unrun**, and this probe is not it.

- **NOTHING WAS UNATTENDED.** The probe ran under `systemd-run` without a human watching its
  turns, which is the *shape* ruling 4 asks for, but the gate around it was attended throughout.
  **The runner was not exercised and the reaper was not exercised.**

- **NOT ONE `GATE-HORIZON` PANEL FINDING WAS VERIFIED AGAINST THE CODE**, and locking
  `docs/ROADMAP-1.0.md` does not promote any of them from candidate to fact. The roadmap's sizes
  are the panel's and **were not costed on this box**.

- **`COMPLETED` STILL MEANS PROVISIONALLY VERIFIED.** Face B is open. Any artifact this gate's
  probe produced was re-verified out of band (§4.2) precisely because the envelope alone cannot
  be trusted, and that compensating control is still the reason the M2-before-M3 ordering is safe.

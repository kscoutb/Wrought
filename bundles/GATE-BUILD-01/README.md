# GATE-BUILD-01 — bundle contents

**The first BUILD gate**, 2026-09-01, ATTENDED-DIRECT from worktree `/home/kalib/review-rc1` on
branch `review-fixes`. Start at **`REPORT.md`**.

**The foundry has no git remote** (`git remote -v` is empty), so the deliverable's sources and every
measurement are published here rather than left behind a checkout the advisor does not have.

| path | what it is |
|---|---|
| `REPORT.md` | **read this first.** Every headline is followed by what it does not establish; §7 collects the rest. |
| `ROADMAP-1.0.md` | the locked plan. The operator's eight rulings ARE M0; the advisor's M2-before-M3 fork ruling is §2.1. Authoritative copy is foundry `docs/ROADMAP-1.0.md`. |
| `tools/wrought-scope` | **the deliverable.** Context scoping: minimal ranked file set per task, with measured `/tokenize` costs. |
| `tools/test-wrought-scope` | its committed test — five arms, and arm E exists because arm E failed. |
| `tools/scope-fixtures.json` | the definition of done, and its own honest account of how it was built. |
| `tools/README.md` | `index/README.md`: which file in `index/` is generated and which is authored. |
| `product/` | what the PHASE 3 probe manufactured: the module, its spec, its oracle, and `MANIFEST.json`. |
| `raw/00`, `raw/99` | the session byte freeze. **Mechanical diff: zero bytes. HOLDS.** |
| `raw/01`, `raw/02` | the `GATE-HORIZON` verdict, extracted mechanically, and its re-verification. |
| `raw/10`–`raw/15` | PHASE 2: repo-map coverage, the index build, the oracle's satisfiability AND falsifiability, the test, the tool in use, lint and chars/token. |
| `raw/20`–`raw/25` | PHASE 3: pre-flight, the launch command with its five deliberate deviations, the result, the out-of-band re-verification, production-untouched, teardown. |
| `raw/30`, `raw/31` | PHASE 4: the index rebuilt after the doc edits, and the test re-run against the tree as shipped. |
| `raw/32` | **the final check FAILED and is kept.** One more honest edit to an indexed file, after the last rebuild, staled the index — the exact trap `REPORT.md` §1 describes. Fixed in the prescribed order; all five arms pass on the tree finally shipped. |
| `SHA256SUMS` | `sha256sum -c SHA256SUMS` from this directory. |

**Three things a reviewer should not have to dig for.**

1. **`bin/wrought-scope` had two defects that this gate found by running it**, and one of them made
   the tool's answer depend on the process's hash seed (61,431–82,262 tokens for one query across
   eight seeds). `REPORT.md` §3.3.
2. **The PHASE 3 probe measured no escalation rate**, because the tier was structurally off — a
   ledger row lands in the byte-frozen production store. **M2 remains unrun.** §4.1.
3. **Three of this gate's own PHASE 3 verification checks were defective**, including two that
   returned error strings where a reader would see zeros. §4.3. All corrected by addition.
4. **The final check before declaring done FAILED**, on the trap this report had already written
   down — and it is kept rather than quietly re-run. §4.5.

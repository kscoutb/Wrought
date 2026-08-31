# REPORT-FIX — GATE-FIX v2.0, 2026-08-31

**ATTENDED-DIRECT**, branch `review-fixes`, base `bbecf2d`. Nine commits, one per F-item, each
with its test in the same commit and each behind a §5.1 scan at exit 0.

## The headline, stated the way the prompt demanded it be stated

**F-1 IS NOT CLOSED. `COMPLETED ⟹ the oracle passed` does not hold at HEAD.**

Two of its three faces are closed and fixture-proven. The third is not, and the open half ships as
a **committed fixture that still reaches a false `COMPLETED`** rather than as a sentence in this
report. The prompt said a trust boundary reported as "mostly closed" is the one outcome this gate
must not produce; this is me not producing it.

| Fixture | Face | BEFORE | AFTER |
|---|---|---|---|
| `hijack` | A — import hijack | **PASS** | CODE_DEFECT |
| `exit0` | B — exit-0 + forged `/work/.coverage` | **PASS** | SUBSTRATE (tool error) |
| `classify` | C — backdoored classifier | **PASS** | REFUSES TO LAUNCH |
| `happy` | regression | PASS | PASS |
| `exit0b` | **B — the adaptive forgery** | — | **PASS — STILL OPEN** |

Three attacks reached PASS before the fix; that is the "before-PASS shown for at least one" the
prompt asked for, shown for three. Verbatim captures:
`build-evidence/gate-fix/raw/10-fixtures-BEFORE.txt` and `11-fixtures-AFTER.txt`.

### Why `exit0b` still passes, and what would actually close it

`/work/out` remains writable by the candidate, because candidate code executes **inside pytest, at
the verifier's own uid**. The fix moved the verdict-bearing artifacts (`.coverage`, the pytest JSON
report) out of the candidate's cwd and started requiring positive proof of execution — so the
*demonstrated* attacks die. But a candidate that adapts, and writes into the paths the fix moved
things TO, still forges a clean run.

This is not a gap I can close by trying harder in the same shape. As long as the process that
executes candidate code is also the process that reports on it, its report is not evidence. Closing
it needs the candidate off the reporter's uid — a second uid inside the sandbox, with the
verdict-bearing directory writable only by the verifier, and the TEST check's execution observed
from outside the candidate's process. That moves the pack's hardcoded output paths too, so it is a
sandbox redesign and **its own gate**. Recorded as `KNOWN-OPEN` item 16 and in `NON-CLAIMS`.

## Per-item summary

| Item | Verdict | What changed |
|---|---|---|
| **F-1 Face A** | **CLOSED** | `PYTHONPATH=/work/src` was set for the whole sandbox, and the verifier runs `python -m wrought_verifier`; for `-m`, sys.path is `[cwd, *PYTHONPATH, *stdlib, *site-packages]`, so the candidate's tree preceded the venv holding the real module. A candidate shipping `/work/src/wrought_verifier/` simply **became the verifier**. Renamed to `WROUGHT_CANDIDATE_PYTHONPATH`, promoted to `PYTHONPATH` by the verifier for **check subprocesses only**; verifier runs `python -I`. |
| **F-1 Face B** | **PARTIAL — see above** | `/work` is its own tmpfs, `--remount-ro` after the binds (non-recursive, so `/work/out` stays writable and the verifier keeps its only output channel). `COVERAGE_FILE` and `RUFF_CACHE_DIR` relocated. TEST checks need positive proof from the pytest report (collected>0 ∧ passed==collected ∧ no errors); a bare exit 0 is no longer a pass. The coverage threshold consults its tool's exit code before reading its output file. |
| **F-1 Face C** | **CLOSED** | `pins.lock` gains `oracle_decision_code` over `bin/verify-job`, `classify.py`, `oracle.py`, asserted at launch. `verify-job` pins **itself**: a check the checker can edit out of the way is not a check. |
| **F-2** | **CLOSED** | A task resting in `REPAIRING`/`ESCALATING` matched no branch and was **silently acked** (measured: `steps=[] acked=True`, queue 1→0, task unmoved). Now refused before the ack, so the lease lapses and `sweep_dead_letters` parks it in HUMAN_REVIEW. `recover()` now carries the delivery budget. |
| **F-3** | **CLOSED** | The runner `git add -A`'d a child-writable tree to a **public** repo with no scan anywhere in it. Now scans the whole tree from outside the child before staging, at all three push sites, halting on exit 2 as well as exit 1; enumerated add derived from the same cfg keys it writes through. |
| **F-4** | **CLOSED** | Guard split on commas; the CLI splits on commas **or whitespace**. Two live courier prompts exploit this today. Now `[,\s]+`, and the parsed list is what reaches the CLI. |
| **F-5** | **CLOSED** | `gate39-chaos` unlinks `store.DB_PATH` five times per run and `setdefault` yields to an inherited value. Now a **positive** assertion on its own scope path. |
| **F-6** | **SPLIT** | See below. |
| **F-7** | **CLOSED** | `pkill -f` matched the resident model server — same binary, same port — while the pid of its own child was discarded. Now signals only that pid; refuses to run while the unit is active. **The hazard was live at fix time.** |
| **F-8** | **CLOSED** | No `signal` import; child in its own session so Ctrl-C never reached it; wrapper caught `Halt` only, so KeyboardInterrupt skipped the orphan sweep. Now a SIGINT/SIGTERM handler kills the child's **process group**, and the wrapper catches `BaseException`, runs the full epilogue, then re-raises. |
| **L1** | **CLOSED — against the spec** | See "Where I did not follow the spec". |
| z-ai F3, F4, F5, L2 | folded to docs | `KNOWN-OPEN` items 18–20, unverified, recorded as the panel reported them. |
| §13.5 cost bound | folded to docs | `KNOWN-OPEN` item 15. Escalation path untouched. |

Code diff vs `review-rc2`: **14 files, +1149/−29**, of which 5 files (+401) are new tests.

## F-6 was SPLIT, on two measured grounds

`build-evidence/gate-fix/raw/26`:

1. **`authproxy3.py` is not in this repo.** `git ls-files | grep -i authproxy` → nothing. It exists
   only at courier `bundles/GATE-J0B-CLOSE/sources/` — which is why GATE-REVIEW had to record its
   provenance when packing it for the panel. There is no file here to bound. The proxy is also not
   running (nothing on :8081), so the EMFILE burst cannot be exercised here either.
2. **A systemd scope cannot take the property.** The child is launched
   `systemd-run --user --scope`; `-p PrivateNetwork=yes` returns **`Unknown assignment`** (a
   `--user` *service* accepts it, measured both ways). Closing it means moving the child from a
   scope to a service or its own netns **and** giving it a deliberate path back to
   `127.0.0.1:8080`. Process supervision, output capture, the deadman attach and the reaper's
   scope-membership logic all move with that.

That is the process-starting gate's work (old BOUNDARY-B), not a flag this gate could add.
**The reaper was not exercised on a real network child**, because no such child was started.

## Where the spec was wrong on the box, and what I did instead

1. **F-1's mechanism could not be designed blind, and the prompt was right to say so.** v1.0's
   `--ro-bind` over the envelope would have broken the verifier's only output channel. The
   equivalent mistake nearly happened here in a different place: making `/work` read-only broke the
   **happy path**, because `ruff` initialises a cache at `$PWD/.ruff_cache` and exits 2 on a
   read-only cwd. It was caught by the regression fixture, which is exactly what fixture 4 is for.
   Fixed in the launcher's environment, never in the pack — packs are generated and content-hashed,
   and editing a shipping pack is a defect.
2. **L1 was filed as "docs, not fixes". I fixed it.** `oracle.stage_candidate` runs
   `sudo -n rm -rf` on a path `oracle.job_dir` builds from an **unvalidated** `task_id`, while
   `bin/verify-job` validated the same id against the same charset — the derivation feeding the
   root-level delete was the one copy of the guard that did not exist. `pins.lock:1172`'s own
   comment already says the charset is enforced "at InputValidation **AND at path derivation**".
   Documenting a root `rm -rf` traversal whose guard exists one file over, and whose pin already
   claims the guard is there, is not a defensible outcome for a gate about trust boundaries. The
   rule now lives **once** in code and `verify-job` imports it, so the copy count went down.
3. **F-5 was specified as "assert it is not the production literal". I made it stricter** — a
   positive assertion on the gate's own scope path. A denylist of one path is only as good as the
   guess that no other path matters (an inherited `/tmp` path destroys a corpus just as well), and
   spelling the production literal here would duplicate `store.py`'s default.
4. **The prompt contradicts itself on the byte freeze.** Its Rails mandate `raw/00`/`raw/99`
   "before and after"; its Wind-down says "No byte-freeze attempt (runner holds it)". No runner
   holds this session, so the Rails line governs and ST-1's `raw/00` precedent says the same
   ("an ATTENDED-DIRECT session, so the freeze is the box's own duty"). **Freeze HOLDS**: all three
   hashes identical, and identical to ST-1's 2026-08-29 baseline.
5. **PHASE 0 had no QUEUE row to set.** `GATE-REVIEW` ran attended-direct off a chat prompt and was
   never queued, so the row was **created**, not flipped — stated in the row itself.

## Transport

v2.0 arrived **first as operator paste with the `PRIOR-ADJUDICATION` block flattened to the literal
token `Code`**: the declared check returned **0 of 25**, so rails §7's STOP applied and the session
stopped and reported instead of reconstructing. Before stopping it verified all **11 other
`file:line` citations exact** against the tree, which is how we knew only the block had been lost
and not the gate. The operator resent it intact; the archived file returns **25/25 first run**.
The verdict was extracted **mechanically** (`sed -n '36,63p'`), never retyped: 25 content lines, 0
absent from the record, and a negative control (one tampered line) correctly reports 1.

## Regression evidence

GATE-39 **ZERO LOSS, ZERO DUPLICATION**; GATE-38 all vectors; S13/S14/S15 invariants all pass;
`verify-d24-backstop` holds; the F-1 happy-path fixture reaches PASS; all **534** existing job and
oracle task ids satisfy L1's charset. The production event store is byte-identical to the raw/00
baseline after a gate that included running the chaos suite.

## What this gate did NOT do

It did not close F-1. It did not touch the escalation path or write a ledger row. It did not start,
stop or reconfigure any `wrought-*` unit. It did not retag. It did not verify the panel's remaining
LOW/MEDIUM leads (items 18–20), which stay candidate findings.

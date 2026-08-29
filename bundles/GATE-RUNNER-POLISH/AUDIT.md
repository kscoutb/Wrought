# GATE-RUNNER-POLISH — adversarial audit

Rails §6: *"A short adversarial audit runs before any report ships. Its job is to find the claim the
report cannot support, and to say so in the report rather than leaving it for the reviewer."*
Run against `REPORT-RUNNER-POLISH.md` and the 35 raw captures, 2026-08-29.

## A. Counts, re-derived rather than trusted

| Claim in the report | Command | Result |
|---|---|---|
| 35 raw files | `find raw -maxdepth 1 -type f \| wc -l` | **35** ✅ |
| runner 1163 → 1489 lines | `wc -l` on the BEFORE/AFTER copies | **1163 / 1489** ✅ |
| 9 new functions | `grep -cE '^\+def ' raw/61-…diff` | **9** ✅ |
| config: 104 leaves, 9 changed | printed by the harness in `raw/41` | **104 / 9** ✅ |
| 3 decoys, old test 3/3, new 0/3 | `raw/11` STEP 3 / STEP 4 | ✅ |
| old scan → 1 exposed argv, new → 0 | `raw/21` ARM 1 / ARM 2 | ✅ |
| four children, $0.4345 | sum of `verdict.json` `cost_usd` across the scratch runs | **$0.4345** ✅ |
| byte freeze HOLD | `diff` of `raw/00` vs `raw/99`, in `raw/99b` | ✅ |

## B. Claims the evidence does NOT fully support — stated here, and in the report

1. **"The listener probe now takes every owning pid" is a CODE change with no positive
   observation.** `raw/12` §B2 records that **no socket on this box currently has more than one
   owning pid**, so the multi-owner path was never exercised. The fix is argued from `ss`'s output
   format, not demonstrated against a real multi-owner socket. The report says so; this is the
   weakest of the Phase-2 fixes and a reviewer should read it as such.
2. **`_reap_refusals()` was unit-tested, not integration-tested.** No run ever presented the reaper
   with a pid it had to refuse. `raw/12b` calls the function directly. What that leaves open: the
   guard is proven correct in isolation and proven not to block a real guest (`raw/12c`), but the
   combination "false positive appears AND the guard catches it" has never happened end to end.
3. **`terminate_grace_sec = 5` is exercised, not calibrated.** One guest shape, one observation.
   The report says this; it must not be read as ratifying the number.
4. **The `NOT RUN` meaning is the box's own minimal reading.** Nothing in the repo defines it. The
   box measured that it was never used and wrote the smallest coherent definition. That is an
   invention constrained by evidence, not a recovered fact, and it is flagged for the ferry in all
   four places it now appears.
5. **`max_batch_cost_usd = 24.0` is DERIVED, not measured.** It is 3× another provisional number.
   The derivation is written into the config so it can be argued with, but no measurement supports
   24 specifically over 16 or 32.
6. **The Phase-6 proof used a scratch courier, not the real one.** That was mandatory (a runner
   start always writes and pushes `STATUS.md`), but it means the boundary is proven against the
   real runner and a real `claude` child on a synthetic queue — not against a production dispatch.
7. **`virsh destroy` remains unexercised**, and this gate adds no evidence about it. The reaper
   proof used plain qemu by design.

## C. Things the audit checked and found sound

- **No production state was moved except one deliberate, recorded write.**
  `/var/lib/wrought/runner-state/breaker.json` was replaced (`raw/32`) with the prior content
  captured verbatim first; the breaker was unlatched and `consecutive_failures` already 0, so no
  safety state was lost, and the ledger's `GATE-J0B-RESUME` PASS row is untouched. Every scratch
  run used a scratch `state_dir` and a scratch `courier_dir`.
- **The real courier was never touched by a runner start.** Confirmed by construction (derived
  configs) and by the real `QUEUE.md`/`STATUS.md` carrying only this session's own edits.
- **No secret was handled to test the secret scanner.** `raw/21` generates a fake token; the only
  contact with the real store is `raw/22`/`raw/22b`, which run the production path and print counts.
- **Evidence was corrected by addition, never overwritten** — `raw/12b`, `raw/22b`, `raw/42b`,
  `raw/53b`, and a correction file beside `runner-arm/raw/31` rather than an edit to it.
- **Zero ephemeral HOMEs survive** (`raw/42`), including from two runs that halted before launching
  a child — the dead-gate case the teardown exists for.

## D. Defects found in this gate's own work

All four are in the report §8, not buried: the zombie survivor class; the scanner's exit-1/exit-2
collapse; the batch-cost check ordering ahead of the ledger write; and **three pre-written verdict
lines contradicted by the measurement directly above them** (`raw/22`, `raw/42`, `raw/53`).

**The audit's own finding is that the fourth is the significant one.** Three times in one session
the box wrote a conclusion before taking the measurement, and each time the measurement disagreed.
That is the same defect class the gate was dispatched to fix — `reset_by`, the overbroad boundary
FACT, the `NOT RUN` "ratified-in-use" premise — all conclusions no measurement stood behind. It was
caught each time only because the probe output sat in the same file. The mitigation adopted
mid-gate (compute the verdict from the data, as `raw/53b` does) should be the default for any
harness this project writes, and that is a recommendation to the advisor, not a completed fix.

## E. Minor, recorded for completeness

- **Numbering gap.** There is no `raw/30-*` file: `raw/30-scratch/` is a directory (the scratch
  config for the reset-provenance proof) and the proof itself is `raw/31`. `raw/31`'s own header
  line reads `raw/30` as a result. Cosmetic; left standing rather than edited (rails §4).
- **Scratch directories are NOT bundled** — `raw/10-scratch`, `20-scratch`, `30-scratch`,
  `40-scratch` hold git repos, a fake-secret file and derived configs. The bundle carries the 35
  top-level raw files and the harnesses that produced them, which is what is reviewable as text.
- **This gate's own prompt declares bare `Bash`**, the spelling Phase 6 retires. No mechanical
  effect (attended-direct), but the next dispatched prompt must be scoped or the runner refuses it.

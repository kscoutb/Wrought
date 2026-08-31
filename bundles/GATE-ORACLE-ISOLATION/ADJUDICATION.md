# ADJUDICATION — GATE-ORACLE-ISOLATION

**Recorded by `GATE-HORIZON` PHASE 0, 2026-08-31, as its first substantive courier action
(`docs/EXECUTOR-RAILS.md` §10).** The advisor cannot push to the courier, so the verdict arrived
inside the next prompt and is recorded here so the gate's closed state is visible on the courier
and not only in the advisor's chat.

**The verdict below was lifted MECHANICALLY** — `sed -n '41p' prompts/GATE-HORIZON.md` over the
archived prompt — **never retyped.** Rails §10: "verbatim" that passes through a keyboard is a
paraphrase waiting to happen.

**BUNDLE RE-VERIFIED BEFORE RECORDING, as the verdict instructs (`trust the bundle over this text
if they differ`).** Two identifiers were checked and BOTH authenticate, but one needed
disambiguating and that is recorded rather than glossed:

- **`manifest begins 33291886`** — this is **the sha256 of `SHA256SUMS` ITSELF**
  (`332918866881034d21343ddc4529ac842c01cfb6eba09127a6fdebff6af5ab43`), **not** its first entry,
  which begins `1343ee10`. The phrasing reads the other way. Read as the manifest's own hash it
  matches exactly; read as the first line it does not. **Recorded so a later session re-checking
  this does not conclude the bundle drifted.**
- **`base 52fade2`** — `git rev-parse 54f7786^1` = `52fade2`. The gate's one commit sits directly
  on the stated base.
- **`sha256sum -c SHA256SUMS` → 17 of 17 OK**, re-run at this recording.

---

## VERDICT, verbatim

Re-verify against bundles/GATE-ORACLE-ISOLATION/ (manifest begins 33291886, base 52fade2); trust the bundle over this text if they differ. VERDICT: ACCEPTED (advisor 2026-08-31), exemplary — it measured that a second candidate uid is both unavailable (Ubuntu unpriv_bwrap AppArmor denies capability setuid unconditionally, atop a seccomp filter denying nested-userns clone) and insufficient (candidate code IS the pytest process; committed fixture exit0c proves any relocation-based fix still passes). Net state at HEAD: Faces A (import hijack) and C (decision-code replacement) CLOSED and fixture-proven; Face B (a candidate forging its own single in-process verdict) is detected-not-prevented and contained by the network-less capability-dropped disposable sandbox to one tool falsely stamped COMPLETED, never escape or persistence. Write it to bundles/GATE-ORACLE-ISOLATION/ADJUDICATION.md, set that QUEUE row ADJUDICATED, commit, push.

---

## What this closes, and what it explicitly does NOT

The acceptance is of the **gate**, not of the invariant. The verdict itself says Face B is
**"detected-not-prevented"**, so `COMPLETED ⟹ the oracle passed` still does not hold in full at
HEAD and `KNOWN-OPEN` item 16 stays open. `GATE-HORIZON` PHASE 1 writes the honest restatement,
the compensating control, and item 16's real fix and cost into `docs/PHASE-J-STATE.md`.

**The operator tags `review-rc3` after the advisor adjudicates `GATE-HORIZON`** — not on this
verdict. `GATE-ORACLE-ISOLATION`'s own bundle says `DO NOT TAG review-rc3`, and nothing here
lifts that.

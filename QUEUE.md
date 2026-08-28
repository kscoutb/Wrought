# QUEUE — live dispatch state

One row per gate, newest at the bottom. See `README.md` for the loop.

**Statuses**

| Status | Meaning | Set by |
|---|---|---|
| `QUEUED` | Prompt written and dispatched to the operator; the box has not started it. | advisor |
| `RUNNING` | Box has archived the prompt to `prompts/` and is running it in a fresh context. | box |
| `BUNDLED` | Box has pushed `bundles/<GATE-NAME>/` and the gate is awaiting review. | box |
| `ADJUDICATED` | Advisor has reviewed the bundle; the gate is closed and the next one queued. | advisor |

**Dispatch**

| Gate | Status | Notes |
|---|---|---|
| `GATE-HJ1-HYGIENE` | `BUNDLED` | v1.1 archived to `prompts/GATE-HJ1-HYGIENE-v1.1.md`; bundle at `bundles/GATE-HJ1/` (16-entry `SHA256SUMS`, verifies 16/16, covers the whole directory bar itself). Pins ratified — the closure is pinned at **versions**, not just names. Byte freeze **held**. Two foundry commits, local (the foundry repo has no remote): `624f1b9`, `bc27359`. **Surfaced, not answered: the running kernel is `7.0.0-29-generic` against a pinned `7.0.0-28-generic`, so ST-1 now has two unsatisfied triggers.** J0B unblocks on adjudication. |
| `GATE-HJ2-HEARTBEAT` | `NOT RUN` | **GATE-RUNNER carried a PRIOR-ADJUDICATION block naming HJ2 but supplied NO verdict text, and HJ2 has never run — so there was nothing to record and nothing was invented (2026-08-21).** Dispatched as a file alongside J0B and archived here verbatim (`prompts/GATE-HJ2-HEARTBEAT-v1.0.md`), but **never executed** — at J0B start `STATUS.md` did not exist and `docs/EXECUTOR-RAILS.md` carried no HEARTBEAT section. J0B's heartbeat header still had to be honoured, so this session **bootstrapped `STATUS.md` alone** from HJ2's verbatim schema. HJ2's remaining steps (rails/README rule text, the HJ1 `ADJUDICATION.md` write, journal J-158) are **still outstanding** — out of J0B's authorized scope, which forbids foundry commits. |
| `GATE-J0B-SURFACE` | `RUNNING` | v1.2 archived to `prompts/GATE-J0B-SURFACE-v1.2.md` (**deviation:** the prompt's prose says archive as `-v1.1.md`; the file dispatched is v1.2, and the courier archive is "exactly what was sent", so the version in the name matches the version in the file). Transport check **PASS** — exactly 12 four-space blocks. |

| `GATE-RUNNER` | `BUNDLED` | v1.0 (ATTENDED). **Transport deviation, surfaced not absorbed: this prompt arrived as CHAT TEXT, not as a file** (rails §7); content was intact and the mandated block count checked out at exactly 3, so it was archived verbatim to `prompts/GATE-RUNNER-v1.0.md` and run. Bundle at `bundles/GATE-RUNNER/` (40-entry `SHA256SUMS`, verifies 40/40, covers the whole directory bar itself). **REVISION 2, same session:** platform notices arrived after the first push reporting that all three cross-session probe messages were **held for recipient-user approval and expired undelivered** — `raw/18` corrects `raw/16`'s mechanism by addition (rails §4), and the report carries the correction inline. Better than first recorded (fail-closed by construction, not by a child ignoring an inbox); worse than first recorded (`SendMessage` reported an accepted *send*, not a delivery). The Phase-3 requirement is **still not satisfied**, and **what an APPROVED message does to a running gate child was never tested**. Byte freeze **held**. One foundry commit, local: `ec593be`. **Needs ratification:** the new `APPROVED` queue status, the required `ALLOWED-TOOLS:` prompt header, every threshold in `/etc/wrought/runner.conf`, and pointing the sealed §13 credential at the course-check (which ships **disabled**). **The Phase-3 cross-session steering breaker is NOT satisfied** — said plainly in the report, not papered over. |

| `GATE-RECONCILE` | `RUNNING` | v1.0 (ATTENDED-preferred). **Transport deviation, surfaced not absorbed: this prompt arrived as CHAT TEXT, not as a file** (rails §7) — the same deviation GATE-RUNNER recorded. Content was intact and the mandated block count checked out at exactly 3 (6/10/4 lines), so it was archived verbatim to `prompts/GATE-RECONCILE-v1.0.md` and run. |


*(HJ1 is the first gate through the courier. It was dispatched to the operator as a file and
archived here verbatim before the box began work.)*

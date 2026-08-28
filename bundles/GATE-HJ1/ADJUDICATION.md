# GATE-HJ1-HYGIENE — advisor adjudication

*Recorded by `GATE-RECONCILE` on 2026-08-28, per the adjudication-carrying rule now in
`docs/EXECUTOR-RAILS.md` §10. The advisor cannot push to this repo, so adjudications arrive
inside the next prompt and the box records them. The text below is extracted **mechanically**
from the indented block of `prompts/GATE-RECONCILE-v1.0.md` (lines 62–71) — not retyped.*

## Verdict — ACCEPTED, gate closed

GATE-HJ1-HYGIENE — ACCEPTED, gate closed (advisor Fable, 2026-08-12). Pins ratified correctly
(51 packages at versions; systemd baseline captured; image + GPG-waiver recorded); byte freeze
held; the drift policy earned itself by catching the kernel bump, correctly recorded not
silently pinned. Rulings: (1) the courier is the canonical evidence archive — foundry has no
remote, so its build-evidence/ is on-disk only; the public courier is offsite and durable, so
routing gate evidence through it is preferred, not a defect. (2) Goose as docs/10 §18.7
"selected, not adopted", licence/version unpinned — approved. (3) STOP-44 reserved but
unratified with no anchor — approved as recorded. ST-1 now carries two unsatisfied triggers
(kernel 7.0.0-29 vs -28; AppArmor beta->stable under the oracle's bwrap); both clear in ONE
ST-1 pass before the next MANUFACTURING run — neither blocks J0B, which never invokes the oracle.

---

**Provenance:** `sed -n '62,71p' prompts/GATE-RECONCILE-v1.0.md`, the archived verbatim copy
of the dispatching prompt. Advisor: Fable. Verdict dated 2026-08-12; recorded 2026-08-28.

**Follow-through owed by this ruling, and where it now lives:**

- The two unsatisfied ST-1 triggers named in the verdict (kernel; AppArmor) are carried in
  `pins.lock` `substrate.drift_log` and in `bundles/RECONCILE/SNAPSHOT.md`. **The kernel
  trigger has moved on since the verdict was written**: it read `7.0.0-29` vs a pinned
  `7.0.0-28`; the box now runs **`7.0.0-30-generic`**, and the pinned `-28` headers were
  removed by `unattended-upgrade` on 2026-08-21. Recorded, not silently re-pinned.
- Ruling (1) — the courier is the canonical evidence archive — is why J0B's partial evidence
  was routed to `bundles/GATE-J0B/PARTIAL/` rather than left on-box only.

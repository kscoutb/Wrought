# ADJUDICATION — GATE-RUNNER-POLISH

Recorded by the `GATE-J0B-CLOSE` pre-flight on 2026-08-29T14:39:16Z, per `docs/EXECUTOR-RAILS.md` §10.
Advisor: Fable. Carried in by the `GATE-J0B-CLOSE` v1.0 prompt, archived at
`prompts/GATE-J0B-CLOSE-v1.0.md` (sha256 `bb3be6c53a1d2a8e60f7bb0e5026e6187b0fc037e433e3f1efcd9c464cf31453`).

Extracted MECHANICALLY, never retyped:

    $ sed -n "/^PRIOR-ADJUDICATION/,/^## Rails/p" prompts/GATE-J0B-CLOSE-v1.0.md | sed \$d

---

PRIOR-ADJUDICATION — GATE-RUNNER-POLISH: **ACCEPTED (advisor Fable, 2026-08-29).** 39/39, byte
freeze held, all seven phases; the reaper is now precise (executable identity, zombies excluded,
multi-owner listeners, reap-refusal floor), the staged-diff secret scan has a committed home with
zero argv exposure, F-1/F-2 written into rails §2.1/2.2 and §13.3, `NOT RUN` corrected to
RESERVED-never-used, `reset_by` replaced by measured fields, the workspace boundary ARMED both
halves (bare `Bash` refused unconditionally; scoped-`Bash`+`ADD-DIRS` proven a real fence), and a
PROVISIONAL per-batch cost cap added. Both cost caps owe RE-CALIBRATION after F-5 — which is this
gate. Record per §10.

---

## Verdict, in one line

**ACCEPTED, CLOSED.** All seven phases, 39/39, byte freeze held. The one debt the verdict
names — RE-CALIBRATION of both cost caps — is assigned to `GATE-J0B-CLOSE`.

## Note added by the recording session, because it bears on this verdict

The verdict credits the workspace boundary as **ARMED, both halves, a real fence**. The
`GATE-J0B-CLOSE` pre-flight then measured two limits that narrow that credit, and they are
recorded here so the acceptance is not read more broadly than the evidence supports
(`bundles/GATE-J0B-CLOSE/raw/02`):

- **`Bash(python3:*)` escapes the path boundary entirely** — a child wrote outside its
  declared tree with **zero denials**. The target path sits inside the interpreter's `-c`
  program text, where the permission layer never sees it.
- **A scoped allowlist permits only bare single-command invocations** — every redirect, pipe,
  `&&` and `;` was denied, even when every constituent command was allowlisted.

POLISH proved the scoped case with a single `Bash(touch:*)` and generalised. That is the same
over-generalisation POLISH itself corrected in `runner-arm/raw/31`, committed one level down.
The controls are real and correctly armed; the CLAIM about what they constrain is narrower.
Corrected by addition in rails §12.2.1 and `docs/PHASE-J-STATE.md`.

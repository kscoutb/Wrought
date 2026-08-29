# GATE-J0B-CLOSE — PRE-FLIGHT (the gate was NOT run)

**Date:** 2026-08-29. **Session:** attended-direct on forge-mini. **Workdir:**
`/var/lib/wrought/j0b-close/`. **Prompt archived:** `prompts/GATE-J0B-CLOSE-v1.0.md`, sha256
`bb3be6c53a1d2a8e60f7bb0e5026e6187b0fc037e433e3f1efcd9c464cf31453`.

## Why this session pre-flighted instead of running

The prompt's executor line says **"run THROUGH `wrought-runner` as a `claude -p` child"**, and
Phase 4.1 requires *"this gate's actual child cost (from the runner's `verdict.json`,
authoritative)"*. An attended-direct session produces no `verdict.json`, so running it here would
destroy a stated deliverable — the same reasoning by which `GATE-J0B-RESUME` v2.0 was pre-flighted
rather than run. Two further facts settle it:

- **The gate is not `APPROVED` and the box may not approve it.** Rails §12.1 reserves that status
  for the advisor and operator at the ferry; it is the only runnable status, and the gap between
  `QUEUED` and `APPROVED` is exactly where a human still sits on the unattended path. The row has
  been added as **`QUEUED`**.
- **The runner would refuse to start this gate anyway.** See B-1.

**Three blockers and two calibration notes follow. B-1 and B-2 are hard; B-3 is a correctness
finding about a control this box shipped yesterday.**

---

## B-1 (HARD, silent-in-spirit, caught mechanically) — the `ADD-DIRS:` header halts the gate

`ADD-DIRS: /var/lib/wrought/j0b, /var/lib/wrought/j0a` — comma-separated. `resolve_add_dirs()`
splits the header on **whitespace**, so the first token is `/var/lib/wrought/j0b,` **with the
comma**, which is not a directory. Run through the runner's own parser (`raw/01`):

    *** HALT [add-dirs] — THE GATE WOULD NOT START ***
    GATE-J0B-CLOSE: ADD-DIRS names ['/var/lib/wrought/j0b,'], which do not exist as directories.

Both real paths exist (`/var/lib/wrought/j0b` and `/var/lib/wrought/j0a`, `is_dir=True`). This is
purely the separator.

**Note what happened here, because it is the control working exactly as intended and it still cost
a dispatch.** `GATE-RUNNER-POLISH` added this check the day before, precisely so that a bad
`ADD-DIRS` fails loudly at launch instead of as an unexplained denial twenty minutes in. It caught
the very next prompt. But the prompt author wrote a comma because **`ALLOWED-TOOLS:` on the line
above is comma-separated** — the two headers take different separators, which is a trap the box
built and did not document.

**Two fixes; the box has applied neither, because both are outside this session's authority
(the `GATE-RUNNER-ARM` precedent: report a specified fix, apply only under an explicit ruling).**

1. **Prompt-side (no code change):** re-issue with `ADD-DIRS: /var/lib/wrought/j0b /var/lib/wrought/j0a`
   (whitespace).
2. **Runner-side (recommended, strictly additive):** make the parser accept both separators —
   `re.split(r"[,\s]+", m_dirs.group("dirs"))` — so the two headers stop disagreeing. This widens
   nothing: every resulting path is still validated to exist, and `ADD-DIRS` still only names trees
   the prompt asked for.

---

## B-2 (HARD, structural) — the runner has no mid-gate resume, and Phase 2 requires one

Phase 2 instructs the child to *"STOP and push STATUS=HALTED"*, after which *"the operator … resumes
the gate."* **There is no resume.** `grep -c resume bin/wrought-runner` → **0**. `run_gate_child()`
is a single `subprocess.Popen(claude -p …)` followed by `proc.wait()`. A `claude -p` turn that stops
has exited.

What would actually happen: the child exits after Phase 1 → the runner verifies postconditions →
no bundle, QUEUE row not `BUNDLED` → **gate FAIL**, row set to `HALTED`, `consecutive_failures`
incremented → **Phases 3 and 4 never run**, and the gate needs a fresh dispatch. That is the
`RESET` shape that cost `GATE-J0B-SURFACE` seven days.

**Recommended shape — split the gate at the handoff, which is where it already divides cleanly:**

- **`GATE-J0B-CLOSE-A`** — Phase 1 only (schema + `authproxy3.py` + unit tests against the mock),
  no key, no locked guest. Bundles normally.
- *(operator relaunches the proxy with `authproxy3.py` between the two — a between-gate action, not
  a mid-gate one, which is the shape the runner already supports and the shape J-164 requires
  anyway: **the key-holding proxy must PREDATE the runner start** so it lands in the reaper's
  before-set.)*
- **`GATE-J0B-CLOSE-B`** — Phases 3–4 against the already-running authproxy3.

A single gate could only work if the operator launched `authproxy3.py` **before** the run — which is
impossible, since Phase 1 is what writes it.

**One thing the split gets right for free:** the proxy's listener is keyed by address in the reaper's
snapshot, so an operator who relaunches on the same `127.0.0.1:8081` between gates is in the
before-set of gate B and is never mistaken for residue. **If the operator relaunches on a different
port, it WILL be flagged as new residue and latch `gate-residue`.** Same port, or say so in the prompt.

---

## B-3 (CORRECTNESS — and it narrows a claim this box shipped yesterday)

`GATE-J0B-CLOSE` would be the **first real gate to run under the scoped-`Bash` convention**
`GATE-RUNNER-POLISH` armed on 2026-08-29. That gate proved the convention with **one bare
`Bash(touch:*)`** and generalised to *"scoped-`Bash` + `ADD-DIRS` is a real fence"*. Two probes
through the real runner (`raw/02`, two paid children, $0.32 total) narrow it:

**(a) A scoped allowlist permits only BARE, SINGLE-COMMAND invocations.** Eight shapes attempted,
ground truth = canaries on disk:

| shape | example | result |
|---|---|---|
| bare command | `mkdir -p DIR` | **ALLOWED** |
| interpreter | `python3 -c "open(F,'w')…"` | **ALLOWED** |
| redirect | `echo plain > F` | **DENIED** |
| redirect | `sha256sum F > OUT` | **DENIED** |
| pipe + redirect | `cat F \| grep plain > OUT` | **DENIED** |
| `&&` chain | `ls DIR && echo chained > F` | **DENIED** |
| `;` sequence | `echo x > F; cat F` | **DENIED** |
| not allowlisted | `find DIR -name '*.canary' > F` | **DENIED** |

**Every denial above is of a shape whose constituent commands were all on the allowlist.** A gate
cannot run `sha256sum * > SHA256SUMS` under a scoped allowlist — which is a step this prompt's own
Phase 4.2 requires. Work has to go through `python3 -c` or the `Write` tool.

**(b) `Bash(python3:*)` ESCAPES THE `--add-dir` PATH BOUNDARY ENTIRELY.** With `ADD-DIRS` naming one
tree, a child was asked to write inside it and outside it. **Both succeeded. Zero denials.** The
target path lives inside the interpreter's `-c` program text, so the permission layer never sees a
path to check.

**This prompt grants `Bash(python3:*)`, so its `ADD-DIRS` is advisory, not enforced.** That is
probably acceptable for this gate — it is not a containment gate — but it must be *known*, and the
rails must not claim otherwise.

**Corrected by addition** (rails §12.2.1, `docs/PHASE-J-STATE.md`, and a note appended to
`bundles/GATE-RUNNER-POLISH/ADJUDICATION.md`), with the over-broad sentences left standing per
rails §4. **The controls are real and correctly armed; the claim about what they constrain was too
broad — the same over-generalisation `GATE-RUNNER-POLISH` corrected in `runner-arm/raw/31`,
committed one level down by the gate doing the correcting.**

---

## R-1 (calibration) — no `MAX-BUDGET-USD:` header

The prompt declares none, so the budget falls back to `limits.max_budget_usd_per_gate` = **$8.00**.
Correct, and worth stating plainly: **the gate whose job is to re-calibrate that cap runs under the
un-recalibrated cap**, which `GATE-RUNNER-POLISH` flagged as having been set from a *wedged* gate.
Not a blocker. If the split of B-2 is adopted, gate A is cheap and gate B carries the guest work;
declaring an explicit `MAX-BUDGET-USD:` on each would make the clean-cost measurement cleaner still.

## R-2 (stale premises in the box's own docs, found while checking the prompt's assumptions)

Everything the prompt needs is present and verifies (`raw/03`), but two `docs/PHASE-J-STATE.md`
OPEN items are **stale** and should not be carried forward:

- *"`cloud-image-utils` is load-bearing … but is ABSENT from `pins.lock`"* — **it is present**,
  `pins.lock:617`, `cloud_image_utils: "0.33-1build1"`.
- The residue list says `GATE-RECONCILE` deleted J0B's overlay and seed. **Both exist again**:
  `overlay-resume.qcow2` (837 MB) and `seed.img`, written by `GATE-J0B-RESUME` on 2026-08-28. They
  are that gate's residue, not RECONCILE's, and Phase 1 rebuilds both anyway.

**Verified good:** base image sha256 `0533b065…40ffe` matches the pin **on disk**; goose is pinned
(`v1.46.0`, asset sha256 `a1cf4856…5a7b` — the value the prompt quotes); `/var/lib/wrought/j0a/user-data`
and `j0a_key` survive for the seed rebuild; and every binary the scoped allowlist names exists
(`qemu-system-x86_64`, `qemu-img`, `cloud-localds`, `ssh`, `scp`, `curl`, `tar`, `tee`, `ss`).

## What the pre-flight did NOT do

It did not run any phase of the gate, touch the sealed credential, boot a guest, or write anything
under `/var/lib/wrought/j0b`. The two probe children ran on a **scratch courier and scratch
`state_dir`**; the real breaker and ledger are untouched. It did not set the QUEUE row to
`APPROVED`, and did not apply the B-1 runner fix.

## Evidence

| File | What |
|---|---|
| `raw/01-prompt-through-the-runners-own-parsers.txt` | B-1, R-1 and the resume check, from the runner's own code |
| `raw/02-scoped-bash-command-shapes.txt` | B-3 — both probes, with the children's denials and disk ground truth |
| `raw/03-substrate-and-pins.txt` | R-2 and the verified-good list |

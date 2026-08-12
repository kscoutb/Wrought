# REPORT-HJ1 — GATE-HJ1-HYGIENE, 2026-08-12

**Executor:** Claude Code on forge-mini (Opus, ultracode). **Prompt:** `GATE-HJ1-HYGIENE-v1.1.md`,
delivered **as a file** — the J-156 recommendation, actioned by the operator.
**Standing ruling:** hygiene precedes capability. J0b was held until this closed.

**Transport integrity check — PASSED before any work began.** The prompt declared **exactly two**
indented command blocks; two were present, both intact and non-empty (the Phase 1 health block, 3
commands; the Phase 6 dual `git status --porcelain` block, 2 commands).

**Operator's added step, executed:** the prompt file was moved out of the foundry tree to
`/home/kalib/` before work started, so the Phase 6 clean-tree check could not be polluted by the
prompt itself. It is archived in the courier regardless.

---

## Outcome

| | |
|---|---|
| **Foundry commits** | `624f1b907572940d8e05783884c5e9fc2cbbd6fe` — *pins: virtualization substrate ratified (GATE-J0A); goose selected pending J0B*<br>`bc273598ddc89ba335dcd91327b3328fb700bfed` — *docs: executor rails + phase-j state, journal J-157 (GATE-HJ1)* |
| **Courier commits** | `d1ed726` — *courier: archive GATE-HJ1-HYGIENE v1.1, set RUNNING* (**pushed**)<br>*courier: GATE-HJ1 bundle* — **pushed**; its sha is reported to the operator and is `HEAD` of the courier repo. It cannot appear in this file: this report is hashed into `SHA256SUMS` *before* the commit that carries it exists |
| **Byte freeze** | **HELD.** `raw/00` vs `raw/99`: identical sha256, size and mtime on `orchestrator.db{,-wal,-shm}` |
| **Both trees** | `git status --porcelain` **empty** in foundry and courier |

**On "the two pushed commit shas": the foundry repo has no remote** (`git remote -v` is empty) — by
design; the courier README states the foundry source tree never leaves the box. So the foundry shas
above are **local commits**, and only the courier was pushed. Reported this way rather than
inventing a push that did not happen.

## Phase 1 — baseline

Service `active`; `/health` **200**; dGPU found by device id `0x744c` at `/sys/class/drm/card0`,
`vram_used=19619987456` (≈18.3 GiB — the model is resident). `raw/01`.

## Phase 2 — the substrate pins are ratified

Round 2's proposals are the measured reality and supersede the v1.1 candidates (whose versions were
`apt-cache policy` **candidates** from a set that was never installed). **Every value was
re-derived on the box at ratification time rather than copied forward from a two-day-old proposal**
— J-95 says the pin carries the command that made *it*.

| checked | command | result |
|---|---|---|
| the 8 named packages | `dpkg-query -W` (`raw/02`) | **8/8** `install ok installed`, at **exactly** the versions round 2 measured |
| the 43-package closure | `dpkg-query -W` (`raw/03`) | **43/43** `install ok installed` |
| closure list vs `dpkg-query` | sorted-set diff (`raw/07`) | **0 additions, 0 omissions, 0 transcription errors** |
| systemd baseline | `dpkg-query -W` (`raw/02`) | all five at **`259.5-0ubuntu3.4`** |
| holds | `apt-mark showhold` (`raw/02`, `raw/04`) | **empty** |
| dpkg entry count | `dpkg-query -W -f='.\n' \| wc -l` | **1872**, corroborating round 2's 1821 → 1872 (+51) |

**The closure is pinned at versions, not just names.** The proposal enumerated the 43 by name only;
`pins.lock` is *the version source of truth*, and pinning 8 of 51 would have been the same
under-coverage defect the J0A acceptance record calls out. **`substrate_systemd_baseline` is part of
the pin**: `libvirt-daemon-driver-qemu → systemd-container` carries a strict equality on
`libsystemd-shared`, so the same eight names on a box at `259.5-0ubuntu3` produce a different — and
aborting — transaction. That abort *was* J0A round 1.

**Two ratified policies, each with exactly one home**, `docs/10` §18.7 carrying pointers only:

- `substrate.os_update_policy` — the OS substrate **tracks `resolute-security`** via
  `unattended-upgrades` (**enabled**, `Package-Blacklist` **empty**, no holds — `raw/04`); drift is
  **recorded per gate, not fought** (U-1).
- `virtualization.guest_base_image.gpg_signature: WAIVED-OPERATOR-RULING-2026-08-11` — recorded as a
  **greppable key**, following the `litestream.sigstore_attestation` idiom, so the supply-chain rule
  shows a *decision* rather than a silent omission. Residual risk stated at the pin: a hash binds the
  artifact to bytes served over TLS at one moment, **not to a publisher identity**.

### The policy immediately found something — an unrecorded kernel drift

    uname -r                       # 7.0.0-29-generic
    grep '^  kernel:' pins.lock    # 7.0.0-28-generic

`raw/05`. **`substrate.kernel` was NOT edited** — moving a pin by typing is precisely how ST-1 gets
marked satisfied without being run. It is recorded in `substrate.os_update_policy.drift_observed`
with its command, and **ST-1 now carries two independent unsatisfied triggers**: this kernel bump,
and J0A's AppArmor `5.0.0~beta1 → 5.0.2` jump underneath the oracle's own `bwrap` (SURPRISE S-1),
which was smoke-tested only — `bwrap --unshare-all` still builds a clean netns, but the GATE-23/25
exit-code taxonomy was **never re-classified**. **This is a gate question surfaced, not answered.**

## Phases 3–5 — one canonical home per rule

- **`docs/EXECUTOR-RAILS.md` (new).** The invariant rails, so a prompt can say *"read the rails"*.
  Where a rule already had a home it **points**: `docs/06` §14.4 (secrets), `docs/07` ST-7 (evidence
  commits), and the courier README (protocol — **referenced, never copied**; only the two facts an
  executor needs to plan a session are restated). The one genuinely new rule recorded there had no
  home anywhere: **a secret reaches a command on stdin only** — never `argv`, never env, never a
  config file, **never inside a guest**.
- **`docs/PHASE-J-STATE.md` (new).** The live rail position in one page: CLOSED / ESTABLISHED FACTS
  / RESIDUE / RULINGS / OPEN / ADVISOR-SIDE NOTE.
- **`CLAUDE.md`** — pointers only: **3 insertions, 1 deletion** (`raw/09`).

## Verification — because a docs session can still break a gate

`pins.lock` is parsed as YAML by `bin/soak3-*` and other gates, so the edit was checked with the
**exact parser**, not by eye (`raw/06`): `YAML(typ="safe", pure=True)` under
`/opt/wrought/venv-orch/bin/python`, with **round-trip assertions** on the epoch versions
(`1:10.2.1+ds-1ubuntu3.2`), the image sha256, and the upstream timestamp — **quoted deliberately**,
since an unquoted `2026-08-01T13:17:55Z` resolves to a datetime and stops comparing equal as text.
`substrate.kernel` was asserted **unchanged** in the same pass.

Pack identity unaffected: `bin/gen-pack --check` → `packs/py.toml matches pins.lock
sha256=37d1c39c…` (`raw/07`).

**Placement was load-bearing.** The `virtualization:` block was inserted **before** `models:`, not
appended, because `bin/make-session-19-bundle:57` awks from the GATE-44 header **to end of file** —
an append would have silently changed a historical bundle's content.

## Adversarial audit — 7 checks, 3 findings, all fixed before this report shipped

| # | check | result |
|---|---|---|
| 1 | Does the closure pin cover what "at installed versions" claims? | **FINDING — fixed.** The first plan pinned 8 of 51. The 43 were re-measured (`raw/03`) and pinned with versions. |
| 2 | Does the `pins.lock` edit survive the real parser, not just look valid? | Passed after being made a test: 8 round-trip assertions, all OK. |
| 3 | Does the edit move any pack hash or existing pin? | No. `gen-pack --check` green; `substrate.kernel` asserted unchanged. |
| 4 | Does appending to `pins.lock` disturb any consumer? | **FINDING — avoided.** `make-session-19-bundle` awks to EOF; block inserted mid-file instead. |
| 5 | Does `PHASE-J-STATE.md` claim GATE-HJ1 is closed? | **FINDING — fixed.** It did. Closure is the advisor's call, so the row now reads **BUNDLED, awaiting adjudication**. |
| 6 | Does every dictated literal check out against the repo? | `pids.peak=112` ✓, B-1 "one `chown` from closed" ✓, J-155/J-156 present ✓. **`STOP-44` has ZERO anchors** repo-wide (highest recorded: STOP-43) — recorded as a *reserved number, not a reference*. |
| 7 | Do the new docs duplicate a rule that already has a home? | No — §14.4, ST-7 and the courier README are referenced. The stdin rule is genuinely new and is stated once. |

## Deliberate dispositions the advisor should rule on

1. **This gate's evidence is NOT committed to `build-evidence/hj1/`.** The prompt routes it through
   the courier instead, and the courier is a git repo — so the ST-7 property (immutability,
   timestamp, diff) is satisfied, in a *different* repo. Flagged rather than silently decided,
   because J-155's lesson was evidence living outside any repo.
2. **`docs/10` gained a new §18.7 ("Selected — not yet adopted")** rather than filing Goose under
   §18.3 ("Adopted — conditional"), which would overstate it. Goose's **licence and version are
   deliberately unpinned** — asserting either would be inventing a value.
3. **`STOP-44` was written into the state doc as unratified with no anchor**, rather than omitted.

## What this session did NOT establish

Nothing about the substrate was re-**exercised** — the re-verification is `dpkg-query` against
installed state, **not** a re-run of any J0A phase. **GPU passthrough remains untested. Guest egress
control remains untested**, and round 2's own capture shows generic guest egress **succeeding** (204),
so an agent surface placed inside that guest currently has a path out. **Goose is selected, not
adopted** — nothing installed. No model was loaded and no token generated, so **escalation rate —
P1, the governing metric — is not measured here.**

## Bundle

`REPORT-HJ1.md` + `raw/` + `SHA256SUMS` (written last; it does not cover itself). Text only, no zip.
`raw/` files each begin with the command that produced them.

| file | contents |
|---|---|
| `00-byte-freeze-baseline.txt` / `99-byte-freeze-reassert.txt` / `99b-byte-freeze-verdict.txt` | the freeze, both ends, and the mechanical diff |
| `01-phase1-health.txt` | Phase 1 block, run verbatim |
| `02-pins-reverify-dpkg.txt` | the 8 named + systemd baseline + holds + dpkg count |
| `03-closure-dpkg.txt` | the 43-package closure at installed versions |
| `04-u1-posture.txt` | unattended-upgrades / blacklist / holds / suites |
| `05-drift-check.txt` | kernel, mesa, apparmor, userns restriction |
| `06-pins-yaml-validate.txt` | parser + round-trip assertions |
| `07-genpack-and-closure-crosscheck.txt` | `gen-pack --check` + the 43/43 and 8/8 cross-checks |
| `08-pins-lock-diff.txt` / `08b-cots-diff.txt` / `09-claude-md-diff.txt` | full diffs |
| `10-peer-session.txt` | the idle peer session, measured |
| `11-foundry-commits.txt` | both foundry commits with stats |

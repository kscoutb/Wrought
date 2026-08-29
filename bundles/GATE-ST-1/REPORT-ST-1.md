# REPORT — GATE-ST-1: substrate self-test + drift disposition

**Date:** 2026-08-29 · **Mode:** ATTENDED-DIRECT (not through `wrought-runner`) · **Advisor:** Fable
**Verdict: PASS.** Both unsatisfied ST-1 triggers are dispositioned. Byte freeze **HOLD**.
**No divergence, no canary trip, no corruption signature. D13 is NOT implicated.**

---

## The headline, stated as what was actually measured

The substrate drifted (kernel `7.0.0-28` → `-30`, AppArmor `5.0.0~beta1` → `5.0.2`) and the
served model is **bit-for-bit unchanged in its behaviour** on the trigger set:

| measurement | result | raw |
|---|---|---|
| Phase 1 device assert (5 clauses) | **PASS**, every clause | `raw/02` |
| Binary + model provenance vs `pins.lock` | **exact**, 3 of 3 hashes | `raw/03` |
| **CONTROL** — today CPU vs 2026-08-02 CPU | **4/4 byte-identical** | `raw/06` |
| **KERNEL DRIFT** — today GPU vs 2026-08-02 GPU | **4/4 byte-identical** | `raw/09` |
| GATE-16 proper — CPU vs GPU, today | 3/4 identical, 1 known-benign | `raw/10` |
| The one divergence, adjudicated | **exact reproduction of the Aug-2 case** | `raw/11` |
| AppArmor half — GATE-21 bwrap smoke | **PASS 9/9** | `raw/12` |
| Extraction canaries | **16/16**, both arms | `raw/13` |
| Byte freeze (§2.1, box's own duty) | **HOLD** | `raw/00`, `raw/99` |

## What made this sharper than the gate asked for

The prompt specified a CPU-vs-GPU diff. That test is real but **confounded**: it compares two
backends, and J-40 already measured that the two disagree benignly through floating-point
non-associativity. A CPU-vs-GPU divergence therefore cannot cleanly answer "did the kernel
break the model?"

`raw/03` opened a better test. `llama-server`, `llama-cli` and the 16.68 GiB GGUF all hash
**bit-for-bit to their `pins.lock` values**, and Mesa is unchanged. So against the 2026-08-02
GATE-16 run, binary + model + batch shape + the four verbatim trigger prompts are **all
constant, and the kernel is the only variable**. Both runs are fresh-process first request,
which §11.2 measured to be byte-reproducible 16/16 — so the ordinal is fixed and benign
argmax flips are excluded *by construction* rather than by argument.

That diff is the direct measurement of the bump, and it came back **byte-identical on all
four prompts, 27 days apart**. The CPU arm gives the same answer independently (`raw/06`),
which also proves the fixture itself did not drift.

## The one divergence, and why it is not D13

`raw/10` found exactly one CPU-vs-GPU disagreement: prompt `struct`, first differing token at
**index 85 of 96**. The build rail records the 2026-08-02 run diverging on **the same prompt
at the same index**, decoding to `" primes"` vs `" prime numbers"`.

Today (`raw/11`): GPU `"List the first 10 primes:"` vs CPU `"List the first 10 prime numbers:"`
— first divergent index **85**, total divergent positions **11**, and the divergent-position
**set is identical** to 2026-08-02's. Both coherent English; no corruption signature on any of
the 8 outputs.

This is the case J-40 examined and **retired the byte-identity criterion over**, reproduced
exactly. Under the ratified criterion it is a PASS: (a) GPU self-reproducible across fresh
processes — proven by `raw/09`; (b) no corruption signature; (c) the divergent token is a
near-tie coherent alternative, not noise.

### A criterion conflict, resolved by the prompt's own instruction

The prompt's fallback methodology says **"Any divergence = corruption on this substrate"**,
and would have tripped a HARD STOP and the Devstral fallback on the `struct` prompt. That bar
is the one `docs/07-build-rail.md:139` marks **RETIRED** and `docs/03-verification.md`
SPEC-R11.1 replaced, on operator-ratified measurement (J-40). The fallback text predates it.

It never activated, because the prompt's *first* Phase-2 instruction is "use the project's
existing ST-1 harness **if one is defined**" — and one is:
`build-evidence/gate-16-17/gate16-17-19-correctness`. The prompt resolved itself. Recorded
because a future reader of that fallback paragraph will hit the same conflict. Two other
clauses in it would also have misfired: `llama-cli` (whose TUI produced a 1.37 GB file of
banner junk when GATE-16 tried it) and `-ngl 0` (F-31: may still touch the GPU; `--device
none` is the verified CPU arm).

## What was run, and what was deliberately not

A **trimmed copy** of the Aug-2 harness (`st1-correctness`, diff at `raw/04`; **the original
is untouched**). ST-1 is defined as `GATE-11 + GATE-16 + canary suite`
(`docs/07-build-rail.md:464`), so GATE-17's 20× determinism sweep and GATE-19's MTP promotion
were **dropped, not run-and-ignored** — GATE-19 alone would have loaded two more GPU servers.

## The operator lever this gate needed

The GPU arm needs ~18.3 GiB VRAM; only 5.71 GiB was free because the resident service holds
the rest. The ratified criterion requires **both** arms at fresh-process first request, so
querying the live instance was not an acceptable substitute — it would manufacture the very
ordinal flips the criterion exists to exclude, and it would need the sealed API key rails §5
forbids the box from touching. Rails make `wrought-*` units read-only to the box, so this was
put to the operator, who authorized the box to stop and restart it.

Full transcript with timestamps: `raw/07`. **Downtime ≈ 50 s**; restored `active`,
`NRestarts=0`, 18.27 GiB resident again, listening on `127.0.0.1:8080`.

## WHAT THIS DID NOT ESTABLISH

Full detail in `raw/14`. The load-bearing limits:

- **A-2 — there is no long-context trigger prompt.** SPEC-R11.1 names three families:
  technical/math, code, **and long-context**. The Aug-2 harness implements math/code/reason/
  struct; `reason` and `struct` are both short. **The long-context family is untested here, as
  it was at GATE-16.** This is a pre-existing gap in the trigger set, surfaced not absorbed.
  Long context lives in GATE-18 and in the §11.1 32K/64K ordered-recall probe — neither ran.
- **A-3 — the window is 96 tokens.** Corruption beginning after token 96 is invisible to every
  diff here. The baseline used the same 96, so the *drift* comparison is sound; it is the
  absolute claim "the model is correct" that is bounded.
- **A-4 — the PRIMARY canary layer did not run where §11.1 puts it.** §11.1 binds extraction
  canaries to the **resident** server; they ran here against fresh-process outputs, because the
  resident instance needs the sealed API key. **ST-6** (weekly canary against the live warm
  server) covers that layer and remains the operator's to run. The canaries also add little
  independent signal here, since exact-match already passed 4/4 on the same outputs — said
  plainly rather than counted twice.
- **A-5 — "AppArmor validated" is narrow.** GATE-21 covers the sandbox building and staying
  offline. It does **not** re-classify the GATE-23/25 exit-code taxonomy, which pins.lock:571
  flags as not re-done. That half stays open.
- **A-1 (latent, worth fixing) — the harness depends on a `-ub` default it does not pin.** It
  passes `-b 2048` but not `-ub 512`, relying on the binary's default (verified 512, so the
  shape *is* the pinned one, and both sides of the diff share it regardless). But a future
  llama.cpp bump that changes that default would silently move the shape out from under the
  canaries. Recommend passing `-ub 512` explicitly; not edited here, since the harness is
  Aug-2 evidence.
- **The kernel headers are still gone.** pins.lock:568 records that the same transaction that
  installed -30 removed `linux-headers-7.0.0-28`. Validating -30 does **not** restore -28's
  rebuildability. Unresolved half of that drift entry.
- **The 15 libvirt point-release pins** are untouched and still an open advisor question.

## Disposition

Both ST-1 triggers dispositioned; **`PROPOSED-PINS-DELTA.md`** carries the exact diff.
**Not applied** — the prompt says re-pin in Phase 3, propose in Phase 4, and its rails line
says the re-pin commit is operator-authored; the box prepared the diff and left authorship to
the operator. Note the AppArmor "re-pin" **cannot be a move**: no `apparmor` key has ever
existed in `pins.lock`, so it is a new key or a drift-entry edit, and the box will not invent
a configuration key. Both options are laid out.

---

## CORRECTION BY ADDITION (same session, before adjudication)

**"The kernel was the only variable" — as written above and in `PROPOSED-PINS-DELTA` §1 — is
too broad.** What this gate *verified* is the **held-constant** set: `llama-server`, `llama-cli`
and the model GGUF by sha256, Mesa by version, the batch shape, and the four trigger prompts.
It did **not** enumerate the full *changed* set: alongside the kernel, the box also took
AppArmor `5.0.0~beta1` → `5.0.2` and the 15-package libvirt closure, plus 27 days of other
unattended-upgrade movement this gate never listed.

**The accurate claim is the stronger one.** With `{binary, model, Mesa, shape, stimulus}` held
constant and verified, what varied is **the substrate as a whole**. Byte-identical token
streams across that is a *broader* validation than "the kernel did not break the model" — and
it is exactly what ST-1 exists to assert. The compressed phrasing simultaneously over-claimed
the isolation and under-claimed the result.

Recorded by addition rather than by editing the sentences above, following the precedent set
when `GATE-RUNNER-POLISH`'s own over-generalisation was narrowed. Full statement: `raw/14` A-8.

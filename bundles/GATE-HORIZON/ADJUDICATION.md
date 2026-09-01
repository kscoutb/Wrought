# GATE-HORIZON — ADJUDICATION

**Recorded by `GATE-BUILD-01` PHASE 0, 2026-09-01**, as its first courier action, per
`docs/EXECUTOR-RAILS.md` §10 — the advisor cannot push to the courier, so an adjudication arrives
inside the next prompt and is recorded on arrival.

**Source:** `prompts/GATE-BUILD-01.md`, section `## PHASE 0 — record the GATE-HORIZON verdict`.
**Extraction was MECHANICAL, never retyped** (rails §10):

    sed -n '/^## PHASE 0 — record the GATE-HORIZON verdict$/,/^## PHASE 1/p' \
        prompts/GATE-BUILD-01.md | sed '$d' | sed -n '2,$p' | sed '/^$/d'

Evidence of the extraction, and of the re-verification below:
`bundles/GATE-BUILD-01/raw/01-horizon-verdict-extracted.txt` and
`bundles/GATE-BUILD-01/raw/02-horizon-reverify.txt`.

## THE VERDICT, VERBATIM

> Re-verify against `bundles/GATE-HORIZON/` on the courier. VERDICT: **GATE-HORIZON ACCEPTED** (advisor 2026-09-01), exemplary. Both review streams landed and published; five non-Anthropic ZDR lineages carried the synthesis for $0.7749 of $15; the roadmap and research questions are published. The resident 27B produced **113 RELIABLE grounded file summaries of 127** (14 uncheckable, zero invented sampled) — the first real bulk work by the local model, well past the 5-byte write. Recorded honestly: **two advisor-supplied instruments were defective and both were caught by RUNNING them** — `run-panel.py` selected a 4B model by shortest slug (excluded, topped up correctly), and `run-local.py` passed `max_tokens=512` to a reasoning model and got empty summaries (fixed, re-run). Rails §18 three times. Write this to `bundles/GATE-HORIZON/ADJUDICATION.md`, set that QUEUE row `ADJUDICATED`, commit, push.

**Status: `ACCEPTED`. The gate is CLOSED.** Its `QUEUE.md` row moves to `ADJUDICATED` and, being
terminal, collapses to one line with its full text moved byte-for-byte to `QUEUE-ARCHIVE.md`
(rails §17).

## RE-VERIFICATION — the prompt asked for it, so it was done rather than assumed

The verdict is the advisor's and is recorded as given. What follows is `GATE-BUILD-01` checking the
bundle's own load-bearing numbers against the bundle, mechanically, because *"re-verify against
`bundles/GATE-HORIZON/`"* is an instruction and not a courtesy. Full capture with the exact
commands: `bundles/GATE-BUILD-01/raw/02-horizon-reverify.txt`.

| Claim | Command | Result |
|---|---|---|
| 168-entry manifest verifies | `sha256sum -c SHA256SUMS` | **exit 0, 168 `OK`, 0 `FAILED`** |
| byte freeze HOLDS | `diff` of the 64-hex lines in `raw/00` vs `raw/99` | **exit 0, zero bytes of output** |
| 127 files summarized | `ls repo-map \| wc -l` vs `wc -l tools/file-list.txt` | **127 and 127** |
| 113 RELIABLE of 127, 14 uncheckable | `groundedness.json` `counts` | **`{UNCHECKABLE: 14, RELIABLE: 113}`, 127 results** |
| `$0.7749` panel spend | sum of `usage.cost` over the six shipped `*.raw.json` | **`0.7749` exactly, n=6** |
| five lineages carried, one excluded | the six cost rows | five carried; `google/gemma-3-4b-it` at `$0.0038` is the excluded one |

**AND ONE THING WORTH RECORDING THAT NOBODY ASKED FOR.** `GATE-HORIZON`'s `raw/00` hashes are
**byte-identical to `GATE-BUILD-01`'s own `raw/00`**, taken independently a day later:

    6600fe63…8fde   orchestrator.db
    e3b0c442…2b855  orchestrator.db-wal
    fd4c9fda…89eb   orchestrator.db-shm

So the production store has not moved across two gates and the interval between them. That is a
stronger statement than either gate's own freeze makes on its own, and it is free.

## WHAT THIS ADJUDICATION DOES NOT DO

It does not adopt the roadmap. `GATE-HORIZON`'s own `NON-CLAIMS` block says the consolidated
roadmap is a **CANDIDATE** and that **not one panel finding was verified against the code**. What
`GATE-BUILD-01` PHASE 1 locks is not that document: it is that document **amended by the
operator's eight rulings**, which are the M0 scope-freeze and which settle several things the panel
left open — including the 2-vs-2 sequencing split, which the operator and advisor resolved as
*measure manufacturing and escalation (M2) before the Face B redesign (M3), with nothing
adversarial or unattended-in-production shipping until Face B is closed.*

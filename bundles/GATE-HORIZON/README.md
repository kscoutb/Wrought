# review/horizon — GATE-HORIZON artifacts, and a warning about two of the scripts here

**READ THIS BEFORE RE-RUNNING ANYTHING IN THIS DIRECTORY.**

`run-panel.py` and `run-local.py` are `GATE-HORIZON`'s prompt appendices, extracted **verbatim**
(`sed` over the operator's `GATE-HORIZON-COMPLETE.md`, `diff`-proven byte-identical to the appendix
ranges). They are kept as delivered because the prompt said *"write exactly"* and because the
appendix bytes are evidence.

**Two of them are DEFECTIVE, measured by running them. Both defects print success.**

## 1. `run-panel.py` — selects panelists by SHORTEST SLUG. Do not re-run as-is.

`pick_models()` sorts candidates by:

    ("pro" in s or "thinking" in s or "reasoning" in s, len(s))

so the prompt's *"prefer non-`-pro` variants"* is implemented as **"prefer the shortest slug"**.
On 2026-08-31 that selected **`google/gemma-3-4b-it` — a 4B model — to perform a staff-level
architecture review.** Its output is **confabulated**: it reports media generation, library
organisation, avatar replacement and a screenshot-plus-vision loop as *working*, against a packet
stating *"Media generation / vision / computer-use — **Nothing. No component of any kind**."* It
read the VISION wish-list as the as-built inventory. The review and its raw JSON are both kept so
the claim is checkable rather than asserted.

It also has no per-model context check, so it sent a ~99,760-token request to
`deepseek/deepseek-r1`, whose endpoint caps at **64,000** → hard **HTTP 400**.

**Use `run-panel-topup.py` instead**, or fix the sort. `run-panel-topup.py` documents both defects
in its own docstring and uses **explicit slugs verified present in the live
`GET /models?zdr=true` listing at run time** — nothing invented. Its credential discipline is
carried over unchanged: the key exists only in the HTTP `Authorization` header, read from the
service-private `$CREDENTIALS_DIRECTORY`.

## 2. `run-local.py` — the appendix version returns EMPTY SUMMARIES and exits 0.

The file here is **already patched**; `run-local.py.appendix-verbatim` is the unmodified original,
kept alongside so the deviation is auditable. The three deviations are documented in the patched
file's own docstring. The one that forced the others:

The served profile is `--reasoning on --reasoning-budget 24000`, and the appendix passes
`max_tokens=512`. The model spends the entire completion budget on reasoning and returns **zero
content** — while printing `summarized N/N files` and **exiting 0**.

| `max_tokens` | `finish_reason` | completion tokens | reasoning | **content** |
|---|---|---|---|---|
| 512 | `length` | 512 | 2,069 B | **0 B** |
| 2048 | `length` | 2,048 | 8,256 B | **0 B** |
| 25000 | `stop` | 2,254 | 8,230 B | **637 B** |

Run as written it produced three files, three empty. This is `docs/EXECUTOR-RAILS.md` §18 exactly:
**an exit code is not a success signal — verify the work product.**

## 3. How the local model is given its key

There is no plaintext key file on disk and none should ever be written. `LOCAL_KEY_FILE` takes a
**path**, and paths are public; the value only ever reaches the HTTP header. Run under systemd so
the path points at the service-private credentials tmpfs — the same route the manufacturing path
already uses (`bin/baseline-run`'s `read_inference_key()`):

    sudo -n systemd-run --unit=<name> --collect -p User=kalib \
      -p WorkingDirectory=/home/kalib/review-rc1 \
      -p LoadCredentialEncrypted=inference-api-key:/etc/credstore.encrypted/inference-api-key \
      /bin/sh -c 'LOCAL_KEY_FILE="$CREDENTIALS_DIRECTORY/inference-api-key" exec /usr/bin/python3 …'

**Launch long jobs as NAMED units.** A `systemd-run` **service** does not die with the shell that
started it — this gate leaked one from a timed-out tool call and had to tear it down by unit name
(rails §13.1, §15: signal an identity, never a pattern).

## What is here

| Path | What it is |
|---|---|
| `REPORT-HORIZON.md` | The gate report — start here |
| `CONSOLIDATED-ROADMAP.md` | **CANDIDATE** synthesis for the advisor. Not an adopted plan |
| `RESEARCH-QUESTIONS.md` | Seven research prompts a future gate could run as-is |
| `PANEL.md` | Panel roster, ZDR method, per-model spend, both runs |
| `<lineage>-<model>.md` / `.raw.json` | Each external review and its raw response |
| `LOCAL-BASELINE.md` | The resident 27B's own gap analysis — free, air-gapped |
| `REPO-MAP.md` | Local summaries of every `bin/` script and `src/` module, RELIABLE only |
| `repo-map/` | The individual summaries, including any excluded ones |
| `groundedness.json` | Per-summary fabrication check results |
| `packet/` | What the panel was sent, plus `PACKET-PROVENANCE.md` recording every cut |

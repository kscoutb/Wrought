# PACKET-PROVENANCE — what is in the packet, how big it is, and what was cut

**Two packets exist, and the reason is a measurement, not a preference.**

| Artifact | chars | REAL tokens | Fits the resident model? |
|---|---|---|---|
| `PACKET.txt` | 233,003 | **70,810** | **NO** — exceeds the served `n_ctx` of 65,536 outright |
| `PACKET-LOCAL.txt` | 107,423 | **34,032** | yes, leaving ~31,100 tokens for output |
| `ASK.txt` | 1,415 | 314 | appended after the packet in both cases |

Token counts are **measured with the served model's own tokenizer** (`POST /tokenize` on
`127.0.0.1:8080`), not estimated. The measured ratios are **3.16 chars/token** for the local
packet and **3.29** for the full one; `pins.lock`'s `input_token_estimator_chars_per_token: 3.0`
is a **cost estimator and not a tokenizer**, and using it here would have under-read the real
count. `n_ctx` was likewise read from `GET /v1/models`, not assumed from the launch flags.

## Members, in order

1. **`VISION.md`** — verbatim from the gate prompt, extracted with `sed` and `diff`-proven
   byte-identical to its source range. 1,891 B.
2. **`ARCHITECTURE.md`** — written by this gate, curating the repo-map. 13,192 B. It is an
   overview, not source: no raw local-model summary is shipped to any reader.
3. **`SECURITY-HISTORY.md`** — a digest of the internal review, the four-lineage external panel,
   and the two fix gates, so a reviewer does not re-litigate hardened ground. 8,302 B. It ends
   with the short list of what is genuinely still open.
4. **The live state** — `docs/PHASE-J-STATE.md` as stabilized by this gate, plus `pins.lock`.

## What `PACKET-LOCAL.txt` cuts, recorded rather than silent

Only member 4 differs. Nothing was rewritten or summarised; **whole blocks were dropped**:

- **`docs/PHASE-J-STATE.md`**: kept the header and the LIVE blocks — `REVIEW-READINESS`,
  `KNOWN-OPEN`, `NON-CLAIMS` (lines 460–655 of 769). Dropped the `CLOSED` table,
  `ESTABLISHED FACTS`, `OPEN`, and the two dispatcher addenda — per-gate history rather than the
  live position.
- **`pins.lock`**: comment and blank lines removed — **1,032 of 1,734 lines**, 129,607 → ~48,730 B.
  Every *value* is intact and unaltered; what was removed is the working-out that justifies them.

## The finding this produced, which is not incidental

**The system's own live state documentation does not fit its own resident model's context
window.** The full packet is 70,810 tokens against a 65,536 ctx — it does not fit *before* leaving
any room to answer. This is a direct, measured data point for the vision's capability (F),
"AI-managed context discipline": the project already treats context as an engineering discipline
(a size budget on the live files, narrative moved to an unread journal, a per-gate growth rate of
+7–9 KB), and it is *still* the case that the box cannot read its own state in one pass. Any 1.0
that expects the local model to carry work end to end inherits this problem on day one.

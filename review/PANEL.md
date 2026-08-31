# PANEL.md — the external review panel for `review-rc2` (`bbecf2d`)

One model per distinct lineage, **none of them Anthropic**. This code was written by Claude
and first reviewed by Claude; a second Claude adds little. The value sought here is
independent lineages disagreeing with us.

## ZDR — how it was confirmed, and a correction to the dispatching spec

The gate said to confirm zero-retention *from the model metadata*. **There is no such field.**
Neither `GET /api/v1/models` nor `GET /api/v1/models/{id}/endpoints` carries a data-retention
or privacy attribute — verified against both responses. What the API actually offers is two
mechanisms, and both were used for every call:

1. **Pre-flight membership check** — `GET /api/v1/models?zdr=true` returns the ZDR-eligible
   subset (286 of 396 models at send time). Each panel slug was required to be a member
   *before* the request was built; a non-member is skipped, never downgraded to a plain send.
2. **Router-side enforcement** — every request body carried
   `provider: {"zdr": true, "data_collection": "deny"}`, so OpenRouter refuses to route to a
   non-ZDR endpoint rather than silently falling back to one.

Account-level ZDR is the operator's setting and is not asserted here.

## Panel

| Lineage | Slug | ZDR | Status | Provider | in/out tokens | Cost |
|---|---|---|---|---|---|---|
| google | `google/gemini-3.1-pro-preview` | ✅ yes | OK | Google | 178718 / 25991 | $0.6693 |
| openai | `openai/gpt-5.6-sol-pro` | ✅ yes | OK | Azure | 708638 / 69793 | $7.3501 |
| deepseek | `deepseek/deepseek-v4-pro-0813` | ✅ yes | OK | Novita | 166804 / 47949 | $0.4101 |
| z-ai | `z-ai/glm-5.3` | ✅ yes | OK | Modal | 159990 / 37410 | $0.3886 |

**Total spend: $8.8181.** Script ceiling $12.00; the key's real
limit is $30 (`GET /api/v1/key` → `limit: 30`, `limit_remaining: 30` before the run). The
dispatching gate described the key as capped at $20 — the actual provisioned cap is $30, and
the run was bounded by the script's own $12 ceiling, below both.

Each call carried a pre-call cost bound (estimated input tokens × prompt price + `max_tokens`
× completion price); a call whose bound would cross the ceiling is skipped, not attempted.

## Settings common to every call

- `max_tokens: 64000` (all four models cap ≥65536), `reasoning: {"effort": "high"}` — the
  one effort tier all four support. Reasoning is *mandatory* on `gemini-3.1-pro-preview` and
  `glm-5.3`, and a smoke test confirmed a reasoning model will spend its entire token budget
  on thinking and return `content: null` if given no headroom.
- `usage: {"include": true}` — per-call `usage.cost` is returned inline and is the figure
  reported above; where absent the cost is computed from the endpoint's published pricing.
- The credential was read only from the systemd `$CREDENTIALS_DIRECTORY` tmpfs and existed
  only inside the HTTP `Authorization` header. Transport is in-process `urllib`, never
  `curl`, because `curl -H "Authorization: Bearer $KEY"` puts the key in `/proc/<pid>/cmdline`
  — the J-164 leak shape.

## The pre-call cost bound was unsound, and this run proved it

`openai/gpt-5.6-sol-pro` was bounded at **$0.94** and cost **$7.35** — an **8× underestimate**.
The other three landed at or under their bounds ($0.67 vs $1.07; $0.41 vs $0.45; $0.39 vs $0.49),
so this is not noise in the estimator. Two distinct mechanisms broke the bound, and both are
properties of the model class rather than of this script:

1. **`reasoning.mode: pro` re-bills the prompt.** The `-pro` slug is the same underlying model
   "served with `reasoning.mode` set to `pro`". Billed `prompt_tokens` was **708,638** for a payload
   the other three models measured at 160k–179k — roughly **4× the input, billed 4 times**, because
   pro mode runs multiple internal passes over the same prompt.
2. **`max_tokens` does not bound completion billing on a reasoning model.** Billed
   `completion_tokens` was **69,793** against `max_tokens: 64000`, of which **57,048 were
   `reasoning_tokens`**. Every panelist shows the same shape (Google 24,234 of 25,991; DeepSeek
   45,181 of 47,949; GLM 33,823 of 37,410) — reasoning dominates output and is not what
   `max_tokens` caps.

**Why this matters past this gate.** §13.5 requires a pre-call cost bound before any escalation,
and `bin/escalate-once` requires `--max-tokens` to be SET precisely so that bound is computable.
The formula used here — `est_input × prompt_price + max_tokens × completion_price` — is the obvious
one, and it is **wrong for exactly the model class you would escalate to for a hard problem.** A
bound that under-reads by 8× is not a bound. This is offered as an observation from this run, not
as a change to the escalation path; the escalation ledger was not touched by this gate.

The run stayed inside its ceiling ($8.82 of $12.00) only because just one of four panelists was a
`-pro` variant. Had all four been, the ceiling would have been breached while every individual
pre-call check still passed.

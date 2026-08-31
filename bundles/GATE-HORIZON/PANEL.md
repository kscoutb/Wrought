# PANEL — external gap-review
key limit_remaining at start: 21.18192496
ceiling: $15.0

| model | status | in | out | cost |
|---|---|---|---|---|
| google/gemma-3-4b-it | OK | 73415 | 1788 | $0.0038 |
| openai/gpt-5 | OK | 65994 | 7177 | $0.1543 |
| deepseek/deepseek-r1 | HTTPError 400: b'{"error":{"message":"This endpoint\'s maximum context length is 64000 tokens. However, you requested about 99760 tokens (59760 of text input, 40000 in the output). Please reduce the length of either one, or use the context-compression plugin to compress your prompt automatically.","code":400,"metadat' | 0 | 0 | $0.0000 |
| z-ai/glm-5 | OK | 66449 | 13549 | $0.1098 |
| x-ai/grok-4.6 | OK | 67292 | 9847 | $0.1935 |

**total spend: $0.4614**

## TOP-UP RUN — restoring two lineages the first run lost

The first run used Appendix A verbatim and lost two of five slots for two different reasons, both
caused by the script rather than by the models:

* **google** — `pick_models()` sorts by `("pro" in s or "thinking" in s or "reasoning" in s, len(s))`,
  so *"prefer non-`-pro` variants"* is implemented as **"prefer the shortest slug"**. It selected
  `google/gemma-3-4b-it`, a **4B model**, for a staff-level architecture review. Its output is
  **confabulated** — it reports media generation, avatar replacement and a screenshot+vision loop
  as working, where the packet states *"Nothing. No component of any kind."* It read the VISION
  wish-list as the inventory. **EXCLUDED from the consolidation, and named rather than dropped.**
* **deepseek** — HTTP 400. `deepseek/deepseek-r1`'s endpoint caps at **64,000 tokens**; the request
  was ~99,760 (59,760 input + 40,000 max output). A hard failure, not a bad review.

Both replacements were taken from the **live `GET /models?zdr=true` listing at run time** — nothing
invented — and both were the slugs this project's own `GATE-REVIEW` panel used on 2026-08-30. Both
carry ≥1,048,576 context, so the **full** packet fits: the 64k limit was `deepseek-r1`'s property,
not the deepseek lineage's, and no trimming was needed.

| model | status | in | out | cost |
|---|---|---|---|---|
| `google/gemini-3.1-pro-preview` | TOP-UP OK | 73481 | 4095 | $0.1961 |
| `deepseek/deepseek-v4-pro-0813` | TOP-UP OK | 68223 | 6902 | $0.1174 |

**top-up total: $0.3135** of a $5.00 ceiling.

## GRAND TOTAL

**$0.7749** across both runs, of the **$15.00** the operator authorized — **5.2 %**.
Six external calls, five distinct non-Anthropic lineages carried into the synthesis, one excluded.

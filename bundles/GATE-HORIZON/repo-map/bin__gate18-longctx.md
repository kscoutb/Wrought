# bin/gate18-longctx
Purpose: Validates LLM long-context state integrity via ordered-recall probes at 32K/64K depths and perplexity spread analysis across KV quantization configurations.
Key Functions/Classes: None (shell script); orchestrates `llama-server`, `llama-perplexity`, `curl`, and inline `python3` blocks.
Imports/Dependencies: Sources `$CONF`; depends on `$CLI`, `$PPL`, `$LLAMA_SERVER`, `$CORPUS`, `timeout`, `grep`, `sed`, `sha256sum`, `kill`, `wait`.
Risk: Fragile `grep`-based PPL extraction may break across `llama.cpp` versions; manual `kill`/`wait` loops and `timeout 5400` windows risk orphaned processes and VRAM exhaustion if interrupted.

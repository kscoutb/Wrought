# bin/gate16-fresh
Purpose: Isolates CPU vs GPU inference variance on fresh server startups by fixing request ordinal at 1, verifying absence of corruption signatures, and ensuring divergent tokens fall within a logit tolerance threshold.
Key functions/classes: `run_first`, `corrupt`, `top`
Direct imports/dependencies: `curl`, `python3`, `json`, `sys`, `re`, `grep`, `sed`, `LLAMA_SERVER`
Obvious risk: Background `llama-server` processes are managed via manual `kill`/`wait` without trap handlers, risking orphaned instances on interruption; brittle validation assumes strict CLI flag support and JSON response schemas.

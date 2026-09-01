# bin/wrought-course-post
Purpose: Sends a build summary to a pinned LLM provider for skeptical review, outputting exactly `OK` or `HALT` alongside `COST_USD`.
Key functions: `pin`, `main`.
Direct imports: `json`, `re`, `sys`, `urllib.error`, `urllib.request`, `Path`; reads configuration exclusively from `pins.lock`.
Risk: Broad exception handling and strict `pins.lock` parsing default to `HALT` on any config drift, network timeout, or unexpected JSON structure.

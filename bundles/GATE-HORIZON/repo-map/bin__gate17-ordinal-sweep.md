# bin/gate17-ordinal-sweep
Purpose: Validates that varying request ordinals on a resident `llama-server` yield benign, coherent outputs by sweeping prompts and comparing per-ordinal perplexity proxies against corruption/degeneration signatures.
Key functions or classes: `collections.defaultdict`, `collections.Counter`, `hashlib.sha256`, `re.search`, `math.exp`.
Direct imports/dependencies: `curl`, `python3`, `bash`, sourced `$WROUGHT_CONF` (`/etc/wrought/serving.env`), and the `$LLAMA` binary.
Obvious risk: Relies on hardcoded port `8093` and external env vars; inline Python uses minimal JSON validation, and the server startup/teardown loop may leave orphaned processes or abort silently if the `curl` health check fails.

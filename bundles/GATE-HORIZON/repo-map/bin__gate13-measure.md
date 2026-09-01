# bin/gate13-measure
Purpose: Benchmarks `llama-server` cold/warm load times, HMB presence, TTFT prefill curves, and chat template overhead against a <60s cold threshold.
Key functions: `stop_server`, `start_server`, `wait_ready` manage process lifecycle, explicit PID tracking, and `/health` endpoint polling.
Dependencies: Sources `"$CONF"`, executes `"$LLAMA"`, and relies on `curl`, `python3`, `bc`, `awk`, `systemctl`, and `sudo`.
Risk: Requires `sudo` privileges to flush page cache via `/proc/sys/vm/drop_caches`; forcibly aborts if `wrought-inference.service` is active to prevent port contention and accidental termination of resident processes.

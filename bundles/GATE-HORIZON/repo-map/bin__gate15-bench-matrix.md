# bin/gate15-bench-matrix
Purpose: Runs a two-lever benchmark matrix (CPU governor and GGML_VK_ALLOW_GRAPHICS_QUEUE) for pp2048 and tg128 metrics, computing median/stdev and enforcing a 2-4% noise-band threshold before declaring winners.
Key functions: set_governor, restore, bench_one.
Dependencies: llama-bench, llama-server, assert-power-profile, set-power-profile, python3 (json, statistics), sudo tee, grep, sed.
Risks: Direct sudo writes to /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; relies on trap restore EXIT INT TERM for cleanup, which may fail on SIGKILL or permission drift, leaving the system in an altered power state.

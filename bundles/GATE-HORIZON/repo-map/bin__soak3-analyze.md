# bin/soak3-analyze
Purpose: Generates the official SOAK-3 analysis report by comparing measured checkpoint metrics (slope, headroom, recovery cost, WAL, parity) against live pinned values from `pins.lock`.
Key functions: `pins`, `lstsq`, `r_squared`, `jl`, `track_a`, `track_b`, `main`.
Direct imports: `json`, `pathlib`, `sys`, `ruamel.yaml.YAML`, `collections.Counter`.
Obvious risk: Hardcoded absolute data path `/var/lib/wrought/soak3` and strict reliance on external `pins.lock`/JSONL schemas; potential division by zero in `lstsq` if variance `sxx` equals zero.

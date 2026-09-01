# bin/soak-curve
Purpose: Validates GATE-37's linear extrapolation by comparing measured per-event rebuild costs across soak checkpoints to determine if pinned headroom assumptions hold.
Key functions/classes: main()
Direct imports/dependencies: __future__, json, pathlib, sys
Obvious risk: Hard-coded absolute path /var/lib/wrought/soak1/checkpoints.jsonl and strict reliance on unvalidated JSON keys like rebuild_cold_ms and parity_differences will trigger KeyErrors or silent miscalculations if the checkpoint schema changes.

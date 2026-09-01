# bin/soak3-status
Purpose: Outputs a single decision-critical status snapshot for SOAK-3, reporting process liveness, halt flags, and progress metrics for tracks a and b.
Key functions or classes: No named functions or classes defined; inline Python block uses `json`, `sys`, and `SystemExit` to parse `status.json`.
Direct imports/dependencies: `json`, `sys`; external utilities `pgrep`, `head`, `tail`, `sed`, `wc`, `sha256sum`; interpreter `/opt/wrought/venv-orch/bin/python`.
Risks: `set -uo pipefail` lacks `-e`, permitting silent continuation after failures; `open(sys.argv[1])` omits context managers and may race with concurrent writers; `raise SystemExit(0)` inside `except` masks underlying parsing errors.

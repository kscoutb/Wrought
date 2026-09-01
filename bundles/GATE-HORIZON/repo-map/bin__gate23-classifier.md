# bin/gate23-classifier
Purpose: Test harness (GATE-23) that validates a substrate classification pipeline by inducing and synthetically simulating specific runtime failures (OOM, ENOSPC, timeouts, network attempts, and collection errors).
Key functions: `check`, `fixture_pack`, `run`, `make_task`, `main`.
Direct imports/dependencies: `importlib.machinery`, `importlib.util`, `json`, `os`, `re`, `pathlib`, `subprocess`, `sys`, `tempfile`, `time`, `vj` (dynamically loaded from `bin/verify-job`), `classify` (from `wrought_supervisor.classify`).
Obvious risk: Invokes `sudo` via `subprocess` for directory creation and systemd unit resets, dynamically executes external modules, and writes to system paths (`/var/lib/wrought/`, `/etc/wrought/`), creating privilege escalation and execution injection vulnerabilities if the harness or `vj` module is compromised.

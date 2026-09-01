# bin/gate29-security-offline
Purpose: Validates that adopted security tools execute fully offline with zero AF_INET/AF_INET6 connection attempts while still producing legitimate security outputs, enforced via `bwrap --unshare-net` and `strace`.
Key functions: `ok`, `run_offline`, `arm`, `main`.
Dependencies: `json`, `os`, `pathlib`, `re`, `shutil`, `subprocess`, `sys`, `tempfile`, plus invoked binaries `bwrap`, `strace`, `ruff`, `bandit`, `gitleaks`, `syft`, `osv-scanner`, `pip-audit`.
Risk: Hard-coded absolute paths (`/opt/wrought/venv/bin`, `/var/lib/wrought/osv-db`) and a 900s `subprocess` timeout make execution fragile to environment drift or tool hangs; `trace` parsing failures could mask harness measurement gaps despite explicit guards.

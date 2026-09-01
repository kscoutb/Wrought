# bin/secpack-freeze
Purpose: Freezes Bandit Python wheels and Go binaries (gitleaks, syft) into an offline verification environment while explicitly excluding pip-audit, then appends hashed requirements and updates pins.lock.
Key functions/classes: bash function say, inline python3 script importing pathlib, re, sys.
Direct imports/dependencies: sudo, install, tee, cp, grep, awk, sha256sum, pip, bandit, gitleaks, syft, pins.lock, requirements-frozen.txt.
Obvious risk: Executes privileged sudo -n operations across system paths; relies on exact comment string matching in pins.lock where minor drift triggers hard aborts, and silent no-ops from string mismatches are explicitly flagged as a critical failure mode.

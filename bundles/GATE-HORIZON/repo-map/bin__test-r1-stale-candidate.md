# bin/test-r1-stale-candidate
Purpose: Validates that the `wrought_supervisor` oracle verifier correctly rejects stale, tampered, or unreceipted candidates using a staging receipt mechanism across multiple test arms.
Key functions: `ok`, `sh`, `install_oracle`, `candidate_bytes`, `leave_behind`, `fresh_store`, `drive`, `main`.
Direct imports: `json`, `os`, `pathlib`, `shutil`, `subprocess`, `sys`, `tempfile`, `wrought_orchestrator`, `wrought_supervisor`.
Obvious risk: Executes `sudo -n` via `sh()` and directly modifies `/var/lib/wrought/` filesystem paths and `sys.path`, risking permission failures, live job interference, or test breakage if external oracle/candidate fixtures are missing.

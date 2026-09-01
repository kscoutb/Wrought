# bin/gate25-hardening
Purpose: Validates sandbox hardening and containment (GATE-25) by executing hostile and clean tasks via the production launcher, verifying systemd slice limits, seccomp/bwrap restrictions, and oracle integrity.
Key functions: `say`, `check`, `run_job`, `main`.
Direct imports/dependencies: `json`, `pathlib`, `subprocess`, `sys`; relies on external binaries `./bin/verify-job`, `systemctl`, `sudo`, and `sha256sum`.
Risks: Invokes `subprocess.run` with `sudo` and unvalidated external commands; mutates a global `FAIL` variable for test aggregation; assumes stable output formats and availability of host tools without robust fallbacks.

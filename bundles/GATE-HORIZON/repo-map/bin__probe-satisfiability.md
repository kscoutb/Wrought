# bin/probe-satisfiability
Purpose: Determines whether a fixture's test oracle is genuinely satisfiable or defective by running a reference implementation against committed tests via `bin/verify-job`.
Key functions: `_run`, `install_oracle`, `stage`, `main`.
Direct imports: `argparse`, `hashlib`, `json`, `pathlib`, `shutil`, `subprocess`, `sys`.
Risk: Executes `sudo -n` to manage `/var/lib/wrought/` directories without authentication, creating privilege escalation and unauthorized filesystem modification vulnerabilities.

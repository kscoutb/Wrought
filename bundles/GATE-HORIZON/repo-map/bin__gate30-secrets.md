# bin/gate30-secrets
Purpose: Validates secure credential placement and leak prevention across five compliance arms, verifying `systemd-creds` storage, service access via `$CREDENTIALS_DIRECTORY`, sandbox isolation, and binary drift detection.
Key functions/executables: `say`, `assert`, `secret-leak-scan`, `wrought-secret-watch`, `installed-drift-check`.
Dependencies: `systemd-creds`, `systemd-run`, `bwrap`, `sudo`, `python3`, `systemctl`, and data files `/var/lib/wrought/metrics/secret-exposure.prom` and `/etc/wrought/accepted-secret-exposures.tsv`.
Risk: Pipes decrypted secrets to `secret-leak-scan` via stdin and relies heavily on `sudo`; explicitly exits with `PARTIAL` status due to a blocked REPLICA arm awaiting external R2 credentials, while exemption logic depends on live Prometheus metrics and active system timers.

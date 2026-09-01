# bin/soak3-launch
Purpose: Asserts SOAK-3 preconditions, byte-freezes orchestrator.db, records launch evidence, and detaches soak3-track-a and soak3-track-b into background.
Key scripts: soak3-importcheck, soak3-track-a, soak3-track-b, soak3-build-pool, verify-job.
Dependencies: git, sha256sum, systemctl, sudo, df, /opt/wrought/venv-orch/bin/python, pins.lock, orchestrator.db.
Risks: Background processes launched via setsid nohup ... & lack startup validation beyond a hardcoded sleep 3; requires passwordless sudo -n; DB freeze relies on static checksums without file locks, risking silent state drift if writers bypass the freeze claim.

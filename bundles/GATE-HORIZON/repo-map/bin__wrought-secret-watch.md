# bin/wrought-secret-watch
Purpose: Continuously detects unauthorized secret exposures by decrypting credentials and scanning target trees, emitting Prometheus metrics to alert on unaccepted leaks.
Key functions: load_accepted, scan_one, main
Direct imports/dependencies: os, pathlib, re, subprocess, sys, time; shells out to systemd-creds, secret-leak-scan, and installed-drift-check.
Obvious risk: Silent failures or missing external tools could mask exposures, though the script explicitly aborts clean metric generation on validation errors; relies on strict filesystem permissions for /etc/credstore.encrypted and world-readable metric outputs.

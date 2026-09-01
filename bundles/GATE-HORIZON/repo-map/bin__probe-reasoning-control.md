# bin/probe-reasoning-control
Purpose: Determines whether per-request enable_thinking kwargs override server-side --reasoning flags to validate a reasoning-OFF control arm.
Key functions: api_key, ask, main
Direct imports: json, subprocess, sys, time, urllib.request
Obvious risks: Hardcoded URL; invokes sudo and systemd-creds for secret decryption; uses subprocess.run with shell commands; explicitly warns that failed overrides render the control arm unsafe.

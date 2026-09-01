# bin/probe-reasoning-budget
Purpose: Determines whether a pinned llama-server supports per-request reasoning token budgeting to prevent reasoning exhaustion that yields empty generations (J-116).
Key functions: api_key, ask, main
Direct imports/dependencies: json, pathlib, subprocess, sys, time, urllib.error, urllib.request
Obvious risk: Executes sudo -n systemd-creds decrypt to fetch sealed inference keys, risking credential exposure or execution failure, and assumes a hardcoded local server at URL.

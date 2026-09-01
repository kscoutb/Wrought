# bin/gate42-fallback-baseline
Purpose: Swaps the active inference profile to `devstral.args`, runs a fallback baseline for Devstral Small 2 across ten fixtures, and automatically restores the primary `qwen36.args` profile.
Key functions/classes: `say`, `active_name`, `restore`.
Dependencies: Invokes `./bin/baseline-run` and `/opt/wrought/bin/wait-healthy`; relies on `sudo`, `systemctl`, `curl`, and variables `GATE42_RUN`, `GATE42_OUT`, `GATE42_MAXTOK`.
Risks: Requires `sudo -n` for profile symlinks and service restarts; hardcodes entry-state validation against `qwen36.args`; uses unauthenticated local `curl` to port 8080; potential race condition if external processes modify the active profile symlink during execution.

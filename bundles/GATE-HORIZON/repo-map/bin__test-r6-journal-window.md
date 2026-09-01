# bin/test-r6-journal-window
Purpose: Validates RULING 3 to prevent journal window rounding and transient scope name reuse from leaking prior run verdicts into subsequent task classifications.
Key functions/classes: `main`, `ok`, `sh`, `C._unit_result`, `oracle.stage_candidate`.
Direct imports/dependencies: `wrought_supervisor.classify`, `wrought_supervisor.oracle`, `subprocess`, `bin/verify-job`, `systemctl`.
Obvious risk: Invokes privileged `sudo -n` commands for systemd management; monkeypatches `C.subprocess.run`; hardcodes `/var/lib/wrought/` paths.

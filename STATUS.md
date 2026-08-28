# STATUS — forge-mini executor heartbeat
updated:  2026-08-28T18:36:43Z
gate:     GATE-RUNNER-ARM
state:    RUNNING P3
last:     Phase 2 CLOSED, and it found the ROOT CAUSE of the self-update: `autoUpdates: false` WAS ALREADY SET in ~/.claude.json and did NOT stop it — the resolver's config arm is VOID on a native install when autoUpdatesProtectedForNative=true, so `claude doctor` reported "Auto-updates: enabled" with the preference in place. Only the ENV arm is reachable. Fixed at BOTH surfaces, and both are required: HARDEN's ephemeral HOME (the steering fix) RE-OPENED autoupdate for gate children, measured — ephemeral HOME + nothing in env => "enabled". Child: hardcoded in build_child_env(). Interactive: ~/.claude/settings.json env block. Both measured honoured via `claude doctor`, which names the var. pins.lock: supervisor_toolchain added (2.1.250, commit 2f71b9f41af6) + drift entry, YAML parses.
next:     Phase 3 — re-verify the four safety properties (b)(c)(d)(a) on 2.1.250 against HARDEN/RUNNER's own harnesses. If any changed, STOP and do not clear the runner.
usage:    n/a

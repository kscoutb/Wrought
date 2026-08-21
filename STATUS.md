# STATUS — forge-mini executor heartbeat
updated:  2026-08-21T02:13:19Z
gate:     GATE-RUNNER
state:    RUNNING P2
last:     Phase 2/3 written: bin/wrought-runner (python3 stdlib, ~700 lines), bin/wrought-runner-hook (PreToolUse, deny-or-defer, never widens), bin/wrought-course-check + bin/wrought-course-post (sealed key on STDIN ONLY, deliberately NOT bin/escalate-once — that path writes the ledger inside the byte-frozen orchestrator.db and would trip our own tripwire). Config /etc/wrought/runner.conf + runner-hooks.json, both strict-JSON, all thresholds PROPOSED-UNRATIFIED. Containment is kernel-first per the Phase-1 evidence; hooks are defence-in-depth with pre-launch JSON validation. Env is an ALLOWLIST, which is also the cross-session-steering breaker.
next:     Phase 4 — dry run against a LOCAL bare-repo courier and a SCRATCH db trio; six proofs.
usage:    n/a

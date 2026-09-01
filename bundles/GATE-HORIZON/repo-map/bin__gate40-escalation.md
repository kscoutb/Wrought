# bin/gate40-escalation
Purpose: Validates GATE-40 escalation instrumentation by verifying ledger schema, dual-window budget caps, request payloads, secret redaction, and crash/falsification guards before authorizing cloud API calls.
Key Functions: main, round_a, round_b, round_c, round_d, round_e, round_f, round_g, round_h, round_i, fresh_db, ok, eq, _seed_spend
Dependencies: wrought_escalation, client, config, escalate, ledger, wrought_orchestrator, redact, store, sqlite3, subprocess, signal, argparse, tempfile
Risks: Uses sudo and systemd-run to inject credentials during --live execution; queries the production ledger in round_i; round_g sends SIGKILL to child processes, risking orphaned temp databases or unreconciled ledger state on interruption.

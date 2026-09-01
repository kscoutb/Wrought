# bin/escalate-once
Purpose: Executes a single production escalation call with strict credential isolation and explicit ledger verification.
Key functions/classes: main, config.load, store.init_db, store.append_and_project, escalate.read_credential, escalate.escalate, ledger.authority, ledger.summary.
Direct imports: argparse, json, pathlib, sys, wrought_escalation.config, wrought_escalation.escalate, wrought_escalation.ledger, wrought_orchestrator.store.
Risk: Mandates precise systemd-run execution to inject secrets via $CREDENTIALS_DIRECTORY; improper invocation causes credential exposure or runtime crashes, and sys.path.insert mutates runtime imports.

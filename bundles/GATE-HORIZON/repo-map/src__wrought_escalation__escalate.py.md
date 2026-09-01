# src/wrought_escalation/escalate.py
Purpose: Manages end-to-end model escalations by atomically reserving budget against a production ledger before opening network sockets, enforcing strict FSM transitions and cost reconciliation.
Key functions: read_credential, prompt_hash, attempt_key, escalate, _escalate.
Direct imports: hashlib, json, os, pathlib, time, wrought_orchestrator.store, wrought_orchestrator.fsm.guard_ok, .client, .ledger.
Obvious risks: Hard exits if $CREDENTIALS_DIRECTORY is unset; ledger-first commit ordering intentionally sacrifices crash atomicity to prevent unattributable spend, risking conservative over-counting; explicitly blocks credential fallbacks to avoid /proc/*/environ leaks.

# src/wrought_orchestrator/worker.py
Implements a durable task worker with outbox-pattern side effects, fault-tolerant recovery, and deterministic chaos injection.
Key functions: `process_one`, `run`, `recover`, `run_external_step`, `_transition`, `archive_completed`, `_chaos`.
Direct dependencies: `os`, `signal`, `sqlite3`, `json`, `time`, `.store`, `.fsm` (`REPAIR_CAP`, `next_state`, `guard_ok`).
Obvious risk: `_chaos` triggers uncatchable `signal.SIGKILL` that bypasses cleanup, and complex verification/escalation branches may leave messages claimed but unacked if non-terminal states are missed.

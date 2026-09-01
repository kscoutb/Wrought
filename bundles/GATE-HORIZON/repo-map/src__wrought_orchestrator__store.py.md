# src/wrought_orchestrator/store.py
Purpose: Stdlib-only SQLite event store, task projection cache, and queue enforcing atomic transactions for state changes and using an outbox pattern for external side effects.
Key Functions/Classes: `connect`, `init_db`, `append_and_project`, `enqueue`, `claim`, `ack`, `dead_letter`, `sweep_dead_letters`, `apply_external_effect`, `rebuild_projection`, `projection_parity`, `VersionConflict`.
Direct Imports: `json`, `os`, `pathlib`, `sqlite3`, `time`, `uuid`, `redact`.
Risk: Manual `BEGIN IMMEDIATE` handling and hardcoded default paths (`DB_PATH`, `EFFECTS_DIR`) can cause WAL bloat or accidental data loss; `apply_external_effect` writes outside database transactions, risking ledger inconsistency if processes crash before ledger writes.

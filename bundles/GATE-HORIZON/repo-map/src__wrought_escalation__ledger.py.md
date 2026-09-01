# src/wrought_escalation/ledger.py
Purpose: Manages atomic pre-call budget reservations and cost tracking for AI escalations across D21 weekly/monthly windows, ensuring spend is recorded before any HTTP request is issued.
Key functions/classes: `reserve_standalone`, `reserve_in_txn`, `check_budget`, `assert_budget_unmoved`, `finalize`, `BudgetMoved`, `production_db_path`, `authority`, `unreconciled`, `worst_case_bound_rows`.
Direct imports/dependencies: `sqlite3`, `json`, `datetime`, `contextlib`, `pathlib`, `ruamel.yaml`, `wrought_orchestrator`.
Obvious risk: Historical TOCTOU budget validation races, automatic worst-case over-charging on process crashes or timeouts, and strict reliance on external `pins.lock` for database paths and pricing pins.

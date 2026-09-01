# bin/test-s15-invariants
Purpose: Deterministic regression tests for session 15 ledger rulings (RULING 3/STOP-29a and RULING 4/STOP-29b), verifying reconciliation decisions for known-zero costs versus worst-case bounds without network, GPU, or model dependencies.
Key functions/classes: `ok`, `_Pins`, `_fresh`, `_drive`, `test_ruling_3`, `test_ruling_4`, `main`.
Direct imports/dependencies: `sys`, `tempfile`, `wrought_escalation.ledger`, `wrought_escalation.escalate`, `wrought_escalation.client`, `wrought_orchestrator.store`, and implicit `sqlite3`.
Obvious risk: Tightly coupled to internal implementation via monkeypatching `escalate.client.call`, direct database writes through `ledger._insert`, and hardcoded schema assumptions (`_INSERT_COLS`, `cost_microusd`), causing fragility if production modules or DB structures change.

# bin/test-r5-budget-toctou
Purpose: Validates that budget reservation logic prevents TOCTOU race conditions where concurrent escalations commit off a stale snapshot and exceed D21 weekly/monthly caps.
Key functions/classes: main, ok, Pins, fresh_ledger, seed_spend, week_spend, tripwire, ledger.reserve_standalone, ledger.reserve_in_txn, ledger.check_budget, escalate.escalate, client.call.
Direct imports/dependencies: os, pathlib, sys, tempfile, wrought_escalation.client, wrought_escalation.escalate, wrought_escalation.ledger, wrought_orchestrator.store.
Obvious risk: Relies on ledger.BudgetMoved re-reads and runtime monkeypatching of client.call; incomplete transactional atomicity could bypass the cap backstop and allow financial overspend.

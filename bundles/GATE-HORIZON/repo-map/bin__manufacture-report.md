# bin/manufacture-report
Purpose: Generates a five-part audit report for a single `bin/manufacture` run by cross-referencing a JSON records file, an event log, and the production ledger to verify attempts, FSM/oracle alignment, staging receipts, provenance, and spend.
Key functions/classes: `main`
Direct imports/dependencies: `argparse`, `json`, `pathlib`, `sys`, `ledger`, `store`, `oracle`
Obvious risks: Dynamic `sys.path.insert()` alters module resolution; raw SQL queries and direct `json.loads()` on event payloads lack strict validation or error handling; assumes `ledger.production_db_path()` and scoped DB files exist without fallback.

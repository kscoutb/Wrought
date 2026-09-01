# bin/test-s13-invariants
Purpose: Executes deterministic regression tests verifying session 13 invariants for `json_metric` parsing, production ledger spend authority, manifest SHA-256 integrity, and failure signature persistence.
Key Functions/Classes: `ok`, `test_r1_json_metric`, `test_r4_ledger_authority`, `test_r5_manifest`, `test_r6_signature_persistence`, `_FakePins`, `main`.
Dependencies: `sys`, `wrought_verifier.__main__`, `wrought_verifier.pack`, `wrought_escalation`, `wrought_orchestrator`, `bin/verify-job`, `json`, `tempfile`, `hashlib`, `subprocess`.
Risk: `sys.path.insert(0, "src")` mutates runtime import resolution, risking module shadowing, and dynamically executes `bin/verify-job` via `importlib` without sandboxing.

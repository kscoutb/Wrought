# bin/test-s14-invariants
Purpose: Deterministic offline regression suite validating session 14's architectural rulings on ledger authority routing, statistical interval reporting, and spec validation lints.
Key functions/classes: ok, _Pins, test_ruling_a, test_stop27_intervals, test_ruling_b, main
Direct imports/dependencies: sys, tempfile, pathlib, wrought_escalation, wrought_orchestrator
Obvious risk: Dynamic execution via exec(compile(...)) on bin/baseline-report bypasses static analysis and introduces maintenance/security concerns, alongside direct sys.path manipulation.

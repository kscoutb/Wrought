# bin/redaction-corpus
Purpose: Validates that every §14.4 redaction rule fires correctly while asserting negative properties to prevent over-redaction of ordinary text and allowlisted digests.
Key functions: `ok`, `must_redact`, `main`
Direct imports: `pathlib`, `sys`, `wrought_orchestrator.redact`
Risk: Hardcoded shebang (`#!/opt/wrought/venv-orch/bin/python`) and runtime `sys.path.insert` injection harm portability, while fragile string-matching validation of `store.py` may break during refactoring.

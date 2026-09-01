# src/wrought_escalation/driver.py
Purpose: Orchestrates end-to-end escalation for cap-exhausted tasks by staging candidates, executing the real oracle for verification, computing failure signatures, and returning routing verdicts.
Key functions: `drive`, `_drive`, `_stage`, `prompt_for`, `spec_hash`.
Dependencies: Directly imports `hashlib`, `pathlib`, `subprocess`, `wrought_orchestrator.store`, `wrought_supervisor.oracle`, `wrought_supervisor.classify.classify`, `wrought_supervisor.router.failure_signature`, and local `.config`, `.escalate`, `.ledger`.
Risk: Tightly couples financial ledger commits with sandbox oracle execution (`oracle.verify`), and a broad `except Exception` in `_drive` may mask unexpected errors during verification or staging.

# src/wrought_supervisor/router.py
Purpose: Implements a deterministic, six-rule ordered FSM routing policy to assign task outcomes based on verdict classification and historical repair data.
Key functions/classes: `TaskState`, `failure_signature`, `route`
Direct imports/dependencies: `hashlib`, `json`, `re`, `dataclasses`, `__future__`
Obvious risk: Raises `ValueError` on unmatched verdicts instead of a safe fallback, and relies on hardcoded regex patterns (`_NOISE`) for failure normalization that may miss novel error formats.

# src/wrought_verifier/pack.py
Purpose: Parses and strictly validates verification pack TOML definitions inside a sandbox, enforcing default-deny rules to reject malformed configs before execution.
Key functions/classes: `PackInvalid`, `Check`, `Pack`, `_require`, `loads`, `load`
Direct imports/dependencies: `tomllib`, `dataclasses` (`dataclass`, `field`), `hashlib`
Obvious risk: Hardcoded metric allowlists (`KNOWN_METRICS`, `KNOWN_JSON_METRICS`) and strict config file path checks mitigate substrate incidents, but validation bypasses or non-UTF-8 inputs could cause silent tool fallbacks or decoding crashes.

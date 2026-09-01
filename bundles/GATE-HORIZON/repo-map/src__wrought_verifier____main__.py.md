# src/wrought_verifier/__main__.py
Purpose: In-sandbox verification runner that executes lint, test, and coverage checks, then writes a final `result.json` envelope as the sole output channel within a restricted `bwrap` namespace.
Key functions: `main`, `_run`, `_judge`, `_execution_proof_error`, `_write_envelope`, `_envelope_tamper`, `_statvfs_out`.
Direct imports/dependencies: `argparse`, `hashlib`, `json`, `os`, `subprocess`, `sys`, `time`, `load_pack`, `PackInvalid`.
Obvious risk: Documented `F-1 Face B` isolation gap where candidate code shares the reporting process, making TEST and COVERAGE verdicts self-reported and forgeable.

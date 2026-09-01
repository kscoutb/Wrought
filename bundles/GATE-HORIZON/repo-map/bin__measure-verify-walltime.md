# bin/measure-verify-walltime
Purpose: Computes empirical verification wall-clock statistics from committed baseline records and sandbox envelopes to establish a strict time bound (STOP-32).
Key functions: `load_records`, `load_envelopes`, `stats`, and `main` parse JSON evidence, calculate distribution metrics, and format or serialize output.
Direct imports: `argparse`, `json`, `pathlib`, `re`, `statistics`, `sys`.
Obvious risk: Hardcoded `JOB_ROOT` and silent skipping of missing/malformed JSON files may yield incomplete datasets that underestimate the maximum duration, while deliberate exclusion of pathological runs could mask edge-case timing failures.

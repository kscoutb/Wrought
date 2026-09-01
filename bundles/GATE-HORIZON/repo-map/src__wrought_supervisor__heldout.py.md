# src/wrought_supervisor/heldout.py
Purpose: Implements GATE-44's held-out feedback filter to strip named failures, progress lines, and counts from pytest output and verification envelopes, ensuring held-out tests remain hidden from the model while grading uses the full suite.
Key functions: `load_pinned_split`, `filter_envelope`, `filter_pytest_stdout`, `filter_result`, `guard`, `grade`, `node_function`.
Direct imports: `copy`, `json`, `pathlib`, `re`, and `ruamel.yaml` (loaded locally inside `load_pinned_split`).
Obvious risk: Filter misses could leak held-out test identifiers to the model; the `guard` backstop catches residual leaks but flags an experimental defect, and the module strictly exits if `pins.lock` lacks the pinned split.

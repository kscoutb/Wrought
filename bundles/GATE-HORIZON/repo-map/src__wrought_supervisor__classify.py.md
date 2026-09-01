# src/wrought_supervisor/classify.py
Purpose: Supervisor-side classification of sandbox job outcomes, prioritizing substrate signatures over tool exit codes to prevent misattributing repairable code defects as infrastructure failures.
Key Functions: `classify`, `_candidate_collection_failure`, `_running_check`, `_unit_result`
Direct Imports: `json`, `re`, `subprocess`, `time`, `__future__.annotations`
Obvious Risk: Polling `journalctl` via `subprocess` in `_unit_result` introduces timing race conditions if systemd verdicts fail to settle within the 5-second window, potentially returning provisional classifications; heavy reliance on hardcoded string heuristics may misroute failures if tool output formats change.

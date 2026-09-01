# src/wrought_supervisor/oracle.py
Purpose: Centralizes verification execution and classification-to-FSM-verdict mapping for the wrought supervisor, enforcing artifact provenance via staging receipts and eliminating silent routing defaults.
Key functions: `stage_candidate`, `assert_staged_for_attempt`, `verify`, `verdict_for`, `oracle_verdict`, `job_dir`.
Direct imports/dependencies: `hashlib`, `re`, `json`, `os`, `pathlib`, `subprocess`, `time`; invokes `bin/verify-job` and feeds `worker.process_one`.
Risks: Executes `sudo -n rm -rf` and `sudo -n install` during staging; relies strictly on `TASK_ID_RE` and `MODULE_FILENAME_RE` to prevent path traversal, and raises hard `RuntimeError` on receipt mismatches or unclassified outputs, risking pipeline halts.

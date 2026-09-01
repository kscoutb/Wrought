# bin/gate44-report
Purpose: Generates a statistical dashboard comparing visible vs held-out test pass rates to detect model reward-hacking, including historical controls and escalation spend tracking.
Key functions: `_load_baseline_report_helpers`, `sign_test_p`, `final_attempt`, `envelope_for`, `counts`, `g43c_control`, `main`.
Direct imports: `argparse`, `glob`, `json`, `math`, `os`, `pathlib`, `sqlite3`, `sys`, `wrought_supervisor.heldout`, `wrought_escalation.config`, `wrought_escalation.ledger`.
Risk: Dynamically executes code via `exec(compile(...))` to load `wilson`, `overlap`, and `ci_s` from `bin/baseline-report`, bypassing standard module resolution and introducing security/maintainability vulnerabilities.

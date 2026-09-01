# bin/wrought-runner-hook
Purpose: Defense-in-depth `PreToolUse` hook that audits tool invocations and blocks catastrophic actions via a regex deny-list, deferring all other decisions to the primary permission system.
Key functions: `log_path`, `decide`, `main`.
Direct imports: `json`, `os`, `re`, `sys`, `datetime`, `timezone`, `Path`.
Risks: Audit logging silently disables if `CONFIG` parsing fails; broad regex patterns in `DENY` may produce false positives; explicitly documented as non-load-bearing and vulnerable to silent failure under `claude -p`.

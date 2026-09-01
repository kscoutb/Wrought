# bin/test-gate44-heldout
Purpose: Validates the GATE-44 held-out filter across eight test arms using real envelope data to ensure hidden test names are stripped from model inputs while visible failures survive.
Key functions: `main`, `ok`, `_feedback_from`, `g43c_envelopes`, and `heldout.filter_result`, `heldout.filter_envelope`, `heldout.guard`, `heldout.grade`, `heldout.node_function`.
Dependencies: `copy`, `glob`, `json`, `pathlib`, `subprocess`, `sys`, and `from wrought_supervisor import heldout`; relies on `bin/baseline-run`, `bin/gate44-split`, and git.
Risk: `_feedback_from` uses `exec(compile(...))` to dynamically evaluate scraped source code from an external script, introducing execution safety and fragility hazards.

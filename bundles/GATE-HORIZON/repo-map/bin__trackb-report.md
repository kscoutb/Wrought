# bin/trackb-report
Purpose: Generates §13.8 dashboard tables from Track-B records, comparing FSM terminal states against Oracle final verdicts and calculating run-to-run error bars.
Key functions: `load`, `pct`, `oracle_passed`, `disagrees`, `arm_table`, `main`.
Dependencies: Directly imports `json`, `pathlib`, `sys`, and `__future__.annotations`.
Risk: Relies on a hardcoded `TRACKB` path and assumes strict record dictionaries without validation, risking unhandled `KeyError` or `TypeError` on malformed data; the script also exits with code 1 on any FSM-Oracle divergence, potentially blocking automated workflows.

# bin/resolve-ruff-ruleset
Purpose: Reproducibly resolves and emits the active `ruff` rule set, enforcing a narrowed F + S selection per project policy S13/RULING 1.
Key functions/classes: None; standalone bash script orchestrating variables `RUFF`, `ARGS`, `RULES`, `COUNT`, and `PREFIXES`.
Direct imports/dependencies: External commands `ruff`, `mktemp`, `sed`, `grep`, `sort`, `tr`, `awk`, `date`, and `hostname`.
Risk: Fragile regex parsing of `ruff --show-settings` output may break across tool versions; hardcodes `/opt/wrought/venv/bin/ruff` assuming a specific environment layout.

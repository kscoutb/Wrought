# src/wrought_escalation/config.py
Purpose: Strictly loads and validates pinned escalation configuration from `pins.lock` without applying defaults.
Key components: `EscalationPins` dataclass and `load` function enforce all keys listed in `_REQUIRED`.
Dependencies: `pathlib`, `dataclasses.dataclass`, and `ruamel.yaml.YAML`.
Risk: YAML string-to-boolean coercion (e.g., `bool("no")` evaluates to `True`) could silently invert critical routing pins like `allow_fallbacks`, causing unapproved endpoint usage and financial loss despite explicit load-time type assertions.

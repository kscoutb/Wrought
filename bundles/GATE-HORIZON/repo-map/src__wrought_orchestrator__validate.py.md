# src/wrought_orchestrator/validate.py
Purpose: Validates TASK.md inputs against a strict YAML subset, JSON Schema, EARS phrasing rules, and REQ/CON mapping requirements per specs §7.5/§7.6.
Key components: ValidationResult, validate, split_task_md, canon_v2, req_lines, ears_pattern, _strict_subset_violations.
Dependencies: hashlib, io, re, jsonschema, rfc8785, ruamel.yaml.
Risk: _strict_subset_violations uses text-based regex to reject YAML anchors/aliases/merge keys, explicitly risking false positives on unquoted scalars, while ears_pattern relies on regex matching that may misclassify complex phrasing despite negative controls.

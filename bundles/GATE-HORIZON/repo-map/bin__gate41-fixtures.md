# bin/gate41-fixtures
Purpose: Validates ten committed fixture tasks against GATE-41/D11 specifications, enforcing provenance checks, schema lints, test node resolution, EARS phrasing compliance, SHA256 stability, and spec-oracle module alignment.
Key Functions/Classes: `main`, `test_nodes`, `fixture_dirs`, `sh`, `ok`, `say`.
Direct Imports/Dependencies: `ast`, `pathlib`, `re`, `subprocess`, `sys`, `wrought_orchestrator.validate` (`validate`, `ears_pattern`, `canon_v2`, `split_task_md`, `req_lines`), `io`, `ruamel.yaml`.
Obvious Risk: Runtime `sys.path` manipulation, hardcoded `SESSION_IDENTITY` and `STAGING` paths, and reliance on unversioned `ruamel.yaml` and external `git` subprocess calls create environment fragility and potential portability issues.

# bin/gen-canon-vectors
Purpose: Generates committed SHA256 conformance vectors and digests for `canon_v2` to prevent silent specification drift and validate normalization rules.
Key functions/classes: `digest`, `main`.
Direct imports/dependencies: `hashlib`, `io`, `json`, `pathlib`, `sys`, `ruamel.yaml.YAML`, `wrought_orchestrator.validate.canon_v2`, `wrought_orchestrator.validate.split_task_md`.
Obvious risk: Direct `sys.path.insert` manipulation can cause import collisions; strict `SystemExit` on digest mismatches will abruptly halt execution if `canon_v2` behavior changes unintentionally.

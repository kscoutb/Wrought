# bin/gate38-canon
Purpose: Validates canon_v2 hash stability and conformance against committed digests in fixtures/canon-v2-vectors.json to detect specification drift.
Key functions/classes: ok, digest, main, TRANSFORMS, canon_v2, split_task_md, YAML.
Direct imports/dependencies: hashlib, io, json, pathlib, subprocess, sys, ruamel.yaml, wrought_orchestrator.validate.
Obvious risk: Relies on hardcoded string replacements and sys.path.insert manipulation, making it brittle across environments; subprocess calls assume Unix tools and specific PATH configurations.

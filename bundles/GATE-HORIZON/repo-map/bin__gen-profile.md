# bin/gen-profile
Purpose: Sole generator and drift checker for `/etc/wrought/profiles/*.args` files, strictly deriving every CLI flag value from `pins.lock` without defaults, self-referential copying, or hand-editing.
Key functions/classes: `dig`, `render`, `generate`, `main`, `PROFILES`.
Direct imports/dependencies: `argparse`, `hashlib`, `io`, `pathlib`, `sys`, `ruamel.yaml`.
Obvious risk: Unconditionally aborts on any missing or `DEFERRED` pin instead of providing fallbacks, enforces hardcoded `/etc/wrought/profiles/` paths, and catches `SystemExit` in `main` which may obscure underlying YAML parsing or key-lookup failures.

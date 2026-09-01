# bin/gate44-split
Purpose: Mechanically resolves a held-out/visible test split for evaluation fixtures using `k = max(1, ceil(n_fail_to_pass / 3))` to prevent model influence, outputting JSON or a `pins.lock` YAML block.
Key functions: `_entries`, `resolve`, `load_pinned`, `main`
Direct imports/dependencies: `argparse`, `hashlib`, `json`, `math`, `pathlib`, `re`, `sys`, `wrought_orchestrator.validate.validate`, `wrought_supervisor.heldout.load_pinned_split`
Obvious risk: Hard `sys.exit` on substring name collisions or empty visible sets will halt runs; silent exclusion of `undeclared_collected` tests and strict `pins.lock` versioning make the pipeline brittle to fixture changes.

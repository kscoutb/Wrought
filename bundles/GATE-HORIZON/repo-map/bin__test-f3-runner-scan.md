# bin/test-f3-runner-scan
Purpose: Validates that `wrought-runner` halts publishing on non-zero `SECRET_SCAN` exit codes and confirms `wrought-precommit-secret-scan` detects fake tokens in a `bundles/` tree.
Key functions/classes: `_Log`, `runner.secret_scan_or_halt`, `runner.Halt`, `subprocess.run`
Direct imports/dependencies: `importlib.machinery`, `importlib.util`, `pathlib`, `shutil`, `subprocess`, `sys`, `tempfile`; dynamically loads `wrought-runner` and invokes `wrought-precommit-secret-scan`.
Obvious risk: Dynamic module loading via `importlib.util.spec_from_loader` catches only `SystemExit`, potentially masking import failures or executing compromised code; `subprocess.run` executes external binaries without sandboxing.

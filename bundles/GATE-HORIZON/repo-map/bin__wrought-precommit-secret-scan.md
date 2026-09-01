# bin/wrought-precommit-secret-scan
Purpose: Pre-commit scanner that checks staged git diffs or specified trees for leaked credentials while strictly preventing secret exposure via command-line arguments.
Key functions: `load_secrets_from_credstore`, `load_secrets_from_path`, `staged_diff`, `scan_tree`, `main`.
Direct imports/dependencies: `argparse`, `os`, `subprocess`, `sys`, `Path`, plus external CLI tools `systemd-creds` and `git`.
Obvious risk: Requires `sudo` to decrypt `/etc/credstore.encrypted`; permission or decryption failures return exit code `2` rather than halting, potentially masking a failed scan as a non-event while the script continues with zero secrets.

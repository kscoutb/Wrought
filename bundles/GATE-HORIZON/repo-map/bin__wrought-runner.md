# bin/wrought-runner
Purpose: Operator-started daily batch runner that walks a courier QUEUE to execute approved gate prompts in isolated `claude -p` sessions under systemd scopes, with mechanical verification and circuit breakers.
Key functions/classes: `Halt`, `load_config`, `RunLog`, `parse_queue`, `set_queue_status`, `make_ephemeral_home`, `reap`, `build_child_env`, `validate_allowed_tools`, `secret_scan_or_halt`, `install_signal_handlers`.
Direct imports/dependencies: stdlib-only modules (`argparse`, `fcntl`, `hashlib`, `json`, `os`, `re`, `shutil`, `signal`, `subprocess`, `sys`, `threading`, `time`, `datetime`, `pathlib`).
Obvious risk: Requires `sudo` for `secret_scan_or_halt` and invokes `virsh`/`ss`/`systemctl` via `subprocess`; orphaned VMs or sockets may survive if `reap` or `kill_live_children` fails, and progress is explicitly gated by manual operator starts rather than automation.

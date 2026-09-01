# bin/soak3-track-b
Purpose: Endurance soak harness that repeatedly invokes `bin/verify-job` over a committed corpus to assert classification reproducibility, seccomp pin stability, wall-clock bounds, and zero process leaks.
Key functions/classes: `main`, `verify_once`, `assert_run`, `restage`, `checkpoint`, `halt`, `PidSampler`, `tasks_current`, `leaked_scopes`, `stray_bwrap`, `substrate_sample`.
Direct imports/dependencies: `json`, `os`, `pathlib`, `subprocess`, `sys`, `threading`, `time`, `wrought_supervisor.oracle`, `ruamel.yaml`.
Obvious risk: Unattended infinite loop that executes `sudo rm -rf` during staging, immediately halts on any invariant or disk-cap violation, and relies on external cgroup/systemd interfaces that may be absent or race-prone.

# bin/gate25-measure-tasksmax
Purpose: Empirically measures peak process counts via systemd cgroup `pids.peak` to calculate a data-driven `TasksMax` limit with a 4x safety margin.
Key functions: `slice_cgroup`, `poll_peak`, `one_run`, `main`.
Direct imports/dependencies: `json`, `pathlib`, `statistics`, `subprocess`, `sys`, `threading`, `time`; relies on external `./bin/verify-job` and `/sys/fs/cgroup`.
Obvious risks: Cgroup teardown race may miss spikes after the final sample; hardcodes `wrought-verify.slice` and `GATE-25-SELFTEST`; depends on dynamic globbing of scope names.

# bin/soak3-build-pool
Purpose: Builds a fixed, cycled corpus pool for SOAK-3 Track B endurance testing by staging candidates from committed `-g42c`/`-g44` tasks and attaching reference classifications from `records-g42c.json`.
Key Functions/Classes: `link_task`, `corpus_classifications`, `main`
Direct Imports/Dependencies: `json`, `pathlib`, `shutil`, `subprocess`, `sys`, `wrought_supervisor.oracle`
Obvious Risk: Unconditionally executes `shutil.rmtree` on existing oracle directories and symlinks into production roots (`REAL_JOBS`, `REAL_ORACLE`) with a hard `SystemExit` guard, risking data loss or unexpected halts if paths conflict.

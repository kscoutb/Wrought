# bin/gate39-chaos
Purpose: Validates crash recovery correctness by simulating `kill -9` chaos to guarantee zero task loss or duplication, exercising lease lapse, fenced acks, dead-lettering, and event log invariants.
Key functions: `reset`, `work_subprocess`, `work_parallel`, `audit`, `drain`, `main`.
Dependencies: `json`, `os`, `pathlib`, `random`, `shutil`, `signal`, `sqlite3`, `subprocess`, `sys`, `time`, `store`, `worker`, and `./bin/orchestrator`.
Risk: `reset()` destructively unlinks the database and `-wal/-shm` siblings; if `WROUGHT_DB` is inherited from the environment, it will erase unrelated databases despite the explicit assertion guard.

# bin/gate37-replay
Purpose: Validates projection-rebuild parity against an event log and measures GATE-37 replay/snapshot cadence thresholds for full-projection and per-stream reconstructions using a synthetic corpus.
Key functions/classes: `main`, `ok`, `drop_caches`, `connect`, `rebuild_projection`, `projection_parity`, `STATES`.
Direct imports/dependencies: `__future__`, `json`, `pathlib`, `subprocess`, `os`, `sys`, `time`, `wrought_orchestrator.store`, `wrought_orchestrator.fsm`.
Risks: Requires `sudo` to flush OS caches; tightly coupled to `GATE-39` which may unlink the corpus DB; timing measurements are explicit synthetic floors, not production ceilings.

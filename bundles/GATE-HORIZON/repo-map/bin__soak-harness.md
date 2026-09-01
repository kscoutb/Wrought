# bin/soak-harness
Purpose: Detached soak testing harness that measures bulk event ingestion throughput and validates chaos recovery invariants (zero loss/duplication, fenced-ack) while strictly isolating state from production.
Key functions: `bulk_round`, `chaos_round`, `audit`, `fenced_ack_holds`, `checkpoint`, `halt`, and `main`.
Direct imports: `json`, `os`, `pathlib`, `signal`, `subprocess`, `sys`, `time`, and `wrought_orchestrator.store`.
Risk: Executes `sudo` to drop OS caches via `drop_caches`, recursively applies `chmod 0o444` on failure, and forcefully `SIGKILL`s worker subprocesses, risking resource locks or masked stability defects.

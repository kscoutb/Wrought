# bin/soak3-track-a
Purpose: Executes SOAK-3 Track A chaos endurance tests, validating bulk event ingestion, worker SIGKILL resilience, FSM/oracle consistency, and recovery performance while strictly isolating soak state from production.
Key Functions: bulk_round, chaos_round, audit, verdict_source_audit, fsm_oracle_both_directions, recover_reconciles, recover_cost, checkpoint, halt, oom_kills, substrate_sample, main.
Direct Imports: json, os, pathlib, signal, subprocess, sys, time, wrought_orchestrator.store, wrought_orchestrator.worker.
Risks: Invokes sudo to drop OS page caches via /proc/sys/vm/drop_caches, risking host I/O disruption; hardcodes WROUGHT_DB and WROUGHT_EFFECTS_DIR environment variables and directly reads /sys hardware metrics that may fail or lack permissions in restricted environments.

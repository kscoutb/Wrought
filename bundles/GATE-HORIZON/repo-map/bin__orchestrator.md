# bin/orchestrator
Purpose: CLI for initializing databases, enqueuing tasks, running workers with strict visibility/timeout controls, recovering state, and managing projections/archival.
Key functions/classes: main, store.init_db, store.connect, store.enqueue, worker.run, worker.recover, store.sweep_dead_letters, worker.archive_completed, store.rebuild_projection, oracle.oracle_verdict.
Direct imports/dependencies: argparse, json, os, signal, pathlib, sys, wrought_orchestrator.store, wrought_orchestrator.worker, wrought_supervisor.oracle.
Obvious risk: Deliberately omits defaults for --visibility-s and --max-receive to prevent unsafe queue redelivery; uses direct sys.path.insert manipulation and includes a WROUGHT_CHAOS_KILL environment hook that triggers os.kill unexpectedly if misconfigured.

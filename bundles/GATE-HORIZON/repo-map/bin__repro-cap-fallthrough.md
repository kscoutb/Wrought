# bin/repro-cap-fallthrough
Purpose: Deterministic reproducer and regression test for bug J-91, where exceeding REPAIR_CAP causes a code_defect verdict to fall through to a terminal else clause, incorrectly marking a task COMPLETED.
Key functions/classes: main, worker.process_one, store.init_db, store.append_and_project, store.enqueue.
Direct imports/dependencies: json, os, pathlib, sys, tempfile, wrought_orchestrator.store, wrought_orchestrator.worker.
Obvious risk: Mutates sys.path at runtime and uses tempfile.mkdtemp for a scratch database without explicit cleanup or exception handling, risking orphaned temporary files.

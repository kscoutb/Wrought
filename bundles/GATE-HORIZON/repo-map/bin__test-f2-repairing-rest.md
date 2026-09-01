# bin/test-f2-repairing-rest
Purpose: Validates that tasks resting in REPAIRING are not silently acked by worker.process_one and that delivery budgets accumulate across worker.recover calls until store.sweep_dead_letters transitions the task to HUMAN_REVIEW.
Key functions/classes: worker.process_one, worker.recover, store.init_db, store.append_and_project, store.enqueue, store.sweep_dead_letters
Direct imports: pathlib, sys, tempfile, store, worker
Obvious risk: Runtime sys.path.insert mutation and lack of explicit cleanup for the tempfile.mkdtemp directory may cause import resolution issues or leave orphaned files on test failure.

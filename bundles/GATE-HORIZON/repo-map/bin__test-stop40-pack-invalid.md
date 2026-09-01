# bin/test-stop40-pack-invalid
Purpose: Regression test for operator decision D-F verifying that `PACK_INVALID` classifications route to `HUMAN_REVIEW` via the FSM instead of requeuing as `substrate_incident`.
Key functions/classes: `main`, `drive`, `ok`, `fresh_store`, `evs`, `classify`, `oracle.verdict_for`, `next_state`, `worker.run`.
Dependencies: `wrought_orchestrator`, `wrought_orchestrator.fsm`, `wrought_supervisor`, `wrought_supervisor.classify`, `wrought_verifier.__main__`, `json`, `pathlib`, `tempfile`, `sys`, `os`.
Risks: Runtime `sys.path.insert` mutation risks import shadowing; `drive` swallows tracebacks via `except Exception`; execution tightly couples to the live `/etc/wrought/packs/py.toml` deployment path.

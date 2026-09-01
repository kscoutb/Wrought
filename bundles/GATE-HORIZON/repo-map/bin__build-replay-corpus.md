# bin/build-replay-corpus
Purpose: Generates a synthetic replay corpus spanning all projection states, repair indices, and escalation flags for parity testing and GATE-37 validation.
Key functions: `main`, `sh`, `sh_env`, and `_with_db` orchestrate the workflow and CLI argument injection.
Dependencies: `argparse`, `json`, `pathlib`, `subprocess`, `sys`, `time`, `os`, and `wrought_orchestrator.store`.
Risk: Explicitly refuses to run against `store.DB_PATH` unless `--allow-production` is passed, but relies entirely on `./bin/orchestrator` subprocess execution with injected chaos environment variables (`WROUGHT_CHAOS_KILL`) that could obscure CLI failure diagnostics.

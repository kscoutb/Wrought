# bin/trackb-run
Purpose: Executes synthetic coding tasks through a local LLM generation, real sandbox verification, and a capped repair loop to measure escalation rates and substrate incidents.
Key functions: `main`, `run_task`, `generate`, `verify`, `read_api_key`, `substrate_sample`, `install_oracle`.
Dependencies: `urllib.request`, `subprocess`, `wrought_orchestrator.store`, `wrought_supervisor.classify`, and invoked scripts `bin/verify-job` and `bin/orchestrator`.
Risk: Heavy `sudo` and `subprocess` usage with privileged system binaries introduces privilege escalation and injection vulnerabilities; hardcoded absolute paths and direct `os.environ` overrides require strict environment isolation.

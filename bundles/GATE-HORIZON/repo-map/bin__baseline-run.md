# bin/baseline-run
Purpose: Runs a controlled baseline benchmark of operator-authored fixtures to measure LLM code-generation success rates and escalation demand under strict, auditable constraints.
Key Functions: `load_fixtures`, `build_messages`, `generate`, `run_task`, `main`
Direct Imports: `wrought_escalation`, `wrought_orchestrator`, `wrought_supervisor`, `ruamel.yaml`, `urllib.request`, `subprocess`
Obvious Risk: Depends on `sudo` execution, systemd credential decryption, and hardcoded paths; token budget misconfiguration or queue desyncs trigger hard refusals or silent truncation.

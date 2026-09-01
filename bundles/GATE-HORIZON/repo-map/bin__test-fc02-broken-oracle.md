# bin/test-fc02-broken-oracle
Purpose: Validates FSM routing fixes (§8.1a) and oracle.verdict_for() mappings for BROKEN_ORACLE, substrate_incident, same_failure, and pack_invalid across five test arms.
Key functions: main(), install_broken_oracle(), fresh_store(), ok(), worker.run(), store.append_and_project(), next_state(), guard_ok(), oracle.verdict_for().
Dependencies: wrought_orchestrator.store, wrought_orchestrator.worker, wrought_orchestrator.fsm, wrought_supervisor.oracle, subprocess, tempfile.
Risk: sh() executes sudo -n with unsanitized argument interpolation, creating a command injection and privilege escalation vulnerability, alongside hardcoded system paths.

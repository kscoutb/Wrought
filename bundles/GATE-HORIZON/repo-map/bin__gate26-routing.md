# bin/gate26-routing
Purpose: Validates routing-classifier policy and FSM transition rules for task failure handling, escalation, and human-review routing.
Key functions/classes: main, ok, pytest_env, verdict_for, route, TaskState, failure_signature, classify, validate, guard_ok.
Direct imports: json, pathlib, subprocess, sys, inspect, ast, wrought_orchestrator.fsm, wrought_supervisor.router, wrought_supervisor.classify, wrought_orchestrator.worker, wrought_verifier.pack.
Risk: Executes sudo cat and hardcodes absolute system paths requiring root privileges; explicitly discloses that route() is unwired from the production FSM and only invoked by this test script.

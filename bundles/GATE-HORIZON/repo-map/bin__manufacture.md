# bin/manufacture
Purpose: Executes a single operator task through a real production path where the worker independently drives its own oracle for verification, avoiding injected verdicts from baseline harnesses.
Key functions: main, run_task, load_task, refuse_production, fsm_view, _import_baseline_run.
Dependencies: wrought_escalation, wrought_orchestrator, wrought_supervisor, importlib.util, and dynamically loaded bin/baseline-run.
Risk: Mutating os.environ before module imports and dynamically executing bin/baseline-run bypass standard packaging, while aggressive sys.exit() guards and hardcoded path checks create brittle failure modes that could mask configuration drift or accidental production writes.

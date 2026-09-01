# bin/gate43-report
Purpose: Produces a GATE-43 comparative report analyzing repair-feedback A/B arms by calculating escalation demand, repair-round knees, REQ-ID citation convergence, and per-fixture movements.
Key functions: _load_baseline_report, load, knee, req_id_convergence, delivered, main.
Direct imports: argparse, importlib.machinery, importlib.util, json, pathlib, sys, and dynamically loads bin/baseline-report.
Risk: Dynamically imports baseline-report via raw path instead of standard packaging, risking silent definition drift and tight coupling; also assumes a hardcoded /var/lib/wrought/baseline directory and strict JSON record schemas.

# bin/decompose-baseline
Purpose: Decomposes baseline task runs into comparative metrics (escalation demand/resolve, completion rates, and blocker classifications) for a before/after oracle analysis.
Key functions: load, blockers, classify_best, main.
Direct imports: collections, glob, json, pathlib, sys.
Risk: Hardcoded search paths in SEARCH and potential ZeroDivisionError if n=0; historically vulnerable to miscounting empty generations as passes despite current guards.

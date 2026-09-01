# bin/baseline-report
Purpose: Generates a baseline dashboard reporting escalation demand/resolution rates, oracle pass metrics, repair histograms, and cost ledgers using pooled binomial Wilson confidence intervals.
Key functions: pct, wilson, ci_s, overlap, _measure_synthetic, run_pack_ids, oracle_passed, escalation_demanded, main
Direct imports: argparse, glob, json, pathlib, statistics, sys, wrought_orchestrator.store, wrought_escalation.ledger
Obvious risks: Hardcoded absolute paths (/var/lib/wrought/*) limit portability; broad except Exception blocks silently swallow database/package errors; dynamic late imports may crash if dependencies are missing.

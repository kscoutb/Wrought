# STATUS — forge-mini executor heartbeat
updated:  2026-08-21T02:03:25Z
gate:     GATE-RUNNER
state:    RUNNING P1
last:     Phase 1 RT0 verifications COMPLETE on claude 2.1.238 (raw/02-09). (a) HOLDS — fresh -p runs share no memory; corollary: per-project AUTO-MEMORY is a live cross-invocation channel. (b) HOLDS with a correction — there is NO mode named default-deny; dontAsk and manual are default-deny-with-allowlist, while acceptEdits and auto SILENTLY RAN an un-allowlisted Bash call. Every case exited rc=0 incl. every denial. (c) REFUTES RT0 pass-2 — PreToolUse hooks DO fire under -p and their deny is enforced; but a MALFORMED settings file is SILENTLY ignored under -p (rc=0, empty stderr, hook layer gone). (d) HOLDS — output cap and bash timeout both take effect, but the bash timeout BACKGROUNDS rather than kills, and --max-budget-usd overshot its cap 4.6x.
next:     Phase 2 — design and write bin/wrought-runner + /etc/wrought/runner.conf, containment kernel-first.
usage:    n/a

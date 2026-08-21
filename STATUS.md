# STATUS — forge-mini executor heartbeat
updated:  2026-08-21T02:26:48Z
gate:     GATE-RUNNER
state:    RUNNING P4
last:     Dry runs 1-2 done against a LOCAL bare-repo courier and a SCRATCH db trio. Happy path PASSES end to end (fresh context, contained scope, bundle pushed, manifest verified mechanically, byte freeze held, 45s pacing exact). THREE DEFECTS FOUND AND FIXED, each by measurement not inspection: (1) MemoryMax alone does NOT cap memory here — 1 GiB under a 256M cap succeeded via the 8 GiB swap file; MemorySwapMax=0 makes it an rc=137 kill. (2) A Bash call targeting a path OUTSIDE the session cwd is DENIED under dontAsk even when explicitly allowlisted — isolated with a 2x2 against the hook; fixed with minimal --add-dir. (3) My own breaker latched on gate-cap/wall-clock, which would have poisoned the next morning's start; now only real faults latch.
next:     remaining Phase 4 scenarios — tripwire, consecutive-failure breaker, stubbed course-check HALT, a real-claude scope kill, and the cross-session steering question.
usage:    n/a

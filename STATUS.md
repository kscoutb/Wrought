# STATUS — forge-mini executor heartbeat
updated:  2026-08-28T18:50:37Z
gate:     GATE-RUNNER-ARM
state:    RUNNING P5
last:     SECOND HARD BLOCKER FOUND, unasked. Phase 5(i): the PermissionError IS GONE — the runner loaded the INSTALLED config, made its state dir, took its lock, wrote a ledger. But it then HALTED with a LATCHING queue-parse breaker and CANNOT RUN AT ALL against the real courier: parse_queue's QUEUE_STATUSES does not know two RATIFIED terminal statuses — 'RESET' (GATE-J0B-SURFACE) and 'FOLDED INTO <gate>' (GATE-HJ2-HEARTBEAT, and it is PARAMETRIC so it needs a prefix match). rails §12.1, the courier README and QUEUE.md's own legend all bless both; only the parser is out of sync. It also carries an extra 'NOT RUN' that no doc defines. Never caught before because every prior dry run used a SCRATCH courier with a synthetic queue — the same never-exercised-against-production shape as HARDEN raw/23. NOT FIXED: outside this prompt's authorized change set; fix specified in raw/24 for a ruling. NOTE the previous STATUS line here (commit 3f6f819, gate GATE-BATCH) was written by the runner itself during that probe — a runner start is NOT read-only, it writes and PUSHES STATUS.md.
next:     Phase 5(ii) — the end-to-end proof on a scratch courier + scratch state, which is unaffected by the defect because a synthetic queue uses only known statuses.
usage:    n/a

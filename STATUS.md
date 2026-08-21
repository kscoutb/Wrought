# STATUS — forge-mini executor heartbeat
updated:  2026-08-21T00:22:05Z
gate:     GATE-J0B-SURFACE
state:    RUNNING P4
last:     Phase 3 PASS, after one real failure and fix. AIR-GAP PROVEN: external FAIL (curl 6 by name, curl 7 by IP literal, raw SYN Network-unreachable), 10.0.2.2:8080 FAIL (refused), pinhole 10.0.2.100:8081 = 200 and is genuinely primary-qwen27b. Host-surface sweep: the pinhole is the ONLY reachable endpoint. Guest holds no key; wrong key still 200. FINDING: QEMU guestfwd is a SINGLE startup chardev, not a per-connection forwarder — proxy rewritten (authproxy2.py) to per-request upstream; socat absent so the prompt's fallback block could not be run.
next:     Phase 4 — point Goose at the pinhole and build the C5 exposure map.
usage:    n/a

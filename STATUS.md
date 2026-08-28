# STATUS — forge-mini executor heartbeat
updated:  2026-08-28T14:08:20Z
gate:     GATE-RUNNER-HARDEN
state:    RUNNING P4
last:     BLOCKER 1 CLOSED and BLOCKER 2 CLOSED, both measured. P2: the prompt's premise was wrong — discovery is NOT keyed on ~/.claude/daemon/roster.json (that file stayed {} and stale through all six probes). There are TWO surfaces with DIFFERENT keys: the peer LISTING is keyed on $HOME, the addressable SOCKET on $XDG_RUNTIME_DIR/cc-socks/<pid>.sock. Both now fenced per gate. Minimal HOME is THREE files; probe D2 authenticated, ran 7 turns with 0 denials and PUSHED to origin/main from inside the isolated shape. P3: the sweep detected+reaped a leaked guest-shaped process AND a listener on 8081 and HALTED LATCHED; a scope descendant died with the scope at RuntimeMaxSec, sweep clean. Also found: the CLI SELF-UPDATED 2.1.238 -> 2.1.250 today at 12:56Z, under the pin.
next:     Phase 4 — rails additions (APPROVED status, ALLOWED-TOOLS header, scope-parenting rule) + courier mirrors; then Phase 5 dry-run regression, audit, bundle.
usage:    n/a

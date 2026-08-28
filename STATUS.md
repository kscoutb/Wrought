# STATUS — forge-mini executor heartbeat
updated:  2026-08-28T18:48:07Z
gate:     GATE-RUNNER-ARM
state:    RUNNING P5
last:     Phase 4 CLOSED. DBUS_SESSION_BUS_ADDRESS DROPPED — and it closed a real hole, not a cosmetic one: HARDEN's isolation left every gate child holding the REAL bus address (unix:path=/run/user/1000/bus) despite a private runtime dir. Took the TIGHTER option: removed from the allowlist outright rather than a child-only strip, because MEASURED that `systemd-run --user --scope` works with no DBUS address as long as XDG_RUNTIME_DIR is set (sd-bus derives it); control with both removed fails. Proved a real gate child still runs: 3 turns, 0 denials, 0 bytes stderr, git works. Ground truth taken from INSIDE the child, not its prose — it wrote DBUS=[<UNSET>], XDG_RUNTIME_DIR=[the private one], DISABLE_AUTOUPDATER=[1]. Nothing needed re-adding. Runner diff is 35 lines, exactly two changes.
next:     Phase 5 — two sub-proofs: (i) the runner STARTS on the INSTALLED /etc/wrought/runner.conf verbatim (PermissionError gone), (ii) one real claude gate end-to-end on a scratch courier + scratch state, never the real store.
usage:    n/a

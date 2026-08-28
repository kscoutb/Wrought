# STATUS — forge-mini executor heartbeat
updated:  2026-08-28T14:24:26Z
gate:     GATE-RUNNER-HARDEN
state:    BUNDLED
last:     REVISION 2, same session. Both blockers remain CLOSED and measured; config ratified; rails §12-14 added; 9/9 regressions pass. NEW at wind-down, and a gap this gate's own audit missed: every runner invocation used a SCRATCH config, so the INSTALLED /etc/wrought/runner.conf and the modified runner had never been loaded together. The change IS compatible (load_config accepts it), BUT the runner still cannot start — PermissionError on /var/lib/wrought/runner-state, which is root:root 0755. PRE-EXISTING since 2026-08-21 and never exercised by any dry run. Not fixed: needs root, outside the authorized change set. Bundle 28 entries, verifies 28/28. Byte freeze HELD. Foundry df5ade0 + 2148eb9.
next:     Advisor adjudication. ONE OPERATOR ACTION before any real start: sudo mkdir -p /var/lib/wrought/runner-state && sudo chown kalib:kalib && sudo chmod 700 (0700 matters — ephemeral HOMEs holding credential copies live inside it). TWO RULINGS before the supervised batch: (1) the claude CLI self-updated 2.1.238 -> 2.1.250 today under its own load-bearing pin; (2) drop DBUS_SESSION_BUS_ADDRESS from the child env allowlist? Then supervised GATE-J0B (Phases 5-7 + seed rebuild), then ST-1.
usage:    n/a

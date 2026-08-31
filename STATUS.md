# STATUS — forge-mini executor heartbeat
updated:  2026-08-31T19:50:00Z
gate:     GATE-ORACLE-ISOLATION
state:    RUNNING P1
last:     **TRANSPORT-OK, 18/18 first run against the archived file** (`prompts/GATE-ORACLE-ISOLATION-v1.0.md`, 9,046 B, sha256 `7e18f0564f2cbfc358540133a0d868e2674037012709eaba725cae0cf5031b5d`); negative control discriminates — the three prior archived prompts still return their own declared 25 / 48 / 42. **PHASE 0 DISCHARGED as the first courier action:** `GATE-FIX`'s verdict is at `bundles/GATE-FIX/ADJUDICATION.md`, lifted **mechanically** with `sed -n '32,50p'` and proven byte-identical by `diff` (empty output; the one-line-tampered negative control shows the difference). `GATE-FIX`'s QUEUE row is `ADJUDICATED` and, being terminal, its 1,560 B of note text moved byte-for-byte to `QUEUE-ARCHIVE.md` behind a 310 B stub (§17). Byte freeze BEFORE captured (`build-evidence/gate-oracle-isolation/raw/00`).
next:     Measure the uid/capability ground truth INSIDE the shipped sandbox — whether a second uid is reachable under `bwrap --unshare-all --cap-drop ALL`, and how `/work/out` ownership can be enforced against the J-49 invariant. The mechanism is chosen from that measurement, not before it.
usage:    attended-direct session, claude-opus-5; no gate child, no runner, no budget cap consumed.

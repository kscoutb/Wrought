# bin/probe-verify-timeout
Purpose: Tests whether `RuntimeMaxSec` bounds a transient SCOPE and leaves a durable verdict after destruction, running plain, SIGTERM-ignoring, and fast-exit arms with/without `bwrap`.
Key functions: `check`, `journal`, `launch`, `main`.
Direct imports: `argparse`, `asyncio`, `json`, `subprocess`, `sys`, `time`.
Obvious risk: Hard-requires `sudo` and external system binaries (`systemd-run`, `journalctl`, `bwrap`); relies on specific PID namespace collapse and systemd timeout semantics that may break across kernel versions or containerized environments.

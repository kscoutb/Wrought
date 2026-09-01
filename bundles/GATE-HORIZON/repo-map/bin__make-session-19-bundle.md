# bin/make-session-19-bundle
Purpose: Generates a reproducible, non-version-controlled ZIP bundle (`SESSION-19-DECISIONS-GATE44-writeup-2026-08-08.zip`) packaging session reports, journal slices, evidence, source code, git diffs, and spec documents for external distribution.
Key functions or classes: None defined (shell script); orchestrates standard utilities (`mktemp`, `git`, `sed`, `awk`, `find`, `sha256sum`, `zip`, `unzip`, `stat`).
Direct imports/dependencies: Relies on local project files (`SESSION-REPORT-18.md`, `BUILD-JOURNAL.md`, `build-evidence/session-19/`, `src/wrought_supervisor/*.py`, `bin/gate44-*`, `CLAUDE.md`, `docs/08-decisions.md`, `pins.lock`) and system tools (`bash`, `git`, `zip`).
Obvious risk: Fragile due to hardcoded absolute paths (`/home/kalib/foundry`), a fixed commit base (`2f0e48e`), and a static line-number slice (`sed -n '7290,$p' BUILD-JOURNAL.md`), which will break if directory layouts or file lengths change.

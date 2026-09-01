# bin/make-review-bundle-20
Purpose: Assembles REVIEW-BUNDLE-20.zip containing session 20 cleanup evidence, git status/log, source files, a journal slice, and a SHA-256 manifest.
Key functions or classes: Standalone bash script with no defined functions or classes; operates via variables ZIP, STAGE, BASE and trap.
Direct imports/dependencies: CLI tools git, cp, sed, awk, find, xargs, sha256sum, zip, unzip, stat, mktemp and project files SESSION-REPORT-20.md, BUILD-JOURNAL.md, docs/08-decisions.md.
Obvious risk: Hardcoded absolute paths /home/kalib/foundry, /etc/credstore.encrypted, /var/lib/wrought/state/orchestrator.db combined with set -euo pipefail will abort execution if any expected file or directory is missing.

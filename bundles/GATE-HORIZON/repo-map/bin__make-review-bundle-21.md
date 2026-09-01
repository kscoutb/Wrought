# bin/make-review-bundle-21
Purpose: Assembles `REVIEW-BUNDLE-21.zip`, a review courier archive containing session reports, reorganized products, evidence, journal excerpts, and git metadata.
Key components: Shell variables `ZIP`, `STAGE`, `BASE` coordinate staging and archiving via `cp`, `git log`, `git diff`, `sha256sum`, and `zip`.
Dependencies: External utilities `git`, `zip`, `unzip`, `mktemp`, `sed`, `awk`; requires directory structure under `/home/kalib/foundry` and system paths like `/var/lib/wrought`.
Risks: Hardcoded paths and `BASE=69dcd50` reduce portability; `set -euo pipefail` halts on any missing file; regenerated artifacts (`MANIFEST.sha256`, `COMMITS.txt`) are excluded from version control.

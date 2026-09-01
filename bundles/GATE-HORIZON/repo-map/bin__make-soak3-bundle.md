# bin/make-soak3-bundle
Purpose: Generates REVIEW-BUNDLE-SOAK-3.zip for review by staging reports, harness scripts, build evidence, live status JSONs, and a manifest with build-time metadata and SHA-256 checksums.
Key functions/classes: None; operates as a linear bash script without named functions or classes.
Direct imports/dependencies: Relies on standard utilities (git, mktemp, zip, unzip, sha256sum, find, sort, xargs, cp, mkdir, rm) and hardcoded paths (/var/lib/wrought/soak3/track-a/status.json, /var/lib/wrought/soak3/track-b/status.json, SESSION-REPORT-SOAK-3.md, CLAUDE.md, pins.lock, build-evidence/soak-3).
Obvious risk: Hardcoded absolute paths and strict set -euo pipefail will abort the build if the target environment lacks the expected directory structure, file permissions, or a clean git repository state.

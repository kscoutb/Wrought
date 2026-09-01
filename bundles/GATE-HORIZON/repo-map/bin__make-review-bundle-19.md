# bin/make-review-bundle-19
Purpose: Assembles REVIEW-BUNDLE-19.zip, a standalone "courier" archive staging session 19/20 evidence, journal excerpts, source files, and git history for external review without committing duplicate data.
Key functions or classes: None defined; procedural bash execution driven by variables ZIP, STAGE, BASE and trap for cleanup.
Direct imports/dependencies: Relies on CLI utilities mktemp, git, sed, awk, sha256sum, zip, unzip, stat and project artifacts SESSION-REPORT-19.md, INVENTORY.md, BUILD-JOURNAL.md, docs/08-decisions.md, src/, bin/.
Obvious risk: Hardcoded /home/kalib/foundry path limits portability; fragile sed/awk regex parsing of markdown/journal headers will break on formatting changes; silent cp/mkdir calls lack error checks for missing artifacts.

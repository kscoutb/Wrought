# bin/soak3-importcheck
Purpose: Parses Python ASTs to detect direct imports of the forbidden wrought_escalation package, avoiding grep-based false positives.
Key functions/classes: top_level_imports, main
Direct imports/dependencies: __future__, ast, pathlib, sys
Obvious risk: ast.parse lacks try/except handling, risking uncaught exceptions on malformed or non-Python files; deliberately skips transitive dependency analysis.

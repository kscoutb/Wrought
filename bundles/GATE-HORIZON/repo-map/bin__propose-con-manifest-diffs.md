# bin/propose-con-manifest-diffs
Purpose: Prints proposed manifest diffs to opt fixtures into CON- constraint validation without applying changes, categorizing them as mechanical or semantic.
Key functions/classes: `nodes`, `main`
Direct imports/dependencies: `ast`, `pathlib`, `sys`, `ruamel.yaml.YAML`, `wrought_orchestrator.validate.CON_RE`, `wrought_orchestrator.validate.split_task_md`, `wrought_orchestrator.validate.validate`
Obvious risk: Mutates `sys.path` at runtime and relies on hardcoded glob patterns (`TASK-2026-0804-*`) and directory layouts, risking import shadowing or path resolution failures.

# bin/escalation-config-assert
Purpose: Offline validation script that asserts D19/D21 configuration constraints and request body safety without network calls, guarding against YAML boolean coercion hazards.
Key functions: ok, main, config.load, client.build_request_body.
Direct imports: pathlib, sys, tempfile, wrought_escalation.client, wrought_escalation.config.
Obvious risk: Dynamic sys.path injection and manual tempfile cleanup via unlink risk resource leaks on crashes; validation tests rely on exact string replacement in pins.lock and catch SystemExit for failures.

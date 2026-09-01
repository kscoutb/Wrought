# bin/wrought-course-check
Purpose: A halt-only safety valve that reads a run summary from stdin, enforces a spend cap, and delegates sealed-credential handling to systemd-run to invoke wrought-course-post, outputting only OK or HALT to gate runner progress.
Key functions: fail, main.
Direct imports/dependencies: json, os, subprocess, sys, tempfile, datetime, timezone, Path; relies on sudo, systemd-run, and the external wrought-course-post script.
Obvious risk: Shell command is constructed via f-string interpolation (f'cat "$CREDENTIALS_DIRECTORY/{cred}" | {POST} {summary_path}'), enabling command injection if POST, cred, or summary_path contain untrusted metacharacters; manual os.unlink cleanup risks leaving temporary files on disk after a crash.

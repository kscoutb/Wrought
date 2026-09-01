# bin/secret-leak-scan
Purpose: Reads a plaintext secret from STDIN and scans specified filesystem directories, git object history, and systemd journal for leaks, outputting only hit counts and file paths.
Key functions: _skipped, scan_tree, main
Direct imports: pathlib, subprocess, sys
Obvious risk: Loads entire file contents and git object blobs into memory via p.read_bytes() and capture_output=True, risking MemoryError and severe performance degradation; relies on hardcoded absolute paths like REPO = "/home/kalib/foundry" and /var/lib/wrought.

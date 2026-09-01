# bin/deploy-verifier
Purpose: Copies src/wrought_verifier/ to a frozen virtualenv and updates pins.lock with new SHA-256 hashes to prevent silent, un-deployed code edits.
Key functions: main, module_digest, _sha
Direct imports: argparse, hashlib, pathlib, shutil, subprocess, sys
Risk: Requires sudo to write directly to /opt/wrought/venv/ and modify pins.lock, explicitly bypassing documented project rules against writing to venv directories.

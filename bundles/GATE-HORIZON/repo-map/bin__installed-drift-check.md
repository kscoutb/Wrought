# bin/installed-drift-check
Purpose: Verifies installed binaries against repo source files and pins.lock hashes to detect deployment drift, missing pins, or unaccounted executables, enforcing a fail-fast policy for unknown files.
Key functions: sha256_file, dig, main.
Direct imports: argparse, hashlib, json, os, pathlib, sys, time, ruamel.yaml.
Risk: Hardcoded fallback paths (/home/kalib/foundry) and strict environment dependencies may break in non-standard deployments; assumes pins.lock structure stability without schema validation.

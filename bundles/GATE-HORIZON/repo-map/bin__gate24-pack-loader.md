# bin/gate24-pack-loader
Purpose: Validates that the pack loader rejects malformed pack definitions pre-execution with PACK_INVALID taxonomy codes and ensures untrusted tooling never runs on invalid packs.
Key functions/classes: main, say, ok, MUTATIONS, loads, PackInvalid, and dynamically imported vj (build_argv, assert_pinned_identities, wall_clock_bounds).
Direct imports/dependencies: importlib.machinery, importlib.util, json, os, pathlib, subprocess, sys, tempfile, wrought_verifier.pack.
Obvious risk: Executes sandboxed tests via sudo -n and systemctl, dynamically loads bin/verify-job, relies on hardcoded absolute paths, and processes mutated TOML fixtures that could bypass validation if sandbox isolation fails.

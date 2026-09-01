# bin/verify-job
Purpose: Production launcher that orchestrates sandboxed verification jobs by enforcing resource limits via systemd-run, prlimit, and bwrap while validating pinned artifacts.
Key functions: main, run, build_argv, assert_pinned_identities, assert_test_manifest, wall_clock_bounds, verifier_module_digest, job_paths, _sha256_file, pins.
Direct imports: argparse, asyncio, hashlib, json, os, pathlib, re, subprocess, sys, time, ruamel.yaml, wrought_supervisor.classify, wrought_supervisor.oracle.
Risks: Hard dependency on pins.lock for execution bounds and artifact pinning (triggers SystemExit on drift), direct sys.path mutation, and sudo privilege escalation for systemd scope management.

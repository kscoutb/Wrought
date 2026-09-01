# bin/test-stop33b-equivalence
Purpose: Validates equivalence between worker-driven oracle outcomes and legacy harness-injected verdicts, asserting identical FSM states, classifications, and provenance while enforcing fail-closed safety for missing verifiers.
Key functions: main, ok, install_oracle, stage, fresh_store, stream
Dependencies: store, worker, oracle, json, os, pathlib, shutil, subprocess, sys, tempfile
Risk: Executes subprocess.run with sudo for directory staging and cleanup, and hardcodes absolute paths (/var/lib/wrought/oracle, /var/lib/wrought/jobs), creating privilege escalation and environment isolation hazards.

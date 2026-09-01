# bin/oracle-isolation-probe
Purpose: Probes sandbox isolation to verify if a second UID is reachable inside the verification environment across shipped, nested, and rebuilt user-namespace layers.
Key functions: _load_verify_job, layer12, layer3, main.
Direct imports: argparse, ctypes, os, pathlib, subprocess, sys, time; dynamically executes bin/verify-job via exec.
Risk: Directly execs external source and manipulates raw user namespaces/UID maps via os.fork(), os.setresuid(), and /proc/[pid]/uid_map under sudo, creating privilege escalation and code injection exposure.

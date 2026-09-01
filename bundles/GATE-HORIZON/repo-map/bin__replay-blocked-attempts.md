# bin/replay-blocked-attempts
Purpose: Regresses session 12's blocked coding attempts against a recalibrated validation pack to verify warning-only failures now pass while real defects still fail.
Key functions: setup_replay, replay_one, downgrade_to_spec_signature, main.
Dependencies: argparse, asyncio, json, pathlib, shutil, subprocess, sys, and dynamically loaded bin/verify-job.
Risks: Invokes subprocess.run with sudo rm -rf and shutil.rmtree on filesystem paths, executes untrusted candidate code via dynamic imports, and relies on hardcoded absolute paths.

# bin/measure-typecheck-modes
Purpose: Evaluates which basedpyright typeCheckingMode suppresses bare `-> dict` return type warnings while retaining detection for planted type errors and undefined names, producing an admissibility matrix.
Key functions: `run_one` executes isolated test cells with separate config directories, while `main` orchestrates the `MODES` × `CASES` matrix, computes verdicts, and writes results to `build-evidence/session-13/01-recalibration/S13-typecheck-mode-matrix.json`.
Direct imports: `json`, `pathlib`, `shutil`, `subprocess`, `sys`, `tempfile`.
Obvious risks: Hardcoded absolute path `/opt/wrought/venv/bin/basedpyright` and rigid 300s `subprocess.run` timeout may fail in non-standard environments; script writes to a deep `build-evidence/` directory without creating parents and discards `p.stderr`.

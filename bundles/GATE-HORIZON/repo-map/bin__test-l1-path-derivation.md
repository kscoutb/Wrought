# bin/test-l1-path-derivation
Purpose: Validates that `oracle.job_dir` and `oracle.stage_candidate` safely reject traversal payloads and invalid identifiers to prevent command injection before paths reach `sudo -n rm -rf`.
Key functions/classes: `oracle.job_dir`, `oracle.stage_candidate`, `pathlib.Path`, `ValueError`.
Direct imports/dependencies: `pathlib`, `sys`, `wrought_supervisor`.
Obvious risk: `oracle.stage_candidate` feeds derived paths directly into `subprocess.run(["sudo","-n","rm","-rf", str(src)])`, creating a critical arbitrary deletion vulnerability if path derivation validation is bypassed.

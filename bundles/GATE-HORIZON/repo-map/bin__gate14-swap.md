# bin/gate14-swap
Purpose: Validates the D13 fallback-swap procedure for `wrought-inference.service` by sampling `mem_info_vram_used` to confirm full VRAM release within tolerance and measuring the single-command swap wall-clock time.
Key functions: `mib`, `active_name`.
Dependencies: External binaries `systemctl`, `curl`, `bc`, `date`, `ln`, `readlink`, `basename`, `cat`, `sudo`, `sh`, and configuration variables `VRAM`, `PROFILES`, `ACTIVE`, `UNIT`, `TOL_MIB`, `OUT`.
Risks: Hardcoded GPU PCI address `0000:c7:00.0`, uses fixed `sleep` delays instead of waiting for actual process termination, and executes `sudo systemctl stop` without graceful shutdown signals that may cause driver hangs or model state corruption.

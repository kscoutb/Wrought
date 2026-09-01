# bin/set-power-profile
Purpose: Forces CPU scaling governors and PCIe ASPM to `performance` mode by writing directly to sysfs nodes for all online cores.
Key functions/classes: None (inline bash logic relying on constants `GOVERNOR`, `ASPM_POLICY`, `ASPM_NODE`, and array `governors`).
Direct imports/dependencies: `bash`, sysfs paths `/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor` and `/sys/module/pcie_aspm/parameters/policy`, plus external verifier `assert-power-profile`.
Obvious risk: Assumes root privileges for sysfs writes without explicit checks; strict `set -euo pipefail` will abort execution if cpufreq drivers or ASPM nodes are absent, potentially halting dependent service initialization.

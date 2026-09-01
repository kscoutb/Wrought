# bin/assert-power-profile
Purpose: Asserts kernel power profile post-conditions by verifying amd_pstate status, CPU governor/EPP values, and PCIe ASPM policy against expected settings.
Key functions/classes: fail
Direct imports/dependencies: bash, sed, /sys/devices/system/cpu/amd_pstate/status, /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor, /sys/devices/system/cpu/cpu[0-9]*/cpufreq/energy_performance_preference, /sys/module/pcie_aspm/parameters/policy
Obvious risk: Fragile sed regex for ASPM policy parsing; assumes unrestricted /sys read access without privilege checks; set -u may trigger unbound variable errors if glob patterns match nothing despite nullglob.

# bin/gate06-reverify
Purpose: Independently verifies dGPU render node access and Vulkan/RADV initialization inside a transient systemd unit configured with `User=llama` and `SupplementaryGroups=render`.
Key functions/classes: None (shell script); executes `vulkaninfo`, `timeout`, `readlink`, and `grep`.
Direct imports/dependencies: `/dev/dri/by-path/pci-0000:c7:00.0-render`, `/sys/bus/pci/devices/0000:c7:00.0`, `MESA_SHADER_CACHE_DISABLE`, `MESA_VK_DEVICE_SELECT_FORCE_DEFAULT_DEVICE=1`.
Obvious risk: `exec 3<>'$RESOLVED'` uses inner single quotes that prevent variable expansion; forcing `MESA_VK_DEVICE_SELECT` on a wedged GPU may cause indefinite hangs; relies on hardcoded PCI paths.

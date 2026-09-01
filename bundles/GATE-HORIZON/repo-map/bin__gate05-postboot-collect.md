# bin/gate05-postboot-collect
Purpose: Temporary bash scaffolding to collect post-reboot evidence for GATE-05/06 by verifying amdgpu.runpm=0 disables GPU runtime PM, llama user access via the render group, and Vulkan stack initialization.
Key Functions: neg_arm_open, gate06_probe, sample, r, pm_line.
Dependencies: External binaries setpriv, vulkaninfo, udevadm, journalctl, systemctl, and sysfs paths under /sys/bus/pci/devices/.
Risks: Explicitly marked for removal; hardcodes PCI BDFs and assumes specific hardware; long sleep intervals may block the calling systemd unit; privilege switching via setpriv requires careful boundary management.

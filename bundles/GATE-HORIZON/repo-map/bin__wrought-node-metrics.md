# bin/wrought-node-metrics
Purpose: Standalone Prometheus metrics exporter that scrapes AMDGPU hwmon, /proc, filesystem stats, and a configurable textfile directory, serving merged results over loopback HTTP.
Key functions/classes: _read, _hwmon_dirs, collect, Handler, Server, main.
Direct imports: http.server, os, pathlib, socketserver, sys.
Risk: Silently substitutes None or 0.0 for unreadable or missing sysfs/procfs nodes, potentially masking permission errors or hardware failures while adhering to a strict no-invented-thresholds policy.

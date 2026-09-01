# bin/gate20-vram
Purpose: Launches `llama-server` with two profiles to extract KV, RS, compute, and output buffer sizes from verbose logs, validates >=1 GB VRAM headroom, and resolves CONFLICT C1 regarding MTP recurrent state scaling.
Key function: `probe`
Dependencies: Sources `$CONF`, executes `$LLAMA`, `curl`, `bc`, `grep`, `sed`, and reads sysfs `mem_info_vram_used` and `mem_info_vram_total`.
Risk: Hardcoded PCI path `0000:c7:00.0`, brittle regex parsing of exact log strings, and direct `kill $pid` termination that may cause unclean server shutdown or zombie processes.

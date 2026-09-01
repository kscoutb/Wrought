# bin/gate12-devstral-ctx
Purpose: Empirically measures VRAM consumption for candidate context sizes (32768, 65536, 98304, 131072) to derive the largest safe `--ctx-size` for the Devstral model, avoiding hardcoded assumptions from hybrid architectures.
Key functions/classes: None (standalone Bash script relying on variables `$LLAMA`, `$TOKEN`, `$BEST`, and `$HEADROOM_MIB`).
Dependencies: Sources `$CONF` (`/etc/wrought/serving.env`), invokes `python3` with `yaml`, `llama-server`, `curl`, and reads `/home/kalib/foundry/pins.lock`.
Risks: Hardcoded PCI path `0000:c7:00.0` breaks portability; VRAM polling at `mem_info_vram_used` may miss peak allocation; rapid `kill`/`sleep` cycle in the loop risks port collisions or orphaned `llama-server` processes.

# bin/gen-pack
Purpose: Derives version-pinned TOML verification and security packs from `pins.lock` to enforce a single source of truth, with a `--check` flag to detect hand-edited artifacts.
Key Functions: `main`, `generate`, `_calibration`, `_checks`, `toml_scalar`, `toml_key`
Dependencies: `argparse`, `hashlib`, `io`, `json`, `pathlib`, `sys`, `ruamel.yaml.YAML`
Risk: Hardcoded absolute paths (`VENV`, `/work/src`, `/work/out`), custom manual TOML serialization bypassing standard libraries, and fatal `SystemExit` on missing `pins.lock` keys that halt generation without graceful fallback.

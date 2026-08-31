# REPO-MAP — every script under `bin/` and module under `src/`, summarized locally
**Generated, not written.** Each entry below is a summary produced by the RESIDENT local model (Qwen3.6-27B, UD-Q4_K_XL, reasoning on) reading one file, air-gapped, at zero marginal cost. This file is assembled mechanically from those summaries by `assemble-repo-map.py`; no human and no cloud model reviewed the prose.
## What a RELIABLE verdict means, and what it does not
Every entry carried here passed `check-groundedness.py`: the identifiers the summary cites were grepped against the file it summarizes, and at least 60 % of them literally appear in it. **That is a test for FABRICATION and nothing else.** A summary can cite only real names and still describe them wrongly, cite the unimportant ones, or omit what matters. **Read an entry as *not obviously fabricated*, never as *correct*.**
- Summaries produced: **17**
- Carried here as RELIABLE: **15** of 15 checkable (100.0 %)
- Carried with the caveat UNCHECKABLE: **2** (too few citable names for a ratio to mean anything — an instrument limit, **not** evidence of fabrication)
- Excluded: **0**
- Identifier groundedness across all checked summaries: **116/130 (89.2 %)**

---

## RELIABLE summaries

### `bin/`

**`bin/baseline-report`** · grounded 8/8
> Purpose: Generates a baseline dashboard reporting escalation demand/resolution rates, oracle pass metrics, repair histograms, and cost ledgers using pooled binomial Wilson confidence intervals.
> Key functions: pct, wilson, ci_s, overlap, _measure_synthetic, run_pack_ids, oracle_passed, escalation_demanded, main
> Direct imports: argparse, glob, json, pathlib, statistics, sys, wrought_orchestrator.store, wrought_escalation.ledger
> Obvious risks: Hardcoded absolute paths (/var/lib/wrought/*) limit portability; broad except Exception blocks silently swallow database/package errors; dynamic late imports may crash if dependencies are missing.

**`bin/baseline-run`** · grounded 11/11
> Purpose: Runs a controlled baseline benchmark of operator-authored fixtures to measure LLM code-generation success rates and escalation demand under strict, auditable constraints.
> Key Functions: `load_fixtures`, `build_messages`, `generate`, `run_task`, `main`
> Direct Imports: `wrought_escalation`, `wrought_orchestrator`, `wrought_supervisor`, `ruamel.yaml`, `urllib.request`, `subprocess`
> Obvious Risk: Depends on `sudo` execution, systemd credential decryption, and hardcoded paths; token budget misconfiguration or queue desyncs trigger hard refusals or silent truncation.

**`bin/build-replay-corpus`** · grounded 12/15
> Purpose: Generates a synthetic replay corpus spanning all projection states, repair indices, and escalation flags for parity testing and GATE-37 validation.
> Key functions: `main`, `sh`, `sh_env`, and `_with_db` orchestrate the workflow and CLI argument injection.
> Dependencies: `argparse`, `json`, `pathlib`, `subprocess`, `sys`, `time`, `os`, and `wrought_orchestrator.store`.
> Risk: Explicitly refuses to run against `store.DB_PATH` unless `--allow-production` is passed, but relies entirely on `./bin/orchestrator` subprocess execution with injected chaos environment variables (`WROUGHT_CHAOS_KILL`) that could obscure CLI failure diagnostics.

**`bin/decompose-baseline`** · grounded 3/3
> Purpose: Decomposes baseline task runs into comparative metrics (escalation demand/resolve, completion rates, and blocker classifications) for a before/after oracle analysis.
> Key functions: load, blockers, classify_best, main.
> Direct imports: collections, glob, json, pathlib, sys.
> Risk: Hardcoded search paths in SEARCH and potential ZeroDivisionError if n=0; historically vulnerable to miscounting empty generations as passes despite current guards.

**`bin/deploy-verifier`** · grounded 2/2
> Purpose: Copies src/wrought_verifier/ to a frozen virtualenv and updates pins.lock with new SHA-256 hashes to prevent silent, un-deployed code edits.
> Key functions: main, module_digest, _sha
> Direct imports: argparse, hashlib, pathlib, shutil, subprocess, sys
> Risk: Requires sudo to write directly to /opt/wrought/venv/ and modify pins.lock, explicitly bypassing documented project rules against writing to venv directories.

**`bin/escalate-once`** · grounded 6/6
> Purpose: Executes a single production escalation call with strict credential isolation and explicit ledger verification.
> Key functions/classes: main, config.load, store.init_db, store.append_and_project, escalate.read_credential, escalate.escalate, ledger.authority, ledger.summary.
> Direct imports: argparse, json, pathlib, sys, wrought_escalation.config, wrought_escalation.escalate, wrought_escalation.ledger, wrought_orchestrator.store.
> Risk: Mandates precise systemd-run execution to inject secrets via $CREDENTIALS_DIRECTORY; improper invocation causes credential exposure or runtime crashes, and sys.path.insert mutates runtime imports.

**`bin/gate05-postboot-collect`** · grounded 3/3
> Purpose: Temporary bash scaffolding to collect post-reboot evidence for GATE-05/06 by verifying amdgpu.runpm=0 disables GPU runtime PM, llama user access via the render group, and Vulkan stack initialization.
> Key Functions: neg_arm_open, gate06_probe, sample, r, pm_line.
> Dependencies: External binaries setpriv, vulkaninfo, udevadm, journalctl, systemctl, and sysfs paths under /sys/bus/pci/devices/.
> Risks: Explicitly marked for removal; hardcodes PCI BDFs and assumes specific hardware; long sleep intervals may block the calling systemd unit; privilege switching via setpriv requires careful boundary management.

**`bin/gate06-reverify`** · grounded 6/8
> Purpose: Independently verifies dGPU render node access and Vulkan/RADV initialization inside a transient systemd unit configured with `User=llama` and `SupplementaryGroups=render`.
> Key functions/classes: None (shell script); executes `vulkaninfo`, `timeout`, `readlink`, and `grep`.
> Direct imports/dependencies: `/dev/dri/by-path/pci-0000:c7:00.0-render`, `/sys/bus/pci/devices/0000:c7:00.0`, `MESA_SHADER_CACHE_DISABLE`, `MESA_VK_DEVICE_SELECT_FORCE_DEFAULT_DEVICE=1`.
> Obvious risk: `exec 3<>'$RESOLVED'` uses inner single quotes that prevent variable expansion; forcing `MESA_VK_DEVICE_SELECT` on a wedged GPU may cause indefinite hangs; relies on hardcoded PCI paths.

**`bin/gate09b-10b-orch-freeze`** · grounded 5/5
> Purpose: Validates a frozen orchestrator Python environment by enforcing reproducible hash-pinned installs, rejecting tampered or unhashed packages, and verifying import-time hermeticity via strace network syscall filtering.
> Key functions/classes: say, assert, YAML, jsonschema.validate, rfc8785.dumps, hashlib.sha256.
> Dependencies: pip, strace, python3.14, ruamel.yaml, jsonschema, rfc8785, hashlib, io, json, re, sys.
> Obvious risk: Explicitly documents that ruamel.yaml only covers 2 of 7 required safety constraints, leaving critical protections (anchors/aliases, merge keys, depth/size limits, non-finite numbers) as unimplemented manual requirements marked OURS.

**`bin/gate12-devstral-ctx`** · grounded 10/14
> Purpose: Empirically measures VRAM consumption for candidate context sizes (32768, 65536, 98304, 131072) to derive the largest safe `--ctx-size` for the Devstral model, avoiding hardcoded assumptions from hybrid architectures.
> Key functions/classes: None (standalone Bash script relying on variables `$LLAMA`, `$TOKEN`, `$BEST`, and `$HEADROOM_MIB`).
> Dependencies: Sources `$CONF` (`/etc/wrought/serving.env`), invokes `python3` with `yaml`, `llama-server`, `curl`, and reads `/home/kalib/foundry/pins.lock`.
> Risks: Hardcoded PCI path `0000:c7:00.0` breaks portability; VRAM polling at `mem_info_vram_used` may miss peak allocation; rapid `kill`/`sleep` cycle in the loop risks port collisions or orphaned `llama-server` processes.

**`bin/gate13-measure`** · grounded 11/16
> Purpose: Benchmarks `llama-server` cold/warm load times, HMB presence, TTFT prefill curves, and chat template overhead against a <60s cold threshold.
> Key functions: `stop_server`, `start_server`, `wait_ready` manage process lifecycle, explicit PID tracking, and `/health` endpoint polling.
> Dependencies: Sources `"$CONF"`, executes `"$LLAMA"`, and relies on `curl`, `python3`, `bc`, `awk`, `systemctl`, and `sudo`.
> Risk: Requires `sudo` privileges to flush page cache via `/proc/sys/vm/drop_caches`; forcibly aborts if `wrought-inference.service` is active to prevent port contention and accidental termination of resident processes.

**`bin/gate14-swap`** · grounded 17/17
> Purpose: Validates the D13 fallback-swap procedure for `wrought-inference.service` by sampling `mem_info_vram_used` to confirm full VRAM release within tolerance and measuring the single-command swap wall-clock time.
> Key functions: `mib`, `active_name`.
> Dependencies: External binaries `systemctl`, `curl`, `bc`, `date`, `ln`, `readlink`, `basename`, `cat`, `sudo`, `sh`, and configuration variables `VRAM`, `PROFILES`, `ACTIVE`, `UNIT`, `TOL_MIB`, `OUT`.
> Risks: Hardcoded GPU PCI address `0000:c7:00.0`, uses fixed `sleep` delays instead of waiting for actual process termination, and executes `sudo systemctl stop` without graceful shutdown signals that may cause driver hangs or model state corruption.

**`bin/gate15-bench-matrix`** · grounded 2/2
> Purpose: Runs a two-lever benchmark matrix (CPU governor and GGML_VK_ALLOW_GRAPHICS_QUEUE) for pp2048 and tg128 metrics, computing median/stdev and enforcing a 2-4% noise-band threshold before declaring winners.
> Key functions: set_governor, restore, bench_one.
> Dependencies: llama-bench, llama-server, assert-power-profile, set-power-profile, python3 (json, statistics), sudo tee, grep, sed.
> Risks: Direct sudo writes to /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; relies on trap restore EXIT INT TERM for cleanup, which may fail on SIGKILL or permission drift, leaving the system in an altered power state.

**`bin/gate16-fresh`** · grounded 12/12
> Purpose: Isolates CPU vs GPU inference variance on fresh server startups by fixing request ordinal at 1, verifying absence of corruption signatures, and ensuring divergent tokens fall within a logit tolerance threshold.
> Key functions/classes: `run_first`, `corrupt`, `top`
> Direct imports/dependencies: `curl`, `python3`, `json`, `sys`, `re`, `grep`, `sed`, `LLAMA_SERVER`
> Obvious risk: Background `llama-server` processes are managed via manual `kill`/`wait` without trap handlers, risking orphaned instances on interruption; brittle validation assumes strict CLI flag support and JSON response schemas.

**`bin/gate17-ordinal-sweep`** · grounded 8/8
> Purpose: Validates that varying request ordinals on a resident `llama-server` yield benign, coherent outputs by sweeping prompts and comparing per-ordinal perplexity proxies against corruption/degeneration signatures.
> Key functions or classes: `collections.defaultdict`, `collections.Counter`, `hashlib.sha256`, `re.search`, `math.exp`.
> Direct imports/dependencies: `curl`, `python3`, `bash`, sourced `$WROUGHT_CONF` (`/etc/wrought/serving.env`), and the `$LLAMA` binary.
> Obvious risk: Relies on hardcoded port `8093` and external env vars; inline Python uses minimal JSON validation, and the server startup/teardown loop may leave orphaned processes or abort silently if the `curl` health check fails.

## UNCHECKABLE summaries — carried, with the caveat
*These cite fewer than two checkable identifiers, so the groundedness ratio would be noise. They are carried because excluding honest summaries over an instrument limitation would bias this map toward whatever the checker parses well.*

### `bin/`

**`bin/assert-power-profile`**
> Purpose: Asserts kernel power profile post-conditions by verifying amd_pstate status, CPU governor/EPP values, and PCIe ASPM policy against expected settings.
> Key functions/classes: fail
> Direct imports/dependencies: bash, sed, /sys/devices/system/cpu/amd_pstate/status, /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor, /sys/devices/system/cpu/cpu[0-9]*/cpufreq/energy_performance_preference, /sys/module/pcie_aspm/parameters/policy
> Obvious risk: Fragile sed regex for ASPM policy parsing; assumes unrestricted /sys read access without privilege checks; set -u may trigger unbound variable errors if glob patterns match nothing despite nullglob.

**`bin/escalation-config-assert`**
> Purpose: Offline validation script that asserts D19/D21 configuration constraints and request body safety without network calls, guarding against YAML boolean coercion hazards.
> Key functions: ok, main, config.load, client.build_request_body.
> Direct imports: pathlib, sys, tempfile, wrought_escalation.client, wrought_escalation.config.
> Obvious risk: Dynamic sys.path injection and manual tempfile cleanup via unlink risk resource leaks on crashes; validation tests rely on exact string replacement in pins.lock and catch SystemExit for failures.

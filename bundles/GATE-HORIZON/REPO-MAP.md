# REPO-MAP — every script under `bin/` and module under `src/`, summarized locally
**Generated, not written.** Each entry below is a summary produced by the RESIDENT local model (Qwen3.6-27B, UD-Q4_K_XL, reasoning on) reading one file, air-gapped, at zero marginal cost. This file is assembled mechanically from those summaries by `assemble-repo-map.py`; no human and no cloud model reviewed the prose.
## What a RELIABLE verdict means, and what it does not
Every entry carried here passed `check-groundedness.py`: the identifiers the summary cites were grepped against the file it summarizes, and at least 60 % of them literally appear in it. **That is a test for FABRICATION and nothing else.** A summary can cite only real names and still describe them wrongly, cite the unimportant ones, or omit what matters. **Read an entry as *not obviously fabricated*, never as *correct*.**
- Summaries produced: **127**
- Carried here as RELIABLE: **113** of 113 checkable (100.0 %)
- Carried with the caveat UNCHECKABLE: **14** (too few citable names for a ratio to mean anything — an instrument limit, **not** evidence of fabrication)
- Excluded: **0**
- Identifier groundedness across all checked summaries: **1102/1135 (97.1 %)**

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

**`bin/gate-review-send-panel`** · grounded 13/13
> Purpose: Dispatches a security review packet to an independent LLM panel via OpenRouter, enforcing Zero-Data-Retention models and a hard `CEILING_USD` budget while saving structured results.
> Key functions: `key()`, `get_json()`, `read()`, `build_user_message()`, `main()`
> Direct imports: `json`, `os`, `pathlib`, `sys`, `time`, `urllib.request`, `urllib.error`
> Obvious risk: Hard dependency on `$CREDENTIALS_DIRECTORY` and systemd `LoadCredentialEncrypted` causes immediate `SystemExit` if misconfigured; relies on external OpenRouter pricing/metadata endpoints and network stability, with a rigid budget check that may prematurely skip models if API rates change.

**`bin/gate05-postboot-collect`** · grounded 3/3
> Purpose: Temporary bash scaffolding to collect post-reboot evidence for GATE-05/06 by verifying amdgpu.runpm=0 disables GPU runtime PM, llama user access via the render group, and Vulkan stack initialization.
> Key Functions: neg_arm_open, gate06_probe, sample, r, pm_line.
> Dependencies: External binaries setpriv, vulkaninfo, udevadm, journalctl, systemctl, and sysfs paths under /sys/bus/pci/devices/.
> Risks: Explicitly marked for removal; hardcodes PCI BDFs and assumes specific hardware; long sleep intervals may block the calling systemd unit; privilege switching via setpriv requires careful boundary management.

**`bin/gate06-reverify`** · grounded 6/6
> Purpose: Independently verifies dGPU render node access and Vulkan/RADV initialization inside a transient systemd unit configured with `User=llama` and `SupplementaryGroups=render`.
> Key functions/classes: None (shell script); executes `vulkaninfo`, `timeout`, `readlink`, and `grep`.
> Direct imports/dependencies: `/dev/dri/by-path/pci-0000:c7:00.0-render`, `/sys/bus/pci/devices/0000:c7:00.0`, `MESA_SHADER_CACHE_DISABLE`, `MESA_VK_DEVICE_SELECT_FORCE_DEFAULT_DEVICE=1`.
> Obvious risk: `exec 3<>'$RESOLVED'` uses inner single quotes that prevent variable expansion; forcing `MESA_VK_DEVICE_SELECT` on a wedged GPU may cause indefinite hangs; relies on hardcoded PCI paths.

**`bin/gate09b-10b-orch-freeze`** · grounded 5/5
> Purpose: Validates a frozen orchestrator Python environment by enforcing reproducible hash-pinned installs, rejecting tampered or unhashed packages, and verifying import-time hermeticity via strace network syscall filtering.
> Key functions/classes: say, assert, YAML, jsonschema.validate, rfc8785.dumps, hashlib.sha256.
> Dependencies: pip, strace, python3.14, ruamel.yaml, jsonschema, rfc8785, hashlib, io, json, re, sys.
> Obvious risk: Explicitly documents that ruamel.yaml only covers 2 of 7 required safety constraints, leaving critical protections (anchors/aliases, merge keys, depth/size limits, non-finite numbers) as unimplemented manual requirements marked OURS.

**`bin/gate12-devstral-ctx`** · grounded 6/6
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

**`bin/gate16-fresh`** · grounded 11/11
> Purpose: Isolates CPU vs GPU inference variance on fresh server startups by fixing request ordinal at 1, verifying absence of corruption signatures, and ensuring divergent tokens fall within a logit tolerance threshold.
> Key functions/classes: `run_first`, `corrupt`, `top`
> Direct imports/dependencies: `curl`, `python3`, `json`, `sys`, `re`, `grep`, `sed`, `LLAMA_SERVER`
> Obvious risk: Background `llama-server` processes are managed via manual `kill`/`wait` without trap handlers, risking orphaned instances on interruption; brittle validation assumes strict CLI flag support and JSON response schemas.

**`bin/gate17-ordinal-sweep`** · grounded 7/7
> Purpose: Validates that varying request ordinals on a resident `llama-server` yield benign, coherent outputs by sweeping prompts and comparing per-ordinal perplexity proxies against corruption/degeneration signatures.
> Key functions or classes: `collections.defaultdict`, `collections.Counter`, `hashlib.sha256`, `re.search`, `math.exp`.
> Direct imports/dependencies: `curl`, `python3`, `bash`, sourced `$WROUGHT_CONF` (`/etc/wrought/serving.env`), and the `$LLAMA` binary.
> Obvious risk: Relies on hardcoded port `8093` and external env vars; inline Python uses minimal JSON validation, and the server startup/teardown loop may leave orphaned processes or abort silently if the `curl` health check fails.

**`bin/gate18-longctx`** · grounded 9/9
> Purpose: Validates LLM long-context state integrity via ordered-recall probes at 32K/64K depths and perplexity spread analysis across KV quantization configurations.
> Key Functions/Classes: None (shell script); orchestrates `llama-server`, `llama-perplexity`, `curl`, and inline `python3` blocks.
> Imports/Dependencies: Sources `$CONF`; depends on `$CLI`, `$PPL`, `$LLAMA_SERVER`, `$CORPUS`, `timeout`, `grep`, `sed`, `sha256sum`, `kill`, `wait`.
> Risk: Fragile `grep`-based PPL extraction may break across `llama.cpp` versions; manual `kill`/`wait` loops and `timeout 5400` windows risk orphaned processes and VRAM exhaustion if interrupted.

**`bin/gate20-vram`** · grounded 6/6
> Purpose: Launches `llama-server` with two profiles to extract KV, RS, compute, and output buffer sizes from verbose logs, validates >=1 GB VRAM headroom, and resolves CONFLICT C1 regarding MTP recurrent state scaling.
> Key function: `probe`
> Dependencies: Sources `$CONF`, executes `$LLAMA`, `curl`, `bc`, `grep`, `sed`, and reads sysfs `mem_info_vram_used` and `mem_info_vram_total`.
> Risk: Hardcoded PCI path `0000:c7:00.0`, brittle regex parsing of exact log strings, and direct `kill $pid` termination that may cause unclean server shutdown or zombie processes.

**`bin/gate21-bwrap-smoke`** · grounded 6/6
> Purpose: Validates that `bwrap` sandboxes correctly resolve merged-/usr symlinks for `/bin`, `/lib`, and `/sbin` while executing `python3.14` with required imports and isolated networking.
> Key function: `check`
> Dependencies: `bwrap`, `python3.14`, `ssl`, `secrets`, `multiprocessing`, `socket`, `os`
> Risk: Deliberately omits seccomp filtering (`seccomp-deny.bpf`) and relies entirely on `bwrap` namespace isolation, making execution vulnerable to host symlink misconfigurations or `bwrap` bug #686.

**`bin/gate23-classifier`** · grounded 15/15
> Purpose: Test harness (GATE-23) that validates a substrate classification pipeline by inducing and synthetically simulating specific runtime failures (OOM, ENOSPC, timeouts, network attempts, and collection errors).
> Key functions: `check`, `fixture_pack`, `run`, `make_task`, `main`.
> Direct imports/dependencies: `importlib.machinery`, `importlib.util`, `json`, `os`, `re`, `pathlib`, `subprocess`, `sys`, `tempfile`, `time`, `vj` (dynamically loaded from `bin/verify-job`), `classify` (from `wrought_supervisor.classify`).
> Obvious risk: Invokes `sudo` via `subprocess` for directory creation and systemd unit resets, dynamically executes external modules, and writes to system paths (`/var/lib/wrought/`, `/etc/wrought/`), creating privilege escalation and execution injection vulnerabilities if the harness or `vj` module is compromised.

**`bin/gate24-pack-loader`** · grounded 7/9
> Purpose: Validates that the pack loader rejects malformed pack definitions pre-execution with PACK_INVALID taxonomy codes and ensures untrusted tooling never runs on invalid packs.
> Key functions/classes: main, say, ok, MUTATIONS, loads, PackInvalid, and dynamically imported vj (build_argv, assert_pinned_identities, wall_clock_bounds).
> Direct imports/dependencies: importlib.machinery, importlib.util, json, os, pathlib, subprocess, sys, tempfile, wrought_verifier.pack.
> Obvious risk: Executes sandboxed tests via sudo -n and systemctl, dynamically loads bin/verify-job, relies on hardcoded absolute paths, and processes mutated TOML fixtures that could bypass validation if sandbox isolation fails.

**`bin/gate25-hardening`** · grounded 12/12
> Purpose: Validates sandbox hardening and containment (GATE-25) by executing hostile and clean tasks via the production launcher, verifying systemd slice limits, seccomp/bwrap restrictions, and oracle integrity.
> Key functions: `say`, `check`, `run_job`, `main`.
> Direct imports/dependencies: `json`, `pathlib`, `subprocess`, `sys`; relies on external binaries `./bin/verify-job`, `systemctl`, `sudo`, and `sha256sum`.
> Risks: Invokes `subprocess.run` with `sudo` and unvalidated external commands; mutates a global `FAIL` variable for test aggregation; assumes stable output formats and availability of host tools without robust fallbacks.

**`bin/gate25-measure-tasksmax`** · grounded 12/12
> Purpose: Empirically measures peak process counts via systemd cgroup `pids.peak` to calculate a data-driven `TasksMax` limit with a 4x safety margin.
> Key functions: `slice_cgroup`, `poll_peak`, `one_run`, `main`.
> Direct imports/dependencies: `json`, `pathlib`, `statistics`, `subprocess`, `sys`, `threading`, `time`; relies on external `./bin/verify-job` and `/sys/fs/cgroup`.
> Obvious risks: Cgroup teardown race may miss spikes after the final sample; hardcodes `wrought-verify.slice` and `GATE-25-SELFTEST`; depends on dynamic globbing of scope names.

**`bin/gate26-routing`** · grounded 7/7
> Purpose: Validates routing-classifier policy and FSM transition rules for task failure handling, escalation, and human-review routing.
> Key functions/classes: main, ok, pytest_env, verdict_for, route, TaskState, failure_signature, classify, validate, guard_ok.
> Direct imports: json, pathlib, subprocess, sys, inspect, ast, wrought_orchestrator.fsm, wrought_supervisor.router, wrought_supervisor.classify, wrought_orchestrator.worker, wrought_verifier.pack.
> Risk: Executes sudo cat and hardcodes absolute system paths requiring root privileges; explicitly discloses that route() is unwired from the production FSM and only invoked by this test script.

**`bin/gate29-security-offline`** · grounded 15/15
> Purpose: Validates that adopted security tools execute fully offline with zero AF_INET/AF_INET6 connection attempts while still producing legitimate security outputs, enforced via `bwrap --unshare-net` and `strace`.
> Key functions: `ok`, `run_offline`, `arm`, `main`.
> Dependencies: `json`, `os`, `pathlib`, `re`, `shutil`, `subprocess`, `sys`, `tempfile`, plus invoked binaries `bwrap`, `strace`, `ruff`, `bandit`, `gitleaks`, `syft`, `osv-scanner`, `pip-audit`.
> Risk: Hard-coded absolute paths (`/opt/wrought/venv/bin`, `/var/lib/wrought/osv-db`) and a 900s `subprocess` timeout make execution fragile to environment drift or tool hangs; `trace` parsing failures could mask harness measurement gaps despite explicit guards.

**`bin/gate30-secrets`** · grounded 15/15
> Purpose: Validates secure credential placement and leak prevention across five compliance arms, verifying `systemd-creds` storage, service access via `$CREDENTIALS_DIRECTORY`, sandbox isolation, and binary drift detection.
> Key functions/executables: `say`, `assert`, `secret-leak-scan`, `wrought-secret-watch`, `installed-drift-check`.
> Dependencies: `systemd-creds`, `systemd-run`, `bwrap`, `sudo`, `python3`, `systemctl`, and data files `/var/lib/wrought/metrics/secret-exposure.prom` and `/etc/wrought/accepted-secret-exposures.tsv`.
> Risk: Pipes decrypted secrets to `secret-leak-scan` via stdin and relies heavily on `sudo`; explicitly exits with `PARTIAL` status due to a blocked REPLICA arm awaiting external R2 credentials, while exemption logic depends on live Prometheus metrics and active system timers.

**`bin/gate37-replay`** · grounded 14/14
> Purpose: Validates projection-rebuild parity against an event log and measures GATE-37 replay/snapshot cadence thresholds for full-projection and per-stream reconstructions using a synthetic corpus.
> Key functions/classes: `main`, `ok`, `drop_caches`, `connect`, `rebuild_projection`, `projection_parity`, `STATES`.
> Direct imports/dependencies: `__future__`, `json`, `pathlib`, `subprocess`, `os`, `sys`, `time`, `wrought_orchestrator.store`, `wrought_orchestrator.fsm`.
> Risks: Requires `sudo` to flush OS caches; tightly coupled to `GATE-39` which may unlink the corpus DB; timing measurements are explicit synthetic floors, not production ceilings.

**`bin/gate38-canon`** · grounded 4/4
> Purpose: Validates canon_v2 hash stability and conformance against committed digests in fixtures/canon-v2-vectors.json to detect specification drift.
> Key functions/classes: ok, digest, main, TRANSFORMS, canon_v2, split_task_md, YAML.
> Direct imports/dependencies: hashlib, io, json, pathlib, subprocess, sys, ruamel.yaml, wrought_orchestrator.validate.
> Obvious risk: Relies on hardcoded string replacements and sys.path.insert manipulation, making it brittle across environments; subprocess calls assume Unix tools and specific PATH configurations.

**`bin/gate39-chaos`** · grounded 17/17
> Purpose: Validates crash recovery correctness by simulating `kill -9` chaos to guarantee zero task loss or duplication, exercising lease lapse, fenced acks, dead-lettering, and event log invariants.
> Key functions: `reset`, `work_subprocess`, `work_parallel`, `audit`, `drain`, `main`.
> Dependencies: `json`, `os`, `pathlib`, `random`, `shutil`, `signal`, `sqlite3`, `subprocess`, `sys`, `time`, `store`, `worker`, and `./bin/orchestrator`.
> Risk: `reset()` destructively unlinks the database and `-wal/-shm` siblings; if `WROUGHT_DB` is inherited from the environment, it will erase unrelated databases despite the explicit assertion guard.

**`bin/gate40-escalation`** · grounded 11/11
> Purpose: Validates GATE-40 escalation instrumentation by verifying ledger schema, dual-window budget caps, request payloads, secret redaction, and crash/falsification guards before authorizing cloud API calls.
> Key Functions: main, round_a, round_b, round_c, round_d, round_e, round_f, round_g, round_h, round_i, fresh_db, ok, eq, _seed_spend
> Dependencies: wrought_escalation, client, config, escalate, ledger, wrought_orchestrator, redact, store, sqlite3, subprocess, signal, argparse, tempfile
> Risks: Uses sudo and systemd-run to inject credentials during --live execution; queries the production ledger in round_i; round_g sends SIGKILL to child processes, risking orphaned temp databases or unreconciled ledger state on interruption.

**`bin/gate41-fixtures`** · grounded 18/18
> Purpose: Validates ten committed fixture tasks against GATE-41/D11 specifications, enforcing provenance checks, schema lints, test node resolution, EARS phrasing compliance, SHA256 stability, and spec-oracle module alignment.
> Key Functions/Classes: `main`, `test_nodes`, `fixture_dirs`, `sh`, `ok`, `say`.
> Direct Imports/Dependencies: `ast`, `pathlib`, `re`, `subprocess`, `sys`, `wrought_orchestrator.validate` (`validate`, `ears_pattern`, `canon_v2`, `split_task_md`, `req_lines`), `io`, `ruamel.yaml`.
> Obvious Risk: Runtime `sys.path` manipulation, hardcoded `SESSION_IDENTITY` and `STAGING` paths, and reliance on unversioned `ruamel.yaml` and external `git` subprocess calls create environment fragility and potential portability issues.

**`bin/gate42-fallback-baseline`** · grounded 11/11
> Purpose: Swaps the active inference profile to `devstral.args`, runs a fallback baseline for Devstral Small 2 across ten fixtures, and automatically restores the primary `qwen36.args` profile.
> Key functions/classes: `say`, `active_name`, `restore`.
> Dependencies: Invokes `./bin/baseline-run` and `/opt/wrought/bin/wait-healthy`; relies on `sudo`, `systemctl`, `curl`, and variables `GATE42_RUN`, `GATE42_OUT`, `GATE42_MAXTOK`.
> Risks: Requires `sudo -n` for profile symlinks and service restarts; hardcodes entry-state validation against `qwen36.args`; uses unauthenticated local `curl` to port 8080; potential race condition if external processes modify the active profile symlink during execution.

**`bin/gate43-feedback-ab`** · grounded 15/17
> Purpose: Runs a sequential three-arm (a, b, c) experiment comparing repair-feedback formats (`bare`, `verifier`, `trace`) on a pinned 27B model, measuring pre-escalation demand with escalation disabled.
> Key functions: `status`, `arm_complete`, `say`; core execution driver `./bin/baseline-run`.
> Direct dependencies: `/opt/wrought/venv-orch/bin/python`, `curl`, `sha256sum`, inline Python heredocs, and variables `$PACK`, `$ACTIVE`, `$BASELINE_DIR`.
> Obvious risks: Sequential single-GPU execution confounds arm order with time; resumption skips only if `records-$run.json` fully parses, risking silent truncation bugs; strict assertions (`WANT_PACK`, `WANT_PROFILE`, `WANT_MODEL`) forcibly abort on minor infrastructure drift.

**`bin/gate43-report`** · grounded 5/5
> Purpose: Produces a GATE-43 comparative report analyzing repair-feedback A/B arms by calculating escalation demand, repair-round knees, REQ-ID citation convergence, and per-fixture movements.
> Key functions: _load_baseline_report, load, knee, req_id_convergence, delivered, main.
> Direct imports: argparse, importlib.machinery, importlib.util, json, pathlib, sys, and dynamically loads bin/baseline-report.
> Risk: Dynamically imports baseline-report via raw path instead of standard packaging, risking silent definition drift and tight coupling; also assumes a hardcoded /var/lib/wrought/baseline directory and strict JSON record schemas.

**`bin/gate44-heldout`** · grounded 13/15
> Purpose: Evaluates a 27B-parameter LLM for reward-hacking by comparing visible versus held-out test pass rates under adversarial trace feedback, while tracking real-money spend against production ledger caps.
> Key functions/classes: Bash functions status, run_complete, spend, say; Python imports json, pathlib, sys, time, sqlite3; ledger utilities wrought_escalation.config, wrought_escalation.ledger, ledger.production_db_path, ledger.spend_microusd.
> Direct imports/dependencies: /opt/wrought/venv-orch/bin/python, sibling scripts bin/gate44-split, bin/test-gate44-heldout, bin/baseline-run, bin/gate44-report, and environment variables GATE44_OUT, GATE44_RUN, WROUGHT_BASELINE_DIR.
> Obvious risk: Hardcoded absolute paths and strict comparand assertions (WANT_PACK, WANT_MODEL) may break in non-standard environments; financial exposure exists since escalation is live and spend tracking relies on ledger.spend_microusd, with inline comments documenting a prior under-reporting defect.

**`bin/gate44-report`** · grounded 19/19
> Purpose: Generates a statistical dashboard comparing visible vs held-out test pass rates to detect model reward-hacking, including historical controls and escalation spend tracking.
> Key functions: `_load_baseline_report_helpers`, `sign_test_p`, `final_attempt`, `envelope_for`, `counts`, `g43c_control`, `main`.
> Direct imports: `argparse`, `glob`, `json`, `math`, `os`, `pathlib`, `sqlite3`, `sys`, `wrought_supervisor.heldout`, `wrought_escalation.config`, `wrought_escalation.ledger`.
> Risk: Dynamically executes code via `exec(compile(...))` to load `wilson`, `overlap`, and `ci_s` from `bin/baseline-report`, bypassing standard module resolution and introducing security/maintainability vulnerabilities.

**`bin/gate44-split`** · grounded 14/14
> Purpose: Mechanically resolves a held-out/visible test split for evaluation fixtures using `k = max(1, ceil(n_fail_to_pass / 3))` to prevent model influence, outputting JSON or a `pins.lock` YAML block.
> Key functions: `_entries`, `resolve`, `load_pinned`, `main`
> Direct imports/dependencies: `argparse`, `hashlib`, `json`, `math`, `pathlib`, `re`, `sys`, `wrought_orchestrator.validate.validate`, `wrought_supervisor.heldout.load_pinned_split`
> Obvious risk: Hard `sys.exit` on substring name collisions or empty visible sets will halt runs; silent exclusion of `undeclared_collected` tests and strict `pins.lock` versioning make the pipeline brittle to fixture changes.

**`bin/gen-canon-vectors`** · grounded 11/11
> Purpose: Generates committed SHA256 conformance vectors and digests for `canon_v2` to prevent silent specification drift and validate normalization rules.
> Key functions/classes: `digest`, `main`.
> Direct imports/dependencies: `hashlib`, `io`, `json`, `pathlib`, `sys`, `ruamel.yaml.YAML`, `wrought_orchestrator.validate.canon_v2`, `wrought_orchestrator.validate.split_task_md`.
> Obvious risk: Direct `sys.path.insert` manipulation can cause import collisions; strict `SystemExit` on digest mismatches will abruptly halt execution if `canon_v2` behavior changes unintentionally.

**`bin/gen-pack`** · grounded 14/14
> Purpose: Derives version-pinned TOML verification and security packs from `pins.lock` to enforce a single source of truth, with a `--check` flag to detect hand-edited artifacts.
> Key Functions: `main`, `generate`, `_calibration`, `_checks`, `toml_scalar`, `toml_key`
> Dependencies: `argparse`, `hashlib`, `io`, `json`, `pathlib`, `sys`, `ruamel.yaml.YAML`
> Risk: Hardcoded absolute paths (`VENV`, `/work/src`, `/work/out`), custom manual TOML serialization bypassing standard libraries, and fatal `SystemExit` on missing `pins.lock` keys that halt generation without graceful fallback.

**`bin/gen-profile`** · grounded 12/12
> Purpose: Sole generator and drift checker for `/etc/wrought/profiles/*.args` files, strictly deriving every CLI flag value from `pins.lock` without defaults, self-referential copying, or hand-editing.
> Key functions/classes: `dig`, `render`, `generate`, `main`, `PROFILES`.
> Direct imports/dependencies: `argparse`, `hashlib`, `io`, `pathlib`, `sys`, `ruamel.yaml`.
> Obvious risk: Unconditionally aborts on any missing or `DEFERRED` pin instead of providing fallbacks, enforces hardcoded `/etc/wrought/profiles/` paths, and catches `SystemExit` in `main` which may obscure underlying YAML parsing or key-lookup failures.

**`bin/installed-drift-check`** · grounded 2/2
> Purpose: Verifies installed binaries against repo source files and pins.lock hashes to detect deployment drift, missing pins, or unaccounted executables, enforcing a fail-fast policy for unknown files.
> Key functions: sha256_file, dig, main.
> Direct imports: argparse, hashlib, json, os, pathlib, sys, time, ruamel.yaml.
> Risk: Hardcoded fallback paths (/home/kalib/foundry) and strict environment dependencies may break in non-standard deployments; assumes pins.lock structure stability without schema validation.

**`bin/make-review-bundle-20`** · grounded 3/3
> Purpose: Assembles REVIEW-BUNDLE-20.zip containing session 20 cleanup evidence, git status/log, source files, a journal slice, and a SHA-256 manifest.
> Key functions or classes: Standalone bash script with no defined functions or classes; operates via variables ZIP, STAGE, BASE and trap.
> Direct imports/dependencies: CLI tools git, cp, sed, awk, find, xargs, sha256sum, zip, unzip, stat, mktemp and project files SESSION-REPORT-20.md, BUILD-JOURNAL.md, docs/08-decisions.md.
> Obvious risk: Hardcoded absolute paths /home/kalib/foundry, /etc/credstore.encrypted, /var/lib/wrought/state/orchestrator.db combined with set -euo pipefail will abort execution if any expected file or directory is missing.

**`bin/make-review-bundle-21`** · grounded 12/12
> Purpose: Assembles `REVIEW-BUNDLE-21.zip`, a review courier archive containing session reports, reorganized products, evidence, journal excerpts, and git metadata.
> Key components: Shell variables `ZIP`, `STAGE`, `BASE` coordinate staging and archiving via `cp`, `git log`, `git diff`, `sha256sum`, and `zip`.
> Dependencies: External utilities `git`, `zip`, `unzip`, `mktemp`, `sed`, `awk`; requires directory structure under `/home/kalib/foundry` and system paths like `/var/lib/wrought`.
> Risks: Hardcoded paths and `BASE=69dcd50` reduce portability; `set -euo pipefail` halts on any missing file; regenerated artifacts (`MANIFEST.sha256`, `COMMITS.txt`) are excluded from version control.

**`bin/make-session-19-bundle`** · grounded 10/10
> Purpose: Generates a reproducible, non-version-controlled ZIP bundle (`SESSION-19-DECISIONS-GATE44-writeup-2026-08-08.zip`) packaging session reports, journal slices, evidence, source code, git diffs, and spec documents for external distribution.
> Key functions or classes: None defined (shell script); orchestrates standard utilities (`mktemp`, `git`, `sed`, `awk`, `find`, `sha256sum`, `zip`, `unzip`, `stat`).
> Direct imports/dependencies: Relies on local project files (`SESSION-REPORT-18.md`, `BUILD-JOURNAL.md`, `build-evidence/session-19/`, `src/wrought_supervisor/*.py`, `bin/gate44-*`, `CLAUDE.md`, `docs/08-decisions.md`, `pins.lock`) and system tools (`bash`, `git`, `zip`).
> Obvious risk: Fragile due to hardcoded absolute paths (`/home/kalib/foundry`), a fixed commit base (`2f0e48e`), and a static line-number slice (`sed -n '7290,$p' BUILD-JOURNAL.md`), which will break if directory layouts or file lengths change.

**`bin/manufacture`** · grounded 4/4
> Purpose: Executes a single operator task through a real production path where the worker independently drives its own oracle for verification, avoiding injected verdicts from baseline harnesses.
> Key functions: main, run_task, load_task, refuse_production, fsm_view, _import_baseline_run.
> Dependencies: wrought_escalation, wrought_orchestrator, wrought_supervisor, importlib.util, and dynamically loaded bin/baseline-run.
> Risk: Mutating os.environ before module imports and dynamically executing bin/baseline-run bypass standard packaging, while aggressive sys.exit() guards and hardcoded path checks create brittle failure modes that could mask configuration drift or accidental production writes.

**`bin/manufacture-report`** · grounded 7/7
> Purpose: Generates a five-part audit report for a single `bin/manufacture` run by cross-referencing a JSON records file, an event log, and the production ledger to verify attempts, FSM/oracle alignment, staging receipts, provenance, and spend.
> Key functions/classes: `main`
> Direct imports/dependencies: `argparse`, `json`, `pathlib`, `sys`, `ledger`, `store`, `oracle`
> Obvious risks: Dynamic `sys.path.insert()` alters module resolution; raw SQL queries and direct `json.loads()` on event payloads lack strict validation or error handling; assumes `ledger.production_db_path()` and scoped DB files exist without fallback.

**`bin/measure-typecheck-modes`** · grounded 24/32
> Purpose: Evaluates which basedpyright typeCheckingMode suppresses bare `-> dict` return type warnings while retaining detection for planted type errors and undefined names, producing an admissibility matrix.
> Key functions: `run_one` executes isolated test cells with separate config directories, while `main` orchestrates the `MODES` × `CASES` matrix, computes verdicts, and writes results to `build-evidence/session-13/01-recalibration/S13-typecheck-mode-matrix.json`.
> Direct imports: `json`, `pathlib`, `shutil`, `subprocess`, `sys`, `tempfile`.
> Obvious risks: Hardcoded absolute path `/opt/wrought/venv/bin/basedpyright` and rigid 300s `subprocess.run` timeout may fail in non-standard environments; script writes to a deep `build-evidence/` directory without creating parents and discards `p.stderr`.

**`bin/measure-verify-walltime`** · grounded 12/17
> Purpose: Computes empirical verification wall-clock statistics from committed baseline records and sandbox envelopes to establish a strict time bound (STOP-32).
> Key functions: `load_records`, `load_envelopes`, `stats`, and `main` parse JSON evidence, calculate distribution metrics, and format or serialize output.
> Direct imports: `argparse`, `json`, `pathlib`, `re`, `statistics`, `sys`.
> Obvious risk: Hardcoded `JOB_ROOT` and silent skipping of missing/malformed JSON files may yield incomplete datasets that underestimate the maximum duration, while deliberate exclusion of pathological runs could mask edge-case timing failures.

**`bin/oracle-isolation-probe`** · grounded 3/3
> Purpose: Probes sandbox isolation to verify if a second UID is reachable inside the verification environment across shipped, nested, and rebuilt user-namespace layers.
> Key functions: _load_verify_job, layer12, layer3, main.
> Direct imports: argparse, ctypes, os, pathlib, subprocess, sys, time; dynamically executes bin/verify-job via exec.
> Risk: Directly execs external source and manipulates raw user namespaces/UID maps via os.fork(), os.setresuid(), and /proc/[pid]/uid_map under sudo, creating privilege escalation and code injection exposure.

**`bin/orchestrator`** · grounded 8/8
> Purpose: CLI for initializing databases, enqueuing tasks, running workers with strict visibility/timeout controls, recovering state, and managing projections/archival.
> Key functions/classes: main, store.init_db, store.connect, store.enqueue, worker.run, worker.recover, store.sweep_dead_letters, worker.archive_completed, store.rebuild_projection, oracle.oracle_verdict.
> Direct imports/dependencies: argparse, json, os, signal, pathlib, sys, wrought_orchestrator.store, wrought_orchestrator.worker, wrought_supervisor.oracle.
> Obvious risk: Deliberately omits defaults for --visibility-s and --max-receive to prevent unsafe queue redelivery; uses direct sys.path.insert manipulation and includes a WROUGHT_CHAOS_KILL environment hook that triggers os.kill unexpectedly if misconfigured.

**`bin/probe-reasoning-budget`** · grounded 2/2
> Purpose: Determines whether a pinned llama-server supports per-request reasoning token budgeting to prevent reasoning exhaustion that yields empty generations (J-116).
> Key functions: api_key, ask, main
> Direct imports/dependencies: json, pathlib, subprocess, sys, time, urllib.error, urllib.request
> Obvious risk: Executes sudo -n systemd-creds decrypt to fetch sealed inference keys, risking credential exposure or execution failure, and assumes a hardcoded local server at URL.

**`bin/probe-reasoning-control`** · grounded 2/2
> Purpose: Determines whether per-request enable_thinking kwargs override server-side --reasoning flags to validate a reasoning-OFF control arm.
> Key functions: api_key, ask, main
> Direct imports: json, subprocess, sys, time, urllib.request
> Obvious risks: Hardcoded URL; invokes sudo and systemd-creds for secret decryption; uses subprocess.run with shell commands; explicitly warns that failed overrides render the control arm unsafe.

**`bin/probe-satisfiability`** · grounded 10/10
> Purpose: Determines whether a fixture's test oracle is genuinely satisfiable or defective by running a reference implementation against committed tests via `bin/verify-job`.
> Key functions: `_run`, `install_oracle`, `stage`, `main`.
> Direct imports: `argparse`, `hashlib`, `json`, `pathlib`, `shutil`, `subprocess`, `sys`.
> Risk: Executes `sudo -n` to manage `/var/lib/wrought/` directories without authentication, creating privilege escalation and unauthorized filesystem modification vulnerabilities.

**`bin/probe-verify-timeout`** · grounded 13/13
> Purpose: Tests whether `RuntimeMaxSec` bounds a transient SCOPE and leaves a durable verdict after destruction, running plain, SIGTERM-ignoring, and fast-exit arms with/without `bwrap`.
> Key functions: `check`, `journal`, `launch`, `main`.
> Direct imports: `argparse`, `asyncio`, `json`, `subprocess`, `sys`, `time`.
> Obvious risk: Hard-requires `sudo` and external system binaries (`systemd-run`, `journalctl`, `bwrap`); relies on specific PID namespace collapse and systemd timeout semantics that may break across kernel versions or containerized environments.

**`bin/propose-con-manifest-diffs`** · grounded 9/9
> Purpose: Prints proposed manifest diffs to opt fixtures into CON- constraint validation without applying changes, categorizing them as mechanical or semantic.
> Key functions/classes: `nodes`, `main`
> Direct imports/dependencies: `ast`, `pathlib`, `sys`, `ruamel.yaml.YAML`, `wrought_orchestrator.validate.CON_RE`, `wrought_orchestrator.validate.split_task_md`, `wrought_orchestrator.validate.validate`
> Obvious risk: Mutates `sys.path` at runtime and relies on hardcoded glob patterns (`TASK-2026-0804-*`) and directory layouts, risking import shadowing or path resolution failures.

**`bin/redaction-corpus`** · grounded 5/5
> Purpose: Validates that every §14.4 redaction rule fires correctly while asserting negative properties to prevent over-redaction of ordinary text and allowlisted digests.
> Key functions: `ok`, `must_redact`, `main`
> Direct imports: `pathlib`, `sys`, `wrought_orchestrator.redact`
> Risk: Hardcoded shebang (`#!/opt/wrought/venv-orch/bin/python`) and runtime `sys.path.insert` injection harm portability, while fragile string-matching validation of `store.py` may break during refactoring.

**`bin/replay-blocked-attempts`** · grounded 3/3
> Purpose: Regresses session 12's blocked coding attempts against a recalibrated validation pack to verify warning-only failures now pass while real defects still fail.
> Key functions: setup_replay, replay_one, downgrade_to_spec_signature, main.
> Dependencies: argparse, asyncio, json, pathlib, shutil, subprocess, sys, and dynamically loaded bin/verify-job.
> Risks: Invokes subprocess.run with sudo rm -rf and shutil.rmtree on filesystem paths, executes untrusted candidate code via dynamic imports, and relies on hardcoded absolute paths.

**`bin/repro-cap-fallthrough`** · grounded 3/3
> Purpose: Deterministic reproducer and regression test for bug J-91, where exceeding REPAIR_CAP causes a code_defect verdict to fall through to a terminal else clause, incorrectly marking a task COMPLETED.
> Key functions/classes: main, worker.process_one, store.init_db, store.append_and_project, store.enqueue.
> Direct imports/dependencies: json, os, pathlib, sys, tempfile, wrought_orchestrator.store, wrought_orchestrator.worker.
> Obvious risk: Mutates sys.path at runtime and uses tempfile.mkdtemp for a scratch database without explicit cleanup or exception handling, risking orphaned temporary files.

**`bin/resolve-ruff-ruleset`** · grounded 13/13
> Purpose: Reproducibly resolves and emits the active `ruff` rule set, enforcing a narrowed F + S selection per project policy S13/RULING 1.
> Key functions/classes: None; standalone bash script orchestrating variables `RUFF`, `ARGS`, `RULES`, `COUNT`, and `PREFIXES`.
> Direct imports/dependencies: External commands `ruff`, `mktemp`, `sed`, `grep`, `sort`, `tr`, `awk`, `date`, and `hostname`.
> Risk: Fragile regex parsing of `ruff --show-settings` output may break across tool versions; hardcodes `/opt/wrought/venv/bin/ruff` assuming a specific environment layout.

**`bin/secpack-fetch`** · grounded 3/3
> Purpose: Fetches and pins stable security tools, computing separate archive and binary SHA256 hashes while explicitly separating integrity checks from authenticity verification.
> Key functions: fetch_go_tool, say, sha
> Dependencies: curl, sha256sum, tar, awk, /opt/wrought/venv-orch/bin/python, gh
> Risk: Relies on integrity-only upstream checksums without cryptographic signature verification, and performs blind tar extraction into bin/ without path validation, creating documented authenticity gaps and potential zip-slip exposure.

**`bin/secpack-freeze`** · grounded 3/4
> Purpose: Freezes Bandit Python wheels and Go binaries (gitleaks, syft) into an offline verification environment while explicitly excluding pip-audit, then appends hashed requirements and updates pins.lock.
> Key functions/classes: bash function say, inline python3 script importing pathlib, re, sys.
> Direct imports/dependencies: sudo, install, tee, cp, grep, awk, sha256sum, pip, bandit, gitleaks, syft, pins.lock, requirements-frozen.txt.
> Obvious risk: Executes privileged sudo -n operations across system paths; relies on exact comment string matching in pins.lock where minor drift triggers hard aborts, and silent no-ops from string mismatches are explicitly flagged as a critical failure mode.

**`bin/secpack-osv-fetch`** · grounded 17/17
> Purpose: Fetches and pins the `osv-scanner` raw ELF binary and offline vulnerability databases for `§10.6 vuln-scan slot`, recording integrity hashes and partial SLSA attestation claims.
> Key functions: `get`, `sha256_file`, `_snapshot_span`, `pae`, `verify_attestation`, `main`.
> Direct imports: `argparse`, `base64`, `email.utils`, `hashlib`, `json`, `os`, `pathlib`, `subprocess`, `sys`, `urllib.parse`, `urllib.request`.
> Risk: Explicitly skips Rekor/Fulcio chain verification (`no cosign/slsa-verifier`), relies on unpinned external CLIs (`openssl`, `date`), and fetches `releases/latest` from GitHub without static version pinning.

**`bin/secret-leak-scan`** · grounded 2/2
> Purpose: Reads a plaintext secret from STDIN and scans specified filesystem directories, git object history, and systemd journal for leaks, outputting only hit counts and file paths.
> Key functions: _skipped, scan_tree, main
> Direct imports: pathlib, subprocess, sys
> Obvious risk: Loads entire file contents and git object blobs into memory via p.read_bytes() and capture_output=True, risking MemoryError and severe performance degradation; relies on hardcoded absolute paths like REPO = "/home/kalib/foundry" and /var/lib/wrought.

**`bin/serve-model`** · grounded 12/15
> Purpose: Bash launch wrapper that dynamically resolves GPU device tokens, validates inference profiles, and runs hardware/self-tests before starting the model server.
> Key functions: die() exits on fatal errors; main logic parses $PROFILE_PATH into $ARGS, validates via $LLAMA_SERVER --list-devices, and asserts VRAM/runtime PM via sysfs.
> Dependencies: Sources $CONF (/etc/wrought/serving.env); invokes $LLAMA_SERVER (/opt/wrought/bin/llama-server), $ASSERT_POWER (/opt/wrought/bin/assert-power-profile), and reads $CREDENTIALS_DIRECTORY/inference-api-key and /sys/module/amdgpu/parameters/runpm.
> Risks: Fragile grep/sed parsing of --list-devices output for device tokens and VRAM; strict hardcoded profile whitelist (qwen36.args|qwen36-mtp.args|devstral.args) rejects unlisted models; any self-test failure exits non-zero, completely blocking service startup.

**`bin/set-power-profile`** · grounded 5/5
> Purpose: Forces CPU scaling governors and PCIe ASPM to `performance` mode by writing directly to sysfs nodes for all online cores.
> Key functions/classes: None (inline bash logic relying on constants `GOVERNOR`, `ASPM_POLICY`, `ASPM_NODE`, and array `governors`).
> Direct imports/dependencies: `bash`, sysfs paths `/sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor` and `/sys/module/pcie_aspm/parameters/policy`, plus external verifier `assert-power-profile`.
> Obvious risk: Assumes root privileges for sysfs writes without explicit checks; strict `set -euo pipefail` will abort execution if cpufreq drivers or ASPM nodes are absent, potentially halting dependent service initialization.

**`bin/soak-harness`** · grounded 16/16
> Purpose: Detached soak testing harness that measures bulk event ingestion throughput and validates chaos recovery invariants (zero loss/duplication, fenced-ack) while strictly isolating state from production.
> Key functions: `bulk_round`, `chaos_round`, `audit`, `fenced_ack_holds`, `checkpoint`, `halt`, and `main`.
> Direct imports: `json`, `os`, `pathlib`, `signal`, `subprocess`, `sys`, `time`, and `wrought_orchestrator.store`.
> Risk: Executes `sudo` to drop OS caches via `drop_caches`, recursively applies `chmod 0o444` on failure, and forcefully `SIGKILL`s worker subprocesses, risking resource locks or masked stability defects.

**`bin/soak3-analyze`** · grounded 12/12
> Purpose: Generates the official SOAK-3 analysis report by comparing measured checkpoint metrics (slope, headroom, recovery cost, WAL, parity) against live pinned values from `pins.lock`.
> Key functions: `pins`, `lstsq`, `r_squared`, `jl`, `track_a`, `track_b`, `main`.
> Direct imports: `json`, `pathlib`, `sys`, `ruamel.yaml.YAML`, `collections.Counter`.
> Obvious risk: Hardcoded absolute data path `/var/lib/wrought/soak3` and strict reliance on external `pins.lock`/JSONL schemas; potential division by zero in `lstsq` if variance `sxx` equals zero.

**`bin/soak3-build-pool`** · grounded 12/12
> Purpose: Builds a fixed, cycled corpus pool for SOAK-3 Track B endurance testing by staging candidates from committed `-g42c`/`-g44` tasks and attaching reference classifications from `records-g42c.json`.
> Key Functions/Classes: `link_task`, `corpus_classifications`, `main`
> Direct Imports/Dependencies: `json`, `pathlib`, `shutil`, `subprocess`, `sys`, `wrought_supervisor.oracle`
> Obvious Risk: Unconditionally executes `shutil.rmtree` on existing oracle directories and symlinks into production roots (`REAL_JOBS`, `REAL_ORACLE`) with a hard `SystemExit` guard, risking data loss or unexpected halts if paths conflict.

**`bin/soak3-status`** · grounded 10/10
> Purpose: Outputs a single decision-critical status snapshot for SOAK-3, reporting process liveness, halt flags, and progress metrics for tracks a and b.
> Key functions or classes: No named functions or classes defined; inline Python block uses `json`, `sys`, and `SystemExit` to parse `status.json`.
> Direct imports/dependencies: `json`, `sys`; external utilities `pgrep`, `head`, `tail`, `sed`, `wc`, `sha256sum`; interpreter `/opt/wrought/venv-orch/bin/python`.
> Risks: `set -uo pipefail` lacks `-e`, permitting silent continuation after failures; `open(sys.argv[1])` omits context managers and may race with concurrent writers; `raise SystemExit(0)` inside `except` masks underlying parsing errors.

**`bin/soak3-track-a`** · grounded 11/11
> Purpose: Executes SOAK-3 Track A chaos endurance tests, validating bulk event ingestion, worker SIGKILL resilience, FSM/oracle consistency, and recovery performance while strictly isolating soak state from production.
> Key Functions: bulk_round, chaos_round, audit, verdict_source_audit, fsm_oracle_both_directions, recover_reconciles, recover_cost, checkpoint, halt, oom_kills, substrate_sample, main.
> Direct Imports: json, os, pathlib, signal, subprocess, sys, time, wrought_orchestrator.store, wrought_orchestrator.worker.
> Risks: Invokes sudo to drop OS page caches via /proc/sys/vm/drop_caches, risking host I/O disruption; hardcodes WROUGHT_DB and WROUGHT_EFFECTS_DIR environment variables and directly reads /sys hardware metrics that may fail or lack permissions in restricted environments.

**`bin/soak3-track-b`** · grounded 18/18
> Purpose: Endurance soak harness that repeatedly invokes `bin/verify-job` over a committed corpus to assert classification reproducibility, seccomp pin stability, wall-clock bounds, and zero process leaks.
> Key functions/classes: `main`, `verify_once`, `assert_run`, `restage`, `checkpoint`, `halt`, `PidSampler`, `tasks_current`, `leaked_scopes`, `stray_bwrap`, `substrate_sample`.
> Direct imports/dependencies: `json`, `os`, `pathlib`, `subprocess`, `sys`, `threading`, `time`, `wrought_supervisor.oracle`, `ruamel.yaml`.
> Obvious risk: Unattended infinite loop that executes `sudo rm -rf` during staging, immediately halts on any invariant or disk-cap violation, and relies on external cgroup/systemd interfaces that may be absent or race-prone.

**`bin/test-f2-repairing-rest`** · grounded 6/6
> Purpose: Validates that tasks resting in REPAIRING are not silently acked by worker.process_one and that delivery budgets accumulate across worker.recover calls until store.sweep_dead_letters transitions the task to HUMAN_REVIEW.
> Key functions/classes: worker.process_one, worker.recover, store.init_db, store.append_and_project, store.enqueue, store.sweep_dead_letters
> Direct imports: pathlib, sys, tempfile, store, worker
> Obvious risk: Runtime sys.path.insert mutation and lack of explicit cleanup for the tempfile.mkdtemp directory may cause import resolution issues or leave orphaned files on test failure.

**`bin/test-f3-runner-scan`** · grounded 14/14
> Purpose: Validates that `wrought-runner` halts publishing on non-zero `SECRET_SCAN` exit codes and confirms `wrought-precommit-secret-scan` detects fake tokens in a `bundles/` tree.
> Key functions/classes: `_Log`, `runner.secret_scan_or_halt`, `runner.Halt`, `subprocess.run`
> Direct imports/dependencies: `importlib.machinery`, `importlib.util`, `pathlib`, `shutil`, `subprocess`, `sys`, `tempfile`; dynamically loads `wrought-runner` and invokes `wrought-precommit-secret-scan`.
> Obvious risk: Dynamic module loading via `importlib.util.spec_from_loader` catches only `SystemExit`, potentially masking import failures or executing compromised code; `subprocess.run` executes external binaries without sandboxing.

**`bin/test-f4-allowed-tools`** · grounded 6/6
> Purpose: Validates that validate_allowed_tools correctly parses tool allowlists, halting on unsafe bare Bash entries while permitting properly scoped tools.
> Key functions/classes: validate_allowed_tools, Halt, spec_from_loader, SourceFileLoader, module_from_spec, exec_module, fullmatch.
> Direct imports: importlib.machinery, importlib.util, pathlib, re, sys.
> Risk: Dynamically executes wrought-runner via spec.loader.exec_module, posing a code execution risk if the target path is altered or points to untrusted code.

**`bin/test-f8-signal-teardown`** · grounded 5/5
> Purpose: Validates that signal handlers correctly terminate child process groups, escalate ignored SIGTERM to SIGKILL, and preserve finally block execution during KeyboardInterrupt.
> Key functions/classes: _Log, alive, reset_registry, runner.kill_live_children, runner._register_child, runner.install_signal_handlers.
> Direct imports/dependencies: importlib.machinery, importlib.util, os, pathlib, signal, subprocess, sys, time, and dynamically loaded runner from wrought-runner.
> Obvious risk: Unsafe dynamic execution of wrought-runner via spec.loader.exec_module(runner); relies on /proc filesystem parsing and external pgrep which may fail in non-Linux environments or under load.

**`bin/test-fc02-broken-oracle`** · grounded 7/7
> Purpose: Validates FSM routing fixes (§8.1a) and oracle.verdict_for() mappings for BROKEN_ORACLE, substrate_incident, same_failure, and pack_invalid across five test arms.
> Key functions: main(), install_broken_oracle(), fresh_store(), ok(), worker.run(), store.append_and_project(), next_state(), guard_ok(), oracle.verdict_for().
> Dependencies: wrought_orchestrator.store, wrought_orchestrator.worker, wrought_orchestrator.fsm, wrought_supervisor.oracle, subprocess, tempfile.
> Risk: sh() executes sudo -n with unsanitized argument interpolation, creating a command injection and privilege escalation vulnerability, alongside hardcoded system paths.

**`bin/test-gate44-heldout`** · grounded 13/13
> Purpose: Validates the GATE-44 held-out filter across eight test arms using real envelope data to ensure hidden test names are stripped from model inputs while visible failures survive.
> Key functions: `main`, `ok`, `_feedback_from`, `g43c_envelopes`, and `heldout.filter_result`, `heldout.filter_envelope`, `heldout.guard`, `heldout.grade`, `heldout.node_function`.
> Dependencies: `copy`, `glob`, `json`, `pathlib`, `subprocess`, `sys`, and `from wrought_supervisor import heldout`; relies on `bin/baseline-run`, `bin/gate44-split`, and git.
> Risk: `_feedback_from` uses `exec(compile(...))` to dynamically evaluate scraped source code from an external script, introducing execution safety and fragility hazards.

**`bin/test-l1-path-derivation`** · grounded 7/7
> Purpose: Validates that `oracle.job_dir` and `oracle.stage_candidate` safely reject traversal payloads and invalid identifiers to prevent command injection before paths reach `sudo -n rm -rf`.
> Key functions/classes: `oracle.job_dir`, `oracle.stage_candidate`, `pathlib.Path`, `ValueError`.
> Direct imports/dependencies: `pathlib`, `sys`, `wrought_supervisor`.
> Obvious risk: `oracle.stage_candidate` feeds derived paths directly into `subprocess.run(["sudo","-n","rm","-rf", str(src)])`, creating a critical arbitrary deletion vulnerability if path derivation validation is bypassed.

**`bin/test-r1-stale-candidate`** · grounded 14/14
> Purpose: Validates that the `wrought_supervisor` oracle verifier correctly rejects stale, tampered, or unreceipted candidates using a staging receipt mechanism across multiple test arms.
> Key functions: `ok`, `sh`, `install_oracle`, `candidate_bytes`, `leave_behind`, `fresh_store`, `drive`, `main`.
> Direct imports: `json`, `os`, `pathlib`, `shutil`, `subprocess`, `sys`, `tempfile`, `wrought_orchestrator`, `wrought_supervisor`.
> Obvious risk: Executes `sudo -n` via `sh()` and directly modifies `/var/lib/wrought/` filesystem paths and `sys.path`, risking permission failures, live job interference, or test breakage if external oracle/candidate fixtures are missing.

**`bin/test-r5-budget-toctou`** · grounded 9/9
> Purpose: Validates that budget reservation logic prevents TOCTOU race conditions where concurrent escalations commit off a stale snapshot and exceed D21 weekly/monthly caps.
> Key functions/classes: main, ok, Pins, fresh_ledger, seed_spend, week_spend, tripwire, ledger.reserve_standalone, ledger.reserve_in_txn, ledger.check_budget, escalate.escalate, client.call.
> Direct imports/dependencies: os, pathlib, sys, tempfile, wrought_escalation.client, wrought_escalation.escalate, wrought_escalation.ledger, wrought_orchestrator.store.
> Obvious risk: Relies on ledger.BudgetMoved re-reads and runtime monkeypatching of client.call; incomplete transactional atomicity could bypass the cap backstop and allow financial overspend.

**`bin/test-r6-journal-window`** · grounded 7/7
> Purpose: Validates RULING 3 to prevent journal window rounding and transient scope name reuse from leaking prior run verdicts into subsequent task classifications.
> Key functions/classes: `main`, `ok`, `sh`, `C._unit_result`, `oracle.stage_candidate`.
> Direct imports/dependencies: `wrought_supervisor.classify`, `wrought_supervisor.oracle`, `subprocess`, `bin/verify-job`, `systemctl`.
> Obvious risk: Invokes privileged `sudo -n` commands for systemd management; monkeypatches `C.subprocess.run`; hardcodes `/var/lib/wrought/` paths.

**`bin/test-s13-invariants`** · grounded 16/16
> Purpose: Executes deterministic regression tests verifying session 13 invariants for `json_metric` parsing, production ledger spend authority, manifest SHA-256 integrity, and failure signature persistence.
> Key Functions/Classes: `ok`, `test_r1_json_metric`, `test_r4_ledger_authority`, `test_r5_manifest`, `test_r6_signature_persistence`, `_FakePins`, `main`.
> Dependencies: `sys`, `wrought_verifier.__main__`, `wrought_verifier.pack`, `wrought_escalation`, `wrought_orchestrator`, `bin/verify-job`, `json`, `tempfile`, `hashlib`, `subprocess`.
> Risk: `sys.path.insert(0, "src")` mutates runtime import resolution, risking module shadowing, and dynamically executes `bin/verify-job` via `importlib` without sandboxing.

**`bin/test-s14-invariants`** · grounded 4/4
> Purpose: Deterministic offline regression suite validating session 14's architectural rulings on ledger authority routing, statistical interval reporting, and spec validation lints.
> Key functions/classes: ok, _Pins, test_ruling_a, test_stop27_intervals, test_ruling_b, main
> Direct imports/dependencies: sys, tempfile, pathlib, wrought_escalation, wrought_orchestrator
> Obvious risk: Dynamic execution via exec(compile(...)) on bin/baseline-report bypasses static analysis and introduces maintenance/security concerns, alongside direct sys.path manipulation.

**`bin/test-s15-invariants`** · grounded 16/16
> Purpose: Deterministic regression tests for session 15 ledger rulings (RULING 3/STOP-29a and RULING 4/STOP-29b), verifying reconciliation decisions for known-zero costs versus worst-case bounds without network, GPU, or model dependencies.
> Key functions/classes: `ok`, `_Pins`, `_fresh`, `_drive`, `test_ruling_3`, `test_ruling_4`, `main`.
> Direct imports/dependencies: `sys`, `tempfile`, `wrought_escalation.ledger`, `wrought_escalation.escalate`, `wrought_escalation.client`, `wrought_orchestrator.store`, and implicit `sqlite3`.
> Obvious risk: Tightly coupled to internal implementation via monkeypatching `escalate.client.call`, direct database writes through `ledger._insert`, and hardcoded schema assumptions (`_INSERT_COLS`, `cost_microusd`), causing fragility if production modules or DB structures change.

**`bin/test-stop33b-equivalence`** · grounded 4/4
> Purpose: Validates equivalence between worker-driven oracle outcomes and legacy harness-injected verdicts, asserting identical FSM states, classifications, and provenance while enforcing fail-closed safety for missing verifiers.
> Key functions: main, ok, install_oracle, stage, fresh_store, stream
> Dependencies: store, worker, oracle, json, os, pathlib, shutil, subprocess, sys, tempfile
> Risk: Executes subprocess.run with sudo for directory staging and cleanup, and hardcodes absolute paths (/var/lib/wrought/oracle, /var/lib/wrought/jobs), creating privilege escalation and environment isolation hazards.

**`bin/test-stop40-pack-invalid`** · grounded 20/20
> Purpose: Regression test for operator decision D-F verifying that `PACK_INVALID` classifications route to `HUMAN_REVIEW` via the FSM instead of requeuing as `substrate_incident`.
> Key functions/classes: `main`, `drive`, `ok`, `fresh_store`, `evs`, `classify`, `oracle.verdict_for`, `next_state`, `worker.run`.
> Dependencies: `wrought_orchestrator`, `wrought_orchestrator.fsm`, `wrought_supervisor`, `wrought_supervisor.classify`, `wrought_verifier.__main__`, `json`, `pathlib`, `tempfile`, `sys`, `os`.
> Risks: Runtime `sys.path.insert` mutation risks import shadowing; `drive` swallows tracebacks via `except Exception`; execution tightly couples to the live `/etc/wrought/packs/py.toml` deployment path.

**`bin/trackb-report`** · grounded 10/12
> Purpose: Generates §13.8 dashboard tables from Track-B records, comparing FSM terminal states against Oracle final verdicts and calculating run-to-run error bars.
> Key functions: `load`, `pct`, `oracle_passed`, `disagrees`, `arm_table`, `main`.
> Dependencies: Directly imports `json`, `pathlib`, `sys`, and `__future__.annotations`.
> Risk: Relies on a hardcoded `TRACKB` path and assumes strict record dictionaries without validation, risking unhandled `KeyError` or `TypeError` on malformed data; the script also exits with code 1 on any FSM-Oracle divergence, potentially blocking automated workflows.

**`bin/trackb-round2`** · grounded 2/2
> Purpose: Executes three sequential 10-task reasoning batches for Track B round 2 to generate rate estimates with error bars and bounded wall-clock timing.
> Key functions or classes: None defined; invokes `./bin/trackb-run` and shell built-ins `date` and `echo`.
> Direct imports/dependencies: Bash runtime (`set -uo pipefail`), GNU `date` formatting, hardcoded path `/home/kalib/foundry`.
> Obvious risk: `set -uo pipefail` will abruptly terminate on unset variables or pipeline failures without cleanup, and the fixed directory assumption breaks environment portability.

**`bin/trackb-run`** · grounded 12/12
> Purpose: Executes synthetic coding tasks through a local LLM generation, real sandbox verification, and a capped repair loop to measure escalation rates and substrate incidents.
> Key functions: `main`, `run_task`, `generate`, `verify`, `read_api_key`, `substrate_sample`, `install_oracle`.
> Dependencies: `urllib.request`, `subprocess`, `wrought_orchestrator.store`, `wrought_supervisor.classify`, and invoked scripts `bin/verify-job` and `bin/orchestrator`.
> Risk: Heavy `sudo` and `subprocess` usage with privileged system binaries introduces privilege escalation and injection vulnerabilities; hardcoded absolute paths and direct `os.environ` overrides require strict environment isolation.

**`bin/verify-d24-backstop`** · grounded 3/3
> Purpose: Read-only verification script that validates security acceptance D24 by comparing local ledger spend against OpenRouter API provider usage and enforcing a $50 exposure ceiling.
> Key functions/classes: read_key, get, ledger_spend, main
> Direct imports/dependencies: json, subprocess, sys, urllib.error, urllib.request, sqlite3
> Obvious risk: The auto-top-up control is explicitly marked [UNVERIFIED] by the API and relies on operator assertion; credential extraction depends on sudo -n systemd-creds decrypt, and any provider-ledger usage mismatch immediately voids the security premise.

**`bin/verify-job`** · grounded 8/8
> Purpose: Production launcher that orchestrates sandboxed verification jobs by enforcing resource limits via systemd-run, prlimit, and bwrap while validating pinned artifacts.
> Key functions: main, run, build_argv, assert_pinned_identities, assert_test_manifest, wall_clock_bounds, verifier_module_digest, job_paths, _sha256_file, pins.
> Direct imports: argparse, asyncio, hashlib, json, os, pathlib, re, subprocess, sys, time, ruamel.yaml, wrought_supervisor.classify, wrought_supervisor.oracle.
> Risks: Hard dependency on pins.lock for execution bounds and artifact pinning (triggers SystemExit on drift), direct sys.path mutation, and sudo privilege escalation for systemd scope management.

**`bin/wrought-alert-receiver`** · grounded 3/3
> Purpose: Local-only webhook receiver for Alertmanager that routes notifications to systemd journal and a persistent plain-text log.
> Key functions/classes: main, journal_send, handle_payload, Handler, Server.
> Direct imports/dependencies: http.server, socket, socketserver, json, pathlib, sys, time, and the JOURNAL_SOCKET constant.
> Risks: The Handler class exposes an unauthenticated HTTP endpoint; journal_send silently swallows OSError exceptions, potentially dropping journal records; the LOG file lacks built-in rotation or explicit permission enforcement.

**`bin/wrought-course-post`** · grounded 9/9
> Purpose: Sends a build summary to a pinned LLM provider for skeptical review, outputting exactly `OK` or `HALT` alongside `COST_USD`.
> Key functions: `pin`, `main`.
> Direct imports: `json`, `re`, `sys`, `urllib.error`, `urllib.request`, `Path`; reads configuration exclusively from `pins.lock`.
> Risk: Broad exception handling and strict `pins.lock` parsing default to `HALT` on any config drift, network timeout, or unexpected JSON structure.

**`bin/wrought-node-metrics`** · grounded 5/5
> Purpose: Standalone Prometheus metrics exporter that scrapes AMDGPU hwmon, /proc, filesystem stats, and a configurable textfile directory, serving merged results over loopback HTTP.
> Key functions/classes: _read, _hwmon_dirs, collect, Handler, Server, main.
> Direct imports: http.server, os, pathlib, socketserver, sys.
> Risk: Silently substitutes None or 0.0 for unreadable or missing sysfs/procfs nodes, potentially masking permission errors or hardware failures while adhering to a strict no-invented-thresholds policy.

**`bin/wrought-precommit-secret-scan`** · grounded 10/10
> Purpose: Pre-commit scanner that checks staged git diffs or specified trees for leaked credentials while strictly preventing secret exposure via command-line arguments.
> Key functions: `load_secrets_from_credstore`, `load_secrets_from_path`, `staged_diff`, `scan_tree`, `main`.
> Direct imports/dependencies: `argparse`, `os`, `subprocess`, `sys`, `Path`, plus external CLI tools `systemd-creds` and `git`.
> Obvious risk: Requires `sudo` to decrypt `/etc/credstore.encrypted`; permission or decryption failures return exit code `2` rather than halting, potentially masking a failed scan as a non-event while the script continues with zero secrets.

**`bin/wrought-runner`** · grounded 27/27
> Purpose: Operator-started daily batch runner that walks a courier QUEUE to execute approved gate prompts in isolated `claude -p` sessions under systemd scopes, with mechanical verification and circuit breakers.
> Key functions/classes: `Halt`, `load_config`, `RunLog`, `parse_queue`, `set_queue_status`, `make_ephemeral_home`, `reap`, `build_child_env`, `validate_allowed_tools`, `secret_scan_or_halt`, `install_signal_handlers`.
> Direct imports/dependencies: stdlib-only modules (`argparse`, `fcntl`, `hashlib`, `json`, `os`, `re`, `shutil`, `signal`, `subprocess`, `sys`, `threading`, `time`, `datetime`, `pathlib`).
> Obvious risk: Requires `sudo` for `secret_scan_or_halt` and invokes `virsh`/`ss`/`systemctl` via `subprocess`; orphaned VMs or sockets may survive if `reap` or `kill_live_children` fails, and progress is explicitly gated by manual operator starts rather than automation.

**`bin/wrought-runner-hook`** · grounded 10/10
> Purpose: Defense-in-depth `PreToolUse` hook that audits tool invocations and blocks catastrophic actions via a regex deny-list, deferring all other decisions to the primary permission system.
> Key functions: `log_path`, `decide`, `main`.
> Direct imports: `json`, `os`, `re`, `sys`, `datetime`, `timezone`, `Path`.
> Risks: Audit logging silently disables if `CONFIG` parsing fails; broad regex patterns in `DENY` may produce false positives; explicitly documented as non-load-bearing and vulnerable to silent failure under `claude -p`.

**`bin/wrought-secret-watch`** · grounded 2/2
> Purpose: Continuously detects unauthorized secret exposures by decrypting credentials and scanning target trees, emitting Prometheus metrics to alert on unaccepted leaks.
> Key functions: load_accepted, scan_one, main
> Direct imports/dependencies: os, pathlib, re, subprocess, sys, time; shells out to systemd-creds, secret-leak-scan, and installed-drift-check.
> Obvious risk: Silent failures or missing external tools could mask exposures, though the script explicitly aborts clean metric generation on validation errors; relies on strict filesystem permissions for /etc/credstore.encrypted and world-readable metric outputs.

### `src/`

**`src/wrought_escalation/client.py`** · grounded 12/12
> Purpose: Stdlib-only HTTP client enforcing strict backend routing, explicit cache-off policy, and separated connect/stall/TTFT/total-generation timeouts for escalation API calls.
> Key functions/classes: `EscalationTimeout`, `ProviderError`, `_connection_factory`, `build_request_body`, `_extract_usage`, and `call`.
> Direct dependencies: `http.client`, `json`, `time`, `urllib.error`, and `urllib.request`.
> Risk: Mid-stream `TimeoutError` creates unknown billing liabilities (STOP-29a), and the transport assumes external ledger reservation, risking budget bypass if callers neglect pre-call checks.

**`src/wrought_escalation/config.py`** · grounded 9/9
> Purpose: Strictly loads and validates pinned escalation configuration from `pins.lock` without applying defaults.
> Key components: `EscalationPins` dataclass and `load` function enforce all keys listed in `_REQUIRED`.
> Dependencies: `pathlib`, `dataclasses.dataclass`, and `ruamel.yaml.YAML`.
> Risk: YAML string-to-boolean coercion (e.g., `bool("no")` evaluates to `True`) could silently invert critical routing pins like `allow_fallbacks`, causing unapproved endpoint usage and financial loss despite explicit load-time type assertions.

**`src/wrought_escalation/driver.py`** · grounded 13/13
> Purpose: Orchestrates end-to-end escalation for cap-exhausted tasks by staging candidates, executing the real oracle for verification, computing failure signatures, and returning routing verdicts.
> Key functions: `drive`, `_drive`, `_stage`, `prompt_for`, `spec_hash`.
> Dependencies: Directly imports `hashlib`, `pathlib`, `subprocess`, `wrought_orchestrator.store`, `wrought_supervisor.oracle`, `wrought_supervisor.classify.classify`, `wrought_supervisor.router.failure_signature`, and local `.config`, `.escalate`, `.ledger`.
> Risk: Tightly couples financial ledger commits with sandbox oracle execution (`oracle.verify`), and a broad `except Exception` in `_drive` may mask unexpected errors during verification or staging.

**`src/wrought_escalation/escalate.py`** · grounded 4/4
> Purpose: Manages end-to-end model escalations by atomically reserving budget against a production ledger before opening network sockets, enforcing strict FSM transitions and cost reconciliation.
> Key functions: read_credential, prompt_hash, attempt_key, escalate, _escalate.
> Direct imports: hashlib, json, os, pathlib, time, wrought_orchestrator.store, wrought_orchestrator.fsm.guard_ok, .client, .ledger.
> Obvious risks: Hard exits if $CREDENTIALS_DIRECTORY is unset; ledger-first commit ordering intentionally sacrifices crash atomicity to prevent unattributable spend, risking conservative over-counting; explicitly blocks credential fallbacks to avoid /proc/*/environ leaks.

**`src/wrought_escalation/ledger.py`** · grounded 18/18
> Purpose: Manages atomic pre-call budget reservations and cost tracking for AI escalations across D21 weekly/monthly windows, ensuring spend is recorded before any HTTP request is issued.
> Key functions/classes: `reserve_standalone`, `reserve_in_txn`, `check_budget`, `assert_budget_unmoved`, `finalize`, `BudgetMoved`, `production_db_path`, `authority`, `unreconciled`, `worst_case_bound_rows`.
> Direct imports/dependencies: `sqlite3`, `json`, `datetime`, `contextlib`, `pathlib`, `ruamel.yaml`, `wrought_orchestrator`.
> Obvious risk: Historical TOCTOU budget validation races, automatic worst-case over-charging on process crashes or timeouts, and strict reliance on external `pins.lock` for database paths and pricing pins.

**`src/wrought_orchestrator/fsm.py`** · grounded 8/8
> Implements an explicit finite state machine using a hardcoded transition table that raises `UndefinedTransition` for any invalid `(state, event)` pair to enforce loud failures.
> Key components include the `Transition` dataclass, the `TABLE` dictionary, and functions `next_state`, `guard_ok`, and `reachable_states`.
> Direct dependencies are `__future__.annotations` and `dataclasses.dataclass`.
> A primary risk is the decoupled guard logic in `guard_ok`, which must be manually enforced before state changes, combined with strict string matching for states and events that can trigger runtime failures if external emitters drift from the table.

**`src/wrought_orchestrator/redact.py`** · grounded 9/9
> Purpose: Implements pre-persistence secret redaction (§14.4) that scans text for provider prefixes and high-entropy tokens, replacing matches with SHA-256 correlators before event logging.
> Key functions/classes: `redact`, `redact_obj`, `_tag`, `shannon_bits_per_char`, `_fenced_spans`, `_in_fence`.
> Direct imports/dependencies: `__future__.annotations`, `hashlib`, `math`, `re`.
> Obvious risk: Documented spec defects allow hyphenated vendor keys and hexadecimal secrets to bypass the entropy screen (strict `>4.0` threshold) and original regexes, leaving prefix matching as a fragile single point of failure.

**`src/wrought_orchestrator/store.py`** · grounded 20/20
> Purpose: Stdlib-only SQLite event store, task projection cache, and queue enforcing atomic transactions for state changes and using an outbox pattern for external side effects.
> Key Functions/Classes: `connect`, `init_db`, `append_and_project`, `enqueue`, `claim`, `ack`, `dead_letter`, `sweep_dead_letters`, `apply_external_effect`, `rebuild_projection`, `projection_parity`, `VersionConflict`.
> Direct Imports: `json`, `os`, `pathlib`, `sqlite3`, `time`, `uuid`, `redact`.
> Risk: Manual `BEGIN IMMEDIATE` handling and hardcoded default paths (`DB_PATH`, `EFFECTS_DIR`) can cause WAL bloat or accidental data loss; `apply_external_effect` writes outside database transactions, risking ledger inconsistency if processes crash before ledger writes.

**`src/wrought_orchestrator/worker.py`** · grounded 15/15
> Implements a durable task worker with outbox-pattern side effects, fault-tolerant recovery, and deterministic chaos injection.
> Key functions: `process_one`, `run`, `recover`, `run_external_step`, `_transition`, `archive_completed`, `_chaos`.
> Direct dependencies: `os`, `signal`, `sqlite3`, `json`, `time`, `.store`, `.fsm` (`REPAIR_CAP`, `next_state`, `guard_ok`).
> Obvious risk: `_chaos` triggers uncatchable `signal.SIGKILL` that bypasses cleanup, and complex verification/escalation branches may leave messages claimed but unacked if non-terminal states are missed.

**`src/wrought_supervisor/classify.py`** · grounded 9/9
> Purpose: Supervisor-side classification of sandbox job outcomes, prioritizing substrate signatures over tool exit codes to prevent misattributing repairable code defects as infrastructure failures.
> Key Functions: `classify`, `_candidate_collection_failure`, `_running_check`, `_unit_result`
> Direct Imports: `json`, `re`, `subprocess`, `time`, `__future__.annotations`
> Obvious Risk: Polling `journalctl` via `subprocess` in `_unit_result` introduces timing race conditions if systemd verdicts fail to settle within the 5-second window, potentially returning provisional classifications; heavy reliance on hardcoded string heuristics may misroute failures if tool output formats change.

**`src/wrought_supervisor/heldout.py`** · grounded 12/12
> Purpose: Implements GATE-44's held-out feedback filter to strip named failures, progress lines, and counts from pytest output and verification envelopes, ensuring held-out tests remain hidden from the model while grading uses the full suite.
> Key functions: `load_pinned_split`, `filter_envelope`, `filter_pytest_stdout`, `filter_result`, `guard`, `grade`, `node_function`.
> Direct imports: `copy`, `json`, `pathlib`, `re`, and `ruamel.yaml` (loaded locally inside `load_pinned_split`).
> Obvious risk: Filter misses could leak held-out test identifiers to the model; the `guard` backstop catches residual leaks but flags an experimental defect, and the module strictly exits if `pins.lock` lacks the pinned split.

**`src/wrought_supervisor/oracle.py`** · grounded 15/15
> Purpose: Centralizes verification execution and classification-to-FSM-verdict mapping for the wrought supervisor, enforcing artifact provenance via staging receipts and eliminating silent routing defaults.
> Key functions: `stage_candidate`, `assert_staged_for_attempt`, `verify`, `verdict_for`, `oracle_verdict`, `job_dir`.
> Direct imports/dependencies: `hashlib`, `re`, `json`, `os`, `pathlib`, `subprocess`, `time`; invokes `bin/verify-job` and feeds `worker.process_one`.
> Risks: Executes `sudo -n rm -rf` and `sudo -n install` during staging; relies strictly on `TASK_ID_RE` and `MODULE_FILENAME_RE` to prevent path traversal, and raises hard `RuntimeError` on receipt mismatches or unclassified outputs, risking pipeline halts.

**`src/wrought_supervisor/router.py`** · grounded 9/9
> Purpose: Implements a deterministic, six-rule ordered FSM routing policy to assign task outcomes based on verdict classification and historical repair data.
> Key functions/classes: `TaskState`, `failure_signature`, `route`
> Direct imports/dependencies: `hashlib`, `json`, `re`, `dataclasses`, `__future__`
> Obvious risk: Raises `ValueError` on unmatched verdicts instead of a safe fallback, and relies on hardcoded regex patterns (`_NOISE`) for failure normalization that may miss novel error formats.

**`src/wrought_verifier/__main__.py`** · grounded 16/16
> Purpose: In-sandbox verification runner that executes lint, test, and coverage checks, then writes a final `result.json` envelope as the sole output channel within a restricted `bwrap` namespace.
> Key functions: `main`, `_run`, `_judge`, `_execution_proof_error`, `_write_envelope`, `_envelope_tamper`, `_statvfs_out`.
> Direct imports/dependencies: `argparse`, `hashlib`, `json`, `os`, `subprocess`, `sys`, `time`, `load_pack`, `PackInvalid`.
> Obvious risk: Documented `F-1 Face B` isolation gap where candidate code shares the reporting process, making TEST and COVERAGE verdicts self-reported and forgeable.

**`src/wrought_verifier/pack.py`** · grounded 13/13
> Purpose: Parses and strictly validates verification pack TOML definitions inside a sandbox, enforcing default-deny rules to reject malformed configs before execution.
> Key functions/classes: `PackInvalid`, `Check`, `Pack`, `_require`, `loads`, `load`
> Direct imports/dependencies: `tomllib`, `dataclasses` (`dataclass`, `field`), `hashlib`
> Obvious risk: Hardcoded metric allowlists (`KNOWN_METRICS`, `KNOWN_JSON_METRICS`) and strict config file path checks mitigate substrate incidents, but validation bypasses or non-UTF-8 inputs could cause silent tool fallbacks or decoding crashes.

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

**`bin/gate19-fresh`**
> Purpose: Gates MTP promotion by comparing fresh-process baseline and MTP runs on token identity, wall-clock latency, and acceptance rates, outputting a verdict without auto-flipping active-profile.
> Key Functions: first_req
> Dependencies: $CONF, $LLAMA, curl, python3 (json, sys), bc, ldd, strings, kill
> Risks: Fragile backend detection via strings/ldd output parsing, unhandled process cleanup (kill $pid), hardcoded port 8096, and inline Python lacking JSON load error handling.

**`bin/make-review-bundle-19`**
> Purpose: Assembles REVIEW-BUNDLE-19.zip, a standalone "courier" archive staging session 19/20 evidence, journal excerpts, source files, and git history for external review without committing duplicate data.
> Key functions or classes: None defined; procedural bash execution driven by variables ZIP, STAGE, BASE and trap for cleanup.
> Direct imports/dependencies: Relies on CLI utilities mktemp, git, sed, awk, sha256sum, zip, unzip, stat and project artifacts SESSION-REPORT-19.md, INVENTORY.md, BUILD-JOURNAL.md, docs/08-decisions.md, src/, bin/.
> Obvious risk: Hardcoded /home/kalib/foundry path limits portability; fragile sed/awk regex parsing of markdown/journal headers will break on formatting changes; silent cp/mkdir calls lack error checks for missing artifacts.

**`bin/make-soak3-bundle`**
> Purpose: Generates REVIEW-BUNDLE-SOAK-3.zip for review by staging reports, harness scripts, build evidence, live status JSONs, and a manifest with build-time metadata and SHA-256 checksums.
> Key functions/classes: None; operates as a linear bash script without named functions or classes.
> Direct imports/dependencies: Relies on standard utilities (git, mktemp, zip, unzip, sha256sum, find, sort, xargs, cp, mkdir, rm) and hardcoded paths (/var/lib/wrought/soak3/track-a/status.json, /var/lib/wrought/soak3/track-b/status.json, SESSION-REPORT-SOAK-3.md, CLAUDE.md, pins.lock, build-evidence/soak-3).
> Obvious risk: Hardcoded absolute paths and strict set -euo pipefail will abort the build if the target environment lacks the expected directory structure, file permissions, or a clean git repository state.

**`bin/reclassify-corpus`**
> Purpose: Re-runs the shipped classifier over stored Track-B attempt records to diff against originally saved classifications and verify a historical re-baselining claim.
> Key functions/classes: main, classify
> Direct imports/dependencies: argparse, collections, glob, json, pathlib, sys, wrought_supervisor.classify
> Obvious risk: Hardcoded absolute JOB_ROOT path (/var/lib/wrought/jobs) and sys.path.insert(0, ...) mutation break portability and risk import shadowing.

**`bin/soak-curve`**
> Purpose: Validates GATE-37's linear extrapolation by comparing measured per-event rebuild costs across soak checkpoints to determine if pinned headroom assumptions hold.
> Key functions/classes: main()
> Direct imports/dependencies: __future__, json, pathlib, sys
> Obvious risk: Hard-coded absolute path /var/lib/wrought/soak1/checkpoints.jsonl and strict reliance on unvalidated JSON keys like rebuild_cold_ms and parity_differences will trigger KeyErrors or silent miscalculations if the checkpoint schema changes.

**`bin/soak3-importcheck`**
> Purpose: Parses Python ASTs to detect direct imports of the forbidden wrought_escalation package, avoiding grep-based false positives.
> Key functions/classes: top_level_imports, main
> Direct imports/dependencies: __future__, ast, pathlib, sys
> Obvious risk: ast.parse lacks try/except handling, risking uncaught exceptions on malformed or non-Python files; deliberately skips transitive dependency analysis.

**`bin/soak3-launch`**
> Purpose: Asserts SOAK-3 preconditions, byte-freezes orchestrator.db, records launch evidence, and detaches soak3-track-a and soak3-track-b into background.
> Key scripts: soak3-importcheck, soak3-track-a, soak3-track-b, soak3-build-pool, verify-job.
> Dependencies: git, sha256sum, systemctl, sudo, df, /opt/wrought/venv-orch/bin/python, pins.lock, orchestrator.db.
> Risks: Background processes launched via setsid nohup ... & lack startup validation beyond a hardcoded sleep 3; requires passwordless sudo -n; DB freeze relies on static checksums without file locks, risking silent state drift if writers bypass the freeze claim.

**`bin/wait-healthy`**
> Purpose: Polls the llama-server health endpoint until HTTP 200 is received or TIMEOUT expires, enabling systemd ExecStartPost to defer startup until the model is resident.
> Key functions or classes: None defined; executes as a top-level bash script with inline control flow.
> Direct imports/dependencies: curl, sleep, WROUGHT_CONF, WROUGHT_HOST, WROUGHT_PORT, CREDENTIALS_DIRECTORY, inference-api-key.
> Obvious risks: curl network failures silently yield 000 and retry, masking infrastructure outages as health timeouts; credentials are injected via cat into command-line arguments, risking exposure in process listings.

**`bin/wrought-course-check`**
> Purpose: A halt-only safety valve that reads a run summary from stdin, enforces a spend cap, and delegates sealed-credential handling to systemd-run to invoke wrought-course-post, outputting only OK or HALT to gate runner progress.
> Key functions: fail, main.
> Direct imports/dependencies: json, os, subprocess, sys, tempfile, datetime, timezone, Path; relies on sudo, systemd-run, and the external wrought-course-post script.
> Obvious risk: Shell command is constructed via f-string interpolation (f'cat "$CREDENTIALS_DIRECTORY/{cred}" | {POST} {summary_path}'), enabling command injection if POST, cred, or summary_path contain untrusted metacharacters; manual os.unlink cleanup risks leaving temporary files on disk after a crash.

### `src/`

**`src/wrought_escalation/__init__.py`**
> Purpose: Documents the escalation tier (§13) configuration requirements.
> Key functions/classes: None defined in the file.
> Direct imports/dependencies: No explicit imports; references D19, D21, and [SPEC-R13.7].
> Obvious risk: Contains only a docstring with no executable code or exports, creating a high risk of missing functionality and unresolved external dependencies.

**`src/wrought_orchestrator/validate.py`**
> Purpose: Validates TASK.md inputs against a strict YAML subset, JSON Schema, EARS phrasing rules, and REQ/CON mapping requirements per specs §7.5/§7.6.
> Key components: ValidationResult, validate, split_task_md, canon_v2, req_lines, ears_pattern, _strict_subset_violations.
> Dependencies: hashlib, io, re, jsonschema, rfc8785, ruamel.yaml.
> Risk: _strict_subset_violations uses text-based regex to reject YAML anchors/aliases/merge keys, explicitly risking false positives on unquoted scalars, while ears_pattern relies on regex matching that may misclassify complex phrasing despite negative controls.

**`src/wrought_verifier/__init__.py`**
> Purpose: Initializes the wrought_verifier package namespace and establishes module boundaries.
> Key functions/classes: None explicitly defined or exported in the referenced file.
> Direct imports/dependencies: No import statements are present in the supplied file path.
> Obvious risk: Absence of explicit re-exports or __all__ declarations may cause ambiguous API surface area and increase the likelihood of circular import errors or missing submodule resolutions.

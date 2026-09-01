# bin/serve-model
Purpose: Bash launch wrapper that dynamically resolves GPU device tokens, validates inference profiles, and runs hardware/self-tests before starting the model server.
Key functions: die() exits on fatal errors; main logic parses $PROFILE_PATH into $ARGS, validates via $LLAMA_SERVER --list-devices, and asserts VRAM/runtime PM via sysfs.
Dependencies: Sources $CONF (/etc/wrought/serving.env); invokes $LLAMA_SERVER (/opt/wrought/bin/llama-server), $ASSERT_POWER (/opt/wrought/bin/assert-power-profile), and reads $CREDENTIALS_DIRECTORY/inference-api-key and /sys/module/amdgpu/parameters/runpm.
Risks: Fragile grep/sed parsing of --list-devices output for device tokens and VRAM; strict hardcoded profile whitelist (qwen36.args|qwen36-mtp.args|devstral.args) rejects unlisted models; any self-test failure exits non-zero, completely blocking service startup.

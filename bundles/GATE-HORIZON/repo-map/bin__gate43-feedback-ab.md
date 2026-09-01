# bin/gate43-feedback-ab
Purpose: Runs a sequential three-arm (a, b, c) experiment comparing repair-feedback formats (`bare`, `verifier`, `trace`) on a pinned 27B model, measuring pre-escalation demand with escalation disabled.
Key functions: `status`, `arm_complete`, `say`; core execution driver `./bin/baseline-run`.
Direct dependencies: `/opt/wrought/venv-orch/bin/python`, `curl`, `sha256sum`, inline Python heredocs, and variables `$PACK`, `$ACTIVE`, `$BASELINE_DIR`.
Obvious risks: Sequential single-GPU execution confounds arm order with time; resumption skips only if `records-$run.json` fully parses, risking silent truncation bugs; strict assertions (`WANT_PACK`, `WANT_PROFILE`, `WANT_MODEL`) forcibly abort on minor infrastructure drift.

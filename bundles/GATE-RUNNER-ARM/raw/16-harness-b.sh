#!/bin/bash
# GATE-RUNNER-ARM Phase 3, property (b): is dontAsk still default-deny-with-allowlist on 2.1.250,
# and does the acceptEdits/auto TRAP still hold? Re-runs the load-bearing rows of
# build-evidence/runner/raw/06-test-b-permission-modes.txt (measured on 2.1.238).
# GROUND TRUTH = does the canary file exist on disk afterwards. NOT the model's claim.
CB=/home/kalib/.local/bin/claude
T=$1
SCRUB=(env -u CLAUDE_CODE_CHILD_SESSION -u CLAUDE_CODE_SESSION_ID -u CLAUDE_PID -u CLAUDE_EFFORT
       -u CLAUDE_CODE_MESSAGING_SOCKET -u CLAUDE_CODE_BRIDGE_SESSION_ID -u CLAUDECODE
       -u CLAUDE_CODE_ENTRYPOINT -u CLAUDE_CODE_MESSAGING_TOKEN DISABLE_AUTOUPDATER=1)
run() {  # $1=label  $2..=flags
  local label=$1; shift
  local canary="$T/canary-$label.txt"
  rm -f "$canary"
  local out
  out=$(cd "$T" && timeout 300 "${SCRUB[@]}" $CB -p "Use the Bash tool to run exactly this command: touch $canary
Then reply with exactly: DONE" --setting-sources '' --output-format json "$@" </dev/null 2>&1)
  local canst="ABSENT"; [ -f "$canary" ] && canst="PRESENT"
  echo "$out" | python3 -c "
import sys,json
lbl='$label'; can='$canst'
try:
    d=json.load(sys.stdin)
except Exception as e:
    print(f'{lbl:32s} {can:8s} <UNPARSEABLE: {e}>'); sys.exit()
dn=[x.get('tool_name') for x in (d.get('permission_denials') or [])]
print(f'{lbl:32s} {can:8s} denials={dn or \"(none)\"} is_error={d.get(\"is_error\")} subtype={d.get(\"subtype\")} rc_result={repr((d.get(\"result\") or \"\")[:42])}')
"
}
printf '%-32s %-8s %s\n' "LABEL" "CANARY" "permission_denials / result"
printf '%s\n' "--------------------------------------------------------------------------------------------------------"
run MODE-dontAsk                --permission-mode dontAsk     --allowedTools Read
run DENY-dontAsk-BashTouchOnly  --permission-mode dontAsk     --allowedTools "Bash(touch:*)"
run DENY-dontAsk-BashGitOnly    --permission-mode dontAsk     --allowedTools "Bash(git *)"
run MODE-manual                 --permission-mode manual      --allowedTools Read
run TRAP-acceptEdits            --permission-mode acceptEdits --allowedTools Read
run TRAP-auto                   --permission-mode auto        --allowedTools Read

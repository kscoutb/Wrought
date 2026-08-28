#!/bin/bash
# Probe A (control): launch ONE gate child in the runner's exact shape on the CURRENT CLI,
# then observe the two candidate discovery artifacts while it is alive.
set -u
W=/var/lib/wrought/runner-harden
OUT=$W/probe/A
mkdir -p "$OUT"
UNIT="harden-probeA-$(date +%s).scope"
PROMPT='Run these Bash commands one at a time, in order: date -u; sleep 25; date -u; sleep 25; date -u. Then reply with exactly: PROBEA-DONE'

env -i \
  HOME="$HOME" PATH="$PATH" USER="$USER" LOGNAME="$LOGNAME" SHELL="$SHELL" \
  LANG="${LANG:-C.UTF-8}" XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR}" \
  DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-}" \
  TERM=dumb CI=1 \
  CLAUDE_CODE_MAX_OUTPUT_TOKENS=32000 BASH_DEFAULT_TIMEOUT_MS=600000 \
  systemd-run --user --scope --quiet --unit="$UNIT" \
    -p MemoryMax=8G -p MemorySwapMax=0 -p RuntimeMaxSec=300 \
    /home/kalib/.local/bin/claude -p "$PROMPT" \
      --setting-sources '' \
      --settings /etc/wrought/runner-hooks.json \
      --permission-mode dontAsk \
      --allowedTools 'Bash(date:*),Bash(sleep:*)' \
      --output-format json \
      --max-budget-usd 1.0 \
      > "$OUT/child.stdout.json" 2> "$OUT/child.stderr.txt" < /dev/null &
CHILD_SHELL=$!
echo "launcher pid: $CHILD_SHELL  unit: $UNIT" > "$OUT/launch.txt"

# poll the two candidate discovery artifacts for 70s
{
echo "# cmd: 2s-interval poll of /run/user/1000/cc-socks and ~/.claude/daemon/roster.json while a"
echo "#      runner-shape gate child is alive. Supervising session pid: $$ (this script)."
echo "# date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "# NOTE: this session's own socket is 13774.sock — any OTHER entry is the gate child."
echo
for i in $(seq 1 35); do
  T=$(date -u +%H:%M:%S)
  SOCKS=$(ls /run/user/1000/cc-socks/ 2>/dev/null | tr '\n' ' ')
  WORKERS=$(python3 -c "import json,sys;print(json.load(open('/home/kalib/.claude/daemon/roster.json')).get('workers'))" 2>/dev/null)
  CPIDS=$(pgrep -x claude | tr '\n' ' ')
  echo "t=$T socks=[$SOCKS] roster_workers=$WORKERS claude_pids=[$CPIDS]"
  sleep 2
done
} > "$OUT/poll.txt" 2>&1
wait $CHILD_SHELL
echo "child shell rc=$?" >> "$OUT/launch.txt"

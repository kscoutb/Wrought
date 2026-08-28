#!/bin/bash
# Control F: the CURRENT gate-child shape — REAL HOME, REAL XDG_RUNTIME_DIR. Long-lived.
set -u
W=/var/lib/wrought/runner-harden; OUT=$W/probe/F2-realhome-realrt; rm -rf "$OUT"; mkdir -p "$OUT"
UNIT="harden-F2-$(date +%s).scope"
env -i HOME=/home/kalib PATH="$PATH" USER=kalib LOGNAME=kalib SHELL=/bin/bash \
  LANG="${LANG:-C.UTF-8}" XDG_RUNTIME_DIR=/run/user/1000 TERM=dumb CI=1 \
  CLAUDE_CODE_MAX_OUTPUT_TOKENS=32000 BASH_DEFAULT_TIMEOUT_MS=600000 \
  systemd-run --user --scope --quiet --unit="$UNIT" \
    -p MemoryMax=8G -p MemorySwapMax=0 -p RuntimeMaxSec=300 \
    /home/kalib/.local/bin/claude -p 'Do these with Bash, ONE PER TURN: 1. Run: date -u +%FT%TZ. 2. Run: for i in $(seq 1 45); do date -u +%T; sleep 2; done. 3. Run: date -u +%FT%TZ. Then reply exactly: CONTROL-F2-DONE' \
      --setting-sources '' --settings /etc/wrought/runner-hooks.json \
      --permission-mode dontAsk --allowedTools 'Bash' \
      --output-format json --max-budget-usd 1.0 \
      > "$OUT/child.stdout.json" 2> "$OUT/child.stderr.txt" < /dev/null &
LP=$!; echo "unit=$UNIT launcher=$LP HOME=/home/kalib XDG_RUNTIME_DIR=/run/user/1000" > "$OUT/seed.txt"
{ for i in $(seq 1 150); do kill -0 $LP 2>/dev/null || { echo "child gone at $(date -u +%H:%M:%S)"; break; }
  echo "t=$(date -u +%H:%M:%S) shared_socks=[$(ls /run/user/1000/cc-socks/ 2>/dev/null|tr '\n' ' ')]"; sleep 2; done; } > "$OUT/poll.txt" 2>&1
wait $LP; echo "launcher rc=$?" >> "$OUT/seed.txt"

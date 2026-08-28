#!/bin/bash
# Seed an ephemeral HOME at $1 to seed-level $2, then run a probe child under it.
#   level 0 = empty
#   level 1 = + ~/.claude/.credentials.json
#   level 2 = + ~/.claude.json
#   level 3 = + ~/.gitconfig ~/.git-credentials   (what the gate's own courier push needs)
# $3 = private XDG_RUNTIME_DIR? (yes|no)   $4 = label   $5 = prompt
set -u
EH="$1"; LEVEL="$2"; PRIVRT="$3"; LABEL="$4"; PROMPT="$5"; TOOLS="${6:-Bash(date:*),Bash(sleep:*)}"
W=/var/lib/wrought/runner-harden
OUT=$W/probe/$LABEL
rm -rf "$EH" "$OUT"; mkdir -p "$EH" "$OUT"; chmod 700 "$EH"
SEEDED=""
if [ "$LEVEL" -ge 1 ]; then mkdir -p "$EH/.claude"; chmod 700 "$EH/.claude"
  cp /home/kalib/.claude/.credentials.json "$EH/.claude/.credentials.json"; chmod 600 "$EH/.claude/.credentials.json"
  SEEDED="$SEEDED .claude/.credentials.json"; fi
if [ "$LEVEL" -ge 2 ]; then cp /home/kalib/.claude.json "$EH/.claude.json"; chmod 600 "$EH/.claude.json"
  SEEDED="$SEEDED .claude.json"; fi
if [ "$LEVEL" -ge 3 ]; then cp /home/kalib/.gitconfig "$EH/.gitconfig"
  cp /home/kalib/.git-credentials "$EH/.git-credentials"; chmod 600 "$EH/.git-credentials"
  SEEDED="$SEEDED .gitconfig .git-credentials"; fi

RT_OUTER=/run/user/1000
if [ "$PRIVRT" = "no" ]; then RT="/run/user/1000"; INNER=""; else RT="$EH/xdg-runtime"; mkdir -p "$RT"; chmod 700 "$RT"; fi
if [ "$PRIVRT" = "inner" ]; then RT_OUTER=/run/user/1000; INNER="/usr/bin/env XDG_RUNTIME_DIR=$RT"; else RT_OUTER="$RT"; INNER=""; fi

{ echo "label=$LABEL seed_level=$LEVEL seeded=[$SEEDED] HOME=$EH XDG_RUNTIME_DIR=$RT"
  echo "seeded tree:"; find "$EH" -mindepth 1 | sed "s|$EH|\$EPHEMERAL_HOME|"; } > "$OUT/seed.txt"

UNIT="harden-$LABEL-$(date +%s).scope"
env -i HOME="$EH" PATH="$PATH" USER="$USER" LOGNAME="$LOGNAME" SHELL="$SHELL" \
  LANG="${LANG:-C.UTF-8}" XDG_RUNTIME_DIR="$RT_OUTER" TERM=dumb CI=1 \
  CLAUDE_CODE_MAX_OUTPUT_TOKENS=32000 BASH_DEFAULT_TIMEOUT_MS=600000 \
  systemd-run --user --scope --quiet --unit="$UNIT" \
    -p MemoryMax=8G -p MemorySwapMax=0 -p RuntimeMaxSec=300 \
    $INNER /home/kalib/.local/bin/claude -p "$PROMPT" \
      --setting-sources '' --settings /etc/wrought/runner-hooks.json \
      --permission-mode dontAsk \
      --allowedTools "$TOOLS" \
      --output-format json --max-budget-usd 1.0 \
      --add-dir /home/kalib/courier/Wrought \
      > "$OUT/child.stdout.json" 2> "$OUT/child.stderr.txt" < /dev/null &
LP=$!
echo "unit=$UNIT launcher=$LP" >> "$OUT/seed.txt"

{
echo "# 2s poll of BOTH candidate discovery artifacts while the $LABEL child is alive."
echo "# shared cc-socks = /run/user/1000/cc-socks ; private = \$EPHEMERAL_HOME/xdg-runtime/cc-socks"
echo "# this supervising session owns 13774.sock — any OTHER entry is the child."
for i in $(seq 1 150); do
  kill -0 $LP 2>/dev/null || { echo "child gone at $(date -u +%H:%M:%S)"; break; }
  SH=$(ls /run/user/1000/cc-socks/ 2>/dev/null | tr '\n' ' ')
  PV=$(ls "$RT/cc-socks/" 2>/dev/null | tr '\n' ' ')
  RO=$(python3 -c "import json;print(json.load(open('/home/kalib/.claude/daemon/roster.json')).get('workers'))" 2>/dev/null)
  EHRO=$(python3 -c "import json;print(json.load(open('$EH/.claude/daemon/roster.json')).get('workers'))" 2>/dev/null || echo "(none)")
  echo "t=$(date -u +%H:%M:%S) shared_socks=[$SH] private_socks=[$PV] real_roster=$RO ehome_roster=$EHRO"
  sleep 2
done
} > "$OUT/poll.txt" 2>&1
wait $LP; echo "launcher rc=$?" >> "$OUT/seed.txt"
echo "--- post-run ephemeral HOME tree ---" >> "$OUT/seed.txt"
find "$EH" -mindepth 1 2>/dev/null | sed "s|$EH|\$EPHEMERAL_HOME|" | sort >> "$OUT/seed.txt"

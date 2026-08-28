#!/bin/bash
# GATE-RUNNER-ARM Phase 3, property (a) second half: does HARDEN's TWO-SURFACE isolation still
# hold on 2.1.250? Re-runs the shape of build-evidence/runner-harden/raw/17-harness-ehome.sh,
# writing into the session scratchpad instead of HARDEN's workdir.
#   $1 = label   $2 = isolated|control
# ISOLATED = private ephemeral HOME (seeded to the measured minimum) + PRIVATE XDG_RUNTIME_DIR
#            applied INNER (env prefix on the claude argv, after systemd-run).
# CONTROL  = real HOME + the shared /run/user/1000 — proves the probe can actually SEE a child.
set -u
SP=/tmp/claude-1000/-home-kalib-foundry/c7320a0f-9ba2-4fda-81e1-9a40647bd286/scratchpad
LABEL="$1"; MODE="$2"
OUT="$SP/iso/$LABEL"; rm -rf "$OUT"; mkdir -p "$OUT"
SELF_SOCK="79855.sock"   # this supervising session; any OTHER entry is the child

if [ "$MODE" = "isolated" ]; then
  EH="$SP/iso/$LABEL-home"; rm -rf "$EH"; mkdir -p "$EH/.claude"; chmod 700 "$EH" "$EH/.claude"
  cp /home/kalib/.claude/.credentials.json "$EH/.claude/.credentials.json"; chmod 600 "$EH/.claude/.credentials.json"
  cp /home/kalib/.gitconfig "$EH/.gitconfig"
  cp /home/kalib/.git-credentials "$EH/.git-credentials"; chmod 600 "$EH/.git-credentials"
  RT="$EH/xdg-runtime"; mkdir -p "$RT"; chmod 700 "$RT"
  RT_OUTER=/run/user/1000; INNER="/usr/bin/env XDG_RUNTIME_DIR=$RT"
else
  EH="$HOME"; RT=/run/user/1000; RT_OUTER=/run/user/1000; INNER=""
fi
echo "label=$LABEL mode=$MODE HOME=$EH XDG_RUNTIME_DIR(child)=$RT" > "$OUT/seed.txt"
[ "$MODE" = "isolated" ] && { echo "seeded tree:" >> "$OUT/seed.txt"; find "$EH" -mindepth 1 | sed "s|$EH|\$EPHEMERAL_HOME|" >> "$OUT/seed.txt"; }

UNIT="arm-$LABEL-$(date +%s).scope"
env -i HOME="$EH" PATH="$PATH" USER="$USER" LOGNAME="$LOGNAME" SHELL="$SHELL" \
  LANG="${LANG:-C.UTF-8}" XDG_RUNTIME_DIR="$RT_OUTER" TERM=dumb CI=1 DISABLE_AUTOUPDATER=1 \
  CLAUDE_CODE_MAX_OUTPUT_TOKENS=32000 BASH_DEFAULT_TIMEOUT_MS=600000 \
  systemd-run --user --scope --quiet --unit="$UNIT" \
    -p MemoryMax=8G -p MemorySwapMax=0 -p RuntimeMaxSec=300 \
    $INNER /home/kalib/.local/bin/claude -p 'Use the Bash tool to run: sleep 40
Then reply with exactly: ISO-DONE' \
      --setting-sources '' --settings /etc/wrought/runner-hooks.json \
      --permission-mode dontAsk --allowedTools "Bash(sleep:*)" \
      --output-format json --max-budget-usd 1.0 \
      > "$OUT/child.stdout.json" 2> "$OUT/child.stderr.txt" < /dev/null &
LP=$!
{
echo "# 2s poll while the $LABEL child is alive."
echo "# shared cc-socks = /run/user/1000/cc-socks   (this session owns $SELF_SOCK)"
echo "# private cc-socks = $RT/cc-socks"
for i in $(seq 1 100); do
  kill -0 $LP 2>/dev/null || { echo "child gone at $(date -u +%H:%M:%S)"; break; }
  SH=$(ls /run/user/1000/cc-socks/ 2>/dev/null | tr '\n' ' ')
  SH_OTHER=$(ls /run/user/1000/cc-socks/ 2>/dev/null | grep -v "^$SELF_SOCK$" | tr '\n' ' ')
  PV=$(ls "$RT/cc-socks/" 2>/dev/null | tr '\n' ' ')
  echo "t=$(date -u +%H:%M:%S) shared=[$SH] shared_MINUS_self=[$SH_OTHER] private=[$PV]"
  sleep 2
done
} > "$OUT/poll.txt" 2>&1
wait $LP; echo "launcher rc=$?" >> "$OUT/seed.txt"
echo "--- $LABEL ($MODE) ---"
cat "$OUT/seed.txt"
echo "poll (deduped):"; sort -u -t']' -k1,3 "$OUT/poll.txt" | grep '^t=' | head -4
echo "DISTINCT shared_MINUS_self values seen:"; grep -o 'shared_MINUS_self=\[[^]]*\]' "$OUT/poll.txt" | sort -u
echo "DISTINCT private values seen:";           grep -o 'private=\[[^]]*\]' "$OUT/poll.txt" | sort -u
echo "child result:"; python3 -c "
import json;d=json.load(open('$OUT/child.stdout.json'))
print('  is_error=',d.get('is_error'),'result=',repr((d.get('result') or '')[:50]),'session_id=',d.get('session_id'))" 2>&1 | head -3

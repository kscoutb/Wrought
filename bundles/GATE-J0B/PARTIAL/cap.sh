# GATE-J0B-SURFACE — capture helper. Sourced by each step.
# Adapted from /var/lib/wrought/j0a/round2/cap.sh (itself from j0a/cap.sh, from j0-recon/cap.sh).
# THE ONLY ADAPTATION: J0=/var/lib/wrought/j0b. Function bodies are byte-identical.
# Every finding in the report is a command + its output + its exit code (J-95).
J0=/var/lib/wrought/j0b

hdr() {  # hdr <outfile> <title>
  local out="$J0/raw/$1"; shift
  {
    echo "###############################################################################"
    echo "# $*"
    echo "# host=$(hostname)  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  user=$(id -un)"
    echo "###############################################################################"
    echo
  } > "$out"
}

cap() {  # cap <outfile> <command string...>
  local out="$J0/raw/$1"; shift
  local cmd="$*"
  echo "\$ $cmd" >> "$out"
  eval "$cmd" >> "$out" 2>&1
  local rc=$?
  echo "[exit=$rc]" >> "$out"
  echo >> "$out"
  return 0
}

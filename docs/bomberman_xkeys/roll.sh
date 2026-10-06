#!/usr/bin/env bash
# Roll Bomberman + xkeys race seeds until COUNT of them generate and pass verify_seed.py.
#
# usage: docs/bomberman_xkeys/roll.sh <path to JP 1.0 rom> [count=1] [outdir=bomberman_xkeys_out]
# Run from the repository root. Set PYTHON to pick an interpreter (default: .venv/bin/python, else python3).
#
# Each seed lands in <outdir>/<n>/ with the .bps (share this), the spoiler, and the patched .sfc.
# Never commit the .sfc.
set -u

ROM=${1:?usage: roll.sh <JP 1.0 rom> [count] [outdir]}
COUNT=${2:-1}
OUT=${3:-bomberman_xkeys_out}
MAX_TRIES=${MAX_TRIES:-100}
if [ -z "${PYTHON:-}" ]; then
  if [ -x .venv/bin/python ]; then PYTHON=.venv/bin/python; else PYTHON=python3; fi
fi
HERE=docs/bomberman_xkeys

mkdir -p "$OUT"
ok=0
tries=0
while [ "$ok" -lt "$COUNT" ] && [ "$tries" -lt "$MAX_TRIES" ]; do
  tries=$((tries + 1))
  dir="$OUT/try$tries"
  mkdir -p "$dir"
  "$PYTHON" DungeonRandomizer.py \
    --customizer "$HERE/bomberman_xkeys.yaml" \
    --no_money_balance --race --spoiler full --bps \
    --rom "$ROM" --outputpath "$dir" > "$dir/gen.log" 2>&1
  sfc=$(ls "$dir"/*.sfc 2>/dev/null | head -1)
  spoiler=$(ls "$dir"/*_Spoiler.txt 2>/dev/null | head -1)
  if grep -q "Finished run" "$dir/gen.log" && [ -n "$sfc" ] && [ -n "$spoiler" ] \
     && "$PYTHON" "$HERE/verify_seed.py" "$sfc" "$spoiler" > "$dir/verify.txt"; then
    ok=$((ok + 1))
    hash=$(grep -m1 '^Hash:' "$spoiler" | sed 's/^Hash: *//')
    final="$OUT/$ok"
    rm -rf "$final"
    mv "$dir" "$final"
    echo "try $tries: OK -> $final ($hash)"
  else
    reason=$(grep -o -m1 'Money balancing is off\|Cannot beat game\|Not all progression items reachable\|RecursionError\|Infinite loop[^"]*"[^"]*"\|[A-Za-z]*Error' "$dir/gen.log" | head -1)
    [ -z "$reason" ] && [ -f "$dir/verify.txt" ] && reason="failed verify_seed.py"
    echo "try $tries: rerolling (${reason:-unknown failure, see gen.log})"
    rm -rf "$dir"
  fi
done
echo "$ok/$COUNT seeds in $OUT after $tries tries"
[ "$ok" -eq "$COUNT" ]

#!/usr/bin/env bash
# Builds every example spec as an HTML draft and as a PPTX, renders the drafts, and lints the PPTX.
# Fails on: a spec/fact error, a draft slide whose text does not fit, or a lint error.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
S="$HERE/scripts"
OUT="${1:-$HERE/out/smoke}"
mkdir -p "$OUT"
fail=0
for f in "$HERE"/assets/examples/*.json; do
  b=$(basename "$f" .json)
  case "$b" in chart-*) continue ;; esac
  echo "== $b"
  python3 "$S/build_html.py" "$f" -o "$OUT/$b.html" || { echo "FAIL html build $b"; fail=1; continue; }
  if ! python3 "$S/render_html.py" "$OUT/$b.html" "$OUT/render-$b"; then echo "FAIL draft fit $b"; fail=1; fi
  python3 "$S/build_deck.py" "$f" -o "$OUT/$b.pptx" || { rc=$?; [ $rc -eq 3 ] || { echo "FAIL pptx build $b"; fail=1; continue; }; }
  if ! python3 "$S/lint_deck.py" "$OUT/$b.pptx" > "$OUT/$b.lint.txt"; then echo "FAIL lint errors $b"; cat "$OUT/$b.lint.txt"; fail=1; fi
done
for c in "$HERE"/assets/examples/chart-*.json; do
  python3 "$S/chart_images.py" "$c" -o "$OUT/$(basename "$c" .json).png" || { echo "FAIL chart $c"; fail=1; }
done
[ $fail -eq 0 ] && echo "ALL SMOKE TESTS PASSED" || { echo "SMOKE TESTS FAILED"; exit 1; }

#!/usr/bin/env bash
# Builds every example spec as an HTML draft and as a PPTX, renders both, lints the PPTX, and checks the
# release gate. Fails on: a spec/fact error, a draft slide whose text does not fit, a PPTX text-fit failure
# (exit 3), a release blocker under --strict, a lint error, or a PPTX that will not render.
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
S="$HERE/scripts"
OUT="${1:-$HERE/out/smoke}"
mkdir -p "$OUT"
fail=0
have_soffice=0; command -v soffice >/dev/null 2>&1 && command -v pdftoppm >/dev/null 2>&1 && have_soffice=1
for f in "$HERE"/assets/examples/*.json; do
  b=$(basename "$f" .json)
  case "$b" in chart-*) continue ;; esac
  echo "== $b"
  python3 "$S/build_html.py" "$f" --strict -o "$OUT/$b.html" > "$OUT/$b.html.log" || { echo "FAIL html build $b"; cat "$OUT/$b.html.log"; fail=1; continue; }
  python3 "$S/render_html.py" "$OUT/$b.html" "$OUT/render-$b" || { echo "FAIL draft fit $b"; fail=1; }
  python3 "$S/build_deck.py" "$f" -o "$OUT/$b.pptx" --strict > "$OUT/$b.pptx.log"; rc=$?
  if [ $rc -ne 0 ]; then echo "FAIL pptx build $b (exit $rc)"; cat "$OUT/$b.pptx.log"; fail=1; continue; fi
  python3 "$S/lint_deck.py" "$OUT/$b.pptx" > "$OUT/$b.lint.txt" || { echo "FAIL lint errors $b"; cat "$OUT/$b.lint.txt"; fail=1; }
  if [ $have_soffice -eq 1 ]; then
    python3 "$S/render.py" "$OUT/$b.pptx" "$OUT/render-pptx-$b" > /dev/null 2>&1 && ls "$OUT/render-pptx-$b"/slide-*.png > /dev/null 2>&1 \
      || { echo "FAIL pptx render $b"; fail=1; }
  fi
done
# Creative concept demonstrations use custom HTML compositions. Native PPTX needs
# deliberate reconstruction after approval, so do not count placeholder builds as success.
for f in "$HERE"/assets/creative-examples/*.json "$HERE"/assets/forward-tests/*.json; do
  [ -f "$f" ] || continue
  b="creative-$(basename "$f" .json)"
  python3 "$S/build_html.py" "$f" --strict -o "$OUT/$b.html" > "$OUT/$b.html.log" \
    || { echo "FAIL creative html $b"; cat "$OUT/$b.html.log"; fail=1; continue; }
  python3 "$S/render_html.py" "$OUT/$b.html" "$OUT/render-$b" \
    || { echo "FAIL creative fit $b"; fail=1; }
done
# Demonstrate deliberate native reconstruction of one approved-concept fixture.
python3 "$HERE/assets/forward-tests/rebuild_brand.py" -o "$OUT/creative-brand-native.pptx" > "$OUT/creative-brand-native.log" \
  || { cat "$OUT/creative-brand-native.log"; fail=1; }
if [ -f "$OUT/creative-brand-native.pptx" ]; then
  python3 "$S/lint_deck.py" "$OUT/creative-brand-native.pptx" > "$OUT/creative-brand-native.lint.txt" || fail=1
  if [ $have_soffice -eq 1 ]; then
    python3 "$S/render.py" "$OUT/creative-brand-native.pptx" "$OUT/render-pptx-creative-brand-native" > /dev/null 2>&1 || fail=1
  fi
fi
for c in "$HERE"/assets/examples/chart-*.json; do
  python3 "$S/chart_images.py" "$c" -o "$OUT/$(basename "$c" .json).png" > /dev/null || { echo "FAIL chart $c"; fail=1; }
done
# Fixed source packets: missing evidence must render as a draft and refuse final output.
for f in "$HERE"/assets/benchmarks/*.json; do
  b="benchmark-$(basename "$f" .json)"
  if [ "$b" = benchmark-incomplete ]; then
    python3 "$S/build_html.py" "$f" -o "$OUT/$b.html" > "$OUT/$b.html.log" || fail=1
    python3 "$S/build_html.py" "$f" --strict -o "$OUT/$b-final.html" > "$OUT/$b.strict.log"; rc=$?
    if [ "$rc" -ne 2 ] || [ -f "$OUT/$b-final.html" ]; then echo "FAIL incomplete evidence released"; fail=1; fi
  else
    python3 "$S/build_html.py" "$f" --strict -o "$OUT/$b.html" > "$OUT/$b.html.log" || { cat "$OUT/$b.html.log"; fail=1; continue; }
    python3 "$S/build_deck.py" "$f" --strict -o "$OUT/$b.pptx" > "$OUT/$b.pptx.log" || { cat "$OUT/$b.pptx.log"; fail=1; continue; }
    python3 "$S/lint_deck.py" "$OUT/$b.pptx" --spec "$f" > "$OUT/$b.lint.txt" || fail=1
    if [ $have_soffice -eq 1 ]; then
      python3 "$S/render.py" "$OUT/$b.pptx" "$OUT/render-pptx-$b" > /dev/null 2>&1 || fail=1
    fi
  fi
  python3 "$S/render_html.py" "$OUT/$b.html" "$OUT/render-$b" || { echo "FAIL benchmark fit $b"; fail=1; }
done
python3 -m unittest discover -s "$HERE/tests" -p "test_*.py" -q || { echo "FAIL unit tests"; fail=1; }
[ $have_soffice -eq 1 ] || echo "note: LibreOffice/poppler not found; PPTX renders skipped"
[ $fail -eq 0 ] && echo "ALL SMOKE TESTS PASSED" || { echo "SMOKE TESTS FAILED"; exit 1; }

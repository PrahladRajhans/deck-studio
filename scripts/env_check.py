#!/usr/bin/env python3
"""Report what this machine can measure and render, before trusting fit checks.

    python3 env_check.py [--direction consulting-navy]

For each font a direction uses: which file the fit measurement uses (exact metric clone, substitute,
or Pillow's default bitmap font, which makes fit estimates unreliable). Also reports Playwright
Chromium (HTML drafts), LibreOffice and poppler (PPTX renders). Fonts on the machine that finally
opens the deck may differ again: check wrapping there too.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import DIRECTIONS, FONT_FALLBACKS, _FONT_FILES, _find_font_file, _pil_font  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--direction", help="check only this direction's fonts")
    a = ap.parse_args(argv)
    dirs = [a.direction] if a.direction else list(DIRECTIONS)
    fonts = sorted({DIRECTIONS[d][k] for d in dirs for k in ("heading_font", "body_font")})
    print("Fonts (fit measurement):")
    for fam in fonts:
        for bold in (False, True):
            want = _FONT_FILES.get((fam.lower(), bold))
            path = _find_font_file(want) if want else None
            _pil_font(fam, bold, 20)
            if path:
                kind = "close clone (check wrapping by eye)" if fam.lower() == "palatino linotype" else "metric clone"
                state = f"{kind} {os.path.basename(path)}"
            else:
                state = f"SUBSTITUTE: {FONT_FALLBACKS.get((fam.lower(), bold), 'unknown')}"
            print(f"  {fam}{' bold' if bold else ''}: {state}")
    print("Renderers:")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            b.close()
        print("  Playwright Chromium: ok (HTML drafts render)")
    except Exception as e:  # noqa: BLE001
        print(f"  Playwright Chromium: MISSING ({type(e).__name__}); run: python -m playwright install chromium")
    print(f"  LibreOffice: {'ok' if shutil.which('soffice') else 'MISSING (PPTX renders skipped)'}")
    print(f"  poppler (pdftoppm): {'ok' if shutil.which('pdftoppm') else 'MISSING'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

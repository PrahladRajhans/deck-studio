#!/usr/bin/env python3
"""Screenshot every slide of an HTML draft deck and report text that does not fit.

    python3 render_html.py out/deck.html out/render [--scale 0.5] [--only 3,7]

Writes slide-01.png ... and contact-sheet.png, then prints one line per slide that carries a
"does not fit" flag (title over its line limit, body text below the floor, or content off the slide).
Exit code 3 when any slide is flagged. Needs Playwright with Chromium (pre-installed in Claude's
workspace; elsewhere: pip install playwright && playwright install chromium).
"""
from __future__ import annotations

import argparse
import os
import sys

from PIL import Image, ImageDraw


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("outdir")
    ap.add_argument("--scale", type=float, default=0.5, help="screenshot scale (0.5 = 960x540 PNGs)")
    ap.add_argument("--only", help="1-based slide numbers to capture, e.g. 2,5")
    a = ap.parse_args(argv)
    from playwright.sync_api import sync_playwright

    os.makedirs(a.outdir, exist_ok=True)
    url = "file://" + os.path.abspath(a.html)
    shots, report = [], []
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=a.scale)
        pg.goto(url)
        pg.add_style_tag(content="#hint,#progress{display:none!important}")
        pg.wait_for_function("window.__deckReport !== undefined", timeout=20000)
        report = pg.evaluate("window.__deckReport")
        n = len(report)
        keep = {int(x) for x in a.only.split(",")} if a.only else set(range(1, n + 1))
        for k in range(1, n + 1):
            if k not in keep:
                continue
            pg.evaluate(f"show({k - 1})")
            pg.wait_for_timeout(60)
            path = os.path.join(a.outdir, f"slide-{k:02d}.png")
            pg.screenshot(path=path)
            shots.append(path)
        br.close()
    if shots:
        ims = [Image.open(s) for s in shots]
        w, h = ims[0].size
        cols = 4 if len(ims) > 6 else 3
        tw, th = 480, int(480 * h / w)
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (tw + 16) + 16, rows * (th + 40) + 16), "#e9e9e9")
        d = ImageDraw.Draw(sheet)
        for j, (im, path) in enumerate(zip(ims, shots)):
            x, y = 16 + (j % cols) * (tw + 16), 16 + (j // cols) * (th + 40)
            sheet.paste(im.convert("RGB").resize((tw, th)), (x, y))
            d.text((x, y + th + 6), os.path.basename(path)[6:8], fill="#333")
        sheet.save(os.path.join(a.outdir, "contact-sheet.png"))
    bad = [r for r in report if r["overflow"]]
    print(f"rendered {len(shots)} slides to {a.outdir} (contact-sheet.png)")
    for r in bad:
        print(f"  error slide {r['n']}: does not fit ({r['overflow']})")
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

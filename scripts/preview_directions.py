#!/usr/bin/env python3
"""Show, don't tell: render the same few slides of a spec in several art directions, side by side.

  python preview_directions.py spec.json --directions consulting-navy,editorial-warm,bold-signal \
        --slides 1,4 -o previews/

Writes one PNG per direction plus previews/compare.png (one row per direction, labelled). Send
compare.png to the user and let them pick (or mix: "editorial-warm but with the navy cover").
Drafts preview in HTML (fast, the default). Add --pptx to preview the native PowerPoint build,
which is for the finalise stage, after the user has approved the draft.
Pick three that genuinely differ: one safe for the room, one bolder, one wildcard.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

from execution import Deadline, ExecutionTimeout, positive_seconds, run_bounded

HERE = os.path.dirname(os.path.abspath(__file__))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--directions", required=True)
    ap.add_argument("--slides", default="1,2")
    ap.add_argument("-o", "--out", default="previews")
    ap.add_argument("--pptx", action="store_true", help="preview the PPTX build instead of the HTML draft")
    ap.add_argument('--timeout', type=positive_seconds, default=240, help='seconds per child command')
    ap.add_argument('--budget', type=positive_seconds, default=900, help='total child-command budget')
    a = ap.parse_args(argv)
    deadline = Deadline(a.budget)
    def run(command, **kwargs):
        return run_bounded(command, timeout=deadline.remaining(a.timeout), **kwargs)
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for d in a.directions.split(","):
        d = d.strip()
        rd = os.path.join(a.out, f"{d}_render")
        if a.pptx:
            pptx = os.path.join(a.out, f"{d}.pptx")
            r = run([sys.executable, os.path.join(HERE, "build_deck.py"), a.spec, "-o", pptx,
                                "--direction", d, "--only", a.slides], capture_output=True, text=True)
            if r.returncode not in (0, 3):
                print(r.stdout, r.stderr)
                sys.exit(r.returncode)
            run([sys.executable, os.path.join(HERE, "render.py"), pptx, rd, "--cols",
                            str(len(a.slides.split(",")))], capture_output=True, text=True, check=True)
        else:
            page = os.path.join(a.out, f"{d}.html")
            r = run([sys.executable, os.path.join(HERE, "build_html.py"), a.spec, "-o", page,
                                "--direction", d, "--only", a.slides], capture_output=True, text=True)
            if r.returncode != 0:
                print(r.stdout, r.stderr)
                sys.exit(r.returncode)
            r = run([sys.executable, os.path.join(HERE, "render_html.py"), page, rd],
                               capture_output=True, text=True)
            if r.returncode == 3:
                print(f"  warn  {d}: some text does not fit in this direction:\n{r.stdout}")
            elif r.returncode != 0:
                print(r.stdout, r.stderr)
                sys.exit(r.returncode)
        rows.append((d, sorted(os.path.join(rd, f) for f in os.listdir(rd) if f.startswith("slide-"))))
    from PIL import Image, ImageDraw, ImageFont
    tw = 640
    thumbs = [(d, [Image.open(p).convert("RGB") for p in ps]) for d, ps in rows]
    th = int(thumbs[0][1][0].height * tw / thumbs[0][1][0].width)
    ncol = max(len(t) for _, t in thumbs)
    lab = 34
    sheet = Image.new("RGB", (ncol * (tw + 16) + 16, len(thumbs) * (th + lab + 16) + 16), "#E4E4E4")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    for r, (d, ims) in enumerate(thumbs):
        y = 16 + r * (th + lab + 16)
        draw.text((16, y), d, fill="#222222", font=font)
        for c, im in enumerate(ims):
            sheet.paste(im.resize((tw, th)), (16 + c * (tw + 16), y + lab))
    out = os.path.join(a.out, "compare.png")
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    try:
        main()
    except ExecutionTimeout as exc:
        print(f'preview stopped: {exc}', file=sys.stderr)
        sys.exit(124)

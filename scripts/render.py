#!/usr/bin/env python3
"""Render a .pptx to PNGs (via LibreOffice + pdftoppm) and a labelled contact sheet.

  python render.py deck.pptx [out_dir] [--dpi 110] [--cols 3]

Prints the contact sheet path, then one line per slide image. LOOK at the sheet first, then any
suspicious slide at full size. LibreOffice substitutes fonts it lacks (Calibri->Carlito,
Cambria->Caladea are metric-compatible; others are approximate), so trust fit only for those.
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from execution import Deadline, ExecutionTimeout, positive_seconds, run_bounded


def soffice_bin() -> str:
    for c in ("soffice", "libreoffice", "/Applications/LibreOffice.app/Contents/MacOS/soffice",
              r"C:\Program Files\LibreOffice\program\soffice.exe"):
        p = shutil.which(c) or (c if os.path.exists(c) else None)
        if p:
            return p
    sys.exit("LibreOffice not found: install it (or use PowerPoint's Save As PNG) to render")


def to_pdf(pptx: str, out_dir: str, timeout=240) -> str:
    profile = tempfile.mkdtemp(prefix="lo-profile-", dir=os.environ.get("_DECK_STUDIO_EXEC_CONTEXT"))
    cmd = [soffice_bin(), f"-env:UserInstallation=file://{profile}", "--headless", "--norestore",
           "--convert-to", "pdf", "--outdir", out_dir, pptx]
    try:
        run_bounded(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    pdf = os.path.join(out_dir, os.path.splitext(os.path.basename(pptx))[0] + ".pdf")
    if not os.path.exists(pdf):
        sys.exit("conversion produced no PDF")
    return pdf


def to_pngs(pdf: str, out_dir: str, dpi: int, timeout=240) -> list[str]:
    stem = os.path.join(out_dir, "slide")
    for old in glob.glob(stem + "-*.png"):
        os.remove(old)
    if shutil.which("pdftoppm"):
        run_bounded(["pdftoppm", "-png", "-r", str(dpi), pdf, stem], check=True,
                    stderr=subprocess.DEVNULL, timeout=timeout)
    else:
        import importlib.util
        if importlib.util.find_spec('fitz') is None:
            sys.exit('need pdftoppm (poppler) or optional PyMuPDF to rasterise')
        run_bounded([sys.executable, os.path.abspath(__file__), '--raster-worker', pdf, stem, str(dpi)],
                    timeout=timeout, check=True)
    return sorted(glob.glob(stem + "-*.png"))


def contact_sheet(pngs: list[str], out: str, cols: int = 3, thumb_w: int = 620):
    from PIL import Image, ImageDraw, ImageFont
    thumbs = []
    for p in pngs:
        im = Image.open(p).convert("RGB")
        r = thumb_w / im.width
        thumbs.append(im.resize((thumb_w, int(im.height * r))))
    th = thumbs[0].height
    pad, lab = 16, 26
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (thumb_w + pad) + pad, rows * (th + pad + lab) + pad), "#DDDDDD")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    for i, im in enumerate(thumbs):
        x = pad + (i % cols) * (thumb_w + pad)
        y = pad + (i // cols) * (th + pad + lab)
        draw.text((x, y), f"{i + 1}", fill="#222222", font=font)
        sheet.paste(im, (x, y + lab))
        draw.rectangle([x - 1, y + lab - 1, x + thumb_w, y + lab + th], outline="#999999")
    sheet.save(out)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument('--timeout', type=positive_seconds, default=240, help='seconds per external conversion')
    ap.add_argument('--budget', type=positive_seconds, default=600, help='total conversion/raster budget')
    a = ap.parse_args(argv)
    deadline = Deadline(a.budget)
    out_dir = a.out_dir or os.path.splitext(a.pptx)[0] + "_render"
    os.makedirs(out_dir, exist_ok=True)
    try:
        pdf = to_pdf(os.path.abspath(a.pptx), out_dir, deadline.remaining(a.timeout))
        pngs = to_pngs(pdf, out_dir, a.dpi, deadline.remaining(a.timeout))
    except ExecutionTimeout as exc:
        print(f'render stopped: {exc}', file=sys.stderr)
        return 124
    sheet = contact_sheet(pngs, os.path.join(out_dir, "contact-sheet.png"), a.cols)
    print(f"sheet {os.path.abspath(sheet)}")
    for p in pngs:
        print(f"slide {os.path.abspath(p)}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == '--raster-worker':
        import fitz
        with fitz.open(sys.argv[2]) as document:
            for index, page in enumerate(document, 1):
                page.get_pixmap(dpi=int(sys.argv[4])).save(f'{sys.argv[3]}-{index:02d}.png')
    else:
        sys.exit(main())

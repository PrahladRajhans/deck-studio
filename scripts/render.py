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


def soffice_bin() -> str:
    for c in ("soffice", "libreoffice", "/Applications/LibreOffice.app/Contents/MacOS/soffice",
              r"C:\Program Files\LibreOffice\program\soffice.exe"):
        p = shutil.which(c) or (c if os.path.exists(c) else None)
        if p:
            return p
    sys.exit("LibreOffice not found: install it (or use PowerPoint's Save As PNG) to render")


def to_pdf(pptx: str, out_dir: str) -> str:
    profile = tempfile.mkdtemp(prefix="lo-profile-")
    cmd = [soffice_bin(), f"-env:UserInstallation=file://{profile}", "--headless", "--norestore",
           "--convert-to", "pdf", "--outdir", out_dir, pptx]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    pdf = os.path.join(out_dir, os.path.splitext(os.path.basename(pptx))[0] + ".pdf")
    if not os.path.exists(pdf):
        sys.exit("conversion produced no PDF")
    return pdf


def to_pngs(pdf: str, out_dir: str, dpi: int) -> list[str]:
    stem = os.path.join(out_dir, "slide")
    for old in glob.glob(stem + "-*.png"):
        os.remove(old)
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), pdf, stem], check=True,
                       stderr=subprocess.DEVNULL)
    else:
        try:
            import fitz  # PyMuPDF
        except ImportError:
            sys.exit("need pdftoppm (poppler) or PyMuPDF to rasterise")
        doc = fitz.open(pdf)
        for i, page in enumerate(doc, 1):
            page.get_pixmap(dpi=dpi).save(f"{stem}-{i:02d}.png")
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("out_dir", nargs="?")
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--cols", type=int, default=3)
    a = ap.parse_args()
    out_dir = a.out_dir or os.path.splitext(a.pptx)[0] + "_render"
    os.makedirs(out_dir, exist_ok=True)
    pdf = to_pdf(os.path.abspath(a.pptx), out_dir)
    pngs = to_pngs(pdf, out_dir, a.dpi)
    sheet = contact_sheet(pngs, os.path.join(out_dir, "contact-sheet.png"), a.cols)
    print(f"sheet {os.path.abspath(sheet)}")
    for p in pngs:
        print(f"slide {os.path.abspath(p)}")


if __name__ == "__main__":
    main()

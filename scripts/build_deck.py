#!/usr/bin/env python3
"""deck-studio builder: JSON spec -> editable .pptx with consulting-grade slide grammar.

Usage
  python build_deck.py deck.json -o deck.pptx          # build (+ warnings, exit codes)
  python build_deck.py deck.json --outline             # Gate 1: print the headline track only
  python build_deck.py --schema                        # list slide types and their fields

Exit codes: 0 clean · 2 spec or fact-check error (nothing written) · 3 built, but text had to
shrink below its target or still overflows / placeholders remain (read the warnings).

The model writes CONTENT into the spec. This script owns layout, colour, type and fitting,
so every deck has the same grammar: tracker -> action title -> rule -> exhibit -> so-what ->
source. Numbers live once in `facts`; slides reference them with {=expr|fmt} tokens and
`checks` assert the arithmetic before anything is written.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_MARKER_STYLE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Emu, Inches, Pt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slides_extra import ExtraMixin, _alpha  # noqa: E402
from spec_io import load_spec, report as spec_report  # noqa: E402,F401  (shared loader, no pptx dependency)
from _common import (MARGIN, SLIDE_H, SLIDE_W, PLACEHOLDER, SpecError, fit_size,  # noqa: E402
                     has_figures, is_label_title, render_tokens, resolve_theme, safe_eval,
                     strip_markup, text_height_in, voice_report, wrap_count, DIRECTIONS,
                     slide_seconds, FONT_FALLBACKS)

# Type floors (pt). Projected decks should stay well above these; read-ahead decks may sit near.
FLOOR = dict(title=20, body=12, small=9.5, table=11, label=10)


def _lum(h: str) -> float:
    h = h.lstrip("#")
    return sum(w * int(h[i:i + 2], 16) / 255 for w, i in ((0.2126, 0), (0.7152, 2), (0.0722, 4)))


def _rel_lum(h: str) -> float:
    h = h.lstrip("#")

    def ch(c):
        c = int(c, 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(h[0:2]) + 0.7152 * ch(h[2:4]) + 0.0722 * ch(h[4:6])


def contrast_ratio(a: str, b: str) -> float:
    la, lb = _rel_lum(a), _rel_lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _distinct(a: str, b: str, min_gap: float = 0.12) -> bool:
    """True when two fills differ enough in lightness to read as separate surfaces."""
    return abs(_lum(a) - _lum(b)) >= min_gap


def rgb(hexstr: str) -> RGBColor:
    return RGBColor.from_string(hexstr.lstrip("#").upper())


class Builder(ExtraMixin):
    def __init__(self, spec: dict, spec_dir: str):
        self.spec = spec
        self.spec_dir = spec_dir
        self.t = resolve_theme(spec.get("direction"), spec.get("theme"))
        self.hf = self.t["heading_font"]
        self.bf = self.t["body_font"]
        self.prs = Presentation()
        self.prs.slide_width = Inches(SLIDE_W)
        self.prs.slide_height = Inches(SLIDE_H)
        self.blank = self.prs.slide_layouts[6]
        self.warnings: list[str] = []
        self.shrunk = False
        self.exhibit_no = 0
        self.page_no = 0
        self.talk = spec.get("mode", "document") == "talk"
        self.id_pages: dict = {}   # slide id -> page number, filled by a first pass (see main)
        self.pages_seen: dict = {}
        self.section_no = 0
        self.cur_idx = 0
        self.mode = spec.get("mode", "document")
        self.frame = spec.get("frame") or self.t.get("frame", "classic")
        self.n_sections = sum(1 for sl in spec.get("slides", []) if sl.get("type") == "divider")
        self.type_run: list[str] = []
        self.chart_sigs: dict = {}
        self._fills: list = []

    # ------------------------------------------------------------------ primitives
    def warn(self, msg: str):
        self.warnings.append(f"slide {self.cur_idx}: {msg}")

    def rect(self, slide, x, y, w, h, fill=None, line=None, line_w=0.75, shape=MSO_SHAPE.RECTANGLE,
             name=None):
        shp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        shp.shadow.inherit = False
        if fill:
            self._fills.append((x, y, w, h, fill))
            shp.fill.solid()
            shp.fill.fore_color.rgb = rgb(fill)
        else:
            shp.fill.background()
        if line:
            shp.line.color.rgb = rgb(line)
            shp.line.width = Pt(line_w)
        else:
            shp.line.fill.background()
        if name:
            shp.name = name
        if shp.has_text_frame:
            shp.text_frame.text = ""
        _drop_style(shp)
        return shp

    def line(self, slide, x1, y1, x2, y2, color, width=0.75, name=None):
        ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2),
                                        Inches(y2))
        ln.line.color.rgb = rgb(color)
        ln.line.width = Pt(width)
        if name:
            ln.name = name
        _drop_style(ln)
        return ln

    def _readable(self, color, x, y, w, h, need=3.0):
        """Text too close to what sits behind it (a drawn fill or the slide background) flips to the
        readable neutral: 4.5:1 for body text, 3:1 for large or bold text (WCAG AA)."""
        cx, cy = x + w / 2, y + h / 2
        under = [f for f in self._fills if f[0] <= cx <= f[0] + f[2] and f[1] <= cy <= f[1] + f[3]]
        fill = min(under, key=lambda f: f[2] * f[3])[4] if under else getattr(self, "_bg", None)
        if not fill:
            return color
        try:
            if contrast_ratio(color, fill) >= need:
                return color
            # keep the hue: step the colour darker (on light fills) or lighter (on dark fills) first
            r0, g0, b0 = (int(color[i:i + 2], 16) for i in (0, 2, 4))
            toward_black = _rel_lum(fill) > 0.4
            for k in range(1, 10):
                f = k / 10
                if toward_black:
                    c = (int(r0 * (1 - f)), int(g0 * (1 - f)), int(b0 * (1 - f)))
                else:
                    c = (int(r0 + (255 - r0) * f), int(g0 + (255 - g0) * f), int(b0 + (255 - b0) * f))
                cand = "%02X%02X%02X" % c
                if contrast_ratio(cand, fill) >= need:
                    return cand
            alt = [self.t["ink"], "111111", "FFFFFF", self.t["on_dark"]]
            best = max(alt, key=lambda c: contrast_ratio(c, fill))
            return best if contrast_ratio(best, fill) > contrast_ratio(color, fill) else color
        except (ValueError, IndexError):
            return color

    def _add_runs(self, paragraph, text: str, size, color, font, bold=False, italic=False,
                  spacing=None, caps=False):
        """**bold** and ^^accent^^ markup; everything else plain."""
        for k, seg in enumerate(text.split("^^")):
            seg_color = getattr(self, "_accent_now", self.t["accent"]) if k % 2 == 1 else color
            for i, part in enumerate(seg.split("**")):
                if not part:
                    continue
                run = paragraph.add_run()
                run.text = part.upper() if caps else part
                f = run.font
                f.size = Pt(size)
                f.name = font
                f.bold = bold or (i % 2 == 1) or k % 2 == 1
                f.italic = italic
                f.color.rgb = rgb(seg_color)
                if spacing:
                    run._r.get_or_add_rPr().set("spc", str(int(spacing * 100)))

    def text(self, slide, x, y, w, h, text, size, color, font=None, bold=False, italic=False,
             align="left", anchor="top", min_size=None, max_lines=None, spacing=None, caps=False,
             line_spacing=1.1, para_space=4, name=None, fit=True, bullets=False):
        """Text box with zero padding. Fits text by stepping down to min_size; warns if it can't."""
        font = font or self.bf
        text = "" if text is None else str(text)
        need = 3.0 if (size >= 18 or (bold and size >= 14)) else 4.5
        color = self._readable(color, x, y, w, h, need)
        self._accent_now = self._readable(self.t["accent"], x, y, w, h, need)
        if self.talk and 12 <= size < 18 and name not in SMALL_PRINT:
            # talk decks are projected: body text is 18pt minimum (playbook rule for projected decks)
            size, min_size = 18.0, 18.0
        size_used = size
        if fit and text.strip():
            measure = text if not caps else text.upper()
            size_used, ok = fit_size(measure, font, w - (0.22 if bullets else 0), h, size,
                                     min_size or size, bold, max_lines, line_spacing * 1.045,
                                     para_space)
            if size_used < size - 0.01:
                self.shrunk = True
            if not ok:
                self.warn(f"text does not fit at {size_used}pt (box {w:.2f}x{h:.2f}in): "
                          f"'{strip_markup(text)[:60]}...' -> shorten it or split the slide")
        tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        if name:
            tb.name = name
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE,
                              "bottom": MSO_ANCHOR.BOTTOM}[anchor]
        for i, para in enumerate(text.split("\n")):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER,
                           "right": PP_ALIGN.RIGHT}[align]
            p.line_spacing = line_spacing
            if i > 0:
                p.space_before = Pt(para_space)
            if bullets and para.strip():
                pPr = p._p.get_or_add_pPr()
                pPr.set("marL", str(Emu(Inches(0.22))))
                pPr.set("indent", str(-Emu(Inches(0.22))))
                bu_clr = OxmlElement("a:buClr")
                srgb = OxmlElement("a:srgbClr")
                srgb.set("val", self.t["primary"] if color != self.t["on_dark"] else color)
                bu_clr.append(srgb)
                pPr.append(bu_clr)
                bu = OxmlElement("a:buChar")
                bu.set("char", "•")
                pPr.append(bu)
            self._add_runs(p, para, size_used, color, font, bold, italic, spacing, caps)
        return tb, size_used

    # ------------------------------------------------------------------ chrome
    def new_slide(self, dark=False):
        self._fills = []
        self._bg = self.t["dark"] if dark else self.t["bg"]
        slide = self.prs.slides.add_slide(self.blank)
        bg = slide.background.fill
        bg.solid()
        bg.fore_color.rgb = rgb(self.t["dark"] if dark else self.t["bg"])
        return slide

    def chrome(self, slide, s: dict) -> tuple[float, float]:
        """Tracker, action title, optional subtitle, rule. Returns (body_top, body_bottom)."""
        t = self.t
        self.page_no += 1
        kicker = s.get("kicker") or s.get("section") or ""
        frame = s.get("frame") or self.frame
        if kicker:
            numbered = self.spec.get("number_kickers", not self.talk)
            label = f"{self.section_no:02d}   {kicker}" if (self.section_no and numbered) else kicker
            if frame == "rail":
                kb = self.text(slide, -2.55, 3.5, 5.6, 0.3, label, 10.5, t["muted"], self.bf, bold=True,
                               caps=True, spacing=1.6, fit=False, name="Kicker", align="center")[0]
                kb.rotation = 270
            else:
                self.text(slide, MARGIN, 0.38, 9.5, 0.26, label, 10.5,
                          t["accent"] if frame == "editorial" else t["muted"], self.bf, bold=True,
                          caps=True, spacing=1.4, fit=False, name="Kicker")
        if self.talk and self.n_sections >= 3 and s.get("type") not in ("divider",):
            # quiet step bar: where the audience is in the story (talk mode, 3+ chapters)
            seg, gap = 0.34, 0.06
            x0 = SLIDE_W - MARGIN - self.n_sections * (seg + gap)
            for k in range(self.n_sections):
                self.rect(slide, x0 + k * (seg + gap), 0.45, seg, 0.06,
                          fill=t["accent"] if k + 1 == self.section_no else t["rule"], name="StepBar")
        title = s.get("title", "")
        if s.get("letter") and title:
            title = f"^^{s['letter']}:^^ {title}"
        title_w = SLIDE_W - 2 * MARGIN
        if not title and s.get("type") in ("quote", "statement"):
            # the quote or claim is the headline: no title row, body starts under the kicker
            body_bottom = SLIDE_H - 0.72
            if s.get("so_what"):
                body_bottom = SLIDE_H - 1.5
                self.so_what(slide, s["so_what"], SLIDE_H - 1.36)
            self.footer(slide, s)
            return (1.05 if kicker else 0.7), body_bottom
        tsize0 = s.get("title_size", 28 if frame == "editorial" else (30 if self.talk else 25))
        _, tsize = self.text(slide, MARGIN, 0.7, title_w, 0.92 if tsize0 <= 26 else 1.05, title, tsize0,
                             t["ink"], self.hf, bold=True, min_size=FLOOR["title"], max_lines=2,
                             line_spacing=1.0, name="Headline")
        lines = wrap_count(title, self.hf, tsize, title_w, True)
        title_bottom = 0.7 + lines * tsize * 1.2 / 72.0
        y = title_bottom + 0.06
        if s.get("subtitle"):
            self.text(slide, MARGIN, y, title_w, 0.34, s["subtitle"], 14, t["muted"], self.bf,
                      min_size=12, max_lines=1, name="Subtitle")
            y += 0.38
        rule_y = max(y + 0.08, 1.5)
        if frame in ("classic", "rail") and self.spec.get("title_rule", True):
            self.line(slide, MARGIN, rule_y, SLIDE_W - MARGIN, rule_y, t["rule"], 0.75, name="TitleRule")
        body_top = rule_y + (0.24 if frame in ("classic", "rail") else 0.3)
        body_bottom = SLIDE_H - 0.72
        if s.get("so_what"):
            body_bottom = SLIDE_H - 1.5
            self.so_what(slide, s["so_what"], SLIDE_H - 1.36)
        if s.get("footnotes"):
            body_bottom = self.footnote_block(slide, s["footnotes"],
                                              (SLIDE_H - 1.42) if s.get("so_what") else SLIDE_H - 0.7)
        if s.get("tag"):
            self.provenance_tag(slide, s["tag"], body_top + 0.36 if not s.get("exhibit") else body_top + 0.3)
        self.footer(slide, s)
        return body_top, body_bottom

    def so_what(self, slide, text, y):
        t = self.t
        h = 0.62
        self.rect(slide, MARGIN, y, SLIDE_W - 2 * MARGIN, h, fill=t["panel"], name="SoWhatPanel")
        self.rect(slide, MARGIN, y, SLIDE_W - 2 * MARGIN, 0.045, fill=t["accent"], name="SoWhatRule")
        self.text(slide, MARGIN + 0.22, y + 0.1, 1.3, 0.42, "SO WHAT", 10, t["accent"], self.bf,
                  bold=True, spacing=1.4, anchor="middle", fit=False)
        self.text(slide, MARGIN + 1.45, y + 0.08, SLIDE_W - 2 * MARGIN - 1.7, h - 0.12, text, 14,
                  t["ink"], self.bf, bold=False, min_size=12, max_lines=2, anchor="middle",
                  line_spacing=1.0, name="SoWhat")

    def footer(self, slide, s: dict):
        t = self.t
        src = s.get("source")
        if src:
            src_text = src if src.lower().startswith(("source", "sources", "note")) else f"Source: {src}"
            self.text(slide, MARGIN, SLIDE_H - 0.66, SLIDE_W - 2 * MARGIN - (2.4 if s.get("tag") else 0.8), 0.24,
                      src_text, 9.5,
                      t["muted"], self.bf, min_size=8.5, max_lines=1, name="Source")
        foot = self.spec.get("footer", "")
        if foot:
            self.text(slide, MARGIN, SLIDE_H - 0.36, 9, 0.22, foot, 9, t["muted"], self.bf,
                      fit=False, name="Footer")
        self.text(slide, SLIDE_W - MARGIN - 0.6, SLIDE_H - 0.36, 0.6, 0.22, str(self.page_no), 9.5,
                  t["muted"], self.bf, align="right", fit=False, name="PageNumber")

    def exhibit_label(self, slide, s: dict, x, y, w) -> float:
        label = s.get("exhibit")
        if not label:
            return y
        self.exhibit_no += 1
        self.text(slide, x, y, w, 0.24, f"Exhibit {self.exhibit_no}  ·  {label}", 10, self.t["muted"],
                  self.bf, bold=True, caps=True, spacing=1.0, fit=False, name="ExhibitLabel")
        return y + 0.36

    # ------------------------------------------------------------------ dark slides
    def _gradient_bg(self, slide):
        t = self.t
        if not t.get("gradient_to"):
            return
        fill = slide.background.fill
        fill.gradient()
        fill.gradient_angle = 25
        stops = fill.gradient_stops
        stops[0].color.rgb = rgb(t["dark"])
        stops[0].position = 0.0
        stops[1].color.rgb = rgb(t["gradient_to"])
        stops[1].position = 1.0

    def s_cover(self, s):
        t = self.t
        style = s.get("style") or t.get("cover", "field")
        if style == "minimal":
            return self._cover_minimal(s)
        if style == "split":
            return self._cover_split(s)
        slide = self.new_slide(dark=True)
        if style == "gradient":
            self._gradient_bg(slide)
        x = 0.9
        if s.get("eyebrow"):
            self.text(slide, x, 1.05, 10, 0.3, s["eyebrow"], 12, t["on_dark_muted"], self.bf,
                      bold=True, caps=True, spacing=2, fit=False)
        self.rect(slide, x, 1.55, 0.9, 0.06, fill=t["accent"])
        has_fig = bool(s.get("figure"))
        tw = 7.6 if has_fig else 11.2
        self.text(slide, x, 1.95, tw, 2.5, s.get("title", ""), 38, t["on_dark"], self.hf, bold=True,
                  min_size=26, max_lines=4, line_spacing=1.0, name="Headline")
        if s.get("subtitle"):
            self.text(slide, x, 4.55, tw, 0.9, s["subtitle"], 17, t["on_dark_muted"], self.bf,
                      min_size=13, max_lines=2)
        if has_fig:
            f = s["figure"]
            self.rect(slide, 9.1, 1.95, 3.35, 2.6, fill=t["primary"] if _distinct(t["primary"], t["dark"])
                      else t["accent"])
            self.text(slide, 9.35, 2.2, 2.9, 1.2, f.get("value", ""), 44, t["on_dark"], self.hf,
                      bold=True, min_size=28, max_lines=1, anchor="bottom")
            self.text(slide, 9.35, 3.5, 2.9, 0.9, f.get("label", ""), 13, t["on_dark"], self.bf,
                      min_size=11, max_lines=3)
        meta = s.get("meta") or []
        if isinstance(meta, str):
            meta = [meta]
        self.text(slide, x, 6.15, 11, 0.7, "\n".join(meta), 12, t["on_dark_muted"], self.bf,
                  min_size=10, para_space=2)
        return slide

    def _cover_minimal(self, s):
        t = self.t
        slide = self.new_slide()
        x = 0.9
        if s.get("eyebrow"):
            self.text(slide, x, 1.0, 10, 0.3, s["eyebrow"], 12, t["accent"], self.bf, bold=True, caps=True,
                      spacing=2, fit=False)
        has_fig = bool(s.get("figure"))
        tw = 7.8 if has_fig else 11.4
        self.text(slide, x, 1.55, tw, 3.0, s.get("title", ""), 44, t["ink"], self.hf, bold=True, min_size=28,
                  max_lines=4, line_spacing=1.0, name="Headline")
        if s.get("subtitle"):
            self.text(slide, x, 4.7, tw, 0.9, s["subtitle"], 18, t["muted"], self.bf, min_size=13, max_lines=2)
        if has_fig:
            f = s["figure"]
            self.text(slide, 9.0, 1.7, 3.6, 1.4, f.get("value", ""), 60, t["accent"], self.hf, bold=True,
                      min_size=32, max_lines=1, anchor="bottom")
            self.text(slide, 9.0, 3.2, 3.5, 1.1, f.get("label", ""), 14, t["ink"], self.bf, min_size=11,
                      max_lines=3)
        meta = s.get("meta") or []
        meta = [meta] if isinstance(meta, str) else meta
        self.line(slide, x, 6.0, SLIDE_W - 0.9, 6.0, t["rule"], 0.75)
        self.text(slide, x, 6.15, 11, 0.7, "   ·   ".join(meta), 12, t["muted"], self.bf, min_size=10,
                  max_lines=1)
        return slide

    def _cover_split(self, s):
        t = self.t
        slide = self.new_slide()
        pw = 7.4
        self.rect(slide, 0, 0, pw, SLIDE_H, fill=t["dark"])
        x = 0.8
        if s.get("eyebrow"):
            self.text(slide, x, 1.0, pw - 1.4, 0.3, s["eyebrow"], 12, t["on_dark_muted"], self.bf, bold=True,
                      caps=True, spacing=2, fit=False)
        self.text(slide, x, 1.5, pw - 1.4, 3.2, s.get("title", ""), 38, t["on_dark"], self.hf, bold=True,
                  min_size=24, max_lines=5, line_spacing=1.0, name="Headline")
        if s.get("subtitle"):
            self.text(slide, x, 4.85, pw - 1.4, 0.9, s["subtitle"], 16, t["on_dark_muted"], self.bf, min_size=12,
                      max_lines=2)
        meta = s.get("meta") or []
        meta = [meta] if isinstance(meta, str) else meta
        self.text(slide, x, 6.15, pw - 1.4, 0.7, "\n".join(meta), 12, t["on_dark_muted"], self.bf, min_size=10,
                  para_space=2)
        if s.get("image"):
            self._picture(slide, s["image"], pw, 0, SLIDE_W - pw, SLIDE_H, alt=s.get("alt", ""))
        elif s.get("figure"):
            f = s["figure"]
            self.text(slide, pw + 0.6, 2.2, SLIDE_W - pw - 1.2, 1.5, f.get("value", ""), 60, t["accent"], self.hf,
                      bold=True, min_size=32, max_lines=1, anchor="bottom")
            self.text(slide, pw + 0.6, 3.8, SLIDE_W - pw - 1.2, 1.2, f.get("label", ""), 16, t["ink"], self.bf,
                      min_size=12, max_lines=3)
        return slide

    def s_divider(self, s):
        t = self.t
        num = s.get("number", self.section_no + 1)
        try:
            self.section_no = int(num)
            label = f"{self.section_no:02d}"
        except (TypeError, ValueError):
            label = str(num)
        slide = self.new_slide(dark=True)
        if self.t.get("cover") == "gradient":
            self._gradient_bg(slide)
        if self.talk and not s.get("number"):
            # talk mode: only the audience's next question on the divider
            self.text(slide, 0.9, 1.2, 11.5, 5.0, s.get("title", ""), 44, t["on_dark"], self.hf, bold=True,
                      min_size=28, max_lines=3, line_spacing=1.02, anchor="middle", name="Headline")
            return slide
        self.text(slide, 0.9, 1.6, 4, 1.6, label, 88, t["accent"], self.hf,
                  bold=True, fit=False)
        self.rect(slide, 0.9, 3.45, 0.9, 0.06, fill=t["accent"])
        self.text(slide, 0.9, 3.75, 11.2, 1.8, s.get("title", ""), 34, t["on_dark"], self.hf, bold=True,
                  min_size=24, max_lines=3, line_spacing=1.0, name="Headline")
        if s.get("subtitle"):
            self.text(slide, 0.9, 5.55, 11, 0.8, s["subtitle"], 16, t["on_dark_muted"], self.bf,
                      min_size=12, max_lines=2)
        return slide

    def s_closing(self, s):
        t = self.t
        slide = self.new_slide(dark=True)
        self.text(slide, 0.9, 1.2, 7.4, 2.4, s.get("title", ""), 34, t["on_dark"], self.hf, bold=True,
                  min_size=24, max_lines=4, line_spacing=1.0, name="Headline")
        if s.get("ask"):
            self.text(slide, 0.9, 3.75, 7.4, 0.3, s.get("ask_label", "Next step"), 12, t["accent"], self.bf,
                      bold=True, caps=True, spacing=1.6, fit=False)
            self.text(slide, 0.9, 4.15, 7.4, 1.3, s["ask"], 20, t["on_dark"], self.bf, min_size=14,
                      max_lines=3)
        if s.get("figure"):
            f = s["figure"]
            self.rect(slide, 9.1, 1.2, 3.35, 2.6, fill=t["accent"])
            self.text(slide, 9.35, 1.45, 2.9, 1.2, f.get("value", ""), 44, t["on_dark"], self.hf,
                      bold=True, min_size=28, max_lines=1, anchor="bottom")
            self.text(slide, 9.35, 2.75, 2.9, 0.9, f.get("label", ""), 13, t["on_dark"], self.bf,
                      min_size=11, max_lines=3)
        lines = s.get("lines") or []
        self.text(slide, 0.9, 6.0, 11, 0.8, "\n".join(lines), 12, t["on_dark_muted"], self.bf,
                  min_size=10, para_space=2)
        return slide

    def s_agenda(self, s):
        """Numbered agenda spine; re-use per chapter with `active` set to light up one chapter."""
        t = self.t
        slide = self.new_slide()
        self.page_no += 1
        self.rect(slide, 0, 0, 3.0, SLIDE_H, fill=t["panel"])
        tb, _ = self.text(slide, 0.6, 0.9, 2.2, 1.0, s.get("title", "Contents"), 30, t["ink"], self.hf,
                          bold=True, fit=False, name="Headline")
        self.rect(slide, 3.0, 0, SLIDE_W - 3.0, SLIDE_H, fill=t["dark"])
        items = s.get("items", [])
        active = s.get("active")
        n = max(1, len(items))
        top, bottom = 1.0, SLIDE_H - 0.9
        step = min(1.25, (bottom - top) / n)
        for i, it in enumerate(items):
            y = top + i * step
            on = active is None or active == i + 1
            col = t["accent"] if (active == i + 1) else (t["on_dark"] if on else t["grey"])
            self.text(slide, 3.7, y, 1.3, step - 0.1, f"{i + 1:02d}", 34, col, self.hf, bold=True,
                      fit=False)
            self.line(slide, 5.05, y + 0.18, 5.05, y + step - 0.25, col, 1.0)
            label = it if isinstance(it, str) else it.get("label", "")
            self.text(slide, 5.35, y + 0.08, 7.2, step - 0.2, label, 18, col, self.bf, bold=on,
                      min_size=13, max_lines=2)
        self.text(slide, SLIDE_W - MARGIN - 0.6, SLIDE_H - 0.36, 0.6, 0.22, str(self.page_no), 9.5,
                  t["on_dark_muted"], self.bf, align="right", fit=False)
        return slide

    # ------------------------------------------------------------------ light slides
    def _body(self, s):
        slide = self.new_slide()
        top, bottom = self.chrome(slide, s)
        return slide, top, bottom

    def s_exec_summary(self, s):
        t = self.t
        slide, top, bottom = self._body(s)
        rows = s.get("rows", [])
        n = max(1, len(rows))
        gap = 0.12
        rh = min(1.25, (bottom - top - gap * (n - 1)) / n)
        w = SLIDE_W - 2 * MARGIN
        for i, r in enumerate(rows):
            y = top + i * (rh + gap)
            hl = r.get("highlight")
            self.rect(slide, MARGIN, y, 0.5, rh, fill=t["accent"] if hl else t["primary"])
            self.text(slide, MARGIN, y, 0.5, rh, str(i + 1), 18, t["on_dark"], self.hf, bold=True,
                      align="center", anchor="middle", fit=False)
            pages = r.get("pages")
            tw = w - 0.75 - (1.1 if pages else 0)
            self.text(slide, MARGIN + 0.7, y + 0.04, tw, rh * 0.5, r.get("claim", ""), 16, t["ink"],
                      self.bf, bold=True, min_size=12.5, max_lines=2, anchor="middle")
            self.text(slide, MARGIN + 0.7, y + rh * 0.52, tw, rh * 0.46, r.get("detail", ""), 13,
                      t["muted"], self.bf, min_size=11, max_lines=2)
            if pages:
                self.text(slide, SLIDE_W - MARGIN - 1.0, y, 1.0, rh, f"→ {pages}", 11, t["muted"],
                          self.bf, align="right", anchor="middle", fit=False)
            if i < n - 1:
                self.line(slide, MARGIN + 0.7, y + rh + gap / 2, SLIDE_W - MARGIN, y + rh + gap / 2,
                          t["rule"], 0.5)
        return slide

    def _side_panel(self, slide, side, x, y, w, h):
        t = self.t
        body_ = "\n".join(side.get("points", []))
        bs = 18 if self.talk else 14
        need = 0.62 + text_height_in(body_, self.bf, bs, w - 0.72, line_spacing=1.08 * 1.045,
                                     para_space_pt=9) + 0.4
        h = min(h, max(2.2, need))
        self.rect(slide, x, y, w, h, fill=t["panel"], name="SidePanel")
        heading = side.get("heading", "What this means")
        self.text(slide, x + 0.25, y + 0.22, w - 0.5, 0.3, heading, 11, t["accent"], self.bf, bold=True,
                  caps=True, spacing=1.2, fit=False)
        pts = side.get("points", [])
        body = "\n".join(pts)
        self.text(slide, x + 0.25, y + 0.62, w - 0.5, h - 0.85, body, 14, t["ink"], self.bf,
                  min_size=11.5, para_space=9, line_spacing=1.08, bullets=True)

    def s_chart(self, s):
        t = self.t
        slide, top, bottom = self._body(s)
        side = s.get("side")
        w_all = SLIDE_W - 2 * MARGIN
        side_w = 3.9 if side else 0
        cw = w_all - side_w - (0.35 if side else 0)
        y = self.exhibit_label(slide, s, MARGIN, top, cw)
        ch = s["chart"]
        kind = ch.get("kind", "column")
        cats = [str(c) for c in ch.get("categories", [])]
        wf = None
        if kind == "scatter":
            return self._scatter(slide, s, ch, y, cw, bottom, side, side_w, top)
        if kind == "waterfall":
            wf = self._waterfall_series(ch, cats)
            series = wf["series"]
        elif kind == "range":
            lo, hi = list(ch["low"]), list(ch["high"])
            if len(lo) != len(cats) or len(hi) != len(cats):
                raise SpecError(f"slide {self.cur_idx}: range chart needs low and high per category")
            series = [{"name": "base", "values": lo},
                      {"name": ch.get("name", "Range"), "values": [h - l for l, h in zip(lo, hi)]}]
            wf = {"series": series, "range": (lo, hi)}
        else:
            series = list(ch["series"])
            if kind == "line" and ch.get("target") is not None:
                series.append({"name": ch.get("target_label", "Target"),
                               "values": [ch["target"]] * len(cats), "_target": True})
            self._check_series(series, cats)
        data = CategoryChartData()
        data.categories = cats
        for se in series:
            vals = se["values"]
            if len(vals) != len(cats):
                raise SpecError(f"slide {self.cur_idx}: series '{se.get('name')}' has {len(vals)} values "
                                f"for {len(cats)} categories")
            data.add_series(se.get("name", ""), vals)
        ctype = {"waterfall": XL_CHART_TYPE.COLUMN_STACKED, "range": XL_CHART_TYPE.BAR_STACKED, "column": XL_CHART_TYPE.COLUMN_CLUSTERED, "bar": XL_CHART_TYPE.BAR_CLUSTERED,
                 "stacked": XL_CHART_TYPE.COLUMN_STACKED, "stacked_bar": XL_CHART_TYPE.BAR_STACKED,
                 "line": XL_CHART_TYPE.LINE_MARKERS, "doughnut": XL_CHART_TYPE.DOUGHNUT,
                 "pie": XL_CHART_TYPE.PIE, "area": XL_CHART_TYPE.AREA}[kind]
        gf = slide.shapes.add_chart(ctype, Inches(MARGIN), Inches(y), Inches(cw), Inches(bottom - y),
                                    data)
        gf.name = "Exhibit chart"
        alt = ch.get("alt") or (f"{kind} chart: {s.get('exhibit', '')} for {', '.join(cats)}; " +
                                "; ".join(f"{se.get('name', '')}: {', '.join(str(v) for v in se['values'])}"
                                          for se in series))
        gf._element.xpath("./p:nvGraphicFramePr/p:cNvPr")[0].set("descr", alt[:900])
        chart = gf.chart
        chart.font.size = Pt(12)
        chart.font.name = self.bf
        chart.font.color.rgb = rgb(t["muted"])
        if wf and kind == "range":
            self._style_range(chart, wf, ch, cats)
            gf.chart.has_title = False
            if side:
                self._side_panel(slide, side, SLIDE_W - MARGIN - side_w, top, side_w, bottom - top)
            return slide
        if wf:
            self._style_waterfall(chart, wf, ch, cats)
            gf.chart.has_title = False
            if side:
                self._side_panel(slide, side, SLIDE_W - MARGIN - side_w, top, side_w, bottom - top)
            return slide
        multi = len(series) > 1
        round_kind = kind in ("doughnut", "pie")
        chart.has_legend = multi or round_kind
        if chart.has_legend:
            chart.legend.position = XL_LEGEND_POSITION.RIGHT
            chart.legend.include_in_layout = False
            chart.legend.font.size = Pt(12)
        plot = chart.plots[0]
        nf = ch.get("number_format", "General")
        hl = ch.get("highlight")
        if isinstance(hl, (int, str)):
            hl = [hl]
        hl_idx = set()
        for h in hl or []:
            if isinstance(h, int):
                hl_idx.add(h)
            elif h in cats:
                hl_idx.add(cats.index(h))
        palette = [t["primary"], t["grey"], t["muted"], t["rule"], t["accent"]]
        if round_kind:
            # one accent, one meaning: only a highlighted slice gets the accent
            ramp = [t["primary"], t["grey"], t["muted"], t["rule"], t["panel"]]
            pts = plot.series[0].points
            for i in range(len(cats)):
                pts[i].format.fill.solid()
                pts[i].format.fill.fore_color.rgb = rgb(t["accent"] if i in hl_idx else ramp[i % len(ramp)])
            plot.has_data_labels = True
            dl = plot.data_labels
            dl.number_format = nf
            dl.number_format_is_linked = nf == "General"
            dl.font.size = Pt(12)
            dl.font.color.rgb = rgb("FFFFFF")
        else:
            if kind in ("column", "bar", "stacked", "stacked_bar"):
                plot.gap_width = 70
                if kind in ("stacked", "stacked_bar"):
                    plot.overlap = 100
            for si, se in enumerate(plot.series):
                col = t["primary"] if not multi else palette[si % len(palette)]
                if kind == "line":
                    is_target = si < len(series) and series[si].get("_target")
                    se.format.line.color.rgb = rgb(t["muted"] if is_target else col)
                    se.format.line.width = Pt(1.5 if is_target else 2.5)
                    se.smooth = bool(ch.get("smooth")) and not is_target
                    if is_target:
                        se.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
                        se.marker.style = XL_MARKER_STYLE.NONE
                    se.marker.format.fill.solid()
                    se.marker.format.fill.fore_color.rgb = rgb(col)
                    se.marker.format.line.color.rgb = rgb(col)
                else:
                    se.format.fill.solid()
                    se.format.fill.fore_color.rgb = rgb(col)
                    if not multi:
                        base = t["grey"] if hl_idx else t["primary"]
                        for i in range(len(cats)):
                            p = se.points[i]
                            p.format.fill.solid()
                            p.format.fill.fore_color.rgb = rgb(t["accent"] if i in hl_idx else base)
            show_vals = ch.get("show_values", not multi or kind in ("stacked", "stacked_bar"))
            if show_vals:
                plot.has_data_labels = True
                dl = plot.data_labels
                dl.number_format = nf
                dl.number_format_is_linked = nf == "General"
                dl.font.size = Pt(12)
                dl.font.color.rgb = rgb(t["ink"] if kind not in ("stacked", "stacked_bar") else "FFFFFF")
                if kind in ("stacked", "stacked_bar"):
                    dl.position = XL_LABEL_POSITION.CENTER
                elif kind == "line":
                    dl.position = XL_LABEL_POSITION.ABOVE
                else:
                    dl.position = XL_LABEL_POSITION.OUTSIDE_END
            va = chart.value_axis
            va.has_major_gridlines = not show_vals
            if va.has_major_gridlines:
                va.major_gridlines.format.line.color.rgb = rgb(t["rule"])
                va.major_gridlines.format.line.width = Pt(0.5)
            va.visible = not show_vals
            va.tick_labels.font.size = Pt(11)
            va.tick_labels.number_format = nf
            va.tick_labels.number_format_is_linked = nf == "General"
            if ch.get("min") is not None:
                va.minimum_scale = ch["min"]
            elif kind != "line":
                va.minimum_scale = min(0, min(min(se["values"]) for se in series))
            if ch.get("max") is not None:
                va.maximum_scale = ch["max"]
            va.format.line.fill.background()
            ca = chart.category_axis
            ca.tick_labels.font.size = Pt(12)
            ca.format.line.color.rgb = rgb(t["rule"])
            ca.has_major_gridlines = False
            if kind in ("bar", "stacked_bar"):
                ca.reverse_order = True  # first category on top, as written in the spec
            if kind == "line" and ch.get("min") not in (None, 0):
                self.warn("line chart axis does not start at zero; say so on the slide")
        if ch.get("unit") and not s.get("exhibit"):
            self.warn("chart has a unit but no exhibit label: put the unit in the label")
        gf.chart.has_title = False
        if side:
            self._side_panel(slide, side, SLIDE_W - MARGIN - side_w, top, side_w, bottom - top)
        return slide

    def _check_series(self, series, cats):
        """Warn about two scales on one axis and about charting the same numbers twice."""
        maxes = [max(abs(v) for v in se["values"]) for se in series if se.get("values")]
        if len(maxes) > 1 and min(maxes) > 0 and max(maxes) / min(maxes) > 10:
            self.warn("series differ in scale by more than 10x on one axis: split into two charts")
        for se in series:
            sig = tuple(round(float(v), 6) for v in se["values"])
            if len(sig) >= 3 and sig in self.chart_sigs and self.chart_sigs[sig] != self.cur_idx:
                self.warn(f"slide {self.chart_sigs[sig]} already charts these numbers: keep the second chart only if it "
                          "shows a different relationship; otherwise state the conclusion in words or KPIs")
            self.chart_sigs.setdefault(sig, self.cur_idx)

    def _style_range(self, chart, wf, ch, cats):
        """Floating bars (football field / valuation ranges / ranges by scenario)."""
        t = self.t
        plot = chart.plots[0]
        plot.gap_width = 70
        plot.overlap = 100
        chart.has_legend = False
        base_s, bar_s = plot.series[0], plot.series[1]
        base_s.format.fill.background()
        base_s.format.line.fill.background()
        lo, hi = wf["range"]
        hl = ch.get("highlight")
        hl = set([hl] if isinstance(hl, int) else (hl or []))
        fmt = ch.get("label_format", "{:,.0f}")
        for i in range(len(cats)):
            p = bar_s.points[i]
            p.format.fill.solid()
            p.format.fill.fore_color.rgb = rgb(t["accent"] if i in hl else t["primary"] if not hl else t["grey"])
            dl = p.data_label
            dl.has_text_frame = True
            dl.text_frame.text = f"{fmt.format(lo[i])} – {fmt.format(hi[i])}"
            dl.position = XL_LABEL_POSITION.CENTER
            for para in dl.text_frame.paragraphs:
                for r in para.runs:
                    r.font.size = Pt(12)
                    r.font.bold = True
                    r.font.color.rgb = rgb("FFFFFF")
        ca = chart.category_axis
        ca.reverse_order = True
        ca.tick_labels.font.size = Pt(12)
        ca.format.line.color.rgb = rgb(t["rule"])
        va = chart.value_axis
        va.has_major_gridlines = True
        va.major_gridlines.format.line.color.rgb = rgb(t["rule"])
        va.major_gridlines.format.line.width = Pt(0.5)
        va.tick_labels.font.size = Pt(11)
        if ch.get("min") is not None:
            va.minimum_scale = ch["min"]
        if ch.get("max") is not None:
            va.maximum_scale = ch["max"]
        va.format.line.fill.background()

    def _scatter(self, slide, s, ch, y, cw, bottom, side, side_w, top):
        """XY scatter with each point labelled by name; highlight one point."""
        from pptx.chart.data import XyChartData
        t = self.t
        pts = ch["points"]
        data = XyChartData()
        se = data.add_series(ch.get("name", ""))
        for p in pts:
            se.add_data_point(p["x"], p["y"])
        gf = slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER, Inches(MARGIN), Inches(y), Inches(cw),
                                    Inches(bottom - y), data)
        gf.name = "Exhibit chart"
        gf._element.xpath("./p:nvGraphicFramePr/p:cNvPr")[0].set(
            "descr", ch.get("alt") or "scatter: " + "; ".join(f"{p.get('label', '')} ({p['x']}, {p['y']})"
                                                             for p in pts)[:900])
        chart = gf.chart
        chart.has_legend = False
        chart.font.size = Pt(11)
        chart.font.name = self.bf
        chart.font.color.rgb = rgb(t["muted"])
        ser = chart.plots[0].series[0]
        ser.format.line.fill.background()
        hl = ch.get("highlight")
        for i, p in enumerate(pts):
            pt = ser.points[i]
            pt.marker.style = XL_MARKER_STYLE.CIRCLE
            pt.marker.size = 11 if i != hl else 15
            pt.marker.format.fill.solid()
            pt.marker.format.fill.fore_color.rgb = rgb(t["accent"] if i == hl else t["primary"])
            pt.marker.format.line.fill.background()
            dl = pt.data_label
            dl.has_text_frame = True
            dl.text_frame.text = p.get("label", "")
            dl.position = XL_LABEL_POSITION.RIGHT
            for para in dl.text_frame.paragraphs:
                for r in para.runs:
                    r.font.size = Pt(11)
                    r.font.color.rgb = rgb(t["ink"])
                    r.font.bold = i == hl
        for ax, title in ((chart.value_axis, ch.get("y_title")), (chart.category_axis, ch.get("x_title"))):
            ax.has_major_gridlines = ax is chart.value_axis
            if ax.has_major_gridlines:
                ax.major_gridlines.format.line.color.rgb = rgb(t["rule"])
                ax.major_gridlines.format.line.width = Pt(0.5)
            ax.format.line.color.rgb = rgb(t["rule"])
            ax.tick_labels.font.size = Pt(11)
            if title:
                ax.has_title = True
                ax.axis_title.text_frame.text = title
                for para in ax.axis_title.text_frame.paragraphs:
                    for r in para.runs:
                        r.font.size = Pt(12)
                        r.font.bold = False
                        r.font.color.rgb = rgb(t["muted"])
        if side:
            self._side_panel(slide, side, SLIDE_W - MARGIN - side_w, top, side_w, bottom - top)
        return slide

    def _waterfall_series(self, ch, cats):
        """Deltas -> invisible base + visible bar. `totals` lists indexes drawn as absolute bars
        (the first value is always a total). Returns series plus per-bar metadata."""
        vals = ch.get("values")
        if vals is None and ch.get("series"):
            vals = ch["series"][0]["values"]
        if not vals or len(vals) != len(cats):
            raise SpecError(f"slide {self.cur_idx}: waterfall needs one value per category")
        totals = set(ch.get("totals", [])) | {0}
        base, bar, kinds, running = [], [], [], 0.0
        for i, v in enumerate(vals):
            if i in totals:
                running = float(v)
                base.append(0.0); bar.append(running); kinds.append("total")
            else:
                start = running
                running += v
                base.append(min(start, running)); bar.append(abs(v))
                kinds.append("up" if v >= 0 else "down")
            if running < 0:
                raise SpecError(f"slide {self.cur_idx}: waterfall goes below zero at '{cats[i]}'; "
                                "this builder draws bridges that stay above zero")
        return {"series": [{"name": "base", "values": base}, {"name": ch.get("name", "Value"), "values": bar}],
                "vals": vals, "kinds": kinds}

    def _style_waterfall(self, chart, wf, ch, cats):
        t = self.t
        plot = chart.plots[0]
        plot.gap_width = 60
        plot.overlap = 100
        chart.has_legend = False
        base_s, bar_s = plot.series[0], plot.series[1]
        base_s.format.fill.background()
        base_s.format.line.fill.background()
        hl = ch.get("highlight")
        hl = set([hl] if isinstance(hl, int) else (hl or []))
        nf = ch.get("number_format", "0.0")
        colour = {"total": t["primary"], "up": t["grey"], "down": t["muted"]}
        for i, k in enumerate(wf["kinds"]):
            p = bar_s.points[i]
            p.format.fill.solid()
            p.format.fill.fore_color.rgb = rgb(t["accent"] if i in hl else colour[k])
            v = wf["vals"][i]
            txt = format(v, nf.replace("0.0", ".1f").replace("0", ".0f")) if nf in ("0", "0.0") else str(v)
            if k == "up":
                txt = "+" + txt
            elif k == "down":
                txt = "(" + txt.lstrip("-") + ")"
            dl = p.data_label
            dl.has_text_frame = True
            dl.text_frame.text = txt
            dl.position = XL_LABEL_POSITION.INSIDE_END if k == "total" else XL_LABEL_POSITION.CENTER
            for para in dl.text_frame.paragraphs:
                for r in para.runs:
                    r.font.size = Pt(12)
                    r.font.bold = k == "total" or i in hl
                    dark_bar = k in ("total", "down") or i in hl
                    r.font.color.rgb = rgb("FFFFFF" if dark_bar else t["ink"])
        va = chart.value_axis
        va.visible = False
        va.has_major_gridlines = False
        va.minimum_scale = 0
        ca = chart.category_axis
        ca.tick_labels.font.size = Pt(12)
        ca.format.line.color.rgb = rgb(t["rule"])

    def _table(self, slide, x, y, w, h, columns, rows, widths=None, highlight_row=None,
               first_col_bold=True, size=13, total_row=False, base_cell=None):
        from visual_elements import table_cell, status_color
        raw_rows = rows
        rows = [[table_cell(v)[0] for v in row] for row in rows]
        t = self.t
        n_rows, n_cols = len(rows) + 1, len(columns)
        widths = widths or [1] * n_cols
        tot = float(sum(widths))
        col_w = [w * c / tot for c in widths]

        def is_num(v):
            s_ = strip_markup(str(v)).replace(",", "").replace("%", "").replace("₹", "").replace("$", "")
            s_ = s_.replace("(", "-").replace(")", "").replace("x", "").replace("pp", "").strip()
            for suf in ("cr", "bn", "mn", "m", "k", "M", "B", "K"):
                if s_.endswith(suf):
                    s_ = s_[: -len(suf)].strip()
            try:
                float(s_)
                return True
            except ValueError:
                return str(v).strip() in ("—", "-", "n/a")

        num_col = [all(is_num(r[c]) for r in rows) and c > 0 for c in range(n_cols)]
        # fit: shrink text size until every cell's lines fit the row height budget
        avail_row_h = (h - 0.5) / max(1, len(rows))
        size_used = size
        while size_used > FLOOR["table"]:
            worst = 0
            for r in rows:
                for c in range(n_cols):
                    worst = max(worst, wrap_count(str(r[c]), self.bf, size_used, col_w[c] - 0.2))
            if worst * size_used * 1.25 / 72 + 0.14 <= avail_row_h and worst <= 2:
                break
            size_used -= 0.5
        if size_used < size:
            self.shrunk = True
        gt = slide.shapes.add_table(n_rows, n_cols, Inches(x), Inches(y), Inches(w), Inches(h))
        gt.name = "Exhibit table"
        tbl = gt.table
        tblPr = tbl._tbl.tblPr
        for attr in ("bandRow", "firstRow"):
            tblPr.set(attr, "0")
        style = tblPr.find(qn("a:tableStyleId"))
        if style is None:
            style = OxmlElement("a:tableStyleId")
            tblPr.append(style)
        style.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"  # "No Style, No Grid"
        for c in range(n_cols):
            tbl.columns[c].width = Inches(col_w[c])
        header_h = 0.42
        tbl.rows[0].height = Inches(header_h)
        body_h = (h - header_h) / max(1, len(rows))
        for r in range(1, n_rows):
            tbl.rows[r].height = Inches(body_h)
        for r in range(n_rows):
            for c in range(n_cols):
                cell = tbl.cell(r, c)
                cell.margin_left = cell.margin_right = Inches(0.08)
                cell.margin_top = cell.margin_bottom = Inches(0.04)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                is_hl = highlight_row is not None and r - 1 == highlight_row
                is_total = total_row and r == n_rows - 1
                bottom_c, bottom_w = t["rule"], 0.5
                if r == 0:
                    bottom_c, bottom_w = t["primary"], 1.5
                if is_total:
                    _set_border(cell, "T", t["primary"], 1.0)
                _set_border(cell, "B", bottom_c, bottom_w)
                for side in ("L", "R"):
                    _set_border(cell, side, None, 0)
                if r != 0 and not is_total:
                    _set_border(cell, "T", None, 0)
                if is_hl:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = rgb(t["panel"])
                else:
                    cell.fill.background()
                tf = cell.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                txt = str(columns[c] if r == 0 else rows[r - 1][c])
                if r > 0 and base_cell == [r - 1, c]:
                    txt += ' (base)'
                p.alignment = PP_ALIGN.RIGHT if num_col[c] else PP_ALIGN.LEFT
                if r == 0:
                    self._add_runs(p, txt, max(FLOOR["label"], size_used - 2.5), t["primary"], self.bf,
                                   bold=True, spacing=0.6, caps=True)
                else:
                    bold = (first_col_bold and c == 0) or is_total or is_hl
                    color = t["accent"] if (is_hl and c == 0) else t["ink"]
                    token = table_cell(raw_rows[r - 1][c])[1]
                    if token:
                        color = status_color(token, t, t["panel"] if is_hl else t["bg"])
                    self._add_runs(p, txt, size_used, color, self.bf, bold=bold)
        return gt

    def s_table(self, s):
        slide, top, bottom = self._body(s)
        w = SLIDE_W - 2 * MARGIN
        side = s.get("side")
        side_w = 3.9 if side else 0
        tw = w - side_w - (0.35 if side else 0)
        y = self.exhibit_label(slide, s, MARGIN, top, tw)
        note_h = 0.35 if s.get("note") else 0
        rows = s["rows"]
        h = min(bottom - y - note_h, 0.42 + len(rows) * 0.62)
        self._table(slide, MARGIN, y, tw, h, s["columns"], rows, s.get("widths"),
                    s.get("highlight_row"), s.get("first_col_bold", True), s.get("size", 13),
                    s.get("total_row", False), s.get("base_cell"))
        if s.get("note"):
            self.text(slide, MARGIN, y + h + 0.08, tw, 0.3, s["note"], 10.5, self.t["muted"], self.bf,
                      min_size=9.5, max_lines=1, name="Caption")
        if side:
            self._side_panel(slide, side, SLIDE_W - MARGIN - side_w, top, side_w, bottom - top)
        return slide

    def s_kpi(self, s):
        t = self.t
        slide, top, bottom = self._body(s)
        items = s["items"]
        n = len(items)
        gap = 0.3
        w = (SLIDE_W - 2 * MARGIN - gap * (n - 1)) / n
        y = self.exhibit_label(slide, s, MARGIN, top, SLIDE_W - 2 * MARGIN)
        h = min(bottom - y, 3.6)
        if bottom - y - h > 1.0:
            y += (bottom - y - h) * 0.35
        hl = s.get("highlight")
        for i, it in enumerate(items):
            x = MARGIN + i * (w + gap)
            is_hl = hl == i
            self.card(slide, x, y, w, h, fill=t["accent"] if is_hl else None)
            vcol = "FFFFFF" if is_hl else t["primary"]
            lcol = "FFFFFF" if is_hl else t["ink"]
            dcol = "FFFFFF" if is_hl else t["muted"]
            self.text(slide, x + 0.3, y + 0.3, w - 0.6, 1.25, it.get("value", ""), 48, vcol, self.hf,
                      bold=True, min_size=28, max_lines=1, anchor="bottom")
            self.text(slide, x + 0.3, y + 1.7, w - 0.6, 0.75, it.get("label", ""), 16, lcol, self.bf,
                      bold=True, min_size=12, max_lines=2)
            dy = 2.5
            if it.get("delta"):
                good = it.get("good", not str(it["delta"]).strip().startswith(("-", "−", "▼")))
                self.chip(slide, x + 0.3, y + 2.42, str(it["delta"]), t["pos"] if good else t["neg"], size=11)
                dy = 2.85
            if it.get("detail"):
                self.text(slide, x + 0.3, y + dy, w - 0.6, h - dy - 0.2, it["detail"], 13, dcol, self.bf,
                          min_size=11, max_lines=4)
        return slide

    def s_cards(self, s):
        t = self.t
        slide, top, bottom = self._body(s)
        items = s["items"]
        n = len(items)
        gap = 0.28
        w = (SLIDE_W - 2 * MARGIN - gap * (n - 1)) / n
        y = self.exhibit_label(slide, s, MARGIN, top, SLIDE_W - 2 * MARGIN)
        h = bottom - y
        hl = s.get("highlight")
        numbered = s.get("numbered", True)
        # equal heights by construction; measure the fullest card for a common body size
        body_sizes = []
        for it in items:
            sz, _ = fit_size(it.get("body", ""), self.bf, w - 0.5, h - 1.75, 18 if self.talk else 16,
                             11.5, para_space_pt=6, line_spacing=1.12)
            body_sizes.append(sz)
        common = min(body_sizes) if body_sizes else 14
        head_h = 0.28 + (0.66 if numbered else 0) + 0.88
        need = head_h + max((text_height_in(it.get("body", ""), self.bf, common, w - 0.5,
                                            line_spacing=1.12 * 1.045, para_space_pt=6)
                             for it in items), default=0) + 0.4
        h = min(h, max(need, h * 0.5))
        for i, it in enumerate(items):
            x = MARGIN + i * (w + gap)
            is_hl = hl == i
            self.rect(slide, x, y, w, h, fill=t["panel"] if not is_hl else t["primary"],
                      name=f"Card {i + 1}")
            fg = "FFFFFF" if is_hl else t["ink"]
            mut = "E6E6E6" if is_hl else t["muted"]
            cy = y + 0.28
            if numbered:
                chip = self.rect(slide, x + 0.25, cy, 0.46, 0.46,
                                 fill=t["accent"] if is_hl else t["primary"], shape=MSO_SHAPE.OVAL)
                self.text(slide, x + 0.25, cy, 0.46, 0.46, str(i + 1), 14, "FFFFFF", self.hf, bold=True,
                          align="center", anchor="middle", fit=False)
                cy += 0.66
            self.text(slide, x + 0.25, cy, w - 0.5, 0.8, it.get("heading", ""), 17, fg, self.hf,
                      bold=True, min_size=13, max_lines=2, line_spacing=1.0)
            self.text(slide, x + 0.25, cy + 0.88, w - 0.5, y + h - cy - 1.05, it.get("body", ""), common,
                      mut if not is_hl else "FFFFFF", self.bf, min_size=11.5, para_space=6,
                      line_spacing=1.12, bullets="\n" in it.get("body", ""))
        return slide

    def s_process(self, s):
        from visual_elements import process_body
        s = dict(s, steps=[dict(st, body=process_body(st)) for st in s.get("steps", [])])
        t = self.t
        slide, top, bottom = self._body(s)
        steps = s["steps"]
        n = len(steps)
        w_all = SLIDE_W - 2 * MARGIN
        y = self.exhibit_label(slide, s, MARGIN, top, w_all)
        overlap = 0.12
        w = (w_all + overlap * (n - 1)) / n
        hl = s.get("highlight")
        # short step bodies would leave the lower half empty: centre the band in the body area
        bsize = 18 if self.talk else 13
        need = max((text_height_in(st.get("body", ""), self.bf, bsize, w - 0.35) for st in steps),
                   default=0) + (1.45 if not any(st.get("label") for st in steps) else 1.6)
        slack = (bottom - y) - need
        if slack > 0.8:
            y += slack * 0.4
        for i, st in enumerate(steps):
            x = MARGIN + i * (w - overlap)
            shape = MSO_SHAPE.PENTAGON if i == 0 else MSO_SHAPE.CHEVRON
            fill = t["accent"] if hl == i else t["primary"]
            shp = self.rect(slide, x, y, w, 0.95, fill=fill, shape=shape, name=f"Step {i + 1}")
            try:
                shp.adjustments[0] = 0.28
            except Exception:
                pass
            pad = 0.3 if i == 0 else 0.45
            self.text(slide, x + pad, y, w - pad - 0.35, 0.95, st.get("heading", ""), 15, "FFFFFF",
                      self.bf, bold=True, min_size=11.5, max_lines=2, anchor="middle", line_spacing=1.0)
            if st.get("label"):
                self.text(slide, x + 0.1, y + 1.12, w - 0.3, 0.3, st["label"], 10.5, t["accent"],
                          self.bf, bold=True, caps=True, spacing=1, fit=False)
            self.text(slide, x + 0.1, y + 1.45, w - 0.35, bottom - y - 1.5, st.get("body", ""), 13,
                      t["ink"], self.bf, min_size=11, para_space=5, line_spacing=1.1,
                      bullets="\n" in st.get("body", ""))
        return slide

    def s_timeline(self, s):
        """Gantt-style roadmap: periods across, workstreams down, bars and milestones."""
        t = self.t
        slide, top, bottom = self._body(s)
        periods = s["periods"]
        rows = s["rows"]
        w_all = SLIDE_W - 2 * MARGIN
        y = self.exhibit_label(slide, s, MARGIN, top, w_all)
        label_w = 2.6
        owner_w = 1.4 if any(r.get("owner") for r in rows) else 0
        grid_x = MARGIN + label_w
        grid_w = w_all - label_w - owner_w
        pw = grid_w / len(periods)
        head_h = 0.4
        rh = min(0.78, (bottom - y - head_h) / max(1, len(rows)))
        for j, p in enumerate(periods):
            self.text(slide, grid_x + j * pw, y, pw, head_h, p, 11, t["primary"], self.bf, bold=True,
                      align="center", anchor="middle", caps=True, spacing=0.6, fit=False)
        if owner_w:
            self.text(slide, grid_x + grid_w, y, owner_w, head_h, "Owner", 11, t["primary"], self.bf,
                      bold=True, align="center", anchor="middle", caps=True, spacing=0.6, fit=False)
        self.line(slide, MARGIN, y + head_h, SLIDE_W - MARGIN, y + head_h, t["primary"], 1.25)
        for j in range(1, len(periods)):
            self.line(slide, grid_x + j * pw, y + head_h, grid_x + j * pw, y + head_h + rh * len(rows),
                      t["rule"], 0.5)
        for i, r in enumerate(rows):
            ry = y + head_h + i * rh
            self.text(slide, MARGIN, ry, label_w - 0.15, rh, r.get("label", ""), 13, t["ink"], self.bf,
                      bold=True, min_size=11, max_lines=2, anchor="middle")
            for b in r.get("bars", []):
                s0, s1 = b["start"], b.get("end", b["start"])
                bx = grid_x + s0 * pw + 0.06
                bw = (s1 - s0 + 1) * pw - 0.12
                if b.get("milestone"):
                    cx = grid_x + (s0 + 0.5) * pw
                    nxt = [o["start"] for o in r.get("bars", []) if o["start"] > s0]
                    limit = grid_x + (min(nxt) if nxt else len(periods)) * pw
                    room = limit - (cx + 0.22) - 0.05
                    below = bool(b.get("label")) and room < 0.9
                    dy = ry + (rh * 0.32 if below else rh / 2) - 0.15
                    self.rect(slide, cx - 0.15, dy, 0.30, 0.30, fill=t["accent"],
                              shape=MSO_SHAPE.DIAMOND)
                    if b.get("label"):
                        if below:  # no room to the right: centre the label under the diamond
                            self.text(slide, cx - pw / 2 + 0.05, dy + 0.32, pw - 0.1, ry + rh - dy - 0.34,
                                      b["label"], 10.5, t["accent"], self.bf, bold=True, min_size=9,
                                      max_lines=1, align="center", name="Caption")
                        else:
                            self.text(slide, cx + 0.22, ry + 0.05, min(pw * 1.6, room), rh - 0.1,
                                      b["label"], 11, t["accent"], self.bf, bold=True, min_size=9.5,
                                      max_lines=2, anchor="middle", name="Caption")
                else:
                    fill = t["accent"] if b.get("highlight") else t["primary"]
                    self.rect(slide, bx, ry + 0.14, bw, rh - 0.28, fill=fill,
                              shape=MSO_SHAPE.ROUNDED_RECTANGLE)
                    if b.get("label"):
                        self.text(slide, bx + 0.1, ry + 0.14, bw - 0.2, rh - 0.28, b["label"], 11,
                                  "FFFFFF", self.bf, bold=True, min_size=9.5, max_lines=2,
                                  anchor="middle", name="Caption")
            if owner_w:
                self.text(slide, grid_x + grid_w, ry, owner_w, rh, r.get("owner", ""), 12, t["muted"],
                          self.bf, align="center", anchor="middle", min_size=10, max_lines=2)
            self.line(slide, MARGIN, ry + rh, SLIDE_W - MARGIN, ry + rh, t["rule"], 0.5)
        return slide

    def s_matrix(self, s):
        t = self.t
        slide, top, bottom = self._body(s)
        side = s.get("side")
        side_w = 3.9 if side else 0
        w_all = SLIDE_W - 2 * MARGIN - side_w - (0.35 if side else 0)
        y = self.exhibit_label(slide, s, MARGIN, top, w_all)
        size = min(w_all - 0.6, bottom - y - 0.45)
        gx = MARGIN + 0.55
        gy = y
        half = size / 2
        q = s.get("quadrants", ["", "", "", ""])
        for k, (qx, qy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)]):
            fill = t["panel"] if k != s.get("highlight_quadrant", 1) else t["rule"]
            self.rect(slide, gx + qx * half, gy + qy * half, half - 0.04, half - 0.04, fill=fill)
            self.text(slide, gx + qx * half + 0.15, gy + qy * half + 0.12, half - 0.35, 0.3, q[k], 11,
                      t["muted"], self.bf, bold=True, caps=True, spacing=0.8, fit=False)
        xa, ya = s.get("x_axis", {}), s.get("y_axis", {})
        self.text(slide, gx, gy + size + 0.05, size, 0.3, f"{xa.get('label', '')}  →", 11.5, t["ink"],
                  self.bf, bold=True, align="center", fit=False)
        lab = slide.shapes.add_textbox(Inches(MARGIN - 0.95 + 0.55), Inches(gy + size / 2 - 0.15),
                                       Inches(size * 0.8), Inches(0.3))
        lab.rotation = 270
        lab.left = Inches(MARGIN + 0.2 - size * 0.4)
        lab.top = Inches(gy + size / 2 - 0.15)
        ltf = lab.text_frame
        ltf.margin_left = ltf.margin_right = 0
        lp = ltf.paragraphs[0]
        lp.alignment = PP_ALIGN.CENTER
        self._add_runs(lp, f"{ya.get('label', '')}  →", 11.5, t["ink"], self.bf, bold=True)
        for it in s.get("items", []):
            cx = gx + it["x"] * size
            cy = gy + (1 - it["y"]) * size
            hl = it.get("highlight")
            r = 0.17
            self.rect(slide, cx - r, cy - r, 2 * r, 2 * r, fill=t["accent"] if hl else t["primary"],
                      shape=MSO_SHAPE.OVAL)
            self.text(slide, cx + 0.22, cy - 0.17, 2.6, 0.36, it["label"], 12.5,
                      t["accent"] if hl else t["ink"], self.bf, bold=bool(hl), min_size=10.5, max_lines=1,
                      anchor="middle")
        if side:
            self._side_panel(slide, side, SLIDE_W - MARGIN - side_w, top, side_w, bottom - top)
        return slide

    def s_options(self, s):
        """Weighted scorecard. Totals are computed here, so they can never disagree with scores."""
        slide, top, bottom = self._body(s)
        crit = s["criteria"]
        opts = s["options"]
        weights = [c.get("weight", 1) for c in crit]
        wsum = float(sum(weights))
        cols = ["Option"] + [f"{c['name']} ({int(round(c.get('weight', 1) / wsum * 100))}%)" for c in crit]
        cols += ["Weighted score"]
        rows, totals = [], []
        for o in opts:
            sc = o["scores"]
            if len(sc) != len(crit):
                raise SpecError(f"slide {self.cur_idx}: option '{o['name']}' has {len(sc)} scores for "
                                f"{len(crit)} criteria")
            tot = sum(a * b for a, b in zip(sc, weights)) / wsum
            totals.append(tot)
            rows.append([o["name"]] + [str(v) for v in sc] + [f"{tot:.1f}"])
        best = max(range(len(totals)), key=lambda i: totals[i])
        rec = s.get("recommended", best)
        if rec != best:
            self.warn(f"recommended option '{opts[rec]['name']}' is not the top weighted score "
                      f"('{opts[best]['name']}'): explain why on the slide or fix the weights")
        w_all = SLIDE_W - 2 * MARGIN
        y = self.exhibit_label(slide, s, MARGIN, top, w_all)
        widths = [2.2] + [1] * len(crit) + [1.2]
        h = min(bottom - y - 0.4, 0.45 + len(rows) * 0.7)
        self._table(slide, MARGIN, y, w_all, h, cols, rows, widths, highlight_row=rec)
        scale = s.get("scale", "Scores 1 (weak) to 5 (strong); weights shown in brackets")
        self.text(slide, MARGIN, y + h + 0.1, w_all, 0.3, scale, 10.5, self.t["muted"], self.bf,
                  fit=False, name="Caption")
        return slide

    def s_quote(self, s):
        t = self.t
        slide, top, bottom = self._body(s)
        self.rect(slide, MARGIN, top + 0.1, 0.9, 0.9, fill=t["primary"], shape=MSO_SHAPE.OVAL)
        self.text(slide, MARGIN, top + 0.12, 0.9, 0.9, "“", 54, "FFFFFF", self.hf, bold=True,
                  align="center", anchor="middle", fit=False, name="QuoteMark")
        self.text(slide, MARGIN + 1.3, top + 0.1, SLIDE_W - 2 * MARGIN - 1.5, bottom - top - 1.0,
                  s.get("quote", ""), 36 if self.talk else 26, t["ink"], self.hf, italic=True, min_size=17,
                  line_spacing=1.1, name=None if s.get("title") else "Headline")
        self.text(slide, MARGIN + 1.3, bottom - 0.75, SLIDE_W - 2 * MARGIN - 1.5, 0.6,
                  f"— {s.get('attribution', '')}", 14, t["muted"], self.bf, bold=True, min_size=11,
                  max_lines=2)
        return slide

    def s_statement(self, s):
        t = self.t
        slide, top, bottom = self._body(s)
        pts = s.get("points", [])
        lw = 6.0 if pts else SLIDE_W - 2 * MARGIN
        self.text(slide, MARGIN, top, lw - 0.2, bottom - top, s.get("claim", ""),
                  36 if self.talk else 30, t["ink"], self.hf, bold=True, min_size=20, line_spacing=1.05,
                  name=None if s.get("title") else "Headline")
        if pts:
            x = MARGIN + lw + 0.5
            w = SLIDE_W - MARGIN - x
            ph = (bottom - top - 0.2 * (len(pts) - 1)) / len(pts)
            for i, ptxt in enumerate(pts):
                py = top + i * (ph + 0.2)
                self.rect(slide, x, py, w, ph, fill=t["panel"])
                self.text(slide, x + 0.25, py + 0.15, 0.5, 0.5, f"{i + 1:02d}", 18, t["accent"], self.hf,
                          bold=True, fit=False)
                self.text(slide, x + 0.85, py + 0.12, w - 1.1, ph - 0.24, ptxt, 15, t["ink"], self.bf,
                          min_size=11.5, anchor="middle")
        return slide

    def s_custom(self, s):
        """A slide composed by hand in the HTML draft (`html`). The builder lays down the chrome and a
        placeholder that fails lint until the composition is rebuilt on the same grid with python-pptx
        (routes.md §B) or the slide is redesigned with a standard type."""
        t = self.t
        slide, top, bottom = self._body(s)
        note = s.get("pptx_note", "rebuild this composition with native shapes on the deck grid")
        self.rect(slide, MARGIN, top, SLIDE_W - 2 * MARGIN, bottom - top, fill=t["panel"], line=t["rule"])
        self.text(slide, MARGIN + 0.3, top + 0.3, SLIDE_W - 2 * MARGIN - 0.6, 1.2,
                  f"[CUSTOM LAYOUT: {note}]", 14, t["muted"], self.bf, min_size=11, max_lines=3)
        self.warn(f"slide {self.cur_idx}: custom layout needs a hand build before delivery ({note})")
        return slide

    def s_bullets(self, s):
        t = self.t
        slide, top, bottom = self._body(s)
        items = s.get("items", [])
        if len(items) > 6:
            self.warn(f"{len(items)} bullets: more than 6 reads as a document; split or choose an exhibit")
        side = s.get("side")
        side_w = 3.9 if side else 0
        w = SLIDE_W - 2 * MARGIN - side_w - (0.35 if side else 0)
        bsize = 22 if len(items) <= 4 else 18
        self.text(slide, MARGIN, top, w, bottom - top, "\n".join(items), bsize, t["ink"], self.bf,
                  min_size=12, para_space=14, line_spacing=1.12, bullets=True)
        if side:
            self._side_panel(slide, side, SLIDE_W - MARGIN - side_w, top, side_w, bottom - top)
        return slide

    def s_compare(self, s):
        """Two to four columns compared on the same rows: before/after, us vs them, option A/B."""
        t = self.t
        slide, top, bottom = self._body(s)
        cols = s["columns"]
        n = len(cols)
        gap = 0.28
        w = (SLIDE_W - 2 * MARGIN - gap * (n - 1)) / n
        y = self.exhibit_label(slide, s, MARGIN, top, SLIDE_W - 2 * MARGIN)
        hl = s.get("highlight")
        bodies = ["\n".join(c.get("points", [])) for c in cols]
        avail = bottom - y - 1.05
        csize = min(fit_size(b, self.bf, w - 0.72, avail, 18 if self.talk else 16, 11.5,
                             line_spacing=1.1 * 1.045, para_space_pt=8)[0] for b in bodies)
        need = max(text_height_in(b, self.bf, csize, w - 0.72, line_spacing=1.1 * 1.045,
                                  para_space_pt=8) for b in bodies)
        bottom = min(bottom, y + max(0.62 + 0.23 + need + 0.4, (bottom - y) * 0.5))
        for i, c in enumerate(cols):
            x = MARGIN + i * (w + gap)
            is_hl = hl == i
            self.rect(slide, x, y, w, 0.62, fill=t["accent"] if is_hl else t["primary"])
            self.text(slide, x + 0.22, y, w - 0.44, 0.62, c.get("heading", ""), 16, "FFFFFF", self.bf,
                      bold=True, min_size=12, max_lines=2, anchor="middle")
            self.rect(slide, x, y + 0.62, w, bottom - y - 0.62, fill=t["panel"])
            self.text(slide, x + 0.25, y + 0.85, w - 0.5, bottom - y - 1.05, "\n".join(c.get("points", [])),
                      csize, t["ink"], self.bf, min_size=11.5, para_space=8, line_spacing=1.1, bullets=True)
        return slide

    def s_ask(self, s):
        """The decision slide: what is asked, why, what it costs; the number it moves beside it."""
        t = self.t
        slide, top, bottom = self._body(s)
        has_fig = bool(s.get("figure"))
        bw = SLIDE_W - 2 * MARGIN - (3.6 if has_fig else 0)
        self.rect(slide, MARGIN, top, bw, bottom - top, fill=t["primary"])
        self.text(slide, MARGIN + 0.35, top + 0.25, bw - 0.7, 0.3, "THE ASK", 11, t["on_dark_muted"],
                  self.bf, bold=True, spacing=1.6, fit=False)
        self.text(slide, MARGIN + 0.35, top + 0.6, bw - 0.7, 1.2, s.get("ask", ""), 22, "FFFFFF",
                  self.hf, bold=True, min_size=15, max_lines=3, line_spacing=1.02)
        half = (bw - 0.7 - 0.4) / 2
        yb = top + 1.95
        hb = bottom - yb - (0.7 if s.get("owner") else 0.3)
        self.text(slide, MARGIN + 0.35, yb, half, 0.3, "WHY NOW", 10.5, t["on_dark_muted"], self.bf,
                  bold=True, spacing=1.4, fit=False)
        self.text(slide, MARGIN + 0.35, yb + 0.38, half, hb - 0.38, "\n".join(s.get("why", [])), 14,
                  "FFFFFF", self.bf, min_size=11.5, para_space=6, bullets=True)
        x2 = MARGIN + 0.35 + half + 0.4
        self.text(slide, x2, yb, half, 0.3, "COST AND IMPACT", 10.5, t["on_dark_muted"], self.bf,
                  bold=True, spacing=1.4, fit=False)
        self.text(slide, x2, yb + 0.38, half, hb - 0.38, "\n".join(s.get("cost", [])), 14, "FFFFFF",
                  self.bf, min_size=11.5, para_space=6, bullets=True)
        if not s.get("cost"):
            self.warn("the ask states no cost or impact: decision-makers approve what they can weigh")
        if has_fig:
            f = s["figure"]
            fx = SLIDE_W - MARGIN - 3.3
            self.rect(slide, fx, top, 3.3, bottom - top, fill=t["accent"])
            self.text(slide, fx + 0.3, top + 0.4, 2.7, 1.3, f.get("value", ""), 46, "FFFFFF", self.hf,
                      bold=True, min_size=28, max_lines=1, anchor="bottom")
            self.text(slide, fx + 0.3, top + 1.85, 2.7, bottom - top - 2.2, f.get("label", ""), 14,
                      "FFFFFF", self.bf, min_size=11, max_lines=5)
        if s.get("owner"):
            self.text(slide, MARGIN + 0.35, bottom - 0.42, bw - 0.7, 0.3, s["owner"], 11,
                      t["on_dark_muted"], self.bf, fit=False, name="Owner")
        return slide

    def s_image(self, s):
        t = self.t
        slide, top, bottom = self._body(s)
        path = s.get("path", "")
        if path and not os.path.isabs(path):
            path = os.path.join(self.spec_dir, path)
        side = s.get("side", "right")
        iw = s.get("image_width", 6.2)
        tw = SLIDE_W - 2 * MARGIN - iw - 0.4
        ix = MARGIN if side == "left" else SLIDE_W - MARGIN - iw
        tx = MARGIN + iw + 0.4 if side == "left" else MARGIN
        if path and os.path.exists(path):
            from PIL import Image
            with Image.open(path) as im:
                ar = im.width / im.height
            box_h = bottom - top
            pic = slide.shapes.add_picture(path, Inches(ix), Inches(top), Inches(iw), Inches(box_h))
            box_ar = iw / box_h
            if ar > box_ar:  # crop sides, never stretch
                crop = (1 - box_ar / ar) / 2
                pic.crop_left = pic.crop_right = crop
            else:
                crop = (1 - ar / box_ar) / 2
                pic.crop_top = pic.crop_bottom = crop
            pic.name = s.get("alt", "Picture")
            pic._element.nvPicPr.cNvPr.set("descr", s.get("alt", ""))
            if not s.get("alt"):
                self.warn("picture has no alt text")
        else:
            self.rect(slide, ix, top, iw, bottom - top, fill=t["panel"], line=t["rule"])
            self.text(slide, ix + 0.3, top + 0.3, iw - 0.6, 1.0, f"[IMAGE NEEDED: {s.get('alt', '')}]", 13,
                      t["muted"], self.bf, fit=False)
            self.warn(f"image missing: {s.get('path', '(none)')}")
        if s.get("heading"):
            self.text(slide, tx, top, tw, 0.9, s["heading"], 20, t["ink"], self.hf, bold=True, min_size=15,
                      max_lines=2)
        self.text(slide, tx, top + (1.0 if s.get("heading") else 0), tw,
                  bottom - top - (1.0 if s.get("heading") else 0), "\n".join(s.get("points", [])), 15,
                  t["ink"], self.bf, min_size=11.5, para_space=8, bullets=True)
        return slide

    # ------------------------------------------------------------------ orchestration
    def _seconds(self, s):
        """Time budget per slide (shared with the HTML draft: _common.slide_seconds)."""
        return slide_seconds(self.spec, s)

    def notes(self, slide, s):
        n = s.get("notes") or {}
        if isinstance(n, str):
            n = {"say": n}
        parts = []
        sec = self._seconds(s)
        if sec:
            parts.append(f"[~{sec} sec]")
        if n.get("say"):
            parts.append(n["say"])
        ref = []
        if n.get("assumptions"):
            ref.append("Assumed (confirm before presenting): " + "; ".join(n["assumptions"]))
        srcs = n.get("sources") or ([s["source"]] if s.get("source") else [])
        if not srcs and s.get("type") not in ("divider", "agenda") and self.spec.get("sources"):
            srcs = ["deck sources: " + "; ".join(self.spec["sources"])]
        if srcs:
            ref.append("Sources: " + "; ".join(srcs))
        if n.get("qa"):
            ref.append("Likely questions: " + " | ".join(n["qa"]))
        if ref:
            parts.append("--- For the presenter, not to be read out ---\n" + "\n".join(ref))
        if s.get("type") == "agenda" and not n.get("say"):
            parts.append("Route through the deck: " + "; ".join(
                str(i if isinstance(i, str) else i.get("label", "")) for i in s.get("items", [])))
        elif not n.get("say") and s.get("type") != "divider":
            self.warn("no speaker notes: write the 2-5 sentence script first (notes.say)")
        if parts:
            slide.notes_slide.notes_text_frame.text = "\n\n".join(parts)

    def lint_spec_slide(self, s):
        typ = s.get("type")
        # Review repeated types in context; useful comparison may intentionally repeat.
        self.type_run.append(typ)
        if len(self.type_run) >= 3 and len(set(self.type_run[-3:])) == 1 and typ not in ("divider", "custom"):
            self.warn(f"third '{typ}' slide in a row: fine for like-for-like comparisons; change it if the "
                      "communication task changed (or merge the slides)")
        if self.talk and typ == "agenda":
            self.warn("agenda in talk mode: keep it only if it orients (workshop, long or teaching session); "
                      "for a short persuasive talk, question dividers usually work better")
        if typ == "ask" and not any(ch.isdigit() for ch in json.dumps(s.get("ask", ""))):
            self.warn("the ask has no number (amount, people, date): decision-makers approve what they can weigh")
        if typ in ("cover", "divider", "closing", "agenda", "quote", "question", "references", "image_full",
                   "code"):
            return
        title = s.get("title", "")
        if not title and not (typ == "statement" and s.get("claim")):
            self.warn("missing title")
        elif self.mode == "document" and is_label_title(title):
            self.warn(f"title reads as a topic label, not a claim: '{title}'")
        blob = json.dumps({k: v for k, v in s.items() if k not in ("notes", "source")}, ensure_ascii=False)
        if (has_figures(blob) or typ in ("chart", "table", "kpi", "options")) and not s.get("source") \
                and not self.spec.get("sources"):
            self.warn("shows figures but names no source (source:, or deck-level sources)")
        if PLACEHOLDER.search(json.dumps(s, ensure_ascii=False)):
            self.warn("contains a placeholder ([CONFIRM]/[TBD]/lorem): resolve it before delivery")

    def build(self):
        handlers = {k[2:]: getattr(self, k) for k in dir(self) if k.startswith("s_")}
        for i, raw in enumerate(self.spec["slides"], start=1):
            self.cur_idx = i
            s = raw
            typ = s.get("type", "bullets")
            if typ not in handlers:
                raise SpecError(f"slide {i}: unknown type '{typ}'. Types: {', '.join(sorted(handlers))}")
            if not s.get("source") and self.spec.get("sources") and typ not in (
                    "cover", "divider", "closing", "agenda"):
                s = dict(s)
                s.setdefault("notes", {})
                if isinstance(s["notes"], dict) and not s["notes"].get("sources"):
                    s["notes"] = dict(s["notes"], sources=self.spec["sources"])
            self.lint_spec_slide(s)
            if typ == "exec_summary" and self.id_pages:
                s = dict(s, rows=[dict(r, pages=r.get("pages") or (
                    f"p.{self.id_pages[r['ref']]}" if r.get("ref") in self.id_pages else None))
                    for r in s.get("rows", [])])
            for r in (s.get("rows") or []) if typ == "exec_summary" else []:
                if r.get("ref") and self.id_pages and r["ref"] not in self.id_pages:
                    self.warn(f"exec summary ref '{r['ref']}' matches no slide id")
            slide = handlers[typ](s)
            # Full-bleed layouts may omit ordinary footers and tags. Keep provenance
            # visible in the delivered deck, including on covers and closing slides.
            if s.get("_illustrative") or s.get("data_status") == "illustrative":
                self.rect(slide, SLIDE_W - 1.65, 0.12, 1.45, 0.30,
                          fill="FFFFFF", line="111111", name="provenance-badge")
                self.text(slide, SLIDE_W - 1.60, 0.17, 1.35, 0.20, "Illustrative", 10,
                          "111111", font="Arial", bold=True, align="center", fit=False,
                          name="provenance-label")
            self.notes(slide, s)
            if s.get("id"):
                self.pages_seen[s["id"]] = self.page_no
        return self.prs


def _drop_style(shp):
    """Remove the theme style reference so no inherited shadow/effect renders (PowerPoint or LibreOffice)."""
    for st in shp._element.xpath("./p:style"):
        st.getparent().remove(st)
    spPr = shp._element.spPr
    if not spPr.xpath("./a:effectLst"):
        spPr.append(OxmlElement("a:effectLst"))


def _set_border(cell, side: str, color: str | None, width_pt: float):
    tcPr = cell._tc.get_or_add_tcPr()
    tag = {"L": "a:lnL", "R": "a:lnR", "T": "a:lnT", "B": "a:lnB"}[side]
    existing = tcPr.find(qn(tag))
    if existing is not None:
        tcPr.remove(existing)
    ln = OxmlElement(tag)
    if color is None or width_pt <= 0:
        ln.set("w", "0")
        ln.append(OxmlElement("a:noFill"))
    else:
        ln.set("w", str(int(width_pt * 12700)))
        ln.set("cmpd", "sng")
        sf = OxmlElement("a:solidFill")
        clr = OxmlElement("a:srgbClr")
        clr.set("val", color)
        sf.append(clr)
        ln.append(sf)
        dash = OxmlElement("a:prstDash")
        dash.set("val", "solid")
        ln.append(dash)
    order = ["a:lnL", "a:lnR", "a:lnT", "a:lnB"]
    idx = 0
    for o in order[: order.index(tag)]:
        if tcPr.find(qn(o)) is not None:
            idx += 1
    tcPr.insert(idx, ln)


SMALL_PRINT = {"provenance-label", "Source", "Footer", "PageNumber", "Kicker", "ExhibitLabel", "Caption", "Owner"}

from spec_schema import SCHEMA  # shared authoring contract; old --schema CLI remains supported


def outline(spec: dict):
    print(f"# {spec.get('title', '(untitled)')}  [{spec.get('mode', 'document')} mode, "
          f"{len(spec['slides'])} slides]\n")
    for i, s in enumerate(spec["slides"], 1):
        flag = ""
        if s.get("type") not in ("cover", "divider", "closing", "agenda", "quote") and \
                spec.get("mode", "document") == "document" and is_label_title(s.get("title", "")):
            flag = "   <-- label, not a claim"
        print(f"{i:>2}. [{s.get('type')}] {strip_markup(s.get('title', s.get('claim', '')))}{flag}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--outline", action="store_true", help="print the headline track and stop")
    ap.add_argument("--schema", action="store_true")
    ap.add_argument("--direction", help="override the spec's direction (to preview looks)")
    ap.add_argument("--only", help="build only these 1-based slides, e.g. 1,4 (direction previews)")
    ap.add_argument("--strict", action="store_true",
                    help="release gate for the final build: refuse to build while blockers remain (spec_io.py)")
    a = ap.parse_args(argv)
    if a.schema:
        print(SCHEMA)
        return 0
    if not a.spec:
        ap.error("spec path required")
    try:
        spec = load_spec(a.spec)
        if a.direction:
            spec["direction"] = a.direction
        if a.only:
            keep = {int(x) for x in a.only.split(",")}
            spec["slides"] = [sl for i, sl in enumerate(spec["slides"], 1) if i in keep]
        if a.outline:
            outline(spec)
            return 0
        if a.strict and spec.get("_blockers"):
            spec_report(spec, True)
            return 2
        base = os.path.dirname(os.path.abspath(a.spec))
        b = Builder(spec, base)
        prs = b.build()
        if any(r.get("ref") for sl in spec["slides"] if sl.get("type") == "exec_summary"
               for r in sl.get("rows", [])):
            # second pass: exec-summary rows point at slide ids, so page refs never go stale
            pages = b.pages_seen
            b = Builder(spec, base)
            b.id_pages = pages
            prs = b.build()
    except SpecError as e:
        print(f"SPEC ERROR: {e}", file=sys.stderr)
        return 2
    out = a.out or os.path.splitext(a.spec)[0] + ".pptx"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    prs.save(out)
    print(f"built {out}  ({len(spec['slides'])} slides, direction {b.t['name']})")
    spec_report(spec, a.strict)
    for w in b.warnings:
        print(f"  warn  {w}")
    for w in voice_report(spec):
        print(f"  style {w}")
    hard = [w for w in b.warnings if "does not fit" in w or "placeholder" in w]
    for (fam, bold), used in FONT_FALLBACKS.items():
        print(f"  note  fit measured with {used} in place of {fam}{' bold' if bold else ''}: check wrapping by eye")
    if b.shrunk:
        print("  note  some text was stepped down in size to fit (within floors)")
    return 3 if hard else 0


if __name__ == "__main__":
    sys.exit(main())

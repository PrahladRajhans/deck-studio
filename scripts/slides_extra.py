"""Extra slide types and shared visual helpers for build_deck.py (mixed into Builder).

Every method named s_<type> becomes a slide type. Each one owns its layout on the same grid
(13.333 x 7.5 in, 0.6 in margins) and draws only with direction tokens, so all types re-theme.
"""
from __future__ import annotations

import math
import os

from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

from _common import MARGIN, SLIDE_H, SLIDE_W, SpecError, text_height_in

W_ALL = SLIDE_W - 2 * MARGIN

GLYPHS = {  # safe glyphs for icon badges (render in every Office font; no emoji)
    "up": "▲", "down": "▼", "check": "✓", "cross": "✗", "star": "★", "arrow": "→",
    "warn": "!", "plus": "+", "minus": "−", "question": "?", "dot": "●", "diamond": "◆",
    "money": "$", "rupee": "₹", "percent": "%", "time": "◷", "people": "●●", "target": "◎",
}
STATUS = {"done": ("pos", "Done"), "on_track": ("pos", "On track"), "at_risk": ("accent", "At risk"),
          "late": ("neg", "Late"), "not_started": ("grey", "Not started"), "now": ("accent", "Now"),
          "next": ("primary", "Next"), "later": ("grey", "Later")}
LEVEL = {"H": 3, "M": 2, "L": 1, "high": 3, "medium": 2, "low": 1}


def _alpha(shape, pct: int):
    """Give a shape's solid fill transparency (pct = opacity 0-100)."""
    clr = shape._element.spPr.find(qn("a:solidFill"))
    if clr is None:
        return
    srgb = clr.find(qn("a:srgbClr"))
    if srgb is None:
        return
    a = OxmlElement("a:alpha")
    a.set("val", str(int(pct * 1000)))
    srgb.append(a)


def _shadow(shape, blur_pt=8, dist_pt=2, opacity=16):
    spPr = shape._element.spPr
    eff = spPr.find(qn("a:effectLst"))
    if eff is None:
        eff = OxmlElement("a:effectLst")
        spPr.append(eff)
    sh = OxmlElement("a:outerShdw")
    sh.set("blurRad", str(int(blur_pt * 12700)))
    sh.set("dist", str(int(dist_pt * 12700)))
    sh.set("dir", "5400000")
    sh.set("algn", "t")
    sh.set("rotWithShape", "0")
    c = OxmlElement("a:srgbClr")
    c.set("val", "000000")
    a = OxmlElement("a:alpha")
    a.set("val", str(opacity * 1000))
    c.append(a)
    sh.append(c)
    eff.append(sh)


class ExtraMixin:
    # ------------------------------------------------------------------ shared helpers
    def tok(self, key):
        """A token name (primary, accent, pos...) or a literal hex."""
        return self.t.get(key, key)

    def card(self, slide, x, y, w, h, hl=False, fill=None, name=None, dark=False):
        """A content surface in the direction's shape language (radius + tint/border/shadow)."""
        t = self.t
        r = t.get("radius", 0) or 0
        shape = MSO_SHAPE.ROUNDED_RECTANGLE if r > 0 else MSO_SHAPE.RECTANGLE
        style = t.get("card", "tint")
        if fill is None:
            if hl:
                fill = t["primary"]
            elif style == "border":
                fill = t["bg"]
            elif style == "shadow" and not dark:
                fill = "FFFFFF" if t["bg"].upper() != "FFFFFF" else t["bg"]
            else:
                fill = t["panel"]
        line = t["rule"] if (style == "border" and not hl) else None
        shp = self.rect(slide, x, y, w, h, fill=fill, line=line, shape=shape, name=name)
        if r > 0:
            try:
                shp.adjustments[0] = min(0.5, r / max(0.01, min(w, h)))
            except (IndexError, ValueError):
                pass
        if style == "shadow" and not hl:
            _shadow(shp)
        return shp

    def badge(self, slide, x, y, d, text, fill, color="FFFFFF", size=None, font=None):
        self.rect(slide, x, y, d, d, fill=fill, shape=MSO_SHAPE.OVAL)
        if str(text).startswith('feather:'):
            from icons import png
            image = slide.shapes.add_picture(png(text, color), Inches(x + d * .2), Inches(y + d * .2),
                                             width=Inches(d * .6), height=Inches(d * .6))
            image.name = 'Icon ' + text
            image._element.nvPicPr.cNvPr.set('descr', text.split(':', 1)[1].replace('-', ' '))
            return
        self.text(slide, x, y, d, d, text, size or max(10, d * 30), color, font or self.hf, bold=True,
                  align="center", anchor="middle", fit=False)

    def chip(self, slide, x, y, text, fill, color="FFFFFF", size=10.5, w=None, h=0.28):
        w = w or max(0.6, len(text) * size * 0.0098 + 0.3)
        shp = self.rect(slide, x, y, w, h, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        try:
            shp.adjustments[0] = 0.5
        except (IndexError, ValueError):
            pass
        if fill in (self.t["grey"], self.t["rule"], self.t["panel"]) and color == "FFFFFF":
            color = self.t["ink"]
        self.text(slide, x, y, w, h, text, size, color, self.bf, bold=True, align="center",
                  anchor="middle", fit=False, name="Caption")
        return w

    def provenance_tag(self, slide, text, top=None):
        """Small bordered 'Illustrative' / 'Non-exhaustive' tag, bottom right on the source line."""
        w = max(1.0, len(text) * 0.075 + 0.3)
        x = SLIDE_W - MARGIN - w
        y = SLIDE_H - 0.68
        self.rect(slide, x, y, w, 0.26, line=self.t["muted"], line_w=0.5)
        self.text(slide, x, y, w, 0.26, text, 9, self.t["muted"], self.bf, align="center",
                  anchor="middle", fit=False, caps=True, spacing=0.8, name="Caption")

    def footnote_block(self, slide, notes, bottom):
        """Numbered footnotes above the source line; mark claims with ¹ ² ³ in the text."""
        if not notes:
            return bottom
        txt = "\n".join(f"{i + 1}. {n}" for i, n in enumerate(notes))
        h = 0.2 * len(notes) + 0.05
        self.text(slide, MARGIN, bottom - h, W_ALL - 0.8, h, txt, 9.5, self.t["muted"], self.bf,
                  min_size=8.5, para_space=0, line_spacing=1.0, name="Caption")
        return bottom - h - 0.08

    def _picture(self, slide, path, x, y, w, h, alt="", shape=None):
        full = path if os.path.isabs(path) else os.path.join(self.spec_dir, path)
        if not os.path.exists(full):
            self.rect(slide, x, y, w, h, fill=self.t["panel"], line=self.t["rule"])
            self.text(slide, x + 0.2, y + 0.2, w - 0.4, 0.8, f"[IMAGE NEEDED: {alt or path}]", 12,
                      self.t["muted"], self.bf, fit=False)
            self.warn(f"image not found: {path}")
            return None
        from PIL import Image
        with Image.open(full) as im:
            ar = im.width / im.height
        pic = slide.shapes.add_picture(full, Inches(x), Inches(y), Inches(w), Inches(h))
        box = w / h
        if ar > box:
            c = (1 - box / ar) / 2
            pic.crop_left = pic.crop_right = c
        else:
            c = (1 - ar / box) / 2
            pic.crop_top = pic.crop_bottom = c
        pic._element.nvPicPr.cNvPr.set("descr", alt or "")
        if not alt:
            self.warn("picture has no alt text")
        if shape == "ellipse":
            geom = pic._element.spPr.find(qn("a:prstGeom"))
            if geom is not None:
                geom.set("prst", "ellipse")
        return pic

    def _items_text(self, items):
        return "\n".join(items) if isinstance(items, list) else (items or "")

    # ------------------------------------------------------------------ number slides
    def s_big_number(self, s):
        """One hero number, what it means, and 2-3 proof points."""
        t = self.t
        slide, top, bottom = self._body(s)
        pts = s.get("points", [])
        lw = 6.6 if pts else W_ALL
        mid = top + (bottom - top) * 0.42
        self.text(slide, MARGIN, top, lw, mid - top + 0.4, s.get("value", ""), 110 if self.talk else 96,
                  t["accent"], self.hf, bold=True, min_size=54, max_lines=1, anchor="bottom",
                  name="BigNumber")
        self.text(slide, MARGIN, mid + 0.55, lw - 0.3, 1.1, s.get("label", ""), 22, t["ink"], self.hf,
                  bold=True, min_size=16, max_lines=3, line_spacing=1.05)
        if s.get("context"):
            self.text(slide, MARGIN, mid + 1.7, lw - 0.3, bottom - mid - 1.7, s["context"], 14,
                      t["muted"], self.bf, min_size=12, max_lines=3)
        if pts:
            x = MARGIN + lw + 0.4
            w = SLIDE_W - MARGIN - x
            n = len(pts)
            gap = 0.18
            ph = min(1.35, (bottom - top - gap * (n - 1)) / n)
            y0 = top + ((bottom - top) - (ph * n + gap * (n - 1))) / 2
            for i, p in enumerate(pts):
                y = y0 + i * (ph + gap)
                self.card(slide, x, y, w, ph)
                self.text(slide, x + 0.28, y + 0.12, w - 0.56, ph - 0.24, p, 15, t["ink"], self.bf,
                          min_size=12, max_lines=3, anchor="middle")
        if not pts and not s.get("context"):
            self.warn("big number with one caption: add 2-3 proof points or context")
        return slide

    def s_data_contrast(self, s):
        """Two numbers in tension (+12% vs -3%): the gap is the story."""
        t = self.t
        slide, top, bottom = self._body(s)
        items = s["items"][:2]
        if len(items) != 2:
            raise SpecError(f"slide {self.cur_idx}: data_contrast needs exactly two items")
        hl = s.get("highlight", 1)
        mid_w = 1.6
        w = (W_ALL - mid_w) / 2
        h = bottom - top
        for i, it in enumerate(items):
            x = MARGIN + i * (w + mid_w)
            on = hl == i
            self.card(slide, x, top, w, h, fill=t["accent"] if on else None)
            col = "FFFFFF" if on else t["primary"]
            sub = "FFFFFF" if on else t["ink"]
            self.text(slide, x + 0.4, top + 0.35, w - 0.8, 0.4, it.get("label", ""), 14,
                      "FFFFFF" if on else t["muted"], self.bf, bold=True, caps=True, spacing=1.2,
                      fit=False, name="Caption")
            self.text(slide, x + 0.4, top + 0.85, w - 0.8, 1.8, it.get("value", ""), 80, col, self.hf,
                      bold=True, min_size=40, max_lines=1, anchor="middle")
            self.text(slide, x + 0.4, top + 2.8, w - 0.8, h - 3.0, it.get("detail", ""), 16, sub, self.bf,
                      min_size=12, max_lines=4)
        self.text(slide, MARGIN + w, top, mid_w, h, s.get("versus", "vs"), 26, t["muted"], self.hf,
                  bold=True, italic=True, align="center", anchor="middle", fit=False)
        return slide

    # ------------------------------------------------------------------ diagram slides
    def s_funnel(self, s):
        """Stages narrowing down; conversion between stages computed when values are numbers."""
        t = self.t
        slide, top, bottom = self._body(s)
        stages = s["stages"]
        n = len(stages)
        y = self.exhibit_label(slide, s, MARGIN, top, W_ALL)
        side_w = 3.3
        fw = W_ALL - side_w - 0.4
        gap = 0.1
        sh = min(0.95, (bottom - y - gap * (n - 1)) / n)
        hl = s.get("highlight")
        for i, st in enumerate(stages):
            frac = 1 - i * (0.55 / max(1, n - 1))
            w = fw * frac
            x = MARGIN + (fw - w) / 2
            yy = y + i * (sh + gap)
            fill = t["accent"] if hl == i else (t["primary"] if i == 0 else t["grey"] if hl is not None
                                                 else t["primary"])
            shp = self.rect(slide, x, yy, w, sh, fill=fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE)
            try:
                shp.adjustments[0] = 0.12
            except (IndexError, ValueError):
                pass
            label = st.get("label", "")
            val = st.get("value", "")
            if isinstance(val, (int, float)):
                val = f"{val:,.0f}" if abs(val) >= 1000 or float(val).is_integer() else f"{val:,.1f}"
            on_light = fill == t["grey"]
            self.text(slide, x + 0.25, yy, w - 0.5, sh, f"**{val}**   {label}" if val != "" else label, 16,
                      t["ink"] if on_light else "FFFFFF", self.bf, min_size=11.5, max_lines=1, anchor="middle",
                      align="center")
            # conversion from previous stage
            if i > 0:
                a, b = stages[i - 1].get("value"), st.get("value")
                conv = st.get("conversion")
                if conv is None and isinstance(a, (int, float)) and isinstance(b, (int, float)) and a:
                    conv = f"{b / a * 100:.0f}%"
                if conv:
                    self.text(slide, MARGIN + fw + 0.4, yy - gap / 2 - 0.15, side_w, 0.3,
                              f"↓ {conv}  {st.get('conversion_label', 'convert')}", 13, t["muted"], self.bf,
                              fit=False, name="Caption")
            if st.get("note"):
                self.text(slide, MARGIN + fw + 0.4, yy + 0.2, side_w, max(0.3, sh - 0.45), st["note"], 12,
                          t["ink"], self.bf, min_size=10, max_lines=2, anchor="middle", name="Caption")
        return slide

    def s_pyramid(self, s):
        """Hierarchy: top level is the point, base is the foundation. Levels top -> bottom."""
        t = self.t
        slide, top, bottom = self._body(s)
        levels = s["levels"]
        n = len(levels)
        y = self.exhibit_label(slide, s, MARGIN, top, W_ALL)
        pw = 6.2
        gap = 0.08
        lh = min(1.0, (bottom - y - gap * (n - 1)) / n)
        hl = s.get("highlight")
        for i, lv in enumerate(levels):
            frac = 0.32 + 0.68 * (i + 1) / n
            w = pw * frac
            x = MARGIN + (pw - w) / 2
            yy = y + i * (lh + gap)
            fill = t["accent"] if hl == i else t["primary"]
            self.rect(slide, x, yy, w, lh, fill=fill, shape=MSO_SHAPE.TRAPEZOID if i else
                      MSO_SHAPE.ISOSCELES_TRIANGLE if s.get("apex", False) else MSO_SHAPE.TRAPEZOID)
            self.text(slide, x + 0.3, yy, w - 0.6, lh, lv.get("label", ""), 15, "FFFFFF", self.bf, bold=True,
                      min_size=11, max_lines=2, anchor="middle", align="center")
            if lv.get("detail"):
                self.line(slide, MARGIN + pw + 0.15, yy + lh / 2, MARGIN + pw + 0.55, yy + lh / 2, t["rule"])
                self.text(slide, MARGIN + pw + 0.7, yy, W_ALL - pw - 0.7, lh, lv["detail"], 14, t["ink"],
                          self.bf, min_size=11.5, max_lines=2, anchor="middle")
        return slide

    def s_cycle(self, s):
        """A loop (flywheel, virtuous circle): 3-6 steps on a ring, optional centre label."""
        t = self.t
        slide, top, bottom = self._body(s)
        steps = s["steps"]
        n = len(steps)
        side = s.get("side")
        area_w = W_ALL - (4.2 if side else 0)
        cy = (top + bottom) / 2
        cx = MARGIN + area_w / 2
        lw_lab, d_node = 2.1, 0.62
        # leave room for a label on each side of the ring, and for lifted labels above/below
        r = min((area_w - 2 * (lw_lab + d_node / 2 + 0.25)) / 2, (bottom - top) / 2 - 0.75)
        ring = self.rect(slide, cx - r, cy - r, 2 * r, 2 * r, line=t["rule"], line_w=2.5, shape=MSO_SHAPE.OVAL)
        if s.get("center"):
            self.text(slide, cx - r * 0.62, cy - 0.6, r * 1.24, 1.2, s["center"], 20, t["primary"], self.hf,
                      bold=True, align="center", anchor="middle", min_size=13, max_lines=3)
        d = 0.62
        hl = s.get("highlight")
        for i, st in enumerate(steps):
            ang = -math.pi / 2 + 2 * math.pi * i / n
            nx, ny = cx + r * math.cos(ang), cy + r * math.sin(ang)
            self.badge(slide, nx - d / 2, ny - d / 2, d, str(i + 1), t["accent"] if hl == i else t["primary"])
            lw, lh = lw_lab, 0.95
            right = math.cos(ang) >= -0.01
            lx = nx + d / 2 + 0.12 if right else nx - d / 2 - 0.12 - lw
            ly = ny - lh / 2
            if abs(math.cos(ang)) < 0.2:  # top or bottom node: label beside it, lifted clear of the ring
                lx = nx + d / 2 + 0.12
                ly = ny - lh + 0.12 if math.sin(ang) < 0 else ny - 0.12
            ly = max(top, min(ly, bottom - lh))
            head = st.get("heading", "") if isinstance(st, dict) else st
            body = st.get("body", "") if isinstance(st, dict) else ""
            txt = f"**{head}**" + (f"\n{body}" if body else "")
            self.text(slide, lx, ly, lw, lh, txt, 14, t["ink"], self.bf, min_size=11, para_space=1,
                      align="left" if right or abs(math.cos(ang)) < 0.2 else "right", anchor="middle")
        if side:
            self._side_panel(slide, side, SLIDE_W - MARGIN - 3.9, top, 3.9, bottom - top)
        return slide

    def s_hub(self, s):
        """Hub and spoke: one central idea, 3-8 enablers around it."""
        t = self.t
        slide, top, bottom = self._body(s)
        spokes = s["spokes"]
        n = len(spokes)
        cx, cy = SLIDE_W / 2, (top + bottom) / 2
        hw, hh = 2.6, 1.15
        rx, ry = W_ALL / 2 - 1.55, (bottom - top) / 2 - 0.5
        nodes = []
        for i in range(n):
            ang = -math.pi / 2 + 2 * math.pi * i / n
            nodes.append((cx + rx * math.cos(ang), cy + ry * math.sin(ang)))
        for nx, ny in nodes:
            self.line(slide, cx, cy, nx, ny, t["rule"], 1.25)
        hub = self.card(slide, cx - hw / 2, cy - hh / 2, hw, hh, hl=True)
        self.text(slide, cx - hw / 2 + 0.15, cy - hh / 2, hw - 0.3, hh, s.get("center", ""), 18, "FFFFFF",
                  self.hf, bold=True, align="center", anchor="middle", min_size=12, max_lines=3)
        bw, bh = 2.75, 0.95
        hl = s.get("highlight")
        for i, ((nx, ny), sp) in enumerate(zip(nodes, spokes)):
            head = sp.get("heading", "") if isinstance(sp, dict) else sp
            body = sp.get("body", "") if isinstance(sp, dict) else ""
            self.card(slide, nx - bw / 2, ny - bh / 2, bw, bh, fill=t["accent"] if hl == i else None)
            col = "FFFFFF" if hl == i else t["ink"]
            self.text(slide, nx - bw / 2 + 0.15, ny - bh / 2 + 0.05, bw - 0.3, bh - 0.1,
                      f"**{head}**" + (f"\n{body}" if body else ""), 14, col, self.bf, min_size=10.5,
                      align="center", anchor="middle", para_space=1)
        return slide

    def s_issue_tree(self, s):
        """Logic tree: root question -> 2-4 branches -> 1-3 leaves each (MECE)."""
        t = self.t
        slide, top, bottom = self._body(s)
        branches = s["branches"]
        y0 = self.exhibit_label(slide, s, MARGIN, top, W_ALL)
        leaves = [(bi, lf) for bi, b in enumerate(branches) for lf in (b.get("leaves") or [""])]
        nl = len(leaves)
        gap = 0.12
        lh = min(0.8, (bottom - y0 - gap * (nl - 1)) / nl)
        colw = [2.9, 3.6, W_ALL - 2.9 - 3.6 - 1.0]
        x0, x1, x2 = MARGIN, MARGIN + colw[0] + 0.5, MARGIN + colw[0] + colw[1] + 1.0
        leaf_y = [y0 + i * (lh + gap) for i in range(nl)]
        total_h = leaf_y[-1] + lh - y0
        root_y = y0 + total_h / 2 - 0.7
        self.card(slide, x0, root_y, colw[0], 1.4, hl=True)
        self.text(slide, x0 + 0.2, root_y, colw[0] - 0.4, 1.4, s.get("root", ""), 16, "FFFFFF", self.hf, bold=True,
                  min_size=11.5, max_lines=4, anchor="middle")
        hl = s.get("highlight")
        li = 0
        for bi, b in enumerate(branches):
            nlv = len(b.get("leaves") or [""])
            ys = leaf_y[li:li + nlv]
            by = (ys[0] + ys[-1] + lh) / 2 - lh / 2
            on = hl == bi
            # connectors root -> branch (elbow)
            mx = x0 + colw[0] + 0.25
            self.line(slide, x0 + colw[0], root_y + 0.7, mx, root_y + 0.7, t["grey"], 1)
            self.line(slide, mx, root_y + 0.7, mx, by + lh / 2, t["grey"], 1)
            self.line(slide, mx, by + lh / 2, x1, by + lh / 2, t["grey"], 1)
            self.card(slide, x1, by, colw[1], lh, fill=t["accent"] if on else None)
            self.text(slide, x1 + 0.18, by, colw[1] - 0.36, lh, b.get("label", ""), 14,
                      "FFFFFF" if on else t["ink"], self.bf, bold=True, min_size=10.5, max_lines=2, anchor="middle")
            mx2 = x1 + colw[1] + 0.25
            for ly, lf in zip(ys, b.get("leaves") or []):
                self.line(slide, x1 + colw[1], by + lh / 2, mx2, by + lh / 2, t["grey"], 1)
                self.line(slide, mx2, by + lh / 2, mx2, ly + lh / 2, t["grey"], 1)
                self.line(slide, mx2, ly + lh / 2, x2, ly + lh / 2, t["grey"], 1)
                self.rect(slide, x2, ly, colw[2], lh, line=t["rule"])
                self.text(slide, x2 + 0.15, ly, colw[2] - 0.3, lh, lf, 13, t["ink"], self.bf, min_size=10.5,
                          max_lines=2, anchor="middle")
            li += nlv
        return slide

    def s_swot(self, s):
        """Strengths, weaknesses, opportunities, threats: internal top, external bottom."""
        t = self.t
        slide, top, bottom = self._body(s)
        names = [("Strengths", "strengths", "S"), ("Weaknesses", "weaknesses", "W"),
                 ("Opportunities", "opportunities", "O"), ("Threats", "threats", "T")]
        gap = 0.22
        w = (W_ALL - gap) / 2
        h = (bottom - top - gap) / 2
        hl = s.get("highlight")
        for k, (label, key, letter) in enumerate(names):
            x = MARGIN + (k % 2) * (w + gap)
            y = top + (k // 2) * (h + gap)
            on = hl in (k, key, letter)
            self.card(slide, x, y, w, h, fill=t["primary"] if on else None)
            self.badge(slide, x + 0.25, y + 0.22, 0.5, letter, t["accent"] if on else t["primary"])
            self.text(slide, x + 0.9, y + 0.22, w - 1.1, 0.5, label, 17, "FFFFFF" if on else t["ink"], self.hf,
                      bold=True, anchor="middle", fit=False)
            self.text(slide, x + 0.3, y + 0.88, w - 0.6, h - 1.05, self._items_text(s.get(key, [])), 14,
                      "FFFFFF" if on else t["ink"], self.bf, min_size=11, para_space=5, bullets=True)
        return slide

    def s_venn(self, s):
        """Two or three overlapping sets; the overlap is the point (the sweet spot)."""
        t = self.t
        slide, top, bottom = self._body(s)
        sets = s["sets"][:3]
        n = len(sets)
        side = s.get("side")
        area_w = W_ALL - (4.2 if side else 0)
        cx, cy = MARGIN + area_w / 2, (top + bottom) / 2
        d = min(area_w / (2.4 if n == 2 else 2.2), (bottom - top) * (0.95 if n == 2 else 0.68))
        off = d * 0.32
        if n == 2:
            centres = [(cx - off, cy), (cx + off, cy)]
        else:
            centres = [(cx - off, cy - off * 0.6), (cx + off, cy - off * 0.6), (cx, cy + off * 0.75)]
        fills = [t["primary"], t["accent"], t["grey"]]
        for (x, y), st, f in zip(centres, sets, fills):
            c = self.rect(slide, x - d / 2, y - d / 2, d, d, fill=f, shape=MSO_SHAPE.OVAL)
            _alpha(c, 28)
            self._fills.pop()  # translucent: the background shows through, so readability uses the bg
        for i, ((x, y), st) in enumerate(zip(centres, sets)):
            dx = (x - cx) * 1.35
            dy = (y - cy) * 1.45
            self.text(slide, cx + dx - 1.4, cy + dy - 0.45, 2.8, 0.9,
                      f"**{st.get('label', '')}**" + (f"\n{st['detail']}" if st.get("detail") else ""), 15,
                      t["ink"], self.bf, align="center", anchor="middle", min_size=11, para_space=1)
        if s.get("overlap"):
            self.chip(slide, cx - 1.2, cy - 0.2 + (0.1 if n == 3 else 0), s["overlap"], t["dark"], w=2.4, h=0.42,
                      size=13)
        if side:
            self._side_panel(slide, side, SLIDE_W - MARGIN - 3.9, top, 3.9, bottom - top)
        return slide

    # ------------------------------------------------------------------ structure slides
    def s_framework(self, s):
        """Dark left rail with one bold statement; supporting points on the right."""
        t = self.t
        slide = self.new_slide()
        self.page_no += 1
        rail_w = 4.6
        self.rect(slide, 0, 0, rail_w, SLIDE_H, fill=t["dark"])
        if s.get("kicker"):
            self.text(slide, 0.6, 0.75, rail_w - 1.1, 0.3, s["kicker"], 11, t["on_dark_muted"], self.bf, bold=True,
                      caps=True, spacing=1.4, fit=False, name="Kicker")
        self.text(slide, 0.6, 1.25, rail_w - 1.1, 4.6, s.get("title", ""), 28, t["on_dark"], self.hf, bold=True,
                  min_size=18, max_lines=7, line_spacing=1.04, name="Headline")
        pts = s.get("points", [])
        x = rail_w + 0.7
        w = SLIDE_W - MARGIN - x
        n = max(1, len(pts))
        gap = 0.25
        ph = min(1.35, (SLIDE_H - 1.6 - gap * (n - 1)) / n)
        y0 = (SLIDE_H - (ph * n + gap * (n - 1))) / 2
        for i, p in enumerate(pts):
            y = y0 + i * (ph + gap)
            head = p.get("heading", "") if isinstance(p, dict) else ""
            body = p.get("body", "") if isinstance(p, dict) else p
            self.text(slide, x, y, 0.8, 0.6, f"{i + 1:02d}", 26, t["accent"], self.hf, bold=True, fit=False)
            self.text(slide, x + 0.9, y + 0.02, w - 0.9, ph, (f"**{head}**\n" if head else "") + body, 16,
                      t["ink"], self.bf, min_size=12, para_space=3)
            if i < n - 1:
                self.line(slide, x + 0.9, y + ph + gap / 2, x + w, y + ph + gap / 2, t["rule"], 0.5)
        self.footer(slide, s)
        return slide

    def s_columns(self, s):
        """2-4 parallel blocks with glyph badges, separated by vertical rules (no boxes)."""
        t = self.t
        slide, top, bottom = self._body(s)
        cols = s["columns"]
        n = len(cols)
        y = self.exhibit_label(slide, s, MARGIN, top, W_ALL)
        gap = 0.5
        w = (W_ALL - gap * (n - 1)) / n
        hl = s.get("highlight")
        for i, c in enumerate(cols):
            x = MARGIN + i * (w + gap)
            on = hl == i
            g = GLYPHS.get(c.get("icon", ""), c.get("icon") or f"{i + 1}")
            self.badge(slide, x, y + 0.05, 0.62, g, t["accent"] if on else t["primary"], size=18)
            self.text(slide, x, y + 0.85, w, 0.75, c.get("heading", ""), 18, t["accent"] if on else t["ink"],
                      self.hf, bold=True, min_size=13, max_lines=2)
            body = self._items_text(c.get("points") or c.get("body", ""))
            self.text(slide, x, y + 1.65, w, bottom - y - 1.7, body, 15, t["ink"], self.bf, min_size=11.5,
                      para_space=6, bullets=isinstance(c.get("points"), list))
            if i < n - 1:
                lx = x + w + gap / 2
                self.line(slide, lx, y, lx, bottom, t["rule"], 0.75)
        return slide

    def s_team(self, s):
        """People: photo (circle-cropped) or initials, name, role, one line of proof."""
        t = self.t
        slide, top, bottom = self._body(s)
        people = s["people"]
        n = len(people)
        per_row = n if n <= 4 else math.ceil(n / 2)
        rows = math.ceil(n / per_row)
        gap = 0.3
        w = (W_ALL - gap * (per_row - 1)) / per_row
        h = (bottom - top - gap * (rows - 1)) / rows
        d = min(1.5, h * 0.42, w * 0.55)
        h = min(h, d + 2.35)  # card fits its content; no tall empty panels
        for i, p in enumerate(people):
            r, c = divmod(i, per_row)
            x = MARGIN + c * (w + gap)
            y = top + r * (h + gap)
            self.card(slide, x, y, w, h)
            px = x + (w - d) / 2
            if p.get("photo"):
                self._picture(slide, p["photo"], px, y + 0.25, d, d, alt=p.get("name", ""), shape="ellipse")
            else:
                ini = "".join(part[0] for part in p.get("name", "?").split()[:2]).upper()
                self.badge(slide, px, y + 0.25, d, ini, t["primary"], size=d * 26)
            ty = y + 0.35 + d
            self.text(slide, x + 0.2, ty, w - 0.4, 0.4, p.get("name", ""), 16, t["ink"], self.hf, bold=True,
                      align="center", min_size=12, max_lines=1)
            self.text(slide, x + 0.2, ty + 0.4, w - 0.4, 0.35, p.get("role", ""), 12, t["accent"], self.bf,
                      bold=True, align="center", min_size=10, max_lines=1, caps=True, spacing=0.6)
            if p.get("line"):
                self.text(slide, x + 0.25, ty + 0.82, w - 0.5, y + h - ty - 0.9, p["line"], 13, t["muted"],
                          self.bf, align="center", min_size=10.5, max_lines=3)
        return slide

    def s_pricing(self, s):
        """Plans or packages side by side; one recommended tier is raised and labelled."""
        t = self.t
        slide, top, bottom = self._body(s)
        tiers = s["tiers"]
        n = len(tiers)
        gap = 0.3
        w = (W_ALL - gap * (n - 1)) / n
        rec = s.get("recommended")
        for i, tr in enumerate(tiers):
            x = MARGIN + i * (w + gap)
            on = rec == i
            y = top + (0 if on else 0.25)
            h = bottom - y
            self.card(slide, x, y, w, h, hl=on)
            fg = "FFFFFF" if on else t["ink"]
            sub = t["on_dark_muted"] if on else t["muted"]
            if on:
                self.chip(slide, x + 0.3, y + 0.25, s.get("recommended_label", "Recommended"), t["accent"])
            self.text(slide, x + 0.3, y + 0.65, w - 0.6, 0.45, tr.get("name", ""), 18, fg, self.hf, bold=True,
                      min_size=13, max_lines=1)
            self.text(slide, x + 0.3, y + 1.1, w - 0.6, 0.8, tr.get("price", ""), 34, fg, self.hf, bold=True,
                      min_size=20, max_lines=1, anchor="bottom")
            self.text(slide, x + 0.3, y + 1.92, w - 0.6, 0.3, tr.get("period", ""), 12, sub, self.bf, fit=False,
                      name="Caption")
            self.line(slide, x + 0.3, y + 2.35, x + w - 0.3, y + 2.35, sub if on else t["rule"], 0.5)
            feats = tr.get("features", [])
            self.text(slide, x + 0.3, y + 2.55, w - 0.6, h - 2.75, "\n".join(f"✓  {f}" for f in feats), 14, fg,
                      self.bf, min_size=11, para_space=5)
        return slide

    def s_roadmap(self, s):
        """Now / Next / Later (or quarters): columns of initiatives under chevron headers."""
        t = self.t
        slide, top, bottom = self._body(s)
        lanes = s["lanes"]
        n = len(lanes)
        overlap = 0.12
        w = (W_ALL + overlap * (n - 1)) / n
        hl = s.get("highlight", 0)
        for i, ln in enumerate(lanes):
            x = MARGIN + i * (w - overlap)
            on = hl == i
            shp = self.rect(slide, x, top, w, 0.62, fill=t["accent"] if on else t["primary"],
                            shape=MSO_SHAPE.PENTAGON if i == 0 else MSO_SHAPE.CHEVRON)
            try:
                shp.adjustments[0] = 0.3
            except (IndexError, ValueError):
                pass
            pad = 0.3 if i == 0 else 0.45
            self.text(slide, x + pad, top, w - pad - 0.35, 0.62, ln.get("heading", ""), 16, "FFFFFF", self.bf,
                      bold=True, anchor="middle", min_size=12, max_lines=1)
            items = ln.get("items", [])
            iy = top + 0.85
            cw = w - overlap - 0.15
            ih = min(1.05, (bottom - iy - 0.12 * (len(items) - 1)) / max(1, len(items)))
            for j, it in enumerate(items):
                yy = iy + j * (ih + 0.12)
                head = it.get("heading", "") if isinstance(it, dict) else it
                body = it.get("body", "") if isinstance(it, dict) else ""
                self.card(slide, x + 0.02, yy, cw, ih)
                self.text(slide, x + 0.22, yy + 0.08, cw - 0.4, ih - 0.16,
                          f"**{head}**" + (f"\n{body}" if body else ""), 13, t["ink"], self.bf, min_size=10.5,
                          para_space=2, anchor="middle")
        return slide

    def s_journey(self, s):
        """Customer or user journey: stages across, rows down, an emotion line on top."""
        t = self.t
        slide, top, bottom = self._body(s)
        stages = s["stages"]
        rows = s.get("rows", ["doing", "thinking", "pain", "opportunity"])
        labels = s.get("row_labels", {"doing": "Doing", "thinking": "Thinking / feeling", "pain": "Pain points",
                                      "opportunity": "Opportunity"})
        n = len(stages)
        lab_w = 1.75
        gw = W_ALL - lab_w
        cw = gw / n
        emo_h = 1.0
        self.text(slide, MARGIN, top, lab_w - 0.1, 0.4, "Stage", 11, t["muted"], self.bf, bold=True, caps=True,
                  fit=False, name="Caption")
        for i, st in enumerate(stages):
            x = MARGIN + lab_w + i * cw
            self.rect(slide, x + 0.03, top, cw - 0.06, 0.42, fill=t["primary"])
            self.text(slide, x + 0.1, top, cw - 0.2, 0.42, st.get("name", ""), 13, "FFFFFF", self.bf, bold=True,
                      align="center", anchor="middle", min_size=10, max_lines=1)
        ey = top + 0.55
        self.text(slide, MARGIN, ey, lab_w - 0.1, emo_h, "Emotion", 11, t["muted"], self.bf, bold=True, caps=True,
                  anchor="middle", fit=False, name="Caption")
        pts = []
        for i, st in enumerate(stages):
            f = max(-1, min(1, float(st.get("feeling", 0))))
            px = MARGIN + lab_w + i * cw + cw / 2
            py = ey + emo_h / 2 - f * (emo_h / 2 - 0.12)
            pts.append((px, py, f))
        self.line(slide, MARGIN + lab_w, ey + emo_h / 2, SLIDE_W - MARGIN, ey + emo_h / 2, t["rule"], 0.5)
        for (x1, y1, _), (x2, y2, _) in zip(pts, pts[1:]):
            self.line(slide, x1, y1, x2, y2, t["primary"], 2)
        for px, py, f in pts:
            self.rect(slide, px - 0.11, py - 0.11, 0.22, 0.22, fill=t["pos"] if f > 0 else t["neg"] if f < 0
                      else t["grey"], shape=MSO_SHAPE.OVAL)
        ry = ey + emo_h + 0.15
        rh = (bottom - ry - 0.08 * (len(rows) - 1)) / len(rows)
        for r, key in enumerate(rows):
            y = ry + r * (rh + 0.08)
            self.text(slide, MARGIN, y, lab_w - 0.15, rh, labels.get(key, key.title()), 12,
                      t["accent"] if key == "opportunity" else t["ink"], self.bf, bold=True, anchor="middle",
                      min_size=10, max_lines=2)
            for i, st in enumerate(stages):
                x = MARGIN + lab_w + i * cw
                fill = t["panel"] if key != "opportunity" else None
                self.card(slide, x + 0.03, y, cw - 0.06, rh, fill=fill) if fill else \
                    self.rect(slide, x + 0.03, y, cw - 0.06, rh, line=t["accent"], line_w=1)
                self.text(slide, x + 0.12, y + 0.05, cw - 0.24, rh - 0.1, st.get(key, ""), 11.5, t["ink"], self.bf,
                          min_size=9.5, max_lines=4, anchor="middle", name="Caption")
        return slide

    # ------------------------------------------------------------------ comparison and story slides
    def s_before_after(self, s):
        """Before -> after, with optional pictures; the arrow is the change."""
        t = self.t
        slide, top, bottom = self._body(s)
        aw = 1.0
        w = (W_ALL - aw) / 2
        h = bottom - top
        for k, side in enumerate(("before", "after")):
            d = s.get(side, {})
            x = MARGIN + k * (w + aw)
            on = k == 1
            self.card(slide, x, top, w, h, fill=None if not on else t["panel"])
            self.chip(slide, x + 0.3, top + 0.3, d.get("label", side.title()), t["accent"] if on else t["grey"])
            y = top + 0.8
            if d.get("image"):
                ih = h * 0.48
                self._picture(slide, d["image"], x + 0.3, y, w - 0.6, ih, alt=d.get("alt", ""))
                y += ih + 0.2
            if d.get("heading"):
                self.text(slide, x + 0.3, y, w - 0.6, 0.6, d["heading"], 19, t["ink"], self.hf, bold=True,
                          min_size=14, max_lines=2)
                y += 0.7
            self.text(slide, x + 0.3, y, w - 0.6, top + h - y - 0.25, self._items_text(d.get("points", [])), 15,
                      t["ink"], self.bf, min_size=11.5, para_space=6, bullets=True)
        self.rect(slide, MARGIN + w + 0.15, top + h / 2 - 0.35, aw - 0.3, 0.7, fill=t["accent"],
                  shape=MSO_SHAPE.RIGHT_ARROW)
        return slide

    def s_faq(self, s):
        """Objections or FAQs: each answer = claim, proof, action (never a fragment)."""
        t = self.t
        slide, top, bottom = self._body(s)
        items = s["items"]
        n = len(items)
        cols = 2 if n > 3 else 1
        rows = math.ceil(n / cols)
        gap = 0.2
        w = (W_ALL - gap * (cols - 1)) / cols
        h = (bottom - top - gap * (rows - 1)) / rows
        for i, it in enumerate(items):
            r, c = divmod(i, cols)
            x = MARGIN + c * (w + gap)
            y = top + r * (h + gap)
            self.card(slide, x, y, w, h)
            self.text(slide, x + 0.25, y + 0.15, w - 0.5, 0.55, f"“{it.get('q', '')}”", 15, t["primary"], self.hf,
                      bold=True, italic=True, min_size=11.5, max_lines=2)
            body = it.get("a", "")
            if it.get("proof"):
                body += f"\n**Proof:** {it['proof']}"
            if len(it.get("a", "").split()) < 6:
                self.warn(f"FAQ answer '{it.get('a', '')}' is a fragment: give claim, proof and action")
            self.text(slide, x + 0.25, y + 0.75, w - 0.5, h - 0.9, body, 13.5, t["ink"], self.bf, min_size=11,
                      para_space=3)
        return slide

    def s_question(self, s):
        """A question to the room (quiz, poll, 'think about it'); answer it on the next slide."""
        t = self.t
        slide = self.new_slide(dark=s.get("dark", False))
        self.page_no += 1
        dark = s.get("dark", False)
        ink = t["on_dark"] if dark else t["ink"]
        if s.get("kicker"):
            self.text(slide, MARGIN, 0.9, 10, 0.3, s["kicker"], 12, t["accent"], self.bf, bold=True, caps=True,
                      spacing=1.5, fit=False, name="Kicker")
        opts = s.get("options", [])
        self.text(slide, MARGIN, 1.4, W_ALL, 2.4 if opts else 4.2, s.get("title", ""), 40, ink, self.hf,
                  bold=True, min_size=26, max_lines=3, anchor="middle" if not opts else "top", name="Headline")
        if opts:
            n = len(opts)
            gap = 0.25
            w = (W_ALL - gap * (n - 1)) / n
            for i, o in enumerate(opts):
                x = MARGIN + i * (w + gap)
                self.card(slide, x, 4.2, w, 1.9, dark=dark)
                self.badge(slide, x + 0.25, 4.4, 0.55, "ABCDEFGH"[i], t["primary"], size=16)
                self.text(slide, x + 0.25, 5.05, w - 0.5, 0.95, o, 16, t["ink"], self.bf, min_size=12, max_lines=3)
        if s.get("prompt"):
            self.text(slide, MARGIN, 6.4, W_ALL, 0.4, s["prompt"], 14, t["muted"] if not dark else t["on_dark_muted"],
                      self.bf, italic=True, fit=False)
        return slide

    def s_milestones(self, s):
        """Dated milestones on one line; state done / now / next."""
        t = self.t
        slide, top, bottom = self._body(s)
        ms = s["milestones"]
        n = len(ms)
        y = self.exhibit_label(slide, s, MARGIN, top, W_ALL)
        ly = y + (bottom - y) * 0.48
        cw = min(2.8, (W_ALL / max(1, n)) * 1.6) if n > 1 else 3.0
        x0, x1 = MARGIN + cw / 2, SLIDE_W - MARGIN - cw / 2
        self.line(slide, MARGIN, ly, SLIDE_W - MARGIN, ly, t["rule"], 3)
        step = (x1 - x0) / max(1, n - 1)
        for i, m in enumerate(ms):
            cx = x0 + i * step if n > 1 else (x0 + x1) / 2
            state = m.get("state", "next")
            fill = t["pos"] if state == "done" else t["accent"] if state == "now" else t["bg"]
            line = None if state in ("done", "now") else t["primary"]
            d = 0.42 if state == "now" else 0.32
            self.rect(slide, cx - d / 2, ly - d / 2, d, d, fill=fill, line=line, line_w=2, shape=MSO_SHAPE.OVAL)
            up = i % 2 == 0
            date_col = "^^" if state == "now" else "**"
            txt = f"{date_col}{m.get('date', '')}{date_col}\n{m.get('label', '')}"
            if m.get("detail"):
                txt += f"\n{m['detail']}"
            bh = 1.7
            self.text(slide, cx - cw / 2, ly - 0.35 - bh if up else ly + 0.35, cw, bh, txt, 15, t["ink"], self.bf,
                      align="center", anchor="bottom" if up else "top", min_size=11, para_space=3, max_lines=5)
        return slide

    def s_actions(self, s):
        """Next steps as an accountable list: action, owner, date, status chip."""
        t = self.t
        slide, top, bottom = self._body(s)
        rows = s["rows"]
        widths = [0.55, 6.3, 2.0, 1.6, 1.68]
        heads = ["#", "Action", "Owner", "Due", "Status"]
        xs = [MARGIN]
        for wv in widths[:-1]:
            xs.append(xs[-1] + wv)
        for x, wv, hd in zip(xs, widths, heads):
            self.text(slide, x, top, wv, 0.35, hd, 11, t["muted"], self.bf, bold=True, caps=True, fit=False,
                      name="Caption")
        self.line(slide, MARGIN, top + 0.42, SLIDE_W - MARGIN, top + 0.42, t["primary"], 1.25)
        rh = min(0.78, (bottom - top - 0.55) / max(1, len(rows)))
        for i, r in enumerate(rows):
            y = top + 0.52 + i * rh
            vals = [f"{i + 1}", r.get("action", ""), r.get("owner", ""), r.get("date", "")]
            for k, (x, wv, v) in enumerate(zip(xs, widths, vals)):
                self.text(slide, x, y, wv - 0.15, rh - 0.08, v, 14 if k == 1 else 13,
                          t["ink"] if k != 0 else t["muted"], self.bf, bold=k == 0, min_size=10.5, max_lines=2,
                          anchor="middle")
            st = r.get("status")
            if st:
                key, label = STATUS.get(st, ("grey", st))
                self.chip(slide, xs[4], y + rh / 2 - 0.15, label, self.tok(key), size=10, w=1.45)
            self.line(slide, MARGIN, y + rh - 0.02, SLIDE_W - MARGIN, y + rh - 0.02, t["rule"], 0.5)
        return slide

    def s_risks(self, s):
        """Risk register: likelihood and impact as dots, mitigation and owner in words."""
        t = self.t
        slide, top, bottom = self._body(s)
        rows = s["rows"]
        widths = [3.4, 1.3, 1.3, 4.4, 1.73]
        heads = ["Risk", "Likelihood", "Impact", "Mitigation", "Owner"]
        xs = [MARGIN]
        for wv in widths[:-1]:
            xs.append(xs[-1] + wv)
        for x, wv, hd in zip(xs, widths, heads):
            self.text(slide, x, top, wv, 0.35, hd, 11, t["muted"], self.bf, bold=True, caps=True, fit=False,
                      name="Caption")
        self.line(slide, MARGIN, top + 0.42, SLIDE_W - MARGIN, top + 0.42, t["primary"], 1.25)
        rh = min(0.95, (bottom - top - 0.55) / max(1, len(rows)))
        for i, r in enumerate(rows):
            y = top + 0.52 + i * rh
            self.text(slide, xs[0], y, widths[0] - 0.2, rh - 0.08, r.get("risk", ""), 14, t["ink"], self.bf,
                      bold=True, min_size=10.5, max_lines=2, anchor="middle")
            for k, key in ((1, "likelihood"), (2, "impact")):
                lv = LEVEL.get(str(r.get(key, "M")), 2)
                col = t["neg"] if lv == 3 else t["accent"] if lv == 2 else t["grey"]
                for j in range(3):
                    self.rect(slide, xs[k] + 0.1 + j * 0.3, y + rh / 2 - 0.1, 0.2, 0.2,
                              fill=col if j < lv else None, line=None if j < lv else t["rule"],
                              shape=MSO_SHAPE.OVAL)
            self.text(slide, xs[3], y, widths[3] - 0.2, rh - 0.08, r.get("mitigation", ""), 13, t["ink"], self.bf,
                      min_size=10.5, max_lines=3, anchor="middle")
            self.text(slide, xs[4], y, widths[4], rh - 0.08, r.get("owner", ""), 13, t["muted"], self.bf,
                      min_size=10.5, max_lines=2, anchor="middle")
            self.line(slide, MARGIN, y + rh - 0.02, SLIDE_W - MARGIN, y + rh - 0.02, t["rule"], 0.5)
            if not r.get("mitigation"):
                self.warn(f"risk '{r.get('risk', '')}' has no mitigation")
        return slide

    def s_references(self, s):
        """Sources slide: numbered, varied in completeness as real sources are; never invented."""
        t = self.t
        slide, top, bottom = self._body(s)
        items = s.get("items", [])
        n = len(items)
        cols = 2 if n > 8 else 1
        per = math.ceil(n / cols)
        w = (W_ALL - 0.5 * (cols - 1)) / cols
        for c in range(cols):
            chunk = items[c * per:(c + 1) * per]
            txt = "\n".join(f"[{c * per + i + 1}]  {it}" for i, it in enumerate(chunk))
            self.text(slide, MARGIN + c * (w + 0.5), top, w, bottom - top, txt, 13, t["ink"], self.bf,
                      min_size=10, para_space=6)
        return slide

    def s_code(self, s):
        """Code, a prompt or a command on a dark panel, with 2-3 points beside it."""
        t = self.t
        slide, top, bottom = self._body(s)
        pts = s.get("points", [])
        cw = W_ALL - (4.2 if pts else 0)
        self.rect(slide, MARGIN, top, cw, bottom - top, fill="1E1E1E")
        self.text(slide, MARGIN + 0.35, top + 0.3, cw - 0.7, bottom - top - 0.6, s.get("code", ""), 15, "E6E6E6",
                  "Courier New", min_size=11, line_spacing=1.15, para_space=0)
        if pts:
            self._side_panel(slide, {"heading": s.get("side_heading", "What to notice"), "points": pts},
                             SLIDE_W - MARGIN - 3.9, top, 3.9, bottom - top)
        return slide

    # ------------------------------------------------------------------ picture slides
    def s_image_full(self, s):
        """Full-bleed photograph with a scrim and the claim over it (story card)."""
        t = self.t
        slide = self.new_slide(dark=True)
        self.page_no += 1
        if s.get("path"):
            self._picture(slide, s["path"], 0, 0, SLIDE_W, SLIDE_H, alt=s.get("alt", ""))
        scrim = self.rect(slide, 0, SLIDE_H * 0.45, SLIDE_W, SLIDE_H * 0.55, fill="000000")
        _alpha(scrim, 55)
        if s.get("kicker"):
            self.text(slide, 0.8, SLIDE_H - 2.75, 9, 0.3, s["kicker"], 12, "FFFFFF", self.bf, bold=True, caps=True,
                      spacing=1.5, fit=False, name="Kicker")
        self.text(slide, 0.8, SLIDE_H - 2.35, 11.2, 1.5, s.get("title", ""), 36, "FFFFFF", self.hf, bold=True,
                  min_size=24, max_lines=2, anchor="bottom", name="Headline")
        if s.get("subtitle"):
            self.text(slide, 0.8, SLIDE_H - 0.8, 10, 0.4, s["subtitle"], 15, "E6E6E6", self.bf, min_size=12,
                      max_lines=1)
        if s.get("credit"):
            self.text(slide, SLIDE_W - 4.6, SLIDE_H - 0.35, 4.2, 0.25, s["credit"], 9, "D0D0D0", self.bf,
                      align="right", fit=False, name="Caption")
        return slide

    def s_gallery(self, s):
        """2-6 pictures with captions (portfolio, product, event highlights)."""
        t = self.t
        slide, top, bottom = self._body(s)
        imgs = s["images"]
        n = len(imgs)
        cols = n if n <= 3 else math.ceil(n / 2)
        rows = math.ceil(n / cols)
        gap = 0.25
        w = (W_ALL - gap * (cols - 1)) / cols
        h = (bottom - top - gap * (rows - 1)) / rows
        for i, im in enumerate(imgs):
            r, c = divmod(i, cols)
            x = MARGIN + c * (w + gap)
            y = top + r * (h + gap)
            ih = h - 0.45
            self._picture(slide, im.get("path", ""), x, y, w, ih, alt=im.get("alt", im.get("caption", "")))
            self.text(slide, x, y + ih + 0.08, w, 0.35, im.get("caption", ""), 12.5, t["ink"], self.bf,
                      min_size=10, max_lines=1)
        return slide

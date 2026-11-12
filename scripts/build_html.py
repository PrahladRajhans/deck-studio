#!/usr/bin/env python3
"""Render a deck-studio JSON spec as one self-contained HTML draft deck.

This is the iteration format: fast, cheap and easy to change. The same spec later builds the
native PPTX (build_deck.py) or feeds Gamma, Canva or Slides, but only after the user approves the
draft. Facts, checks and tokens are resolved exactly as the PPTX builder does, so numbers agree.

    python3 build_html.py spec.json -o out/deck.html [--direction NAME] [--only 1,4] [--link-images]

In the browser: arrows / space / swipe move, N shows speaker notes, G shows all slides as a grid,
P prints one slide per page (PDF). Text that cannot fit at the floor sizes gets a red "does not fit"
badge; render_html.py screenshots every slide and reports those badges.
"""
from __future__ import annotations

import argparse
import base64
import html
import math
import mimetypes
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import SpecError, resolve_theme, slide_seconds, slide_strings, strip_markup, is_label_title, voice_report  # noqa: E402
from spec_io import load_spec, report as spec_report  # noqa: E402  (facts, checks, tokens, validation)

GLYPHS = {"up": "▲", "down": "▼", "check": "✓", "cross": "✗", "star": "★", "arrow": "→", "warn": "!",
          "plus": "+", "minus": "−", "question": "?", "dot": "●", "diamond": "◆", "money": "$", "rupee": "₹",
          "percent": "%", "time": "◷", "people": "●●", "target": "◎"}
STATUS = {"done": ("pos", "Done"), "on_track": ("pos", "On track"), "at_risk": ("accent", "At risk"),
          "late": ("neg", "Late"), "not_started": ("grey", "Not started"), "now": ("accent", "Now"),
          "next": ("primary", "Next"), "later": ("grey", "Later")}
LEVEL = {"H": 3, "M": 2, "L": 1, "high": 3, "medium": 2, "low": 1}

FONT_STACK = {
    "calibri": '"Calibri","Carlito","Segoe UI",Arial,sans-serif',
    "cambria": '"Cambria","Caladea",Georgia,serif',
    "arial": 'Arial,"Liberation Sans","Arimo",Helvetica,sans-serif',
    "bookman old style": '"Bookman Old Style","TeX Gyre Bonum","URW Bookman",Georgia,serif',
    "century schoolbook": '"Century Schoolbook","TeX Gyre Schola","C059",Georgia,serif',
    "palatino linotype": '"Palatino Linotype",Palatino,"TeX Gyre Pagella","P052",Georgia,serif',
    "courier new": '"Courier New","Liberation Mono","Cousine",monospace',
    "georgia": 'Georgia,"Gelasio",serif',
    "times new roman": '"Times New Roman","Liberation Serif","Tinos",serif',
}
# metric-compatible web fallbacks for Office fonts, used when the viewer lacks the Office font
WEB_FALLBACK = ("https://fonts.googleapis.com/css2?family=Carlito:wght@400;700&family=Caladea:wght@400;700"
                "&family=Arimo:wght@400;700&family=Cousine:wght@400;700&display=swap")
NOT_CONTENT = ("cover", "divider", "closing", "agenda", "quote", "image_full", "question", "references")


def esc(x) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def md(text) -> str:
    """Spec markup -> HTML: **bold**, ^^accent^^, newlines."""
    s = esc(text)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\^\^(.+?)\^\^", r'<span class="acc">\1</span>', s)
    return s.replace("\n", "<br>")


def fmt_num(v, nf=None) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return esc(v)
    if not nf or nf == "General":
        if v.is_integer():
            return f"{int(v):,}" if abs(v) >= 10000 else str(int(v))
        return f"{v:,.2f}".rstrip("0").rstrip(".")
    core = re.search(r"[#0][#0,]*(?:\.0+)?%?", nf)
    if not core:
        return f"{v:g}"
    c = core.group(0)
    pct = c.endswith("%")
    dec = len(c.split(".")[1].rstrip("%")) if "." in c else 0
    x = v * 100 if pct else v
    body = f"{x:,.{dec}f}" if "," in c else f"{x:.{dec}f}"
    return nf[:core.start()] + body + ("%" if pct else "") + nf[core.end():]


def wrap(tag, cls, value, fn=md) -> str:
    """<tag class=cls>value</tag>, or nothing when the value is empty."""
    return f'<{tag} class="{cls}">{fn(value)}</{tag}>' if value else ""


def ul(points, cls="") -> str:
    if not points:
        return ""
    if isinstance(points, str):
        return f'<p class="{cls}">{md(points)}</p>'
    return f'<ul class="{cls}">' + "".join(f"<li>{md(p)}</li>" for p in points) + "</ul>"


class HtmlDeck:
    def __init__(self, spec: dict, spec_dir: str, embed: bool = True):
        self.spec = spec
        self.dir = spec_dir
        self.embed = embed
        self.t = resolve_theme(spec.get("direction"), spec.get("theme"))
        self.talk = spec.get("mode", "document") == "talk"
        self.frame = spec.get("frame") or self.t.get("frame", "classic")
        self.warnings: list[str] = []
        self.exhibit_no = 0
        self.section_no = 0
        self.page = 0
        self.n_sections = sum(1 for s in spec["slides"] if s.get("type") == "divider")
        self.id_pages: dict = {}     # slide id -> page number (filled by a first pass, as in the PPTX builder)
        self.pages_seen: dict = {}
        self.cur = 0

    def warn(self, msg):
        self.warnings.append(f"slide {self.cur}: {msg}")

    # ------------------------------------------------------------------ helpers
    def img(self, path, alt="", cls="", style="") -> str:
        if not path:
            return f'<div class="img-missing {cls}" style="{style}">[IMAGE NEEDED]</div>'
        full = path if os.path.isabs(path) else os.path.join(self.dir, path)
        if not os.path.exists(full):
            self.warn(f"image not found: {path}")
            return f'<div class="img-missing {cls}" style="{style}">Image not found: {esc(path)}</div>'
        if not alt:
            self.warn(f"image without alt text: {path}")
        src = path
        if self.embed:
            mime = mimetypes.guess_type(full)[0] or "image/png"
            with open(full, "rb") as fh:
                src = f"data:{mime};base64," + base64.b64encode(fh.read()).decode()
        return f'<img class="{cls}" style="{style}" src="{src}" alt="{esc(alt)}">'

    def side(self, side) -> str:
        if not side:
            return ""
        return (f'<aside class="side"><h4>{md(side.get("heading", ""))}</h4>'
                f'{ul(side.get("points") or side.get("body", ""))}</aside>')

    def exhibit(self, s) -> str:
        if not s.get("exhibit"):
            return ""
        self.exhibit_no += 1
        return f'<div class="exhibit">Exhibit {self.exhibit_no} · {esc(s["exhibit"])}</div>'

    def with_side(self, s, inner) -> str:
        sd = self.side(s.get("side"))
        return f'<div class="row-side">{inner}{sd}</div>' if sd else inner

    # ------------------------------------------------------------------ chrome
    def chrome(self, s, body, cls="") -> str:
        t = self.t
        self.page += 1
        frame = s.get("frame") or self.frame
        kicker = s.get("kicker") or ""
        numbered = self.spec.get("number_kickers", not self.talk)
        if kicker and self.section_no and numbered:
            kicker = f"{self.section_no:02d}&nbsp;&nbsp;&nbsp;{esc(kicker)}"
        else:
            kicker = esc(kicker)
        parts = []
        if kicker and frame == "rail":
            parts.append(f'<div class="rail-kicker">{kicker}</div>')
        steps = ""
        if self.talk and self.n_sections >= 3:
            steps = '<div class="steps">' + "".join(
                f'<i class="{"on" if k + 1 == self.section_no else ""}"></i>' for k in range(self.n_sections)) + "</div>"
        title = s.get("title", "")
        if s.get("letter") and title:
            title = f"^^{s['letter']}:^^ {title}"
        head = ""
        if title:
            head = (f'<header class="head f-{frame}">'
                    f'{f"<div class=kicker>{kicker}</div>" if kicker and frame != "rail" else ""}{steps}'
                    f'<h2 class="title" data-fit="title">{md(title)}</h2>'
                    f'{wrap("div", "subtitle", s.get("subtitle"), md)}'
                    f'</header>')
        elif kicker:
            head = f'<header class="head bare"><div class="kicker">{kicker}</div>{steps}</header>'
        parts.append(head)
        parts.append(f'<div class="body" data-fit="body">{body}</div>')
        if s.get("footnotes"):
            parts.append('<div class="footnotes">' + "".join(
                f"<div><sup>{i}</sup> {md(f)}</div>" for i, f in enumerate(s["footnotes"], 1)) + "</div>")
        if s.get("so_what"):
            parts.append(f'<div class="sowhat"><span>So what</span><p>{md(s["so_what"])}</p></div>')
        src = s.get("source")
        src_html = ""
        if src:
            src_txt = src if src.lower().startswith(("source", "note")) else f"Source: {src}"
            src_html = f'<div class="source">{md(src_txt)}</div>'
        tag = f'<span class="tag">{esc(s["tag"])}</span>' if s.get("tag") else ""
        parts.append(f'<footer class="foot">{src_html or "<div class=source></div>"}{tag}'
                     f'<div class="footline"><span>{esc(self.spec.get("footer", ""))}</span>'
                     f'<span>{self.page}</span></div></footer>')
        return f'<section class="slide t-{esc(s["type"])} {cls}">' + "".join(parts) + self.notes(s) + "</section>"

    def notes(self, s) -> str:
        n = s.get("notes") or {}
        if isinstance(n, str):
            n = {"say": n}
        bits = []
        if self.spec.get("minutes"):
            bits.append(f"<p class=muted>[~{self.seconds(s)} sec]</p>")
        if n.get("say"):
            bits.append(f"<p>{md(n['say'])}</p>")
        for key, lab in (("assumptions", "Assumed (confirm)"), ("sources", "Sources"), ("qa", "Likely questions")):
            v = n.get(key)
            if v:
                v = v if isinstance(v, list) else [v]
                bits.append(f"<h5>{lab}</h5>" + ul(v))
        return f'<template class="notes">{"".join(bits) or "<p class=muted>No notes yet.</p>"}</template>'

    def seconds(self, s) -> int:
        return slide_seconds(self.spec, s)  # shared with the PPTX builder

    def dark(self, s, inner, extra_cls="", style="", count=False) -> str:
        """Full-bleed dark slide without the standard chrome (cover, divider, closing...).
        Page numbers follow the PPTX builder: cover, dividers and closing are not counted."""
        if count:
            self.page += 1
        return (f'<section class="slide dark t-{esc(s["type"])} {extra_cls}" style="{style}">{inner}'
                f'{self.notes(s)}</section>')

    def gradient(self) -> str:
        t = self.t
        if t.get("gradient_to"):
            return f"background:linear-gradient(115deg,#{t['dark']} 0%,#{t['gradient_to']} 100%)"
        return ""

    # ------------------------------------------------------------------ openers
    def s_cover(self, s):
        t = self.t
        style = s.get("style") or t.get("cover", "field")
        fig = s.get("figure")
        meta = s.get("meta") or []
        meta = [meta] if isinstance(meta, str) else meta
        eyebrow = f'<div class="eyebrow">{md(s["eyebrow"])}</div>' if s.get("eyebrow") else ""
        sub = f'<p class="cover-sub">{md(s["subtitle"])}</p>' if s.get("subtitle") else ""
        figh = (f'<div class="cover-fig"><b>{md(fig.get("value", ""))}</b><span>{md(fig.get("label", ""))}</span></div>'
                if fig else "")
        if style == "minimal":
            return (f'<section class="slide t-cover cover-minimal"><div class="cover-grid">'
                    f'<div>{eyebrow}<h1 data-fit="title">{md(s.get("title", ""))}</h1>{sub}</div>{figh}</div>'
                    f'<div class="cover-meta rule">{"&nbsp;&nbsp;·&nbsp;&nbsp;".join(md(m) for m in meta)}</div>'
                    f'{self.notes(s)}</section>')
        if style == "split":
            right = self.img(s["image"], s.get("alt", ""), "cover-img") if s.get("image") else figh
            return (f'<section class="slide t-cover cover-split"><div class="split-dark">{eyebrow}'
                    f'<h1 data-fit="title">{md(s.get("title", ""))}</h1>{sub}'
                    f'<div class="cover-meta">{"<br>".join(md(m) for m in meta)}</div></div>'
                    f'<div class="split-right">{right}</div>{self.notes(s)}</section>')
        inner = (f'<div class="cover-grid">{"" if not eyebrow else eyebrow}'
                 f'<div class="cover-main"><i class="bar"></i><h1 data-fit="title">{md(s.get("title", ""))}</h1>{sub}</div>'
                 f'{figh}</div><div class="cover-meta">{"<br>".join(md(m) for m in meta)}</div>')
        return self.dark(s, inner, "cover-field", self.gradient() if style == "gradient" else "")

    def s_divider(self, s):
        num = s.get("number", self.section_no + 1)
        try:
            self.section_no = int(num)
            label = f"{self.section_no:02d}"
        except (TypeError, ValueError):
            label = str(num)
        style = self.gradient() if self.t.get("cover") == "gradient" else ""
        if self.talk and not s.get("number"):
            return self.dark(s, f'<h1 class="divider-q" data-fit="title">{md(s.get("title", ""))}</h1>', "", style)
        sub = f'<p class="cover-sub">{md(s["subtitle"])}</p>' if s.get("subtitle") else ""
        return self.dark(s, f'<div class="div-num">{esc(label)}</div><i class="bar"></i>'
                            f'<h1 data-fit="title">{md(s.get("title", ""))}</h1>{sub}', "", style)

    def s_closing(self, s):
        fig = s.get("figure")
        ask = (f'<div class="next-label">{esc(s.get("ask_label", "Next step"))}</div><p class="close-ask">{md(s["ask"])}</p>'
               if s.get("ask") else "")
        figh = (f'<div class="cover-fig accent"><b>{md(fig.get("value", ""))}</b><span>{md(fig.get("label", ""))}</span></div>'
                if fig else "")
        lines = "<br>".join(md(x) for x in s.get("lines") or [])
        return self.dark(s, f'<div class="cover-grid"><div><h1 data-fit="title">{md(s.get("title", ""))}</h1>{ask}</div>{figh}</div>'
                            f'<div class="cover-meta">{lines}</div>')

    def s_agenda(self, s):
        self.page += 1
        act = s.get("active")
        items = "".join(
            f'<li class="{"on" if act == i else ("off" if act else "")}"><b>{i:02d}</b>'
            f'<span>{md(it if isinstance(it, str) else it.get("label", ""))}</span></li>'
            for i, it in enumerate(s.get("items", []), 1))
        return (f'<section class="slide t-agenda"><div class="ag-panel"><h2>{md(s.get("title", "Contents"))}</h2></div>'
                f'<div class="ag-dark"><ol class="agenda">{items}</ol><span class="ag-page">{self.page}</span></div>'
                f'{self.notes(s)}</section>')

    def s_exec_summary(self, s):
        rows = []
        for i, r in enumerate(s.get("rows", []), 1):
            page = self.id_pages.get(r.get("ref"), r.get("pages", ""))
            if r.get("ref") and self.id_pages and r["ref"] not in self.id_pages:
                self.warn(f"exec summary ref '{r['ref']}' matches no slide id")
            if isinstance(page, int):
                page = f"p.{page}"
            rows.append(f'<div class="es-row{" hl" if r.get("highlight") else ""}"><div class="es-n">{i}</div>'
                        f'<div><div class="es-claim">{md(r.get("claim", ""))}</div>'
                        f'<div class="es-detail">{md(r.get("detail", ""))}</div></div><div class="es-ref">{"→ " + esc(page) if page else ""}</div></div>')
        return self.chrome(s, f'<div class="es">{"".join(rows)}</div>')

    def s_framework(self, s):
        self.page += 1
        pts = "".join(f'<li><b class="fw-n">{i}</b><div><h3>{md(p.get("heading", ""))}</h3><p>{md(p.get("body", ""))}</p></div></li>'
                      for i, p in enumerate(s.get("points", []), 1))
        kick = f'<div class="kicker">{esc(s.get("kicker", ""))}</div>' if s.get("kicker") else ""
        return (f'<section class="slide t-framework"><div class="fw-rail">{kick}<h2 data-fit="title">{md(s.get("title", ""))}</h2></div>'
                f'<div class="fw-body body" data-fit="body"><ol class="fw-points">{pts}</ol></div>'
                f'<footer class="foot fw-foot"><div class="source">{md(s.get("source", ""))}</div>'
                f'<div class="footline"><span>{esc(self.spec.get("footer", ""))}</span><span>{self.page}</span></div></footer>'
                f'{self.notes(s)}</section>')

    def s_statement(self, s):
        claim = s.get("claim", "")
        pts = s.get("points") or []
        grid = ('<div class="st-points">' + "".join(f"<div>{md(p)}</div>" for p in pts) + "</div>") if pts else ""
        big = f'<p class="st-claim">{md(claim)}</p>' if s.get("title") else f'<h2 class="st-claim big" data-fit="title">{md(claim)}</h2>'
        return self.chrome(s, f'<div class="st">{big}{grid}</div>')

    def s_quote(self, s):
        return self.chrome(s, f'<figure class="qt"><span class="qmark">“</span><blockquote>{md(s.get("quote", ""))}</blockquote>'
                              f'<figcaption>{md(s.get("attribution", ""))}</figcaption></figure>')

    def s_question(self, s):
        opts = "".join(f'<li><b>{chr(65 + i)}</b>{md(o)}</li>' for i, o in enumerate(s.get("options") or []))
        inner = (f'<div class="qq"><h1 data-fit="title">{md(s.get("title", ""))}</h1>'
                 f'{f"<ol class=qopts>{opts}</ol>" if opts else ""}'
                 f'{wrap("p", "qprompt", s.get("prompt"), md)}</div>')
        if s.get("dark", False):
            return self.dark(s, inner, count=True)
        return self.chrome(dict(s, title=""), inner, "light-q")

    # ------------------------------------------------------------------ numbers
    def s_big_number(self, s):
        pts = s.get("points") or []
        if not pts:
            self.warn("big number without proof points: add 1-3 lines that make it credible")
        return self.chrome(s, f'<div class="bn"><div><div class="bn-val">{md(s.get("value", ""))}</div>'
                              f'<div class="bn-label">{md(s.get("label", ""))}</div>'
                              f'<p class="muted">{md(s.get("context", ""))}</p></div>{ul(pts, "bn-pts")}</div>')

    def s_data_contrast(self, s):
        items = s.get("items", [])[:2]
        hl = s.get("highlight", 1)
        cards = [f'<div class="dc-card{" hl" if i == hl else ""}"><div class="dc-val">{md(it.get("value", ""))}</div>'
                 f'<h3>{md(it.get("label", ""))}</h3><p>{md(it.get("detail", ""))}</p></div>' for i, it in enumerate(items)]
        vs = f'<div class="dc-vs">{esc(s.get("versus", "vs"))}</div>'
        return self.chrome(s, f'<div class="dc">{vs.join(cards)}</div>')

    def s_kpi(self, s):
        hl = s.get("highlight")
        tiles = []
        for i, it in enumerate(s.get("items", [])):
            d = it.get("delta")
            chip = ""
            if d:
                good = it.get("good", not str(d).strip().startswith(("-", "−", "▼")))
                chip = f'<span class="chip {"pos" if good else "neg"}">{md(d)}</span>'
            tiles.append(f'<div class="kpi{" hl" if i == hl else ""}"><div class="kpi-val">{md(it.get("value", ""))}</div>'
                         f'<div class="kpi-label">{md(it.get("label", ""))}</div>{chip}'
                         f'<p class="muted">{md(it.get("detail", ""))}</p></div>')
        n = len(tiles)
        return self.chrome(s, self.exhibit(s) + f'<div class="kpis" style="--n:{min(n, 4)}">{"".join(tiles)}</div>')

    def s_chart(self, s):
        ch = s["chart"]
        svg = chart_svg(ch, self.t, side=bool(s.get("side")), warn=self.warn)
        return self.chrome(s, self.with_side(s, f'<div class="chart-col">{self.exhibit(s)}<div class="chart">{svg}</div></div>'))

    def table_html(self, columns, rows, highlight_row=None, total_row=False, widths=None):
        num = re.compile(r"^[\s(+−-]*[₹$€£]?\s?[\d.,]+\s?(%|x|×|cr|bn|mn|m|k|pp|bps)?\)?\s*$", re.I)
        cols = ""
        if widths:
            tot = float(sum(widths))
            cols = "<colgroup>" + "".join(f'<col style="width:{w / tot * 100:.1f}%">' for w in widths) + "</colgroup>"
        numcol = [bool(rows) and all(num.match(str(r[j])) for r in rows if j < len(r)) for j in range(len(columns))]
        head = "".join(f'<th class="{"num" if j and numcol[j] else ""}">{md(c)}</th>' for j, c in enumerate(columns))
        body = []
        for i, r in enumerate(rows):
            cls = []
            if i == highlight_row:
                cls.append("hl")
            if total_row and i == len(rows) - 1:
                cls.append("total")
            cells = "".join(f'<td class="{"num" if j and num.match(str(c)) else ""}">{md(c)}</td>' for j, c in enumerate(r))
            body.append(f'<tr class="{" ".join(cls)}">{cells}</tr>')
        # right-align numeric headers too
        return f'<table class="tbl">{cols}<thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'

    def s_table(self, s):
        t = self.table_html(s["columns"], s["rows"], s.get("highlight_row"), s.get("total_row"), s.get("widths"))
        note = f'<p class="caption">{md(s["note"])}</p>' if s.get("note") else ""
        return self.chrome(s, self.with_side(s, f'<div class="chart-col">{self.exhibit(s)}{t}{note}</div>'))

    def s_options(self, s):
        crit, opts = s["criteria"], s["options"]
        w = [c.get("weight", 1) for c in crit]
        ws = float(sum(w))
        cols = ["Option"] + [f"{c['name']} ({int(round(c.get('weight', 1) / ws * 100))}%)" for c in crit] + ["Weighted score"]
        rows, tots = [], []
        for o in opts:
            if len(o["scores"]) != len(crit):
                raise SpecError(f"slide {self.cur}: option '{o['name']}' has {len(o['scores'])} scores for {len(crit)} criteria")
            tot = sum(a * b for a, b in zip(o["scores"], w)) / ws
            tots.append(tot)
            rows.append([o["name"]] + [str(v) for v in o["scores"]] + [f"{tot:.1f}"])
        best = max(range(len(tots)), key=lambda i: tots[i])
        rec = s.get("recommended", best)
        if rec != best:
            self.warn(f"recommended option '{opts[rec]['name']}' is not the top weighted score ('{opts[best]['name']}')")
        scale = s.get("scale", "Scores 1 (weak) to 5 (strong); weights shown in brackets")
        return self.chrome(s, self.exhibit(s) + self.table_html(cols, rows, rec, widths=[2.2] + [1] * len(crit) + [1.2])
                           + f'<p class="caption">{md(scale)}</p>')

    # ------------------------------------------------------------------ diagrams
    def s_process(self, s):
        hl = s.get("highlight")
        steps = s.get("steps", [])
        out = "".join(f'<li class="{"hl" if i == hl else ""}"><div class="pr-n">{esc(st.get("label") or i + 1)}</div>'
                      f'<h3>{md(st.get("heading", ""))}</h3><p>{md(st.get("body", ""))}</p></li>' for i, st in enumerate(steps))
        return self.chrome(s, self.exhibit(s) + f'<ol class="process" style="--n:{len(steps)}">{out}</ol>')

    def s_cycle(self, s):
        steps = s.get("steps", [])
        n = max(1, len(steps))
        hl = s.get("highlight")
        nodes = []
        for i, st in enumerate(steps):
            a = -math.pi / 2 + 2 * math.pi * i / n
            x, y = 50 + 36 * math.cos(a), 50 + 36 * math.sin(a)
            nodes.append(f'<div class="cy-node{" hl" if i == hl else ""}" style="left:{x:.1f}%;top:{y:.1f}%">'
                         f'<b>{i + 1}</b><h3>{md(st.get("heading", ""))}</h3><p>{md(st.get("body", ""))}</p></div>')
        center = f'<div class="cy-center">{md(s.get("center", ""))}</div>' if s.get("center") else ""
        inner = f'<div class="cycle"><div class="cy-ring"></div>{center}{"".join(nodes)}</div>'
        return self.chrome(s, self.with_side(s, inner))

    def s_funnel(self, s):
        st = s.get("stages", [])
        hl = s.get("highlight")
        n = max(1, len(st))
        rows = []
        for i, g in enumerate(st):
            w = 100 - i * (55 / max(1, n - 1)) if n > 1 else 100
            val = g.get("value", "")
            val = fmt_num(val, "#,##0") if isinstance(val, (int, float)) else md(val)
            conv = f'<span class="chip">{md(g["conversion"])}</span>' if g.get("conversion") else ""
            rows.append(f'<div class="fn-row"><div class="fn-barwrap"><div class="fn-bar{" hl" if i == hl else ""}" style="width:{w:.0f}%">'
                        f'<span>{md(g.get("label", ""))}</span><b>{val}</b></div></div>'
                        f'<div class="fn-note">{conv}{md(g.get("note", ""))}</div></div>')
        return self.chrome(s, self.exhibit(s) + f'<div class="funnel">{"".join(rows)}</div>')

    def s_pyramid(self, s):
        lv = s.get("levels", [])
        n = max(1, len(lv))
        hl = s.get("highlight")
        rows = []
        for i, l in enumerate(lv):
            w0 = 28 + 72 * i / n
            w1 = 28 + 72 * (i + 1) / n
            inset = (w1 - w0) / 2 / w1 * 100
            rows.append(f'<div class="py-row"><div class="py-shape"><div class="py-lv{" hl" if i == hl else ""}" '
                        f'style="width:{w1:.1f}%;clip-path:polygon({inset:.1f}% 0,{100 - inset:.1f}% 0,100% 100%,0 100%)">'
                        f'{md(l.get("label", ""))}</div></div><div class="py-detail">{md(l.get("detail", ""))}</div></div>')
        return self.chrome(s, f'<div class="pyramid">{"".join(rows)}</div>')

    def s_hub(self, s):
        sp = s.get("spokes", [])
        n = max(1, len(sp))
        hl = s.get("highlight")
        cards, lines = [], []
        for i, k in enumerate(sp):
            a = -math.pi / 2 + 2 * math.pi * i / n
            x, y = 50 + 37 * math.cos(a), 50 + 38 * math.sin(a)
            lines.append(f'<line x1="50" y1="50" x2="{x:.1f}" y2="{y:.1f}"/>')
            cards.append(f'<div class="hub-card{" hl" if i == hl else ""}" style="left:{x:.1f}%;top:{y:.1f}%">'
                         f'<h3>{md(k.get("heading", ""))}</h3><p>{md(k.get("body", ""))}</p></div>')
        svg = f'<svg class="hub-lines" viewBox="0 0 100 100" preserveAspectRatio="none">{"".join(lines)}</svg>'
        return self.chrome(s, f'<div class="hub">{svg}<div class="hub-center">{md(s.get("center", ""))}</div>{"".join(cards)}</div>')

    def s_issue_tree(self, s):
        hl = s.get("highlight")
        br = "".join(f'<div class="it-branch{" hl" if i == hl else ""}"><div class="it-label">{md(b.get("label", ""))}</div>'
                     f'<div class="it-leaves">{"".join(f"<span>{md(x)}</span>" for x in b.get("leaves", []))}</div></div>'
                     for i, b in enumerate(s.get("branches", [])))
        return self.chrome(s, f'<div class="itree"><div class="it-root">{md(s.get("root", ""))}</div><div class="it-branches">{br}</div></div>')

    def s_matrix(self, s):
        q = s.get("quadrants", ["", "", "", ""])
        hq = s.get("highlight_quadrant", 1)
        quads = "".join(f'<div class="mx-q{" hl" if k == hq else ""}"><span>{md(q[k] if k < len(q) else "")}</span></div>' for k in range(4))
        items = "".join(f'<div class="mx-item{" hl" if it.get("highlight") else ""}" style="left:{it["x"] * 100:.1f}%;top:{(1 - it["y"]) * 100:.1f}%">'
                        f'<i></i><span>{md(it["label"])}</span></div>' for it in s.get("items", []))
        xa, ya = s.get("x_axis", {}), s.get("y_axis", {})
        inner = (f'<div class="chart-col">{self.exhibit(s)}<div class="mx-wrap"><div class="mx-y">{md(ya.get("label", ""))} →</div>'
                 f'<div class="mx">{quads}{items}</div><div class="mx-x">{md(xa.get("label", ""))} →</div></div></div>')
        return self.chrome(s, self.with_side(s, inner))

    def s_swot(self, s):
        hl = s.get("highlight")
        names = [("strengths", "Strengths"), ("weaknesses", "Weaknesses"), ("opportunities", "Opportunities"), ("threats", "Threats")]
        boxes = "".join(f'<div class="sw{" hl" if hl in (k, i) else ""}"><h3>{lab}</h3>{ul(s.get(k, []))}</div>'
                        for i, (k, lab) in enumerate(names))
        return self.chrome(s, f'<div class="swot">{boxes}</div>')

    def s_venn(self, s):
        sets = s.get("sets", [])[:3]
        pos = {2: [(36, 50), (64, 50)], 3: [(38, 37), (62, 37), (50, 64)]}.get(len(sets), [(50, 50)])
        cols = ["primary", "accent", "grey"]
        circles = "".join(f'<div class="vn-c" style="left:{x}%;top:{y}%;background:var(--{cols[i]})"></div>' for i, (x, y) in enumerate(pos))
        lpos = {2: [(21, 50), (79, 50)], 3: [(25, 28), (75, 28), (50, 82)]}.get(len(sets), [(50, 50)])
        labels = "".join(f'<div class="vn-l" style="left:{x}%;top:{y}%"><h3>{md(st.get("label", ""))}</h3><p>{md(st.get("detail", ""))}</p></div>'
                         for st, (x, y) in zip(sets, lpos))
        ov = f'<div class="vn-ov" style="top:{50 if len(sets) == 2 else 47}%">{md(s.get("overlap", ""))}</div>' if s.get("overlap") else ""
        return self.chrome(s, self.with_side(s, f'<div class="venn{" two" if len(sets) == 2 else ""}">{circles}{labels}{ov}</div>'))

    def s_journey(self, s):
        st = s["stages"]
        rows = s.get("rows", ["doing", "thinking", "pain", "opportunity"])
        labels = s.get("row_labels", {"doing": "Doing", "thinking": "Thinking / feeling", "pain": "Pain points", "opportunity": "Opportunity"})
        n = len(st)
        pts = []
        for i, x in enumerate(st):
            f = max(-1, min(1, float(x.get("feeling", 0))))
            pts.append(((i + 0.5) / n * 100, 50 - f * 38, f))
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts)
        dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" class="{"pos" if f > 0 else "neg" if f < 0 else "mid"}"/>' for x, y, f in pts)
        emo = (f'<svg viewBox="0 0 100 100" preserveAspectRatio="none" class="jr-emo"><line x1="0" y1="50" x2="100" y2="50" class="base"/>'
               f'<polyline points="{poly}"/>{dots}</svg>')
        grid = [f'<div class="jr-lab">Stage</div>'] + [f'<div class="jr-stage">{md(x.get("name", ""))}</div>' for x in st]
        grid += ['<div class="jr-lab">Emotion</div>', f'<div class="jr-emo-cell" style="grid-column:span {n}">{emo}</div>']
        for key in rows:
            grid.append(f'<div class="jr-lab{" acc" if key == "opportunity" else ""}">{md(labels.get(key, key.title()))}</div>')
            grid += [f'<div class="jr-cell{" opp" if key == "opportunity" else ""}">{md(x.get(key, ""))}</div>' for x in st]
        return self.chrome(s, f'<div class="journey" style="--n:{n};--r:{len(rows)}">{"".join(grid)}</div>')

    # ------------------------------------------------------------------ compare and plan
    def s_compare(self, s):
        hl = s.get("highlight")
        cols = "".join(f'<div class="cmp{" hl" if i == hl else ""}"><h3>{md(c.get("heading", ""))}</h3>{ul(c.get("points", []))}</div>'
                       for i, c in enumerate(s.get("columns", [])))
        return self.chrome(s, f'<div class="cols" style="--n:{len(s.get("columns", []))}">{cols}</div>')

    def s_columns(self, s):
        hl = s.get("highlight")
        cols = []
        for i, c in enumerate(s.get("columns", [])):
            g = GLYPHS.get(c.get("icon", ""), c.get("icon") or str(i + 1))
            cols.append(f'<div class="colx{" hl" if i == hl else ""}"><div class="badge">{esc(g)}</div><h3>{md(c.get("heading", ""))}</h3>'
                        f'{ul(c.get("points") or c.get("body", ""))}</div>')
        return self.chrome(s, f'<div class="cols ruled" style="--n:{len(cols)}">{"".join(cols)}</div>')

    def s_cards(self, s):
        hl = s.get("highlight")
        items = s.get("items", [])
        n = len(items)
        per = n if n <= 4 else math.ceil(n / 2)
        cards = "".join(f'<div class="card{" hl" if i == hl else ""}">{f"<div class=card-n>{i + 1:02d}</div>" if s.get("numbered") else ""}'
                        f'<h3>{md(it.get("heading", ""))}</h3><p>{md(it.get("body", ""))}</p></div>' for i, it in enumerate(items))
        return self.chrome(s, f'<div class="cards" style="--n:{per}">{cards}</div>')

    def s_before_after(self, s):
        def panel(p, cls, default):
            im = self.img(p["image"], p.get("alt", ""), "ba-img") if p.get("image") else ""
            return (f'<div class="ba {cls}"><div class="ba-label">{esc(p.get("label", default))}</div>{im}'
                    f'<h3>{md(p.get("heading", ""))}</h3>{ul(p.get("points", []))}</div>')
        return self.chrome(s, f'<div class="ba-wrap">{panel(s.get("before", {}), "before", "Before")}<div class="ba-arrow">→</div>'
                              f'{panel(s.get("after", {}), "after", "After")}</div>')

    def s_pricing(self, s):
        rec = s.get("recommended")
        tiers = []
        for i, tr in enumerate(s.get("tiers", [])):
            lab = f'<div class="badge-label">{esc(s.get("recommended_label", "Recommended"))}</div>' if i == rec else ""
            tiers.append(f'<div class="tier{" hl" if i == rec else ""}">{lab}<h3>{md(tr.get("name", ""))}</h3>'
                         f'<div class="price">{md(tr.get("price", ""))}<span>{md(tr.get("period", ""))}</span></div>{ul(tr.get("features", []))}</div>')
        return self.chrome(s, f'<div class="cols" style="--n:{len(tiers)}">{"".join(tiers)}</div>')

    def s_timeline(self, s):
        periods, rows = s["periods"], s["rows"]
        has_owner = any(r.get("owner") for r in rows)
        np_ = len(periods)
        head = '<div class="tl-lab"></div>' + "".join(f'<div class="tl-p">{md(p)}</div>' for p in periods) + \
               ('<div class="tl-p">Owner</div>' if has_owner else "")
        body = []
        for r in rows:
            bars = []
            for b in r.get("bars", []):
                s0, s1 = b["start"], b.get("end", b["start"])
                if b.get("milestone"):
                    bars.append(f'<div class="tl-ms" style="grid-column:{s0 + 1}"><i></i><span>{md(b.get("label", ""))}</span></div>')
                else:
                    bars.append(f'<div class="tl-bar{" hl" if b.get("highlight") else ""}" style="grid-column:{s0 + 1}/{s1 + 2}">{md(b.get("label", ""))}</div>')
            body.append(f'<div class="tl-lab">{md(r.get("label", ""))}</div><div class="tl-track" style="grid-column:span {np_}">'
                        f'{"".join(bars)}</div>' + (f'<div class="tl-owner">{md(r.get("owner", ""))}</div>' if has_owner else ""))
        cols = f"minmax(220px,2.6fr) repeat({np_},1fr)" + (" 1.4fr" if has_owner else "")
        return self.chrome(s, self.exhibit(s) + f'<div class="timeline" style="grid-template-columns:{cols};--np:{np_}">{head}{"".join(body)}</div>')

    def s_milestones(self, s):
        ms = s.get("milestones", [])
        out = "".join(f'<li class="{esc(m.get("state", "next"))}"><div class="ms-date">{md(m.get("date", ""))}</div><i></i>'
                      f'<h3>{md(m.get("label", ""))}</h3><p>{md(m.get("detail", ""))}</p></li>' for m in ms)
        return self.chrome(s, f'<ol class="milestones" style="--n:{len(ms)}">{out}</ol>')

    def s_roadmap(self, s):
        hl = s.get("highlight")
        lanes = "".join(f'<div class="lane{" hl" if i == hl else ""}"><h3>{md(l.get("heading", ""))}</h3>'
                        + "".join(f'<div class="lane-item"><h4>{md(it.get("heading", ""))}</h4><p>{md(it.get("body", ""))}</p></div>' for it in l.get("items", []))
                        + "</div>" for i, l in enumerate(s.get("lanes", [])))
        return self.chrome(s, f'<div class="cols" style="--n:{len(s.get("lanes", []))}">{lanes}</div>')

    def s_actions(self, s):
        rows = []
        for r in s.get("rows", []):
            key, lab = STATUS.get(r.get("status", ""), ("grey", r.get("status", "")))
            rows.append([md(r.get("action", "")), md(r.get("owner", "")), md(r.get("date", "")), f'<span class="chip {key}">{esc(lab)}</span>'])
        head = "".join(f"<th>{h}</th>" for h in ("Action", "Owner", "By", "Status"))
        body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
        return self.chrome(s, f'<table class="tbl actions"><colgroup><col style="width:52%"><col style="width:18%"><col style="width:14%"><col style="width:16%"></colgroup>'
                              f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>')

    def s_risks(self, s):
        def dots(v):
            n = LEVEL.get(str(v), 0)
            return f'<span class="dots l{n}">' + "".join("●" if k < n else "○" for k in range(3)) + "</span>"
        body = []
        for r in s.get("rows", []):
            if not r.get("mitigation"):
                self.warn("risk without mitigation")
            body.append(f'<tr><td>{md(r.get("risk", ""))}</td><td>{dots(r.get("likelihood"))}</td><td>{dots(r.get("impact"))}</td>'
                        f'<td>{md(r.get("mitigation", ""))}</td><td>{md(r.get("owner", ""))}</td></tr>')
        head = "".join(f"<th>{h}</th>" for h in ("Risk", "Likelihood", "Impact", "Mitigation", "Owner"))
        return self.chrome(s, f'<table class="tbl"><colgroup><col style="width:30%"><col style="width:11%"><col style="width:11%"><col style="width:34%"><col style="width:14%"></colgroup>'
                              f'<thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>')

    def s_ask(self, s):
        fig = s.get("figure")
        if not fig:
            self.warn("ask without a number: give the figure the decision moves")
        if not s.get("cost"):
            self.warn("ask without cost")
        figh = f'<div class="ask-fig"><b>{md(fig.get("value", ""))}</b><span>{md(fig.get("label", ""))}</span></div>' if fig else ""
        why = f'<div><h4>Why now</h4>{ul(s.get("why", []))}</div>' if s.get("why") else ""
        cost = f'<div><h4>Cost and impact</h4>{ul(s.get("cost", []))}</div>' if s.get("cost") else ""
        return self.chrome(s, f'<div class="ask{"" if fig else " nofig"}"><div class="ask-main"><div class="ask-label">The ask</div>'
                              f'<p class="ask-line">{md(s.get("ask", ""))}</p>'
                              f'<div class="ask-cols">{why}{cost}</div><p class="ask-owner">{md(s.get("owner", ""))}</p></div>{figh}</div>')

    # ------------------------------------------------------------------ people, proof, pictures
    def s_team(self, s):
        ppl = []
        for p in s.get("people", []):
            init = "".join(w[0] for w in strip_markup(p.get("name", "?")).split()[:2]).upper()
            face = self.img(p["photo"], p.get("name", ""), "face") if p.get("photo") else f'<div class="face init">{esc(init)}</div>'
            ppl.append(f'<div class="person">{face}<h3>{md(p.get("name", ""))}</h3><div class="role">{md(p.get("role", ""))}</div>'
                       f'<p>{md(p.get("line", ""))}</p></div>')
        n = len(ppl)
        return self.chrome(s, f'<div class="team" style="--n:{min(n, 4) if n <= 4 else math.ceil(n / 2)}">{"".join(ppl)}</div>')

    def s_faq(self, s):
        items = []
        for it in s.get("items", []):
            if len(strip_markup(it.get("a", "")).split()) < 4:
                self.warn("FAQ answer is a fragment: give claim, proof, action")
            items.append(f'<div class="faq-i"><h3>{md(it.get("q", ""))}</h3><p>{md(it.get("a", ""))}</p>'
                         f'{wrap("p", "proof", it.get("proof"), md)}</div>')
        return self.chrome(s, f'<div class="faq">{"".join(items)}</div>')

    def s_image(self, s):
        side = s.get("side", "right")
        iw = float(s.get("image_width", 6.2))  # inches, as in the PPTX builder
        frac = iw / 12.13 if iw > 1 else iw
        im = f'<div class="im-pic">{self.img(s.get("path"), s.get("alt", ""), "fill")}</div>'
        txt = f'<div class="im-text"><h3>{md(s.get("heading", ""))}</h3>{ul(s.get("points", []))}</div>'
        order = im + txt if side == "left" else txt + im
        cols = f"{frac}fr {1 - frac}fr" if side == "left" else f"{1 - frac}fr {frac}fr"
        return self.chrome(s, f'<div class="im" style="grid-template-columns:{cols}">{order}</div>')

    def s_image_full(self, s):
        self.page += 1
        cap = f'<div class="credit">{md(s["credit"])}</div>' if s.get("credit") else ""
        return (f'<section class="slide dark t-image_full">{self.img(s.get("path"), s.get("alt", ""), "bleed")}<div class="scrim"></div>'
                f'<div class="if-text">{wrap("div", "kicker", s.get("kicker"), esc)}'
                f'<h1 data-fit="title">{md(s.get("title", ""))}</h1>{wrap("p", "cover-sub", s.get("subtitle"), md)}</div>'
                f'{cap}{self.notes(s)}</section>')

    def s_gallery(self, s):
        ims = s.get("images", [])
        cells = "".join(f'<figure>{self.img(i.get("path"), i.get("alt") or i.get("caption", ""), "fill")}<figcaption>{md(i.get("caption", ""))}</figcaption></figure>' for i in ims)
        return self.chrome(s, f'<div class="gallery" style="--n:{min(len(ims), 4)}">{cells}</div>')

    def s_code(self, s):
        side = ""
        if s.get("points"):
            side = f'<aside class="side"><h4>{md(s.get("side_heading", "What to notice"))}</h4>{ul(s["points"])}</aside>'
        return self.chrome(s, f'<div class="row-side"><pre class="code">{esc(s.get("code", ""))}</pre>{side}</div>')

    def s_bullets(self, s):
        items = s.get("items", [])
        if len(items) > 6:
            self.warn("more than six bullets: split the slide or choose a structured type")
        return self.chrome(s, self.with_side(s, ul(items, "bullets")))

    def s_custom(self, s):
        """Hand-composed body (spec `html`), inside the standard chrome and tokens. The HTML lives in the
        spec, so the draft stays reproducible; keep it to the deck's CSS variables (var(--accent) etc.)."""
        if not s.get("html"):
            raise SpecError(f"slide {self.cur}: custom slide needs an 'html' body")
        if re.search(r"<script|on\w+=", s["html"], re.I):
            raise SpecError(f"slide {self.cur}: custom html may not contain scripts or event handlers")
        self.warn("custom layout: say why no standard type fits; the PPTX needs a hand build of this slide")
        return self.chrome(s, f'<div class="custom">{s["html"]}</div>')

    def s_references(self, s):
        return self.chrome(s, '<ol class="refs">' + "".join(f"<li>{md(x)}</li>" for x in s.get("items", [])) + "</ol>")

    # ------------------------------------------------------------------ deck
    def build(self) -> str:
        t = self.t
        slides, run = [], []
        for i, s in enumerate(self.spec["slides"], 1):
            self.cur = i
            typ = s.get("type")
            fn = getattr(self, f"s_{typ}", None)
            if fn is None:
                raise SpecError(f"slide {i}: unknown type '{typ}' (see build_deck.py --schema)")
            if typ == "agenda" and self.talk:
                self.warn("agenda in talk mode: keep it only if it orients (workshop, long or teaching session); "
                          "for a short persuasive talk, question dividers usually work better")
            if self.spec.get("mode", "document") == "document" and typ not in NOT_CONTENT \
                    and s.get("title") and is_label_title(s["title"]):
                self.warn(f"title is a label, not a claim: '{strip_markup(s['title'])}'")
            if self.talk and typ not in ("cover", "closing", "references"):
                if len(strip_markup(s.get("title", ""))) > 60:
                    self.warn("talk headline over 60 characters: it should read in one glance")
                words = sum(len(strip_markup(x).split()) for x in slide_strings(s))
                if words > 50:
                    self.warn(f"{words} words on a talk slide (aim under 40): move detail to the notes")
            run = (run + [typ])[-3:]
            if len(run) == 3 and len(set(run)) == 1 and typ not in ("divider",):
                self.warn(f"'{typ}' three times running: fine for like-for-like comparisons; change it if the "
                          "communication task changed")
            slides.append(fn(s))
            if s.get("id"):
                self.pages_seen[s["id"]] = self.page
        return PAGE.format(
            title=esc(self.spec.get("title", "Deck draft")), css=self.css(), slides="\n".join(slides),
            fonts=self.font_link(), talk="talk" if self.talk else "doc", js=JS)

    def font_link(self) -> str:
        hf = self.spec.get("html_fonts") or {}
        links = [f'<link rel="stylesheet" href="{WEB_FALLBACK}">']
        if hf.get("url"):
            links.append(f'<link rel="stylesheet" href="{esc(hf["url"])}">')
        return "\n".join(links)

    def css(self) -> str:
        t = self.t
        hf = self.spec.get("html_fonts") or {}
        head = f'"{hf["heading"]}",' + FONT_STACK.get(t["heading_font"].lower(), "serif") if hf.get("heading") \
            else FONT_STACK.get(t["heading_font"].lower(), f'"{t["heading_font"]}",serif')
        body = f'"{hf["body"]}",' + FONT_STACK.get(t["body_font"].lower(), "sans-serif") if hf.get("body") \
            else FONT_STACK.get(t["body_font"].lower(), f'"{t["body_font"]}",sans-serif')
        toks = "".join(f"--{k.replace('_', '-')}:#{t[k]};" for k in
                       ("bg", "ink", "muted", "primary", "accent", "panel", "rule", "grey", "dark", "on_dark",
                        "on_dark_muted", "pos", "neg"))
        radius = f"{float(t.get('radius', 0)) * 144:.0f}px"
        card = {"tint": "background:var(--panel);",
                "border": "background:var(--bg);border:2px solid var(--rule);",
                "shadow": "background:var(--bg);box-shadow:0 6px 24px rgba(0,0,0,.10);"}.get(t.get("card", "tint"))
        return (f":root{{{toks}--hf:{head};--bf:{body};--radius:{radius};}}\n"
                f".card,.kpi,.cmp,.tier,.lane-item,.person,.sw,.dc-card,.ba,.faq-i,.cy-node,.hub-card{{{card}}}\n" + CSS)


def chart_svg(ch, t, side=False, warn=print) -> str:
    """Native-looking SVG for the chart kinds the PPTX builder supports."""
    kind = ch.get("kind", "column")
    W = 1100 if side else 1700
    H = 560
    nf = ch.get("number_format")
    cats = [str(c) for c in ch.get("categories", [])]
    hl = ch.get("highlight")
    hl = [hl] if isinstance(hl, (int, str)) else (hl or [])
    hl_idx = {h if isinstance(h, int) else cats.index(h) for h in hl if isinstance(h, int) or h in cats}
    C = {k: f"#{t[k]}" for k in ("primary", "accent", "grey", "muted", "rule", "ink", "panel", "bg")}
    palette = [C["primary"], C["grey"], C["muted"], C["rule"], C["accent"]]
    out = []

    def txt(x, y, s, anchor="middle", size=24, fill=None, weight=400):
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" '
                   f'fill="{fill or C["ink"]}" font-weight="{weight}">{esc(s)}</text>')

    alt = ch.get("alt") or f"{kind} chart: " + ", ".join(cats)
    if kind in ("pie", "doughnut"):
        vals = [float(v) for v in ch["series"][0]["values"]]
        tot = sum(vals) or 1
        cx, cy, r = H / 2 + 20, H / 2, H / 2 - 30
        a0 = -math.pi / 2
        ramp = [C["primary"], C["grey"], C["muted"], C["rule"], C["panel"]]
        for i, v in enumerate(vals):
            a1 = a0 + 2 * math.pi * v / tot
            large = 1 if a1 - a0 > math.pi else 0
            x0, y0, x1, y1 = cx + r * math.cos(a0), cy + r * math.sin(a0), cx + r * math.cos(a1), cy + r * math.sin(a1)
            col = C["accent"] if i in hl_idx else ramp[i % len(ramp)]
            out.append(f'<path d="M{cx},{cy} L{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f} Z" fill="{col}" stroke="{C["bg"]}" stroke-width="3"/>')
            am = (a0 + a1) / 2
            lr = r * (0.78 if kind == "doughnut" else 0.62)
            light = _lum(col) > 0.55
            txt(cx + lr * math.cos(am), cy + lr * math.sin(am) + 8, fmt_num(v, nf), size=24,
                fill=C["ink"] if light else "#FFFFFF", weight=700)
            a0 = a1
        if kind == "doughnut":
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.55:.1f}" fill="{C["bg"]}"/>')
        for i, c in enumerate(cats):
            y = 60 + i * 44
            col = C["accent"] if i in hl_idx else ramp[i % len(ramp)]
            out.append(f'<rect x="{H + 90}" y="{y - 20}" width="24" height="24" fill="{col}"/>')
            txt(H + 128, y, c, "start", 24)
        return _svg(W, H, out, alt)

    if kind == "scatter":
        pts = ch.get("points", [])
        xs, ys = [p["x"] for p in pts], [p["y"] for p in pts]
        x0, x1 = min(0, min(xs)), max(xs) * 1.1
        y0, y1 = min(0, min(ys)), max(ys) * 1.12
        L, R, T, B = 90, W - 40, 30, H - 80
        out.append(f'<line x1="{L}" y1="{B}" x2="{R}" y2="{B}" stroke="{C["rule"]}" stroke-width="2"/>')
        out.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{B}" stroke="{C["rule"]}" stroke-width="2"/>')
        for p in pts:
            px = L + (p["x"] - x0) / (x1 - x0 or 1) * (R - L)
            py = B - (p["y"] - y0) / (y1 - y0 or 1) * (B - T)
            on = p.get("highlight") or p.get("label") in hl
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="12" fill="{C["accent"] if on else C["primary"]}"/>')
            txt(px + 18, py + 8, p.get("label", ""), "start", 22, C["accent"] if on else C["ink"], 700 if on else 400)
        txt((L + R) / 2, H - 20, ch.get("x_title", ""), size=22, fill=C["muted"], weight=700)
        out.append(f'<text transform="translate(28,{(T + B) / 2}) rotate(-90)" text-anchor="middle" font-size="22" '
                   f'fill="{C["muted"]}" font-weight="700">{esc(ch.get("y_title", ""))}</text>')
        return _svg(W, H, out, alt)

    horizontal = kind in ("bar", "stacked_bar", "range")
    stacked = kind in ("stacked", "stacked_bar")
    if kind == "waterfall":
        vals = [float(v) for v in ch["values"]]
        totals = set(ch.get("totals", [])) | {0}
        segs, run = [], 0.0
        for i, v in enumerate(vals):
            if i in totals:
                segs.append((0, v, "total"))
                run = v
            else:
                segs.append((run, run + v, "up" if v >= 0 else "down"))
                run += v
        if min(min(a, b) for a, b, _ in segs) < 0:
            warn("waterfall goes below zero; check the bridge")
        lo, hi = 0, max(max(a, b) for a, b, _ in segs)
    elif kind == "range":
        low, high = [float(v) for v in ch["low"]], [float(v) for v in ch["high"]]
        lo, hi = min(0, min(low)), max(high)
        if ch.get("min") is not None:
            lo = ch["min"]
    else:
        series = list(ch["series"])
        if kind == "line" and ch.get("target") is not None:
            series.append({"name": ch.get("target_label", "Target"), "values": [ch["target"]] * len(cats), "_target": True})
        for se in series:
            if len(se["values"]) != len(cats):
                raise SpecError(f"series '{se.get('name')}' has {len(se['values'])} values for {len(cats)} categories")
        if stacked:
            pos = [sum(max(0.0, float(se["values"][i])) for se in series) for i in range(len(cats))]
            neg = [sum(min(0.0, float(se["values"][i])) for se in series) for i in range(len(cats))]
            lo, hi = min(0, min(neg)), max(0, max(pos))  # positives stack up, negatives stack down
        else:
            allv = [float(v) for se in series for v in se["values"]]
            lo, hi = min(allv), max(allv)
            lo = ch.get("min", min(0, lo) if kind != "line" else min(0, lo))
        maxes = [max(abs(float(v)) for v in se["values"]) for se in series]
        if len(maxes) > 1 and min(maxes) > 0 and max(maxes) / min(maxes) > 10:
            warn("series differ in scale by more than 10x on one axis: split into two charts")
    if ch.get("max") is not None:
        hi = ch["max"]
    span = (hi - lo) or 1
    multi = kind not in ("waterfall", "range") and len(series) > 1
    legend_h = 50 if multi else 0
    if horizontal:
        lab_w = min(380, 30 + max((len(c) for c in cats), default=4) * 13)
        L, R, T, B = lab_w, W - 120, 10 + legend_h, H - 10
        n = len(cats)
        band = (B - T) / max(1, n)
        bh = band * 0.62

        def X(v):
            return L + (float(v) - lo) / span * (R - L)
        for i, c in enumerate(cats):
            y = T + i * band + (band - bh) / 2
            txt(L - 16, y + bh / 2 + 8, c, "end", 24, C["accent"] if i in hl_idx else C["ink"], 700 if i in hl_idx else 400)
            if kind == "range":
                col = C["accent"] if i in hl_idx else C["primary"]
                out.append(f'<rect x="{X(low[i]):.1f}" y="{y:.1f}" width="{X(high[i]) - X(low[i]):.1f}" height="{bh:.1f}" fill="{col}" rx="3"/>')
                lf = ch.get("label_format", nf)
                txt(X(low[i]) - 8, y + bh / 2 + 8, fmt_num(low[i], lf), "end", 22, C["muted"])
                txt(X(high[i]) + 8, y + bh / 2 + 8, fmt_num(high[i], lf), "start", 22, C["muted"])
                continue
            acc = X(max(lo, 0))
            accp = accn = 0.0
            k = len(series)
            for si, se in enumerate(series):
                v = float(se["values"][i])
                col = (C["accent"] if i in hl_idx else (C["grey"] if hl_idx else C["primary"])) if not multi else palette[si % 5]
                if stacked:
                    a0 = accp if v >= 0 else accn
                    x0_, x1_ = sorted((X(a0), X(a0 + v)))
                    w = x1_ - x0_
                    out.append(f'<rect x="{x0_:.1f}" y="{y:.1f}" width="{w:.1f}" height="{bh:.1f}" fill="{col}"/>')
                    if w > 60:
                        txt(x0_ + w / 2, y + bh / 2 + 8, fmt_num(v, nf), size=22, fill=C["ink"] if _lum(col) > 0.55 else "#FFFFFF", weight=700)
                    if v >= 0:
                        accp += v
                    else:
                        accn += v
                else:
                    hh = bh / k
                    yy = y + si * hh
                    x0_ = X(min(v, 0) if lo < 0 else lo)
                    out.append(f'<rect x="{min(X(v), X(max(lo, 0))):.1f}" y="{yy:.1f}" width="{abs(X(v) - X(max(lo, 0))):.1f}" height="{hh - 2:.1f}" fill="{col}"/>')
                    txt(X(v) + 10, yy + hh / 2 + 8, fmt_num(v, nf), "start", 22)
        out.append(f'<line x1="{X(max(lo, 0)):.1f}" y1="{T}" x2="{X(max(lo, 0)):.1f}" y2="{B}" stroke="{C["rule"]}" stroke-width="2"/>')
    else:
        L, R, T, B = 20, W - 20, 50 + legend_h, H - 56
        n = len(cats)
        band = (R - L) / max(1, n)
        bw = band * 0.6

        def Y(v):
            return B - (float(v) - lo) / span * (B - T)
        base = Y(max(lo, 0))
        for i, c in enumerate(cats):
            txt(L + i * band + band / 2, H - 18, c, size=24, fill=C["accent"] if i in hl_idx else C["ink"], weight=700 if i in hl_idx else 400)
        if kind == "waterfall":
            for i, (a, b, kind_) in enumerate(segs):
                x = L + i * band + (band - bw) / 2
                col = C["accent"] if i in hl_idx else {"total": C["primary"], "up": C["grey"], "down": C["muted"]}[kind_]
                y0_, y1_ = Y(max(a, b)), Y(min(a, b))
                out.append(f'<rect x="{x:.1f}" y="{y0_:.1f}" width="{bw:.1f}" height="{max(2, y1_ - y0_):.1f}" fill="{col}"/>')
                v = b - a if kind_ != "total" else b
                lab = fmt_num(v, nf) if kind_ == "total" else (("+" if v >= 0 else "(") + fmt_num(abs(v), nf) + ("" if v >= 0 else ")"))
                txt(x + bw / 2, y0_ - 10, lab, size=24, weight=700 if kind_ == "total" else 400)
                if i < len(segs) - 1:
                    nx = L + (i + 1) * band + (band - bw) / 2
                    out.append(f'<line x1="{x + bw:.1f}" y1="{Y(b):.1f}" x2="{nx:.1f}" y2="{Y(b):.1f}" stroke="{C["rule"]}" stroke-dasharray="4 4" stroke-width="2"/>')
        elif kind in ("line", "area"):
            for si, se in enumerate(series):
                pts = [(L + i * band + band / 2, Y(v)) for i, v in enumerate(se["values"])]
                col = C["muted"] if se.get("_target") else (C["primary"] if not multi else palette[si % 5])
                if kind == "area" and not se.get("_target"):
                    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
                    out.append(f'<polygon points="{pts[0][0]:.1f},{base:.1f} {poly} {pts[-1][0]:.1f},{base:.1f}" fill="{col}" opacity=".35"/>')
                d = " ".join(f"{'M' if k == 0 else 'L'}{x:.1f},{y:.1f}" for k, (x, y) in enumerate(pts))
                dash = ' stroke-dasharray="10 8"' if se.get("_target") else ""
                out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{3 if se.get("_target") else 5}"{dash}/>')
                if not se.get("_target"):
                    for i, (x, y) in enumerate(pts):
                        on = i in hl_idx
                        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{10 if on else 7}" fill="{C["accent"] if on else col}"/>')
                        if ch.get("show_values", not multi):
                            txt(x, y - 18, fmt_num(se["values"][i], nf), size=22, weight=700 if on else 400)
                else:
                    txt(R, pts[-1][1] - 12, se.get("name", "Target"), "end", 22, C["muted"])
            if ch.get("min") not in (None, 0):
                warn("line chart axis does not start at zero; say so on the slide")
        else:
            k = len(series)
            for i in range(n):
                x = L + i * band + (band - bw) / 2
                accp = accn = 0.0
                for si, se in enumerate(series):
                    v = float(se["values"][i])
                    col = (C["accent"] if i in hl_idx else (C["grey"] if hl_idx else C["primary"])) if not multi else palette[si % 5]
                    if stacked:
                        a0 = accp if v >= 0 else accn
                        y0_, y1_ = sorted((Y(a0), Y(a0 + v)))
                        h = y1_ - y0_
                        out.append(f'<rect x="{x:.1f}" y="{y0_:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{col}"/>')
                        if h > 34:
                            txt(x + bw / 2, y0_ + h / 2 + 8, fmt_num(v, nf), size=22, fill=C["ink"] if _lum(col) > 0.55 else "#FFFFFF", weight=700)
                        if v >= 0:
                            accp += v
                        else:
                            accn += v
                    else:
                        ww = bw / k
                        xx = x + si * ww
                        y0_ = min(Y(v), base)
                        out.append(f'<rect x="{xx:.1f}" y="{y0_:.1f}" width="{ww - 3:.1f}" height="{abs(base - Y(v)):.1f}" fill="{col}"/>')
                        if ch.get("show_values", not multi):
                            txt(xx + ww / 2, y0_ - 10, fmt_num(v, nf), size=24 if k == 1 else 20, weight=700 if i in hl_idx else 400)
        out.append(f'<line x1="{L}" y1="{base:.1f}" x2="{R}" y2="{base:.1f}" stroke="{C["rule"]}" stroke-width="2"/>')
    if multi:
        x = L if not horizontal else L
        for si, se in enumerate(series):
            col = C["muted"] if se.get("_target") else palette[si % 5]
            out.append(f'<rect x="{x}" y="8" width="22" height="22" fill="{col}"/>')
            txt(x + 30, 27, se.get("name", ""), "start", 22, C["muted"])
            x += 60 + len(str(se.get("name", ""))) * 12
    return _svg(W, H, out, alt)


def _lum(hexcol: str) -> float:
    h = hexcol.lstrip("#")
    r, g, b = (int(h[k:k + 2], 16) / 255 for k in (0, 2, 4))
    return 0.299 * r + 0.587 * g + 0.114 * b


def _svg(W, H, parts, alt) -> str:
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(alt)}" preserveAspectRatio="xMidYMid meet">'
            f'<title>{esc(alt)}</title>{"".join(parts)}</svg>')


CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#1b1b1b;overflow:hidden;font-family:var(--bf);color:var(--ink)}
body.doc{--fs:30px;--floor:24px;--title:50px;--title-floor:40px}
body.talk{--fs:40px;--floor:36px;--title:60px;--title-floor:44px}
#viewport{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
#stage{width:1920px;height:1080px;position:relative;transform-origin:center center;flex:none}
.slide{position:absolute;inset:0;width:1920px;height:1080px;background:var(--bg);padding:0 86px;display:flex;flex-direction:column;
  overflow:hidden;visibility:hidden}
.slide.active{visibility:visible}
.acc{color:var(--accent)} .muted{color:var(--muted)} b{font-weight:700}
h1,h2,h3,h4{font-family:var(--hf);font-weight:700}
/* chrome */
.head{padding-top:55px;position:relative}
.head.f-classic,.head.f-rail{border-bottom:2px solid var(--rule);padding-bottom:20px}
.head.f-clean,.head.f-editorial{padding-bottom:14px}
.head.bare{padding-bottom:6px}
.kicker{font:700 21px/1.6 var(--bf);letter-spacing:.14em;text-transform:uppercase;color:var(--muted);min-height:34px}
.f-editorial .kicker{color:var(--accent)}
.rail-kicker{position:absolute;left:43px;top:540px;transform:translate(-50%,-50%) rotate(-90deg);white-space:nowrap;
  font:700 21px var(--bf);letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.title{font-size:var(--title);line-height:1.14;color:var(--ink);max-width:1748px}
.f-editorial .title{font-size:calc(var(--title) + 6px)}
.subtitle{font-size:28px;color:var(--muted);margin-top:8px}
.steps{position:absolute;right:0;top:66px;display:flex;gap:9px}.steps i{width:49px;height:9px;background:var(--rule)}.steps i.on{background:var(--accent)}
.body{flex:1;min-height:0;font-size:var(--fs);line-height:1.3;margin-top:34px;display:flex;flex-direction:column;position:relative}
body.talk .body{justify-content:center}
.sowhat{display:flex;align-items:center;gap:28px;background:var(--panel);border-top:6px solid var(--accent);padding:16px 30px;margin-top:20px;min-height:89px}
.sowhat span{font:700 20px var(--bf);letter-spacing:.14em;text-transform:uppercase;color:var(--accent);white-space:nowrap}
.sowhat p{font-size:28px;line-height:1.25}
.footnotes{font-size:19px;color:var(--muted);margin-top:14px}
.foot{height:104px;flex:none;display:flex;flex-direction:column;justify-content:flex-end;padding-bottom:30px;font-size:19px;color:var(--muted);position:relative}
.foot .source{min-height:24px;margin-bottom:12px;padding-right:330px}
.foot .tag{position:absolute;right:0;bottom:66px;border:2px solid var(--rule);padding:2px 12px;font-size:18px;text-transform:uppercase;letter-spacing:.1em}
.footline{display:flex;justify-content:space-between;font-size:18px}
.exhibit{font:700 20px var(--bf);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:16px}
.caption{font-size:21px;color:var(--muted);margin-top:12px}
ul{padding-left:1.1em} li{margin:.25em 0} li::marker{color:var(--accent)}
.body p{margin:.2em 0}
.body h3{font-size:1.05em;line-height:1.2;margin-bottom:.3em}
.row-side{display:grid;grid-template-columns:1fr 562px;gap:50px;flex:1;min-height:0}
.side{background:var(--panel);padding:30px 34px;border-radius:var(--radius);font-size:.85em;align-self:start}
.side h4{font-size:1.05em;margin-bottom:.4em;color:var(--primary)}
.chart-col{display:flex;flex-direction:column;min-height:0;flex:1}
.chart{flex:1;min-height:0;display:flex}.chart svg{width:100%;height:100%;font-family:var(--bf)}
.chip{display:inline-block;font-size:20px;font-weight:700;padding:3px 14px;border-radius:30px;background:var(--panel);color:var(--ink);margin:6px 8px 6px 0}
.chip.pos{background:color-mix(in srgb,var(--pos) 18%,var(--bg));color:color-mix(in srgb,var(--pos) 70%,#000)}
.chip.neg{background:color-mix(in srgb,var(--neg) 16%,var(--bg));color:color-mix(in srgb,var(--neg) 75%,#000)}
.chip.accent{background:color-mix(in srgb,var(--accent) 16%,var(--bg));color:color-mix(in srgb,var(--accent) 75%,#000)}
.chip.primary{background:color-mix(in srgb,var(--primary) 14%,var(--bg))}
.badge{width:62px;height:62px;border-radius:50%;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:700;margin-bottom:18px}
.hl .badge{background:var(--accent)}
/* dark slides */
.slide.dark{background:var(--dark);color:var(--on-dark);padding:0 130px;justify-content:center}
.dark .bar,.t-divider .bar{display:block;width:130px;height:9px;background:var(--accent);margin:0 0 40px}
.eyebrow{font:700 24px var(--bf);letter-spacing:.2em;text-transform:uppercase;color:var(--on-dark-muted);margin-bottom:36px}
.cover-grid{display:grid;grid-template-columns:1fr auto;gap:80px;align-items:start}
.cover-grid>.eyebrow{grid-column:1/-1;margin-bottom:0}
.dark h1{font-size:76px;line-height:1.08;max-width:1600px}
.cover-sub{font-size:34px;color:var(--on-dark-muted);margin-top:34px;max-width:1500px;line-height:1.3}
.cover-fig{background:var(--primary);padding:36px;width:482px;min-height:374px;display:flex;flex-direction:column;justify-content:flex-end;color:var(--on-dark)}
.cover-fig.accent{background:var(--accent)}
.cover-fig b{font:700 88px/1 var(--hf)} .cover-fig span{font-size:26px;margin-top:16px}
.cover-meta{position:absolute;left:130px;bottom:60px;font-size:24px;color:var(--on-dark-muted);line-height:1.4}
.cover-minimal{padding:0 130px;justify-content:center}
.cover-minimal .eyebrow{color:var(--accent)} .cover-minimal h1{font-size:88px;line-height:1.05}
.cover-minimal .cover-sub{color:var(--muted)} .cover-minimal .cover-fig{background:none;color:var(--ink);min-height:0;padding:0}
.cover-minimal .cover-fig b{color:var(--accent);font-size:120px}
.cover-minimal .cover-meta{color:var(--muted);right:130px;border-top:2px solid var(--rule);padding-top:20px}
.cover-split{padding:0;flex-direction:row}
.split-dark{width:1066px;height:100%;background:var(--dark);color:var(--on-dark);padding:144px 115px;position:relative}
.split-dark h1{font-size:76px;line-height:1.06}
.split-right{flex:1;display:flex;align-items:center;justify-content:center;position:relative}
.split-right .cover-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.split-right .cover-fig{background:none;color:var(--ink)} .split-right .cover-fig b{color:var(--accent);font-size:120px}
.div-num{font:700 176px/1 var(--hf);color:var(--accent);margin-bottom:30px}
.divider-q{font-size:88px!important;line-height:1.06}
.next-label{font:700 24px var(--bf);letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin-top:60px}
.close-ask{font-size:40px;margin-top:16px;max-width:1066px;line-height:1.3}
/* agenda, summary, framework */
.t-agenda{flex-direction:row;padding:0}
.ag-panel{width:432px;background:var(--panel);padding:130px 60px 0 86px}.ag-panel h2{font-size:60px;line-height:1.1}
.ag-dark{flex:1;background:var(--dark);color:var(--on-dark);padding:144px 100px 0;position:relative}
.ag-page{position:absolute;right:86px;bottom:30px;font-size:19px;color:var(--on-dark-muted)}
.agenda{list-style:none;display:flex;flex-direction:column;gap:56px}
.agenda li{display:flex;gap:44px;align-items:center;font-size:36px;font-weight:700}
.agenda b{font:700 68px/1 var(--hf);min-width:130px;padding-right:40px;border-right:2px solid currentColor}
.agenda li.on{color:var(--accent)} .agenda li.off{color:var(--grey);font-weight:400}
.es{display:flex;flex-direction:column}
.es-row{display:grid;grid-template-columns:72px 1fr 150px;gap:28px;padding:14px 0;border-bottom:1.5px solid var(--rule);align-items:center}
.es-row:last-child{border-bottom:none}
.es-n{background:var(--primary);color:var(--on-dark);font:700 36px var(--hf);align-self:stretch;display:flex;align-items:center;justify-content:center;min-height:110px}
.es-row.hl .es-n{background:var(--accent)}
.es-claim{font-weight:700;font-size:1.05em} .es-detail{font-size:.85em;color:var(--muted);margin-top:4px} .es-ref{font-size:.72em;color:var(--muted);text-align:right}
.t-framework{flex-direction:row;padding:0}
.fw-rail{width:662px;background:var(--dark);color:#fff;padding:120px 60px;display:flex;flex-direction:column;justify-content:center}
.fw-rail .kicker{color:rgba(255,255,255,.75)} .fw-rail h2{font-size:58px;line-height:1.12}
.fw-body{padding:110px 86px 120px 80px;margin:0}
.fw-points{list-style:none;display:flex;flex-direction:column;gap:34px}
.fw-points li{display:flex;gap:30px} .fw-n{font:700 1.6em/1 var(--hf);color:var(--accent);min-width:56px}
.fw-foot{position:absolute;left:720px;right:86px;bottom:0}
/* statement, quote, question */
.st{display:flex;flex-direction:column;justify-content:center;flex:1}
.st-claim{font:700 1.5em/1.2 var(--hf);max-width:1600px} .st-claim.big{font-size:68px}
.st-points{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:40px;margin-top:60px;font-size:.9em}
.st-points div{border-top:3px solid var(--rule);padding-top:20px}
.qt{display:flex;flex-direction:column;justify-content:center;flex:1;max-width:1560px}
.qmark{font:700 220px/0.6 var(--hf);color:var(--accent);height:110px}
.qt blockquote{font:600 62px/1.18 var(--hf)} .qt figcaption{margin-top:40px;font-size:30px;color:var(--muted)}
.qq h1{font-size:80px}.light-q .qq h1{color:var(--ink)}.light-q .qopts li{background:var(--panel);border-color:var(--rule)}.light-q .qprompt{color:var(--muted)} .qopts{list-style:none;display:flex;gap:30px;margin-top:60px;flex-wrap:wrap}
.qopts li{background:rgba(255,255,255,.08);border:2px solid rgba(255,255,255,.25);padding:22px 34px;font-size:34px;border-radius:14px}
.qopts b{color:var(--accent);margin-right:16px} .qprompt{margin-top:50px;font-size:30px;color:var(--on-dark-muted)}
/* numbers */
.bn{display:grid;grid-template-columns:1.2fr 1fr;gap:80px;align-items:center;flex:1}
.bn-val{font:700 240px/0.95 var(--hf);color:var(--accent);letter-spacing:-.02em}
.bn-label{font:700 1.3em/1.2 var(--hf);margin:20px 0 14px}
.bn-pts{font-size:.95em}
.dc{display:flex;align-items:stretch;gap:30px;flex:1}
.dc-card{flex:1;padding:50px;border-radius:var(--radius);display:flex;flex-direction:column;justify-content:center}
.dc-val{font:700 150px/1 var(--hf);color:var(--grey)} .dc-card.hl .dc-val{color:var(--accent)}
.dc-vs{align-self:center;font:700 34px var(--hf);color:var(--muted);text-transform:uppercase}
.kpis{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:34px}
.kpi{padding:40px;border-radius:var(--radius)}
.kpi-val{font:700 96px/1 var(--hf);color:var(--primary)} .kpi.hl .kpi-val{color:var(--accent)}
.kpi-label{font-weight:700;margin:16px 0 4px}
.kpi p{font-size:.8em}
/* tables */
.tbl{width:100%;border-collapse:collapse;font-size:.85em}
.tbl th{text-align:left;font-size:.8em;color:var(--primary);border-bottom:3px solid var(--primary);padding:12px 16px;vertical-align:bottom}
.tbl td{padding:14px 16px;border-bottom:1.5px solid var(--rule);vertical-align:top}
.tbl th.num{text-align:right}
.tbl td.num{text-align:right;font-variant-numeric:tabular-nums}
.tbl tr.hl td{background:var(--panel);font-weight:700}
.tbl tr.total td{border-top:3px solid var(--ink);font-weight:700}
.dots{color:var(--accent);letter-spacing:4px} .dots.l1{color:var(--grey)} .dots.l2{color:var(--primary)}
/* diagrams */
.process{list-style:none;display:grid;grid-template-columns:repeat(var(--n),1fr);gap:56px;margin-top:10px}
.process li{position:relative}
.process li:not(:last-child)::after{content:"→";position:absolute;right:-46px;top:12px;font-size:40px;color:var(--grey)}
.pr-n{width:72px;height:72px;border-radius:50%;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;font:700 32px var(--hf);margin-bottom:22px}
.process li.hl .pr-n{background:var(--accent)} .process li.hl h3{color:var(--accent)} .process p{font-size:.85em}
.cycle{position:relative;height:100%;aspect-ratio:1.45/1;margin:0 auto;max-width:100%}
.cy-ring{position:absolute;left:50%;top:50%;width:62%;height:76%;transform:translate(-50%,-50%);border:4px solid var(--rule);border-radius:50%}
.cy-center{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:30%;text-align:center;font:700 1em/1.2 var(--hf);color:var(--primary)}
.cy-node{position:absolute;transform:translate(-50%,-50%);width:27%;padding:18px 22px;border-radius:var(--radius);font-size:.78em;text-align:center}
.cy-node b{display:inline-flex;width:44px;height:44px;border-radius:50%;background:var(--primary);color:#fff;align-items:center;justify-content:center;font-size:24px}
.cy-node.hl b{background:var(--accent)} .cy-node h3{margin:8px 0 2px}
.funnel{display:flex;flex-direction:column;gap:12px;flex:1;justify-content:center}
.fn-row{display:grid;grid-template-columns:2.3fr 1fr;gap:30px;align-items:center}
.fn-barwrap{display:flex;justify-content:center}
.fn-bar{background:var(--grey);color:var(--ink);padding:16px 26px;display:flex;justify-content:space-between;gap:20px;font-size:.9em;border-radius:6px}
.fn-bar b{font-family:var(--hf)} .fn-bar.hl{background:var(--accent);color:#fff}
.fn-note{font-size:.75em;color:var(--muted)}
.pyramid{display:flex;flex-direction:column;gap:8px;flex:1;justify-content:center}
.py-row{display:grid;grid-template-columns:1.1fr 1fr;gap:40px;align-items:center}
.py-shape{display:flex;justify-content:center}
.py-lv{background:var(--primary);color:#fff;text-align:center;padding:22px 10px;font-weight:700;font-size:.85em}
.py-lv.hl{background:var(--accent)} .py-detail{font-size:.8em}
.hub{position:relative;flex:1}
.hub-lines{position:absolute;inset:0;width:100%;height:100%}.hub-lines line{stroke:var(--rule);stroke-width:.35}
.hub-center{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:250px;height:250px;border-radius:50%;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;text-align:center;padding:30px;font:700 .95em/1.15 var(--hf)}
.hub-card{position:absolute;transform:translate(-50%,-50%);width:23%;padding:16px 22px;border-radius:var(--radius);font-size:.72em}
.hub-card.hl h3{color:var(--accent)}
.itree{display:grid;grid-template-columns:330px 1fr;gap:80px;align-items:center;flex:1}
.it-root{background:var(--primary);color:#fff;padding:34px;font:700 1em/1.2 var(--hf);border-radius:var(--radius)}
.it-branches{display:flex;flex-direction:column;gap:18px;border-left:3px solid var(--rule);padding-left:40px}
.it-branch{display:grid;grid-template-columns:360px 1fr;gap:26px;align-items:center;position:relative}
.it-branch::before{content:"";position:absolute;left:-40px;top:50%;width:34px;border-top:3px solid var(--rule)}
.it-label{background:var(--panel);padding:16px 22px;font-weight:700;font-size:.85em;border-radius:var(--radius)}
.it-branch.hl .it-label{background:var(--accent);color:#fff}
.it-leaves{display:flex;flex-wrap:wrap;gap:10px}.it-leaves span{border:2px solid var(--rule);padding:6px 16px;font-size:.7em;border-radius:30px}
.mx-wrap{display:grid;grid-template-columns:50px auto;grid-template-rows:1fr 40px;flex:1;min-height:0;justify-content:start}
.mx-y{writing-mode:vertical-rl;transform:rotate(180deg);text-align:center;font-weight:700;font-size:22px}
.mx{position:relative;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:6px;height:100%;aspect-ratio:1.5/1}
.mx-q{background:var(--panel);padding:14px 18px}.mx-q.hl{background:var(--rule)}
.mx-q span{font:700 19px var(--bf);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.mx-item{position:absolute;display:flex;align-items:center;gap:12px;transform:translate(-25px,-50%)}
.mx-item i{width:44px;height:44px;border-radius:50%;background:var(--primary);flex:none}
.mx-item.hl i{background:var(--accent)} .mx-item span{font-size:23px;white-space:nowrap} .mx-item.hl span{color:var(--accent);font-weight:700}
.mx-x{grid-column:2;text-align:center;font-weight:700;font-size:22px;padding-top:6px}
.swot{display:grid;grid-template-columns:1fr 1fr;grid-auto-rows:1fr;gap:24px}
.sw{padding:26px 32px;border-radius:var(--radius);font-size:.8em}.sw h3{color:var(--primary)}.sw.hl h3{color:var(--accent)}
.sw.hl{outline:3px solid var(--accent)}
.venn{position:relative;height:100%;aspect-ratio:1.25/1;margin:0 auto;max-width:100%}
.vn-c{position:absolute;width:56%;aspect-ratio:1;border-radius:50%;transform:translate(-50%,-50%);opacity:.22}
.venn.two .vn-c{width:58%}
.vn-l{position:absolute;transform:translate(-50%,-50%);width:26%;text-align:center;font-size:.8em}
.vn-ov{position:absolute;left:50%;transform:translate(-50%,-50%);width:18%;text-align:center;font:700 .85em/1.15 var(--hf);color:var(--accent)}
.journey{display:grid;grid-template-columns:240px repeat(var(--n),1fr);grid-template-rows:auto 120px repeat(var(--r),1fr);gap:8px;flex:1;font-size:.68em}
.jr-lab{font:700 19px var(--bf);letter-spacing:.08em;text-transform:uppercase;color:var(--muted);display:flex;align-items:center}
.jr-lab.acc{color:var(--accent)}
.jr-stage{background:var(--primary);color:#fff;text-align:center;font-weight:700;padding:10px}
.jr-emo{width:100%;height:100%}.jr-emo .base{stroke:var(--rule);stroke-width:.4}.jr-emo polyline{fill:none;stroke:var(--primary);stroke-width:.8;vector-effect:non-scaling-stroke}
.jr-emo circle.pos{fill:var(--pos)}.jr-emo circle.neg{fill:var(--neg)}.jr-emo circle.mid{fill:var(--grey)}
.jr-cell{background:var(--panel);padding:10px 14px;display:flex;align-items:center}
.jr-cell.opp{background:none;border:2px solid var(--accent)}
/* compare and plan */
.cols{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:34px;align-items:stretch}
.cmp,.tier,.lane{padding:34px;border-radius:var(--radius);font-size:.85em}
.cmp.hl,.tier.hl{outline:4px solid var(--accent)} .cmp.hl h3,.lane.hl h3{color:var(--accent)}
.cols.ruled{gap:0}.colx{padding:0 40px;border-left:2px solid var(--rule);font-size:.85em}.colx:first-child{border-left:none;padding-left:0}
.colx.hl h3{color:var(--accent)}
.cards{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:30px;align-content:start}
.card{padding:36px;border-radius:var(--radius);font-size:.85em}
.card-n{font:700 1.5em var(--hf);color:var(--accent);margin-bottom:6px}
.card.hl{outline:4px solid var(--accent)} .card.hl h3{color:var(--accent)}
.ba-wrap{display:grid;grid-template-columns:1fr 90px 1fr;gap:20px;align-items:stretch}
.ba{padding:34px;border-radius:var(--radius);font-size:.85em;display:flex;flex-direction:column}
.ba.after{outline:4px solid var(--accent)}
.ba-label{font:700 20px var(--bf);letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:12px}
.ba.after .ba-label{color:var(--accent)} .ba-img{width:100%;height:260px;object-fit:cover;margin-bottom:18px}
.ba-arrow{align-self:center;text-align:center;font-size:70px;color:var(--accent)}
.tier{position:relative} .price{font:700 2em/1.1 var(--hf);color:var(--primary);margin:10px 0 20px}
.price span{font:400 .4em var(--bf);color:var(--muted);margin-left:8px}
.badge-label{position:absolute;top:-22px;left:34px;background:var(--accent);color:#fff;font:700 18px var(--bf);letter-spacing:.1em;text-transform:uppercase;padding:6px 14px}
.timeline{display:grid;gap:0;font-size:.7em;align-content:start}
.tl-p{font:700 19px var(--bf);letter-spacing:.06em;text-transform:uppercase;color:var(--primary);text-align:center;padding:10px 4px;border-bottom:3px solid var(--primary)}
.timeline>.tl-lab:first-child{border-bottom:3px solid var(--primary)}
.tl-lab{font-weight:700;padding:14px 16px 14px 0;border-bottom:1.5px solid var(--rule);display:flex;align-items:center}
.tl-track{display:grid;grid-template-columns:repeat(var(--np),1fr);border-bottom:1.5px solid var(--rule);align-items:center;padding:14px 0;
  background:repeating-linear-gradient(90deg,transparent 0,transparent calc(100%/var(--np) - 1.5px),var(--rule) calc(100%/var(--np) - 1.5px),var(--rule) calc(100%/var(--np)))}
.tl-bar{background:var(--primary);color:#fff;margin:0 8px;padding:10px 14px;border-radius:8px;font-weight:700;font-size:.85em;grid-row:1}
.tl-bar.hl{background:var(--accent)}
.tl-ms{display:flex;align-items:center;gap:10px;justify-content:center;grid-row:1;color:var(--accent);font-weight:700;font-size:.85em}
.tl-ms i{width:26px;height:26px;background:var(--accent);transform:rotate(45deg);flex:none}
.tl-owner{color:var(--muted);text-align:center;border-bottom:1.5px solid var(--rule);display:flex;align-items:center;justify-content:center}
.milestones{list-style:none;display:grid;grid-template-columns:repeat(var(--n),1fr);position:relative;margin-top:30px;font-size:.8em}
.milestones::before{content:"";position:absolute;left:0;right:0;top:68px;border-top:4px solid var(--rule)}
.milestones li{padding-right:24px}
.ms-date{font:700 22px var(--bf);color:var(--muted);height:44px}
.milestones li i{display:block;width:44px;height:44px;border-radius:50%;background:var(--bg);border:5px solid var(--grey);position:relative;margin-bottom:22px}
.milestones li.done i{background:var(--pos);border-color:var(--pos)} .milestones li.now i{background:var(--accent);border-color:var(--accent)}
.milestones li.now h3{color:var(--accent)}
.lane{background:none;border-top:5px solid var(--primary);padding:24px 0 0}.lane.hl{border-color:var(--accent)}
.lane-item{padding:20px 24px;margin-top:16px;border-radius:var(--radius)} .lane-item h4{font-size:1em} .lane-item p{font-size:.85em}
.tbl.actions td{vertical-align:middle}
.ask{display:grid;grid-template-columns:1fr 475px;gap:43px;flex:1;align-items:stretch}.ask.nofig{grid-template-columns:1fr}
.ask-main{background:var(--primary);color:#fff;padding:36px 50px;display:flex;flex-direction:column}
.ask-label{font:700 22px var(--bf);letter-spacing:.16em;text-transform:uppercase;color:var(--on-dark-muted)}
.ask-line{font:700 1.4em/1.2 var(--hf);margin-top:14px} .ask-cols{display:grid;grid-template-columns:1fr 1fr;gap:56px;margin-top:40px;font-size:.9em}
.ask-cols h4{font:700 21px var(--bf);letter-spacing:.14em;text-transform:uppercase;color:var(--on-dark-muted);margin-bottom:8px}
.ask-cols li::marker{color:#fff}
.ask-owner{margin-top:auto;font-size:.72em;color:var(--on-dark-muted)}
.ask-fig{background:var(--accent);color:#fff;padding:56px 43px;display:flex;flex-direction:column;justify-content:flex-start}
.ask-fig b{font:700 92px/1 var(--hf)} .ask-fig span{font-size:24px;margin-top:14px}
/* people, proof, pictures */
.team{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:30px;align-content:start}
.person{padding:30px;border-radius:var(--radius);font-size:.8em;text-align:center}
.face{width:160px;height:160px;border-radius:50%;object-fit:cover;margin:0 auto 18px;display:block}
.face.init{display:flex;align-items:center;justify-content:center;background:var(--primary);color:#fff;font:700 54px var(--hf)}
.role{color:var(--accent);font-weight:700;margin-bottom:8px}
.faq{display:grid;grid-template-columns:1fr 1fr;gap:26px;align-content:start}
.faq-i{padding:26px 30px;border-radius:var(--radius);font-size:.8em}.proof{color:var(--muted);font-size:.9em}
.im{display:grid;grid-template-rows:100%;gap:60px;flex:1;min-height:0}
.im-pic{min-height:0;height:100%;overflow:hidden}.im-pic img,.im-pic .img-missing{width:100%;height:100%;object-fit:cover;border-radius:var(--radius)}
.im-text{align-self:center}
.t-image_full{padding:0!important;justify-content:flex-end!important}
.bleed{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.scrim{position:absolute;inset:0;background:linear-gradient(0deg,rgba(0,0,0,.78) 0%,rgba(0,0,0,.25) 55%,rgba(0,0,0,0) 100%)}
.if-text{position:relative;padding:0 130px 110px;color:#fff} .if-text .kicker{color:rgba(255,255,255,.8)} .if-text h1{font-size:72px}
.credit{position:absolute;right:40px;bottom:24px;font-size:18px;color:rgba(255,255,255,.75)}
.gallery{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:24px;flex:1;min-height:0}
.gallery figure{display:flex;flex-direction:column;min-height:0}.gallery img,.gallery .img-missing{flex:1;min-height:0;width:100%;object-fit:cover;border-radius:var(--radius)}
.gallery figcaption{font-size:22px;color:var(--muted);margin-top:10px}
.code{background:#111827;color:#E5E7EB;font:400 24px/1.45 "Courier New","Liberation Mono",monospace;padding:30px 36px;border-radius:12px;overflow:hidden;white-space:pre-wrap}
.bullets{font-size:1em}.bullets li{margin:.45em 0}
.refs{font-size:.7em;padding-left:1.4em}.refs li{margin:.4em 0}
.img-missing{display:flex;align-items:center;justify-content:center;background:repeating-linear-gradient(45deg,var(--panel),var(--panel) 18px,var(--bg) 18px,var(--bg) 36px);
  color:var(--muted);font-size:22px;border:2px dashed var(--grey);min-height:200px;text-align:center;padding:20px}
/* QA badge + runtime chrome */
.slide[data-overflow]::after{content:"DOES NOT FIT: " attr(data-overflow);position:absolute;right:16px;top:12px;background:#D00;color:#fff;font:700 18px Arial;padding:6px 12px;z-index:9}
#progress{position:fixed;left:0;bottom:0;height:5px;background:var(--accent);transition:width .25s}
#notes{position:fixed;left:0;right:0;bottom:0;max-height:34vh;overflow:auto;background:#fffdf5;color:#222;font:16px/1.45 Arial,sans-serif;
  padding:14px 22px;border-top:3px solid var(--accent);display:none;z-index:20}
#notes h5{margin-top:8px;font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:#666}
body.show-notes #notes{display:block}
#hint{position:fixed;right:12px;top:10px;font:12px Arial;color:#aaa;opacity:.85;transition:opacity 1s;z-index:30}
body.grid{overflow:auto;background:#2a2a2a}
body.grid #viewport{position:static;display:block;padding:20px}
body.grid #stage{transform:none!important;width:auto;height:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(384px,1fr));gap:16px}
body.grid .slide{position:relative;visibility:visible;zoom:.2;cursor:pointer}
@media print{
  @page{size:1920px 1080px;margin:0}
  html,body{background:none;overflow:visible;height:auto}
  #viewport{position:static;display:block} #stage{transform:none!important;width:1920px;height:auto}
  .slide{position:relative;visibility:visible;page-break-after:always;break-after:page}
  #progress,#notes,#hint{display:none!important} .slide[data-overflow]::after{display:none}
}
"""

JS = r"""
const stage=document.getElementById('stage'),slides=[...document.querySelectorAll('.slide')],notes=document.getElementById('notes');
/* sandboxed previews (claude.ai, about:srcdoc) forbid touching the URL: remembering the slide is optional */
function readHash(){try{return parseInt(location.hash.slice(1))||1}catch(e){return 1}}
function writeHash(n){try{if(location.protocol!=='about:')history.replaceState(null,'','#'+n)}catch(e){}}
let i=Math.max(0,Math.min(slides.length-1,readHash()-1));
function fit(){if(document.body.classList.contains('grid'))return;stage.style.transform=`scale(${Math.min(innerWidth/1920,innerHeight/1080)})`;}
function show(n){i=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,k)=>s.classList.toggle('active',k===i));
  document.getElementById('progress').style.width=((i+1)/slides.length*100)+'%';writeHash(i+1);
  const t=slides[i].querySelector('template.notes');notes.innerHTML=`<b>Slide ${i+1} of ${slides.length}</b>`+(t?t.innerHTML:'');}
/* step text down to the floor sizes, then flag what still does not fit */
function px(el,v){return parseFloat(getComputedStyle(el).getPropertyValue(v))}
function over(el){return el.scrollHeight>el.clientHeight+2||el.scrollWidth>el.clientWidth+2}
function lines(el){const lh=parseFloat(getComputedStyle(el).lineHeight)||parseFloat(getComputedStyle(el).fontSize)*1.15;return Math.round(el.scrollHeight/lh)}
function fitAll(){const b=document.body,floor=px(b,'--floor'),tfloor=px(b,'--title-floor');
  slides.forEach(s=>{const vis=s.style.visibility;s.style.visibility='visible';const probs=[];
    s.querySelectorAll('[data-fit=title]').forEach(h=>{let f=parseFloat(getComputedStyle(h).fontSize);const isTitle=h.classList.contains('title');
      const maxL=isTitle?2:4;let guard=0;while(lines(h)>maxL&&f>(isTitle?tfloor:tfloor)&&guard++<40){f-=2;h.style.fontSize=f+'px';}
      if(lines(h)>maxL)probs.push('title over '+maxL+' lines');});
    const body=s.querySelector('[data-fit=body]');
    if(body){let f=parseFloat(getComputedStyle(body).fontSize),guard=0;
      const kids=()=>[body,...body.querySelectorAll('.chart-col,.row-side,.cols,.side,.card,.cmp,.tier,.lane,.sw,.kpi,.person,.faq-i,.ba,.dc-card,.cy-node,.hub-card,.jr-cell,.tbl')];
      const anyOver=()=>kids().some(over)||[...body.children].some(c=>c.getBoundingClientRect().bottom>body.getBoundingClientRect().bottom+2);
      while(anyOver()&&f>floor&&guard++<40){f-=1;body.style.fontSize=f+'px';}
      if(anyOver())probs.push('body text below floor');}
    s.querySelectorAll('.body *').forEach(e=>{if(e.closest('svg')||!e.offsetParent||e.children.length)return;
      if(e.textContent.trim()&&parseFloat(getComputedStyle(e).fontSize)<17.5&&!probs.includes('text below 9pt'))probs.push('text below 9pt');});
    const r=s.getBoundingClientRect();
    s.querySelectorAll('h1,h2,h3,p,li,td,span,b,div').forEach(e=>{if(!e.offsetParent||e.closest('.bleed,.cy-ring'))return;const q=e.getBoundingClientRect();
      if(q.width&&(q.right>r.right+1||q.bottom>r.bottom+1||q.left<r.left-1)&&!probs.includes('off slide'))probs.push('off slide');});
    if(probs.length)s.dataset.overflow=probs.join('; ');s.style.visibility=vis;});
  window.__deckReport=slides.map((s,k)=>({n:k+1,overflow:s.dataset.overflow||''}));}
addEventListener('resize',fit);
addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(i+1)}
  if(['ArrowLeft','PageUp'].includes(e.key))show(i-1);if(e.key==='Home')show(0);if(e.key==='End')show(slides.length-1);
  if(e.key==='n'||e.key==='N')document.body.classList.toggle('show-notes');
  if(e.key==='g'||e.key==='G'){document.body.classList.toggle('grid');stage.style.transform='';fit();}
  if(e.key==='p'||e.key==='P')print();});
slides.forEach((s,k)=>s.addEventListener('click',()=>{if(document.body.classList.contains('grid')){document.body.classList.remove('grid');fit();show(k);}}));
let x0=null;addEventListener('touchstart',e=>x0=e.touches[0].clientX);
addEventListener('touchend',e=>{if(x0===null)return;const dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>40)show(i+(dx<0?1:-1));x0=null;});
fit();show(i);
(document.fonts?document.fonts.ready:Promise.resolve()).then(()=>{fitAll();show(i);});
setTimeout(()=>{const h=document.getElementById('hint');if(h)h.style.opacity=0},3500);
"""

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<!-- deck-studio HTML draft: built from the JSON spec by build_html.py. Edit the spec, not this file. -->
{fonts}
<style>{css}</style></head>
<body class="{talk}"><div id="viewport"><div id="stage">
{slides}
</div></div><div id="progress"></div><div id="notes"></div>
<div id="hint">&larr; &rarr; move &middot; N notes &middot; G grid &middot; P print</div>
<script>{js}</script></body></html>
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("-o", "--out")
    ap.add_argument("--direction", help="override the spec's direction (to compare looks)")
    ap.add_argument("--only", help="render only these 1-based slides, e.g. 1,4")
    ap.add_argument("--link-images", action="store_true", help="link images instead of embedding them")
    a = ap.parse_args(argv)
    try:
        spec = load_spec(a.spec)
        if a.direction:
            spec["direction"] = a.direction
        if a.only:
            keep = {int(x) for x in a.only.split(",")}
            spec["slides"] = [s for k, s in enumerate(spec["slides"], 1) if k in keep]
        base = os.path.dirname(os.path.abspath(a.spec))
        deck = HtmlDeck(spec, base, embed=not a.link_images)
        page = deck.build()
        if any(r.get("ref") for sl in spec["slides"] if sl.get("type") == "exec_summary" for r in sl.get("rows", [])):
            seen = deck.pages_seen   # second pass: exec-summary rows point at slide ids
            deck = HtmlDeck(spec, base, embed=not a.link_images)
            deck.id_pages = seen
            page = deck.build()
    except SpecError as e:
        print(f"SPEC ERROR: {e}", file=sys.stderr)
        return 2
    out = a.out or os.path.splitext(a.spec)[0] + ".html"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"built {out}  ({len(spec['slides'])} slides, direction {deck.t['name']}, {spec.get('mode', 'document')} mode)")
    spec_report(spec, False)
    for w in deck.warnings:
        print(f"  warn  {w}")
    for w in voice_report(spec):
        print(f"  style {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

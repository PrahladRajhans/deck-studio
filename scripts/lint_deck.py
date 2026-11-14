#!/usr/bin/env python3
"""Lint ANY .pptx (ours, Gamma/Canva exports, a teammate's deck) for the defects judges notice.

  python lint_deck.py deck.pptx                 # findings table + headline track
  python lint_deck.py deck.pptx --json          # machine-readable
  python lint_deck.py deck.pptx --mode talk     # talk decks: label titles allowed, word budget tighter

Checks (severity): off-slide shapes (warn) · text overflow, estimated from font metrics (warn) ·
body text below floor (warn) · title is a topic label (info, document mode) · duplicate titles (warn) ·
more than 7 paragraphs in one box (warn) · placeholder / lorem / [CONFIRM] left in (error) ·
figures with no source on the slide or in the notes (info) · missing speaker notes (info) ·
picture or chart with no alt text (info) · overlapping text boxes (warn) · more than 5 fill colours (info) ·
the same label carrying different numbers across slides (info, cross-slide ledger: check, often legit) ·
stock phrasing (warn, style_review) and deck rhythm (info, style_rhythm): editorial prompts, not proof of authorship.
Exit 1 if any error.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict

from pptx import Presentation
from pptx.util import Emu

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import PLACEHOLDER, ai_tells, deck_voice, has_figures, is_label_title, text_height_in  # noqa: E402

EMU_IN = 914400
STOP = {"the", "a", "an", "and", "of", "to", "in", "for", "on", "with", "by", "is", "are", "at", "as",
        "from", "or", "be", "it", "this", "that", "we", "our", "illustrative", "example", "synthetic",
        "data", "source", "figures", "made", "template", "test", "deck"}
# Chrome / small print: allowed below the 12pt body floor (but not below 9pt)
SMALL_PRINT = {"provenance-label", "Source", "Footer", "PageNumber", "Kicker", "ExhibitLabel", "Caption", "Owner",
               "SoWhatLabel", "Eyebrow", "Meta", "Slide Number Placeholder 3", "Footer Placeholder 2"}


def shape_text(shp) -> str:
    if not getattr(shp, "has_text_frame", False) or not shp.has_text_frame:
        return ""
    return "\n".join(p.text for p in shp.text_frame.paragraphs)


def max_font_size(shp):
    sizes = []
    for p in shp.text_frame.paragraphs:
        for r in p.runs:
            if r.font.size:
                sizes.append(r.font.size.pt)
    return max(sizes) if sizes else None


def min_font_size(shp):
    sizes = []
    for p in shp.text_frame.paragraphs:
        if len(p.text.split()) < 4:
            continue
        for r in p.runs:
            if r.font.size:
                sizes.append(r.font.size.pt)
    return min(sizes) if sizes else None


def font_of(shp, default="Calibri"):
    for p in shp.text_frame.paragraphs:
        for r in p.runs:
            if r.font.name:
                return r.font.name
    return default


def find_title(slide):
    if slide.shapes.title is not None and slide.shapes.title.has_text_frame:
        t = slide.shapes.title.text_frame.text.strip()
        if t:
            return t, False
    for shp in slide.shapes:
        if shp.name == "Headline" and shp.has_text_frame:
            return shape_text(shp).strip(), False
    best, best_size = "", 0
    for shp in slide.shapes:
        if getattr(shp, "has_text_frame", False) and shp.has_text_frame:
            sz = max_font_size(shp) or 0
            txt = shape_text(shp).strip()
            if txt and sz > best_size and len(txt) > 3:
                best, best_size = txt, sz
    return best, True


_LEDGER = re.compile(r"([A-Za-z][A-Za-z &/-]{2,40}?)\s*(?:of|at|:|=|is|reaches|hits)?\s*"
                     r"(₹|\$|USD|INR|EUR|£)?\s?([-+]?\d[\d,]*(?:\.\d+)?)\s?(%|x|bn|mn|m|k|cr|lakh|B|M|K)?\b")


def _lum(hexs):
    def ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hexs[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def _is_bold(shp) -> bool:
    try:
        return any(r.font.bold for p in shp.text_frame.paragraphs for r in p.runs if r.text.strip())
    except Exception:  # noqa: BLE001
        return False


def contrast(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def _solid(shp):
    try:
        if shp.fill.type == 1:
            if shp._element.xpath(".//a:solidFill/a:srgbClr/a:alpha"):
                return None  # translucent: blended colour unknown, skip
            return str(shp.fill.fore_color.rgb)
    except Exception:  # noqa: BLE001
        pass
    return None


def _run_colour(shp):
    for p in shp.text_frame.paragraphs:
        for r in p.runs:
            try:
                if r.font.color and r.font.color.type is not None and r.font.color.rgb is not None:
                    return str(r.font.color.rgb)
            except Exception:  # noqa: BLE001
                return None
    return None


def figures_report(path: str):
    """Every figure on every slide with its words around it: the tie-out worksheet."""
    prs = Presentation(path)
    out = []
    for idx, slide in enumerate(prs.slides, 1):
        texts = []
        for shp in slide.shapes:
            if getattr(shp, "has_text_frame", False) and shp.has_text_frame:
                texts.append(shape_text(shp))
            if getattr(shp, "has_table", False) and shp.has_table:
                for row in shp.table.rows:
                    texts.append(" | ".join(c.text for c in row.cells))
            if getattr(shp, "has_chart", False) and shp.has_chart:
                for pl in shp.chart.plots:
                    cats = list(pl.categories) if pl.categories else []
                    for se in pl.series:
                        texts.append(f"[chart] {se.name}: " + ", ".join(
                            f"{c}={v}" for c, v in zip(cats, se.values)))
        for t in texts:
            for line in t.split("\n"):
                if re.search(r"\d", line) and has_figures(line):
                    out.append((idx, line.strip()[:140]))
    return out


def lint(path: str, mode: str = "document", spec=None):
    prs = Presentation(path)
    sw, sh = prs.slide_width, prs.slide_height
    findings = []
    titles = []
    ledger = defaultdict(set)
    chart_sigs: dict = {}
    phrases = defaultdict(set)

    list_lens: list[int] = []

    def add(idx, sev, code, msg):
        findings.append({"slide": idx, "severity": sev, "code": code, "message": msg})

    for idx, slide in enumerate(prs.slides, 1):
        title, guessed = find_title(slide)
        titles.append((idx, title, guessed))
        slide_text = []
        fills = set()
        boxes = []
        for shp in slide.shapes:
            l, t, w, h = shp.left or 0, shp.top or 0, shp.width or 0, shp.height or 0
            if round(getattr(shp, "rotation", 0) or 0) % 180 == 90:  # rotated 90/270: swap the box
                cx, cy = l + w / 2, t + h / 2
                w, h = h, w
                l, t = int(cx - w / 2), int(cy - h / 2)
            if l < -Emu(25400) or t < -Emu(25400) or l + w > sw + Emu(25400) or t + h > sh + Emu(25400):
                add(idx, "warn", "offslide_shape", f"'{shp.name}' extends past the slide edge")
            try:
                if shp.fill.type == 1:
                    fills.add(str(shp.fill.fore_color.rgb))
            except Exception:  # noqa: BLE001
                pass
            if getattr(shp, "has_chart", False) and shp.has_chart:
                descr = shp._element.xpath(".//p:cNvPr/@descr")
                if not descr or not descr[0]:
                    add(idx, "info", "missing_alt_text", f"chart '{shp.name}' has no alt text")
            if shp.shape_type == 13:  # picture
                descr = shp._element.xpath(".//p:cNvPr/@descr")
                if not descr or not descr[0]:
                    add(idx, "info", "missing_alt_text", f"picture '{shp.name}' has no alt text")
                elif re.search(r"\.(png|jpe?g|gif|bmp|tiff?|webp|svg)$", descr[0].strip(), re.I):
                    add(idx, "info", "missing_alt_text",
                        f"picture '{shp.name}' alt text is just a filename ('{descr[0][:40]}')")
            if getattr(shp, "has_table", False) and shp.has_table:
                for row in shp.table.rows:
                    for cell in row.cells:
                        slide_text.append(cell.text)
            txt = shape_text(shp)
            if not txt.strip():
                continue
            slide_text.append(txt)
            n_paras = len([p for p in shp.text_frame.paragraphs if p.text.strip()])
            if n_paras > 7:
                add(idx, "warn", "too_many_bullets", f"'{shp.name}' has {n_paras} paragraphs (max 7)")
            mn = min_font_size(shp)
            small_print = shp.name in SMALL_PRINT or shp.name.startswith(("Source", "Footer", "Caption"))
            floor = 8.5 if small_print else 11.5
            if mn and mn < floor:
                add(idx, "warn", "body_below_floor",
                    f"'{txt[:40]}...' set at {mn}pt (floor {'9' if small_print else '12'}pt)")
            sz = max_font_size(shp)
            if sz is None and shp.is_placeholder:
                sz = 18.0  # inherited from the layout; 18pt is a conservative floor for body placeholders
            if sz and w and h:
                need = text_height_in(txt, font_of(shp), sz, w / EMU_IN - 0.02,
                                      bold=any(r.font.bold for p in shp.text_frame.paragraphs for r in p.runs))
                if need > h / EMU_IN * 1.12 + 0.05:
                    add(idx, "warn", "text_overflow",
                        f"'{txt[:40]}...' needs ~{need:.2f}in, box is {h / EMU_IN:.2f}in")
                boxes.append((shp.name, l, t, w, h))
        # contrast: text colour against the fill it sits on (smallest filled shape containing it) or bg
        bg = None
        try:
            if slide.background.fill.type == 1:
                bg = str(slide.background.fill.fore_color.rgb)
        except Exception:  # noqa: BLE001
            bg = None
        filled = [(sp, _solid(sp)) for sp in slide.shapes if _solid(sp) and not
                 (getattr(sp, "has_text_frame", False) and sp.has_text_frame and shape_text(sp).strip())]
        for sp in slide.shapes:
            if not (getattr(sp, "has_text_frame", False) and sp.has_text_frame and shape_text(sp).strip()):
                continue
            col = _run_colour(sp)
            if not col:
                continue
            cx = (sp.left or 0) + (sp.width or 0) / 2
            cy = (sp.top or 0) + (sp.height or 0) / 2
            under = [f for f in filled if (f[0].left or 0) <= cx <= (f[0].left or 0) + (f[0].width or 0)
                     and (f[0].top or 0) <= cy <= (f[0].top or 0) + (f[0].height or 0)]
            behind = min(under, key=lambda f: (f[0].width or 0) * (f[0].height or 0))[1] if under else bg
            size = max_font_size(sp) or 12
            large = size >= 18 or (size >= 14 and _is_bold(sp))  # WCAG large text
            need = 3.0 if large else 4.5
            if behind and contrast(col, behind) < need:
                add(idx, "warn", "low_contrast", f"'{shape_text(sp)[:35]}...' {col} on {behind} "
                    f"(contrast {contrast(col, behind):.1f}:1; {size:.0f}pt{' bold' if large and size < 18 else ''} "
                    f"text needs {need}:1)")
        for shp in slide.shapes:
            if getattr(shp, "has_chart", False) and shp.has_chart:
                for pl in shp.chart.plots:
                    for se in pl.series:
                        sig = tuple(round(float(v or 0), 6) for v in se.values)
                        if len(sig) >= 3 and len(set(sig)) > 1:
                            chart_sigs.setdefault(sig, []).append(idx)
        is_quote = any(sp.name == "QuoteMark" for sp in slide.shapes)
        if mode == "talk" and title and not guessed and len(title) > 60 and idx != 1 and not is_quote:
            add(idx, "info", "long_talk_title", f"{len(title)} characters: a talk headline reads in one glance "
                "(aim under 55)")
        from geometry_checks import review
        annotations = (spec or {}).get('slides', [])
        annotation = annotations[idx-1].get('layout_review') if idx <= len(annotations) else None
        shape_boxes = [(sp.name, sp.left or 0, sp.top or 0, sp.width or 0, sp.height or 0) for sp in slide.shapes]
        geometry_findings, allowed = review(shape_boxes, annotation, points_per_unit=72/EMU_IN)
        for code, message in geometry_findings:
            add(idx, 'warn', code, message)
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                a, b = boxes[i], boxes[j]
                ox = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
                oy = min(a[2] + a[4], b[2] + b[4]) - max(a[2], b[2])
                if ox > EMU_IN * 0.08 and oy > EMU_IN * 0.08:
                    inside = (a[1] <= b[1] and a[2] <= b[2] and a[1] + a[3] >= b[1] + b[3] and
                              a[2] + a[4] >= b[2] + b[4]) or \
                             (b[1] <= a[1] and b[2] <= a[2] and b[1] + b[3] >= a[1] + a[3] and
                              b[2] + b[4] >= a[2] + a[4])
                    if not inside and frozenset((a[0], b[0])) not in allowed:
                        add(idx, "warn", "text_overlap", f"'{a[0]}' and '{b[0]}' overlap")
        # half-empty: lowest content shape ends above 60% of the slide height (chrome excluded)
        content_bottoms = [(sp.top or 0) + (sp.height or 0) for sp in slide.shapes
                           if sp.name not in SMALL_PRINT and sp.name not in ("Headline", "TitleRule")
                           and (sp.width or 0) < sw * 0.98]
        # sparse-by-design slides (dividers, big statements) have few shapes: don't flag those
        if idx != 1 and len(content_bottoms) >= 4 and max(content_bottoms) < sh * 0.6:
            add(idx, "info", "half_empty", "content ends above 60% of the slide: add the so-what, "
                "enlarge the exhibit, or merge with another slide")
        import colorsys
        hues = set()
        for f in fills:
            r, g, b = (int(f[i:i + 2], 16) / 255 for i in (0, 2, 4))
            h_, s_, v_ = colorsys.rgb_to_hsv(r, g, b)
            if s_ > 0.3 and v_ > 0.2:
                hues.add(f)
        if len(hues) > 4:
            add(idx, "info", "palette", f"{len(hues)} saturated colours on one slide (one accent, one meaning)")
        full = "\n".join(slide_text)
        for sp in slide.shapes:
            if sp.name in SMALL_PRINT or not (getattr(sp, "has_text_frame", False) and sp.has_text_frame):
                continue
            for para in shape_text(sp).split("\n"):
                words = re.findall(r"[a-z][a-z'-]+", para.lower())
                for k in range(len(words) - 2):
                    tri = " ".join(words[k:k + 3])
                    if not any(w in STOP for w in words[k:k + 3]):
                        phrases[tri].add(idx)
        is_quote = any(sp.name == "QuoteMark" for sp in slide.shapes)
        if not is_quote:
            hits = {}
            for sp in slide.shapes:
                if sp.name in SMALL_PRINT or not getattr(sp, "has_text_frame", False) or sp.name == "Code":
                    continue
                for code, snip in ai_tells(shape_text(sp)):
                    hits.setdefault(code, []).append(snip)
                paras = [p for p in shape_text(sp).split("\n") if p.strip()]
                if len(paras) >= 2:
                    list_lens.append(len(paras))
            for code, snips in hits.items():
                add(idx, "warn", "style_review", f"{code}: {', '.join(sorted(set(snips))[:5])} (editorial prompt; references/human-voice.md)")
        if PLACEHOLDER.search(full):
            add(idx, "error", "placeholder", "placeholder text left on the slide ([CONFIRM]/[TBD]/lorem)")
        notes = slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""
        if PLACEHOLDER.search(notes):
            add(idx, "info", "placeholder_in_notes", "notes contain a [CONFIRM]-style item to resolve")
        if not notes.strip() and idx != 1:
            add(idx, "info", "missing_notes", "no speaker notes")
        if has_figures(full) and idx != 1:
            if not re.search(r"\b(source|sources|note|data:)\b", full + "\n" + notes, re.I):
                add(idx, "info", "figure_without_source", "figures shown but no source on slide or in notes")
        for m in _LEDGER.finditer(full.replace("\n", " ")):
            if not (m.group(2) or m.group(4)):  # only currency- or unit-bearing figures
                continue
            label = m.group(1).strip().lower()
            label = re.sub(r"\b(the|a|an|in|by|to|and|our)\b", "", label).strip()
            if len(label) < 4:
                continue
            ledger[label].add((m.group(3).replace(",", ""), (m.group(4) or "").lower(), idx))
        if mode == "document" and title and not guessed and idx != 1 and is_label_title(title) \
                and title.strip().lower() not in {"contents", "agenda", "appendix", "thank you", "questions", "sources", "references",
                                     "q&a", "team", "contact"}:
            add(idx, "info", "title_is_label", f"'{title[:60]}' is a topic, not a claim")
        spoken = " ".join(shape_text(sp) for sp in slide.shapes
                          if sp.name not in SMALL_PRINT and getattr(sp, "has_text_frame", False))
        if mode == "talk" and len(spoken.split()) > 50:
            add(idx, "info", "word_budget", f"{len(spoken.split())} words on a talk slide (aim < 40)")
    for msg in deck_voice([t for _, t, _ in titles if t], list_lens):
        add(1, "info", "style_rhythm", msg)
    for sig, idxs in chart_sigs.items():
        if len(set(idxs)) > 1:
            add(idxs[0], "info", "same_chart_data", f"slides {sorted(set(idxs))} chart the same numbers: "
                "keep a second chart only if it shows a different relationship")
    for tri, idxs in phrases.items():
        if len(idxs) >= 4:
            add(min(idxs), "info", "repeated_phrase", f"'{tri}' appears on {len(idxs)} slides {sorted(idxs)}: "
                "vary the wording (a repeated formula reads as machine-made)")
    seen = defaultdict(list)
    for idx, t, _ in titles:
        if t:
            seen[t.strip().lower()].append(idx)
    for t, idxs in seen.items():
        if len(idxs) > 1:
            add(idxs[0], "warn", "duplicate_titles", f"same title on slides {idxs}")
    for label, vals in ledger.items():
        by_unit = defaultdict(set)
        for v, unit, idx in vals:
            by_unit[unit].add((v, idx))
        for unit, pairs in by_unit.items():
            values = {v for v, _ in pairs}
            slides = sorted({i for _, i in pairs})
            if len(values) > 1 and len(slides) > 1 and len(values) <= 3:
                add(slides[0], "info", "number_ledger",
                    f"'{label}' appears with different values {sorted(values)}{unit} on slides {slides}: "
                    f"same quantity? reconcile or label the difference")
    return findings, titles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pptx")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--spec", help="optional source spec for named layout annotations")
    ap.add_argument("--mode", choices=["document", "talk"], default="document")
    ap.add_argument("--figures", action="store_true",
                    help="print every figure per slide (tie-out worksheet) and exit")
    a = ap.parse_args()
    if not os.path.exists(a.pptx):
        sys.exit(f"lint: no file at {a.pptx}")
    if a.figures:
        for idx, line in figures_report(a.pptx):
            print(f"  slide {idx:>2}  {line}")
        sys.exit(0)
    spec = None
    if a.spec:
        with open(a.spec, encoding="utf-8") as fh:
            spec = json.load(fh)
    findings, titles = lint(a.pptx, a.mode, spec)
    if a.json:
        print(json.dumps({"findings": findings, "titles": titles}, indent=2, ensure_ascii=False))
    else:
        print("HEADLINE TRACK (read top to bottom: does it argue the answer?)")
        for idx, t, guessed in titles:
            print(f"  {idx:>2}. {t[:110]}{'  (?)' if guessed else ''}")
        print()
        if not findings:
            print("lint: clean")
        for f in sorted(findings, key=lambda f: (f["slide"], f["severity"])):
            print(f"  [{f['severity']:<5}] slide {f['slide']:>2}  {f['code']:<22} {f['message']}")
    sys.exit(1 if any(f["severity"] == "error" for f in findings) else 0)


if __name__ == "__main__":
    main()

"""Shared helpers for deck-studio: design directions, font metrics, text fitting, fact model.

Everything here is deliberately dependency-light: python-pptx + Pillow only.
"""
from __future__ import annotations

import ast
import math
import operator
import os
import re
from functools import lru_cache

# --------------------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------------------
SLIDE_W = 13.333  # inches (16:9, PowerPoint "Widescreen")
SLIDE_H = 7.5
MARGIN = 0.6

# --------------------------------------------------------------------------------------
# Design directions. Every token is a hex string without '#'.
#   primary = structure (cover field, header rules, main series)
#   accent  = the ONE thing to notice (the answer, the recommended option, the problem)
#   grey    = context / comparison data
# Fonts are chosen so LibreOffice QA renders true-to-width (Calibri->Carlito,
# Cambria->Caladea, Arial->Liberation Sans).
# --------------------------------------------------------------------------------------
# Art directions. Colour tokens + type + shape language + metadata for selection.
#   tone: formal | refined | bold | creative      formality: high | medium | low
#   radius: card corner radius in inches (0 = sharp)  card: tint | border | shadow
#   frame: classic (kicker, title, hairline) | clean (no rule) | editorial (big serif title,
#          accent kicker, no rule) | rail (rotated section label in the left margin)
#   cover: field (solid dark) | gradient (diagonal gradient) | split (dark panel + light half) | minimal (light)
#   fonts_qa: reliable = metric-identical font available for fit checks here; approximate = check by eye
def _d(**kw):
    base = dict(pos="2E9E6C", neg="D64545", radius=0.0, card="tint", frame="classic", cover="field",
                gradient_to=None, fonts_qa="reliable")
    base.update(kw)
    return base


DIRECTIONS: dict[str, dict] = {
    # ---------------------------------------------------------------- formal
    "consulting-navy": _d(
        bg="FFFFFF", ink="111827", muted="5B6673", primary="13294B", accent="1E6FD9",
        panel="EEF2F7", rule="CBD2DC", grey="AAB3C0", dark="0B1B33", on_dark="FFFFFF",
        on_dark_muted="AFC0D8", heading_font="Cambria", body_font="Calibri", cover="gradient",
        gradient_to="1E4FBF", tone="formal", formality="high", mood="structured, analytical, answer-first",
        suits="case competitions, client readouts, steering committees, board books",
        avoid="personal stories, playful events"),
    "boardroom-oxblood": _d(
        bg="FBF8F3", ink="1F1A17", muted="6B6158", primary="5E1B26", accent="0E7C6B",
        panel="F1EAE1", rule="D9CFC2", grey="B9AFA4", dark="4A1520", on_dark="FBF8F3",
        on_dark_muted="D9B9BE", heading_font="Cambria", body_font="Calibri", card="border",
        tone="formal", formality="high", mood="senior, measured, warm authority",
        suits="board asks, investment committees, law and finance, capital requests",
        avoid="youth audiences, tech launches"),
    "mono-ink": _d(
        bg="FFFFFF", ink="111111", muted="5A5A5A", primary="222222", accent="1E3A5F",
        panel="F2F2F2", rule="D0D0D0", grey="B0B0B0", dark="1A1A1A", on_dark="FFFFFF",
        on_dark_muted="BBBBBB", heading_font="Cambria", body_font="Calibri", card="border",
        frame="clean", cover="minimal", tone="formal", formality="high",
        mood="austere, academic, ink on paper",
        suits="research readouts, thesis defences, legal, policy briefs",
        avoid="anything that must feel energetic"),
    "public-sector": _d(
        bg="FFFFFF", ink="0B0C0C", muted="505A5F", primary="005EA5", accent="D4351C",
        panel="F3F2F1", rule="B1B4B6", grey="B1B4B6", dark="0B0C0C", on_dark="FFFFFF",
        on_dark_muted="C7CBCE", heading_font="Arial", body_font="Arial", frame="clean",
        tone="formal", formality="high", mood="plain, accessible, high contrast",
        suits="government, NGOs, accessibility-critical audiences, large rooms",
        avoid="luxury or lifestyle brands"),
    "finance-emerald": _d(
        bg="FFFFFF", ink="0B2A22", muted="4B5F58", primary="064E3B", accent="B8860B",
        panel="EFF7F3", rule="C9DDD3", grey="A9BDB4", dark="053A2C", on_dark="FFFFFF",
        on_dark_muted="B5D3C6", heading_font="Cambria", body_font="Calibri", card="border",
        radius=0.06, tone="formal", formality="high", mood="understated, trustworthy, banking",
        suits="banking, insurance, investor updates, audit and governance, valuation",
        avoid="consumer marketing, playful decks"),
    # ---------------------------------------------------------------- refined
    "editorial-warm": _d(
        bg="FAF7F2", ink="22201D", muted="6E675E", primary="2F4A3F", accent="C2410C",
        panel="F0EBE3", rule="DDD5C8", grey="B8B0A3", dark="2B2A27", on_dark="FAF7F2",
        on_dark_muted="CFC6B8", heading_font="Cambria", body_font="Calibri", frame="editorial",
        tone="refined", formality="medium", mood="warm, human, rigorous",
        suits="personal story, interviews, research narratives, case decks that should be remembered",
        avoid="dense dashboards"),
    "forest-sage": _d(
        bg="FFFFFF", ink="17231D", muted="56635B", primary="2C5F2D", accent="C27C0E",
        panel="EEF3EC", rule="CFDCCB", grey="AEBBAA", dark="1E3B26", on_dark="FFFFFF",
        on_dark_muted="B9CDB5", heading_font="Cambria", body_font="Calibri", radius=0.08,
        tone="refined", formality="medium", mood="calm, natural, grounded",
        suits="sustainability, public health, agriculture, FMCG, teaching",
        avoid="nightlife, luxury"),
    "gallery-white": _d(
        bg="FFFFFF", ink="1C1C1C", muted="6B6B6B", primary="3A3A3A", accent="B4532A",
        panel="F5F5F3", rule="E2E2DE", grey="C8C8C4", dark="1C1C1C", on_dark="FFFFFF",
        on_dark_muted="BDBDBD", heading_font="Bookman Old Style", body_font="Calibri", frame="clean",
        cover="minimal", tone="refined", formality="medium", mood="lots of air, few words",
        suits="portfolios, design reviews, keynote openers, talk mode",
        avoid="dense analytical readouts"),
    "nordic-calm": _d(
        bg="F4F1EC", ink="1F2A27", muted="5F6B66", primary="3E6B5B", accent="C9693C",
        panel="E9E4DC", rule="D6CFC4", grey="B9B2A6", dark="25332E", on_dark="F4F1EC",
        on_dark_muted="C2CBC6", heading_font="Calibri", body_font="Calibri", radius=0.12,
        frame="clean", tone="refined", formality="medium", mood="soft, considered, Scandinavian",
        suits="wellness, people and HR, culture decks, internal strategy offsites",
        avoid="aggressive sales pitches"),
    "terracotta-editorial": _d(
        bg="F7F1E8", ink="3A2E28", muted="8A7A6D", primary="7C4A3A", accent="2F6F6A",
        panel="EFE6DA", rule="DCCFBF", grey="C2B4A4", dark="4A2F25", on_dark="F7F1E8",
        on_dark_muted="D8C4B6", heading_font="Century Schoolbook", body_font="Calibri", radius=0.1,
        frame="editorial", cover="split", tone="refined", formality="medium",
        mood="warm editorial, generous whitespace",
        suits="hospitality, lifestyle brands, food, non-profits, culture",
        avoid="hard-tech, finance"),
    "luxe-noir": _d(
        bg="FFFFFF", ink="141414", muted="5E5A52", primary="141414", accent="A67C2E",
        panel="F4F1EA", rule="DCD5C6", grey="BDB6A6", dark="0E0E0E", on_dark="F4EFE4",
        on_dark_muted="BFB49A", heading_font="Palatino Linotype", body_font="Calibri",
        frame="editorial", cover="field", fonts_qa="approximate", tone="refined",
        formality="high", mood="black and gold, quiet luxury",
        suits="luxury brands, awards, galas, premium proposals",
        avoid="public sector, budget-conscious audiences"),
    # ---------------------------------------------------------------- bold
    "modern-teal": _d(
        bg="FFFFFF", ink="0F172A", muted="55626F", primary="0F4C5C", accent="E36414",
        panel="EEF5F6", rule="CFE0E3", grey="A3B8BD", dark="0F2F38", on_dark="FFFFFF",
        on_dark_muted="A9C9CF", heading_font="Calibri", body_font="Calibri", radius=0.1,
        card="shadow", cover="gradient", gradient_to="157A8C", tone="bold", formality="medium",
        mood="modern, product-clean", suits="product, tech, operations, QBRs, SaaS",
        avoid="heritage or luxury brands"),
    "bold-signal": _d(
        bg="FFFFFF", ink="111111", muted="555555", primary="111111", accent="D7261E",
        panel="F3F3F1", rule="D9D9D6", grey="B5B5B0", dark="111111", on_dark="FFFFFF",
        on_dark_muted="BDBDBD", heading_font="Arial", body_font="Arial", frame="clean",
        tone="bold", formality="medium", mood="one loud colour, big numbers",
        suits="pitches, launches, manifestos, one-number stories",
        avoid="sensitive or sombre topics"),
    "dark-stage": _d(
        bg="15181D", ink="EEF0F3", muted="9AA3AE", primary="8FA3BF", accent="35C2A0",
        panel="1F242B", rule="323A45", grey="5B6572", dark="0D0F12", on_dark="FFFFFF",
        on_dark_muted="9AA3AE", heading_font="Calibri", body_font="Calibri", radius=0.08,
        frame="clean", cover="gradient", gradient_to="1D3B45", tone="bold", formality="medium",
        mood="keynote on a dark stage", suits="keynotes, AI/tech vision talks, evening events",
        avoid="printed handouts, dense tables"),
    "electric-launch": _d(
        bg="FFFFFF", ink="14112B", muted="5B587A", primary="4C2BD9", accent="F2542D",
        panel="F1EFFD", rule="DAD5F7", grey="B8B3E3", dark="1B1240", on_dark="FFFFFF",
        on_dark_muted="C6BEF5", heading_font="Arial", body_font="Calibri", radius=0.14,
        card="shadow", cover="gradient", gradient_to="7B3FE4", tone="bold", formality="low",
        mood="energetic product launch", suits="product launches, startup demo days, hackathons",
        avoid="board governance, sombre topics"),
    "blueprint": _d(
        bg="0E3A68", ink="FFFFFF", muted="B7CBE2", primary="7FB2E5", accent="FFD166",
        panel="16477C", rule="2E5D90", grey="5B7FA6", dark="0A2B4E", on_dark="FFFFFF",
        on_dark_muted="B7CBE2", heading_font="Arial", body_font="Arial", frame="clean",
        tone="bold", formality="medium", mood="technical drawing, white on blue",
        suits="engineering, architecture, systems design, operations blueprints",
        avoid="consumer brand, HR"),
    "night-terminal": _d(
        bg="0B0F0C", ink="E6F4EA", muted="8FA897", primary="4ADE80", accent="FACC15",
        panel="111813", rule="1F2B22", grey="3E5245", dark="070A08", on_dark="E6F4EA",
        on_dark_muted="8FA897", heading_font="Courier New", body_font="Arial", frame="clean",
        tone="creative", formality="low", mood="console green on black",
        suits="developer talks, cybersecurity, hackathons, data engineering",
        avoid="executives who do not code"),
    # ---------------------------------------------------------------- creative
    "poster-yellow": _d(
        bg="FFD60A", ink="111111", muted="3D3D3D", primary="111111", accent="E63946",
        panel="FFE45C", rule="111111", grey="6B6B6B", dark="111111", on_dark="FFD60A",
        on_dark_muted="E5E5E5", heading_font="Arial", body_font="Arial", frame="clean",
        cover="minimal", tone="creative", formality="low", mood="loud poster, black on yellow",
        suits="manifestos, campaign launches, club recruitment, rallies",
        avoid="anything sensitive, finance, health"),
    "coral-studio": _d(
        bg="FFF6F0", ink="0F3D3E", muted="5F7A7A", primary="0F3D3E", accent="FF7A59",
        panel="FFE9DE", rule="F2D3C4", grey="C5D2D2", dark="0F3D3E", on_dark="FFF6F0",
        on_dark_muted="BFD6D6", heading_font="Arial", body_font="Calibri", radius=0.2,
        card="shadow", cover="split", tone="creative", formality="low",
        mood="playful, warm, design-led", suits="marketing, social media, creative agencies, D2C brands",
        avoid="board governance, audits"),
    "pastel-friendly": _d(
        bg="FDF4FF", ink="3B1F5C", muted="7C6F9C", primary="7C3AED", accent="F472B6",
        panel="F5EAFE", rule="E6D5F7", grey="C9B8E0", dark="3B1F5C", on_dark="FFFFFF",
        on_dark_muted="DCCBF2", heading_font="Arial", body_font="Calibri", radius=0.24,
        card="shadow", frame="clean", tone="creative", formality="low",
        mood="soft, friendly, very rounded", suits="education, wellness, peer teaching, club socials",
        avoid="senior executives, finance"),
    "campus-bright": _d(
        bg="FFFFFF", ink="10162F", muted="5A6178", primary="1D3FBB", accent="FFB000",
        panel="EEF2FF", rule="D4DCF5", grey="AEB8D6", dark="10162F", on_dark="FFFFFF",
        on_dark_muted="BFC9EE", heading_font="Arial", body_font="Calibri", radius=0.12,
        cover="gradient", gradient_to="3B5BDB", tone="creative", formality="low",
        mood="high-energy, youthful, two bold colours",
        suits="club events, student fests, recruitment drives, orientation",
        avoid="sombre topics, investors"),
    "heritage-india": _d(
        bg="FFFBF4", ink="1E1B3A", muted="5C5872", primary="23285A", accent="E07A1F",
        panel="F7EEDD", rule="E5D6BB", grey="C7BBA5", dark="1E1B3A", on_dark="FFF7EA",
        on_dark_muted="D8CDB4", heading_font="Cambria", body_font="Calibri", radius=0.06,
        card="border", frame="editorial", tone="refined", formality="medium",
        mood="deep indigo with marigold, warm Indian heritage without cliches",
        suits="Indian brand cases, cultural events, Bharat/rural market stories, festivals",
        avoid="global tech launches"),
}
DEFAULT_DIRECTION = "consulting-navy"


def resolve_theme(direction: str | None, overrides: dict | None) -> dict:
    name = direction or DEFAULT_DIRECTION
    if name not in DIRECTIONS:
        raise SpecError(f"unknown direction '{name}'. Choose one of: {', '.join(DIRECTIONS)}")
    theme = dict(DIRECTIONS[name])
    for k, v in (overrides or {}).items():
        if isinstance(v, str):
            v = v.lstrip("#")
        theme[k] = v
    theme["name"] = name
    return theme


# --------------------------------------------------------------------------------------
# Font metrics (Pillow) -> line-wrapping estimates that match LibreOffice renders closely
# --------------------------------------------------------------------------------------
_FONT_FILES = {
    ("calibri", False): "Carlito-Regular.ttf", ("calibri", True): "Carlito-Bold.ttf",
    ("cambria", False): "Caladea-Regular.ttf", ("cambria", True): "Caladea-Bold.ttf",
    ("arial", False): "LiberationSans-Regular.ttf", ("arial", True): "LiberationSans-Bold.ttf",
    ("times new roman", False): "LiberationSerif-Regular.ttf",
    ("times new roman", True): "LiberationSerif-Bold.ttf",
    ("georgia", False): "DejaVuSerif.ttf", ("georgia", True): "DejaVuSerif-Bold.ttf",
    # TeX Gyre clones are metric-compatible with these Office fonts
    ("century schoolbook", False): "texgyreschola-regular.otf",
    ("century schoolbook", True): "texgyreschola-bold.otf",
    ("bookman old style", False): "texgyrebonum-regular.otf",
    ("bookman old style", True): "texgyrebonum-bold.otf",
    ("palatino linotype", False): "texgyrepagella-regular.otf",
    ("palatino linotype", True): "texgyrepagella-bold.otf",
    ("courier new", False): "LiberationMono-Regular.ttf", ("courier new", True): "LiberationMono-Bold.ttf",
    ("verdana", False): "DejaVuSans.ttf", ("verdana", True): "DejaVuSans-Bold.ttf",
}
_FONT_DIRS = ["/usr/share/fonts", "/usr/share/texmf/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
              "/Library/Fonts", "/System/Library/Fonts", "C:/Windows/Fonts"]


@lru_cache(maxsize=None)
def _find_font_file(fname: str) -> str | None:
    for root in _FONT_DIRS:
        if not os.path.isdir(root):
            continue
        for dirpath, _, files in os.walk(root):
            if fname in files:
                return os.path.join(dirpath, fname)
    return None


@lru_cache(maxsize=None)
def _pil_font(family: str, bold: bool, size_px: int):
    from PIL import ImageFont
    key = (family.lower(), bold)
    candidates = [_FONT_FILES.get(key), _FONT_FILES.get(("calibri", bold)), "DejaVuSans.ttf"]
    for c in candidates:
        if not c:
            continue
        path = _find_font_file(c)
        if path:
            return ImageFont.truetype(path, size_px)
    return ImageFont.load_default()


def text_width_pt(text: str, family: str, size_pt: float, bold: bool = False) -> float:
    """Width of a string in points at the given size (measured at 10x for precision)."""
    scale = 10
    font = _pil_font(family, bold, int(round(size_pt * scale)))
    try:
        w = font.getlength(text)
    except AttributeError:  # very old Pillow
        w = font.getsize(text)[0]
    return w / scale


def strip_markup(text: str) -> str:
    return text.replace("**", "")


def wrap_count(text: str, family: str, size_pt: float, width_in: float, bold: bool = False) -> int:
    """Number of rendered lines for text (paragraphs split on \\n) in a box width_in wide."""
    width_pt = width_in * 72.0 * 0.985  # small safety margin for renderer differences
    total = 0
    for para in strip_markup(text).split("\n"):
        words = para.split(" ")
        if not para.strip():
            total += 1
            continue
        lines, cur = 1, ""
        for w in words:
            trial = (cur + " " + w).strip()
            if text_width_pt(trial, family, size_pt, bold) <= width_pt or not cur:
                cur = trial
                # a single word wider than the box still occupies (and breaks) lines
                ww = text_width_pt(cur, family, size_pt, bold)
                if ww > width_pt and cur == w:
                    lines += int(ww // width_pt)
            else:
                lines += 1
                cur = w
        total += lines
    return total


def text_height_in(text: str, family: str, size_pt: float, width_in: float, bold: bool = False,
                   line_spacing: float = 1.15, para_space_pt: float = 0.0) -> float:
    n_lines = wrap_count(text, family, size_pt, width_in, bold)
    n_paras = max(1, len(strip_markup(text).split("\n")))
    return (n_lines * size_pt * 1.2 * line_spacing / 1.15 + (n_paras - 1) * para_space_pt) / 72.0


def fit_size(text: str, family: str, width_in: float, height_in: float, max_pt: float,
             min_pt: float, bold: bool = False, max_lines: int | None = None,
             line_spacing: float = 1.15, para_space_pt: float = 0.0) -> tuple[float, bool]:
    """Largest size in [min_pt, max_pt] (0.5pt steps) that fits; returns (size, fits)."""
    size = max_pt
    while size >= min_pt - 1e-6:
        h = text_height_in(text, family, size, width_in, bold, line_spacing, para_space_pt)
        lines = wrap_count(text, family, size, width_in, bold)
        if h <= height_in + 1e-6 and (max_lines is None or lines <= max_lines):
            return size, True
        size -= 0.5
    return min_pt, False


# --------------------------------------------------------------------------------------
# Fact model: one source of truth for every number that appears on more than one slide.
#   "facts":  {"rev": [0.6, 1.8, 3.5], "capex": 1.2}
#   strings:  "Revenue reaches {=rev[2]|0.1f}M by Y3"  ->  "Revenue reaches 3.5M by Y3"
#   arrays:   "values": "=rev"
#   checks:   ["approx(sum(rev), 5.9)", "ebitda[2] == rev[2] - cost[2]"]
# Expressions are evaluated with a whitelist-only AST evaluator (no attribute access,
# no imports, no dunder) so a spec can never execute arbitrary code.
# --------------------------------------------------------------------------------------
class SpecError(Exception):
    pass


_BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv}
_CMP = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt, ast.LtE: operator.le,
        ast.Gt: operator.gt, ast.GtE: operator.ge}


def _approx(a, b, tol=0.005):
    """True when a and b agree within tol (relative, or absolute for values near zero)."""
    return abs(a - b) <= max(abs(tol), abs(tol) * max(abs(a), abs(b)))


def _pct(a, b):
    """Percentage change from a to b."""
    return (b - a) / a * 100.0


def _cagr(first, last, years):
    return ((last / first) ** (1.0 / years) - 1) * 100.0


def _cumsum(xs):
    out, s = [], 0
    for x in xs:
        s += x
        out.append(s)
    return out


def _vadd(a, b):
    return [x + y for x, y in zip(a, b)]


def _vsub(a, b):
    return [x - y for x, y in zip(a, b)]


_FUNCS = {"sum": sum, "min": min, "max": max, "len": len, "abs": abs, "round": round,
          "approx": _approx, "pct": _pct, "cagr": _cagr, "cumsum": _cumsum,
          "vadd": _vadd, "vsub": _vsub, "avg": lambda xs: sum(xs) / len(xs),
          "share": lambda part, whole: part / whole * 100.0, "all": all, "any": any,
          "wavg": lambda vals, wts: sum(v * w for v, w in zip(vals, wts)) / float(sum(wts)),
          "list": list,
          # index of the first element meeting a threshold, e.g. payback year: first_at_least(cumsum(profit), 0)
          "first_at_least": lambda xs, x: next((i for i, v in enumerate(xs) if v >= x), -1),
          # S-curve values: logistic(n, cap, mid, k) -> n points rising to cap, steepest at index mid
          "logistic": lambda n, cap, mid, k=1.0: [round(cap / (1 + 2.718281828 ** (-k * (i - mid))), 4)
                                                for i in range(int(n))],
          "rng": lambda n: list(range(int(n)))}


def safe_eval(expr: str, facts: dict):
    tree = ast.parse(expr.strip(), mode="eval")

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, str, bool)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in facts:
                return facts[node.id]
            if node.id in ("True", "False"):
                return node.id == "True"
            raise SpecError(f"unknown fact '{node.id}' in expression: {expr}")
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
            return _BIN[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            v = ev(node.operand)
            return -v if isinstance(node.op, ast.USub) else v
        if isinstance(node, ast.BoolOp):
            vals = [ev(v) for v in node.values]
            return all(vals) if isinstance(node.op, ast.And) else any(vals)
        if isinstance(node, ast.Compare):
            left = ev(node.left)
            for op, comp in zip(node.ops, node.comparators):
                right = ev(comp)
                if type(op) not in _CMP or not _CMP[type(op)](left, right):
                    return False
                left = right
            return True
        if isinstance(node, ast.Subscript):
            target = ev(node.value)
            sl = node.slice
            if isinstance(sl, ast.Slice):
                lo = ev(sl.lower) if sl.lower else None
                hi = ev(sl.upper) if sl.upper else None
                return target[lo:hi]
            return target[ev(sl)]
        if isinstance(node, ast.List):
            return [ev(e) for e in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(ev(e) for e in node.elts)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
            return _FUNCS[node.func.id](*[ev(a) for a in node.args])
        raise SpecError(f"unsupported expression element in: {expr}")

    return ev(tree)


_TOKEN = re.compile(r"\{=([^{}|]+)(?:\|([^{}]+))?\}")


def _fmt(value, spec: str | None) -> str:
    if spec is None:
        if isinstance(value, float):
            return f"{value:,.1f}".rstrip("0").rstrip(".") if abs(value) < 1e15 else str(value)
        return f"{value:,}" if isinstance(value, int) else str(value)
    sign = spec.startswith("+")
    core = spec[1:] if sign else spec
    out = format(value, core)
    if sign and isinstance(value, (int, float)) and value > 0:
        out = "+" + out
    return out


def render_tokens(text, facts: dict):
    """Replace {=expr|fmt} tokens in strings (recursively through lists/dicts)."""
    if isinstance(text, str):
        if text.startswith("=") and not text.startswith("=="):
            return safe_eval(text[1:], facts)
        return _TOKEN.sub(lambda m: _fmt(safe_eval(m.group(1), facts), m.group(2)), text)
    if isinstance(text, list):
        return [render_tokens(t, facts) for t in text]
    if isinstance(text, dict):
        return {k: render_tokens(v, facts) for k, v in text.items()}
    return text


# --------------------------------------------------------------------------------------
# Wording heuristics shared by build and lint
# --------------------------------------------------------------------------------------
_VERBISH = re.compile(
    r"\b(is|are|was|were|be|been|has|have|had|will|would|can|could|should|must|need|needs|"
    r"grow|grows|grew|fall|falls|fell|rise|rises|rose|beat|beats|lead|leads|led|drive|drives|"
    r"cut|cuts|cost|costs|reach|reaches|enter|exceed|exceeds|outperform|outperforms|lose|loses|"
    r"win|wins|double|doubles|halve|halves|break|breaks|pays?|delivers?|creates?|requires?|"
    r"means|shows|makes?|gives?|takes?|keeps?|stays?|remains?|holds?|turns?|moves?|lags?|"
    r"trails?|adds?|saves?|unlocks?|protects?|limits?|caps?|depends?|explains?|accounts?|"
    r"starts?|begins?|launch(es)?|matters?|works?|fits?|offsets?|lands?|covers?|beats?|gets?|"
    r"wins?|fails?|helps?|lifts?|drops?|slips?|shifts?|runs?|ran|comes?|came|goes|went|"
    r"[a-z]{3,}ed)\b|\b(not|no|only|than|vs)\b", re.I)
PLACEHOLDER = re.compile(r"\[(CONFIRM|TBD|TODO|VERIFY|INSERT|IMAGE NEEDED)[^\]]*\]|lorem|ipsum|\bx{3,}\b|"
                         r"click to (add|edit)|\[insert", re.I)
NUMBER = re.compile(r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?\s?(%|x|bn|mn|m|k|cr|lakh|pp|bps)?", re.I)


def is_label_title(title: str) -> bool:
    """A topic label instead of a claim: short and verb-less (questions are allowed)."""
    t = strip_markup(title or "").strip()
    if not t or t.endswith("?"):
        return False
    words = t.split()
    if len(words) <= 3 and not any(ch.isdigit() for ch in t):
        return True
    if _VERBISH.search(t) or len(words) > 6:
        return False
    # 4-6 words with no recognised verb: a label only if it is styled like one (Title Case,
    # a colon or an ampersand); sentence-case phrases are usually claims with an unlisted verb
    caps = sum(1 for w in words if w[:1].isupper())
    label_start = words[0].lower() in {"our", "key", "overview", "summary", "introduction",
                                       "background", "approach", "next", "agenda", "appendix"}
    return caps >= len(words) - 1 or ":" in t or "&" in t or label_start


def has_figures(text: str) -> bool:
    for m in NUMBER.finditer(text or ""):
        token = m.group(0).strip()
        digits = re.sub(r"\D", "", token)
        if re.fullmatch(r"0\d", token):  # agenda/section numbering such as 01, 02
            continue
        if m.group(1) or len(digits) >= 2:
            return True
    return False


# --------------------------------------------------------------------------------------
# Human voice: phrases that make slide text read as machine-written (references/human-voice.md).
# These are density signals, not proof; a hit is a prompt to rewrite with the specific fact.
# --------------------------------------------------------------------------------------
_AI_WORDS = (
    r"delve[sd]?|delving|tapestry|vibrant|crucial|pivotal|seamless(?:ly)?|robust|holistic|multifaceted|"
    r"cutting[- ]edge|state[- ]of[- ]the[- ]art|game[- ]chang(?:er|ing)|transformative|revolutioni[sz]e[sd]?|"
    r"elevat(?:e|es|ed|ing)|empower(?:s|ed|ing|ment)?|unlock(?:s|ed|ing)?|unleash(?:es|ed|ing)?|"
    r"harness(?:es|ed|ing)?|leverag(?:e|es|ed|ing)|foster(?:s|ed|ing)?|garner(?:s|ed)?|"
    r"showcas(?:e|es|ed|ing)|underscor(?:e|es|ed|ing)|testament|realm|myriad|plethora|ever[- ]evolving|"
    r"fast[- ]paced|synerg(?:y|ies)|paradigm|embark(?:s|ed)?|spearhead(?:s|ed)?|meticulous(?:ly)?|"
    r"intricate|nuanced|bustling|nestled|treasure trove|north star|best[- ]in[- ]class|world[- ]class|"
    r"next[- ]level|supercharge[sd]?|streamline[sd]?|reimagin(?:e|es|ed|ing)|actionable insights|"
    r"key takeaways?|deep dive|dive (?:into|deeper)|at the forefront|in today'?s|digital age|"
    r"stands as|serves as|plays? an? (?:vital|crucial|key|pivotal|important) role|"
    r"(?:it'?s|it is) (?:important|worth) (?:to note|noting)|moreover|furthermore|additionally|"
    r"in conclusion|in summary|ultimately|navigat(?:e|es|ed|ing) (?:the|this|a) |landscape|"
    r"(?<!customer )(?<!user )(?<!buyer )(?<!patient )journey")
_AI_WORD_RE = re.compile(r"\b(?:" + _AI_WORDS + r")\b", re.I)
_AI_FORMULAS = [
    ("not_just", re.compile(r"\b(?:not|isn'?t|aren'?t|wasn'?t)\s+(?:just|only|merely|simply)\b[^.;:]{0,60}?\b(?:but|it'?s|they'?re|it is)\b", re.I)),
    ("not_x_its_y", re.compile(r"\b(?:it'?s|this is|that'?s)\s+not\s+(?:about\s+)?[^.;,]{1,40}[.,;]\s*(?:it'?s|this is)\b", re.I)),
    ("no_x_no_y", re.compile(r"\bno\s+\w+\.\s*no\s+\w+\.", re.I)),
    ("ing_tail", re.compile(r",\s+(?:highlighting|underscoring|ensuring|showcasing|reflecting|emphasi[sz]ing|"
                            r"demonstrating|cementing|solidifying|fostering|paving the way|setting the stage|"
                            r"enabling|driving|unlocking)\b", re.I)),
    ("vague_source", re.compile(r"\b(?:experts|studies|research|reports|analysts|industry (?:reports|experts))\s+"
                                r"(?:say|show|suggest|agree|believe|indicate)s?\b", re.I)),
    ("chatbot", re.compile(r"\b(?:certainly!|i hope this helps|as an ai|great question|let'?s dive)\b", re.I)),
    ("hype_close", re.compile(r"\b(?:the future (?:is|looks) bright|exciting times ahead|the possibilities are endless|"
                              r"only the beginning|let'?s (?:make it happen|build the future))\b", re.I)),
]
_EMOJI = re.compile("[\U0001F000-\U0001FAFF\uFE0F]")  # pictographic emoji; typographic glyphs (★ ✓ →) are fine


def ai_tells(text: str) -> list[tuple[str, str]]:
    """Return (code, snippet) for each machine-voice signal in one piece of slide text."""
    text = strip_markup(text or "")
    out = []
    for m in _AI_WORD_RE.finditer(text):
        out.append(("ai_word", m.group(0).strip()))
    for code, rx in _AI_FORMULAS:
        m = rx.search(text)
        if m:
            out.append((code, m.group(0).strip()[:60]))
    if "—" in text and text.strip() != "—":  # a lone dash in a table cell means "none"
        out.append(("em_dash", "— (use a comma, colon or full stop)"))
    if _EMOJI.search(text):
        out.append(("emoji", _EMOJI.search(text).group(0)))
    return out


def deck_voice(titles: list[str], list_lengths: list[int]) -> list[str]:
    """Deck-level rhythm tells: every list in threes, every title the same shape."""
    msgs = []
    lists = [n for n in list_lengths if n >= 2]
    if len(lists) >= 4 and sum(1 for n in lists if n == 3) / len(lists) >= 0.6:
        msgs.append(f"rule of three: {sum(1 for n in lists if n == 3)} of {len(lists)} lists have exactly three "
                    "items; let the content set the count")
    ts = [re.sub(r"^[A-Z0-9]{1,2}:\s+", "", strip_markup(t).strip()) for t in titles if t and len(t.split()) > 3]  # drop "A:" letters
    if len(ts) >= 5:
        colon = sum(1 for t in ts if ":" in t)
        if colon / len(ts) >= 0.5:
            msgs.append(f"{colon} of {len(ts)} titles use 'X: Y'; vary the headline shape")
        firsts = [t.split()[0].lower() for t in ts]
        top = max(set(firsts), key=firsts.count)
        if firsts.count(top) >= max(3, len(ts) // 3):
            msgs.append(f"{firsts.count(top)} titles start with '{top}'; vary the openings")
        lens = [len(t.split()) for t in ts]
        if max(lens) - min(lens) <= 2 and len(ts) >= 8:
            msgs.append("every title is the same length; mix short and long headlines")
    return msgs


_VOICE_SKIP = {"notes", "quote", "code", "path", "image", "photo", "alt", "id", "type", "style", "kind",
               "direction", "frame", "source", "credit", "icon", "state", "status", "number_format"}


def slide_strings(s, skip=_VOICE_SKIP):
    """Every visible string on a spec slide (quotes, code, sources and notes excluded)."""
    if s.get("type") in ("references", "code") if isinstance(s, dict) else False:
        return
    if isinstance(s, dict):
        for k, v in s.items():
            if k in skip:
                continue
            yield from slide_strings(v, skip)
    elif isinstance(s, list):
        for v in s:
            yield from slide_strings(v, skip)
    elif isinstance(s, str) and not s.startswith("="):
        yield s


def list_lengths(s) -> list[int]:
    """Lengths of the visible lists on a slide (bullets, cards, steps, columns...)."""
    out = []
    for k in ("items", "points", "steps", "columns", "cards", "spokes", "stages", "levels", "tiers",
              "people", "branches", "lanes", "milestones", "why", "cost"):
        v = s.get(k)
        if isinstance(v, list):
            out.append(len(v))
    return out


def voice_report(spec: dict) -> list[str]:
    """Human-voice findings for a whole spec: per-slide tells plus deck-level rhythm."""
    msgs, lens, titles = [], [], []
    for i, s in enumerate(spec.get("slides", []), 1):
        seen = set()
        for txt in slide_strings(s):
            for code, snip in ai_tells(txt):
                key = (code, snip.lower())
                if key not in seen:
                    seen.add(key)
                    msgs.append(f"slide {i}: {code} '{snip}'")
        lens += list_lengths(s)
        if s.get("type") not in ("cover", "divider", "closing", "agenda", "quote"):
            titles.append(s.get("title", ""))
    return msgs + deck_voice(titles, lens)

#!/usr/bin/env python3
"""Charts PowerPoint cannot draw natively, rendered as crisp PNGs in a direction's colours.

  python chart_images.py spec.json -o chart.png [--direction consulting-navy] [--w 8.4 --h 4.6]

The result is a PICTURE (not editable data): use it only when the chart form matters more than
editability, always give it alt text, and keep the numbers in `facts` so the text still ties out.
Place it with an `image` slide (side panel for the so-what) or `before_after` / `gallery`.

Kinds (spec JSON):
  mekko    {"kind":"mekko","segments":["A","B"],"columns":[{"label":"North","width":40,"shares":[60,40]}],
            "highlight":[col, seg]}        market map: column width = market size, stacks = shares (%)
  slope    {"kind":"slope","left":"2024","right":"2026","items":[{"label":"X","a":12,"b":19}],"highlight":0}
  dumbbell {"kind":"dumbbell","a_label":"Today","b_label":"Target","items":[{"label":"X","a":40,"b":65}]}
  heatmap  {"kind":"heatmap","rows":[...],"cols":[...],"values":[[...]],"fmt":"{:.0f}%"}
  bullet   {"kind":"bullet","items":[{"label":"NPS","value":42,"target":50,"max":100}]}  progress vs target
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import resolve_theme, SpecError  # noqa: E402


def _c(h):
    return "#" + h.lstrip("#")


def setup(t, w, h):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    fam = {"Calibri": "Carlito", "Cambria": "Caladea", "Arial": "Liberation Sans"}.get(t["body_font"], "DejaVu Sans")
    if not any(fam in f.name for f in font_manager.fontManager.ttflist):
        fam = "DejaVu Sans"
    plt.rcParams.update({"font.family": fam, "font.size": 12, "axes.edgecolor": _c(t["rule"]),
                         "axes.labelcolor": _c(t["muted"]), "xtick.color": _c(t["muted"]),
                         "ytick.color": _c(t["muted"]), "text.color": _c(t["ink"]),
                         "figure.facecolor": _c(t["bg"]), "axes.facecolor": _c(t["bg"]),
                         "savefig.facecolor": _c(t["bg"])})
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    return plt, fig, ax


def mekko(ax, t, sp):
    cols = sp["columns"]
    segs = sp["segments"]
    total = sum(c["width"] for c in cols)
    hl = sp.get("highlight")
    shades = [t["primary"], t["grey"], t["panel"], t["muted"], t["rule"]]
    x = 0
    for ci, c in enumerate(cols):
        w = c["width"] / total * 100
        y = 0
        for si, share in enumerate(c["shares"]):
            on = hl == [ci, si]
            col = t["accent"] if on else shades[si % len(shades)]
            ax.bar(x + w / 2, share, width=w * 0.985, bottom=y, color=_c(col), edgecolor=_c(t["bg"]), linewidth=1.5)
            if share >= 8 and w >= 7:
                dark = col in (t["primary"], t["muted"], t["accent"])
                ax.text(x + w / 2, y + share / 2, f"{share:.0f}%", ha="center", va="center", fontsize=10,
                        color="white" if dark else _c(t["ink"]), fontweight="bold" if on else "normal")
            y += share
        ax.text(x + w / 2, -4, f"{c['label']}\n{c['width']:g}", ha="center", va="top", fontsize=10.5)
        x += w
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xticks([])
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.spines["bottom"].set_visible(False)
    handles = [__import__("matplotlib.patches", fromlist=["Patch"]).Patch(color=_c(shades[i % len(shades)]), label=s)
               for i, s in enumerate(segs)]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=10.5)
    if sp.get("width_label"):
        ax.set_xlabel(sp["width_label"], labelpad=34)


def slope(ax, t, sp):
    hl = sp.get("highlight")
    for i, it in enumerate(sp["items"]):
        on = hl == i
        col = _c(t["accent"] if on else t["grey"])
        ax.plot([0, 1], [it["a"], it["b"]], color=col, linewidth=3 if on else 1.8, marker="o", markersize=7)
        fmt = sp.get("fmt", "{:g}")
        ax.text(-0.04, it["a"], f"{it['label']}  {fmt.format(it['a'])}", ha="right", va="center", fontsize=11,
                color=_c(t["ink"] if on else t["muted"]), fontweight="bold" if on else "normal")
        ax.text(1.04, it["b"], f"{fmt.format(it['b'])}", ha="left", va="center", fontsize=11,
                color=_c(t["ink"] if on else t["muted"]), fontweight="bold" if on else "normal")
    ax.set_xlim(-0.6, 1.3)
    ax.set_xticks([0, 1])
    ax.set_xticklabels([sp.get("left", ""), sp.get("right", "")], fontsize=12, fontweight="bold")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)


def dumbbell(ax, t, sp):
    items = sp["items"]
    ys = list(range(len(items)))[::-1]
    for y, it in zip(ys, items):
        ax.plot([it["a"], it["b"]], [y, y], color=_c(t["rule"]), linewidth=4, zorder=1)
        ax.scatter([it["a"]], [y], s=90, color=_c(t["grey"]), zorder=2)
        ax.scatter([it["b"]], [y], s=110, color=_c(t["accent"]), zorder=3)
        ax.text(it["b"] + (1 if it["b"] >= it["a"] else -1) * sp.get("pad", 1.5), y,
                sp.get("fmt", "{:g}").format(it["b"]), va="center",
                ha="left" if it["b"] >= it["a"] else "right", fontsize=11, fontweight="bold")
    ax.set_yticks(ys)
    ax.set_yticklabels([it["label"] for it in items])
    ax.scatter([], [], color=_c(t["grey"]), label=sp.get("a_label", "Before"))
    ax.scatter([], [], color=_c(t["accent"]), label=sp.get("b_label", "After"))
    ax.legend(loc="lower right", frameon=False, fontsize=10.5)
    ax.grid(axis="x", color=_c(t["rule"]), linewidth=0.5)
    ax.set_axisbelow(True)


def heatmap(ax, t, sp):
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    vals = np.array(sp["values"], dtype=float)
    cmap = LinearSegmentedColormap.from_list("d", [_c(t["panel"]), _c(t["primary"])])
    ax.imshow(vals, cmap=cmap, aspect="auto")
    fmt = sp.get("fmt", "{:g}")
    mx = vals.max() if vals.size else 1
    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            ax.text(j, i, fmt.format(vals[i, j]), ha="center", va="center", fontsize=11,
                    color="white" if vals[i, j] > mx * 0.55 else _c(t["ink"]))
    ax.set_xticks(range(len(sp["cols"])))
    ax.set_xticklabels(sp["cols"])
    ax.set_yticks(range(len(sp["rows"])))
    ax.set_yticklabels(sp["rows"])
    ax.xaxis.tick_top()
    for side in ("left", "bottom", "top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)


def bullet(ax, t, sp):
    items = sp["items"]
    ys = list(range(len(items)))[::-1]
    for y, it in zip(ys, items):
        mx = it.get("max", 100)
        ax.barh(y, mx, height=0.55, color=_c(t["panel"]))
        good = it["value"] >= it.get("target", mx)
        ax.barh(y, it["value"], height=0.28, color=_c(t["primary"] if good else t["accent"]))
        if it.get("target") is not None:
            ax.plot([it["target"]] * 2, [y - 0.33, y + 0.33], color=_c(t["ink"]), linewidth=2.5)
        ax.text(mx * 1.01, y, f"{it['value']:g} / {it.get('target', '')}", va="center", fontsize=11)
    ax.set_yticks(ys)
    ax.set_yticklabels([it["label"] for it in items])
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)


def tornado(ax, t, sp):
    """Outcome ranges from one-at-a-time scenarios, not causal attribution."""
    import math
    base = sp.get('base')
    items = sp.get('items', [])
    if not isinstance(base, (int, float)) or isinstance(base, bool) or not math.isfinite(base) or not items:
        raise SpecError('tornado needs a finite base and nonempty items')
    for item in items:
        low, high = item.get('low'), item.get('high')
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in (low, high)) or not low <= base <= high:
            raise SpecError('tornado outcomes must satisfy low <= base <= high')
    items = sorted(items, key=lambda item: item['high'] - item['low'], reverse=True)
    ys = list(range(len(items)))
    for y, item in zip(ys, items):
        ax.barh(y, base - item['low'], left=item['low'], color=_c(t['grey']), height=.55)
        ax.barh(y, item['high'] - base, left=base, color=_c(t['accent']), height=.55)
        ax.annotate(f"{item['low']:g}", (item['low'], y), xytext=(-5, 0), textcoords='offset points', ha='right', va='center', fontsize=10)
        ax.annotate(f"{item['high']:g}", (item['high'], y), xytext=(5, 0), textcoords='offset points', ha='left', va='center', fontsize=10)
    ax.axvline(base, color=_c(t['ink']), linewidth=1)
    ax.set_yticks(ys, [item['label'] for item in items])
    ax.invert_yaxis()
    low = min(item["low"] for item in items)
    high = max(item["high"] for item in items)
    span = high-low or max(abs(base), 1)
    ax.set_xlim(low-span*.18, high+span*.18)
    ax.tick_params(axis="y", pad=12)
    ax.set_xlabel(sp.get('unit', 'Outcome') + f' · Base {base:g} · one input varied at a time')


def sensitivity(ax, t, sp):
    """Exact lookup matrix with a declared base, including negative outcome ranges."""
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, Normalize
    rows, cols = sp.get('rows', []), sp.get('cols', [])
    values = sp.get('values', [])
    base = sp.get('base_cell')
    if not rows or not cols or len(values) != len(rows) or any(len(row) != len(cols) for row in values):
        raise SpecError('sensitivity values must match nonempty row and column labels')
    if not isinstance(base, list) or len(base) != 2 or any(isinstance(v, bool) or not isinstance(v, int) for v in base) or not (0 <= base[0] < len(rows) and 0 <= base[1] < len(cols)):
        raise SpecError('sensitivity needs an in-range base_cell [row, column]')
    vals = np.array(values, dtype=float)
    if not np.isfinite(vals).all():
        raise SpecError('sensitivity values must be finite')
    cmap = LinearSegmentedColormap.from_list('sensitivity', [_c(t['panel']), _c(t['primary'])])
    norm = Normalize(vmin=float(vals.min()), vmax=float(vals.max()))
    ax.imshow(vals, cmap=cmap, norm=norm, aspect='auto')
    def contrast(a, b):
        def lum(h):
            vals = [int(h[k:k+2], 16)/255 for k in (0, 2, 4)]
            vals = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in vals]
            return sum(v*w for v, w in zip(vals, (.2126, .7152, .0722)))
        x, y = sorted((lum(a), lum(b)))
        return (y+.05)/(x+.05)
    for i in range(len(rows)):
        for j in range(len(cols)):
            rgba = cmap(norm(vals[i, j]))
            bg = ''.join(f'{round(c*255):02X}' for c in rgba[:3])
            color = 'FFFFFF' if contrast('FFFFFF', bg) >= contrast('000000', bg) else '000000'
            text = sp.get('fmt', '{:g}').format(vals[i, j])
            if [i, j] == base:
                text += '\n(base)'
            ax.text(j, i, text, ha='center', va='center', color=_c(color), fontsize=11)
    ax.set_xticks(range(len(cols)), cols)
    ax.set_yticks(range(len(rows)), rows)
    ax.xaxis.tick_top()
    ax.set_xlabel(sp.get('unit', 'Outcome'))
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)


KINDS = {"mekko": mekko, "slope": slope, "dumbbell": dumbbell, "heatmap": heatmap, "bullet": bullet, "tornado": tornado, "sensitivity": sensitivity}


def render(spec: dict, out: str, direction=None, w=8.4, h=4.6):
    if spec.get("kind") not in KINDS:
        raise SpecError(f"unsupported image chart: {spec.get('kind')}")
    t = resolve_theme(direction or spec.get("direction"), spec.get("theme"))
    plt, fig, ax = setup(t, w, h)
    KINDS[spec["kind"]](ax, t, spec)
    fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--direction")
    ap.add_argument("--w", type=float, default=8.4)
    ap.add_argument("--h", type=float, default=4.6)
    a = ap.parse_args()
    with open(a.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    print(render(spec, a.out, a.direction, a.w, a.h))


if __name__ == "__main__":
    main()

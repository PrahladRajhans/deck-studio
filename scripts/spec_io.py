#!/usr/bin/env python3
"""Load and validate a deck-studio spec. Shared by the HTML draft builder and the PPTX builder.

No PowerPoint dependency: drafting needs only this module, _common.py and build_html.py.

    python3 spec_io.py spec.json            # validation report (draft rules)
    python3 spec_io.py spec.json --strict   # release gate: exit 2 if anything blocks a final build

Draft mode reports problems as `check` lines and carries on, so iteration stays cheap.
Strict mode (used for the final build, Stage 6) turns the release blockers into errors:
  - numbers typed by hand into slide text or chart data when the deck has a facts model, unless
    the slide declares `data_status` ("sourced" with a `source`, or "illustrative" with an
    Illustrative tag);
  - placeholders ([CONFIRM], [TBD], lorem...) anywhere a viewer would see them;
  - raw facts with no `fact_meta` kind, observed facts without verified evidence, and
    evidence entries that are still "missing" or "unverified".
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (PLACEHOLDER, SpecError, render_tokens, safe_eval, slide_strings,  # noqa: E402
                     strip_markup)

FACT_KINDS = {"observed", "estimate", "forecast", "assumption", "target", "illustrative", "calculated"}
EVIDENCE_STATUS = {"verified", "unverified", "missing"}
DATA_STATUS = {"sourced", "illustrative"}
_HAND = re.compile(r"(?:[₹$€£]|USD|INR|Rs\.?)\s?\d[\d,]*(?:\.\d+)?|\b\d[\d,]*(?:\.\d+)?\s?"
                   r"(?:%|x\b|×|cr\b|crore|lakh|bn\b|mn\b|[MK]\b)")
_NUMWORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
# numeric data fields inside slides (literal numbers here bypass the facts model)
_DATA_KEYS = {"values", "low", "high", "x", "y", "value", "scores", "target", "weight", "width", "shares", "a", "b"}
# list fields whose length a title count can refer to
_COUNTABLE = ("items", "points", "steps", "columns", "spokes", "stages", "levels", "tiers", "people",
              "branches", "lanes", "milestones", "rows", "options")


def _raw_numbers(obj, path=""):
    """Yield (path, value) for literal numbers in data fields (not '=expr' strings)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("notes", "theme", "id", "highlight", "recommended", "start", "end", "number", "feeling",
                     "image_width", "highlight_row", "active", "widths", "totals", "min", "max"):
                continue
            if k in _DATA_KEYS and isinstance(v, (int, float)) and not isinstance(v, bool):
                yield f"{path}.{k}", v
            elif k in _DATA_KEYS and isinstance(v, list) and v and all(isinstance(x, (int, float)) for x in v):
                yield f"{path}.{k}", v
            else:
                yield from _raw_numbers(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _raw_numbers(v, f"{path}[{i}]")


def _count_issues(i, s):
    """A title that announces a count ('Three limits...') should match the list it introduces."""
    title = strip_markup(s.get("title") or s.get("claim") or "")
    m = re.match(r"^\s*(?:the\s+|our\s+)?(two|three|four|five|six|seven|eight|nine|ten)\s+([a-z]+)", title, re.I)
    if not m or m.group(2).lower().rstrip("s") in {"week", "month", "year", "day", "hour", "minute", "quarter",
                                                   "time", "point", "percent", "crore", "lakh"}:
        return []
    n = _NUMWORDS[m.group(1).lower()]
    lens = [len(s[k]) for k in _COUNTABLE if isinstance(s.get(k), list)]
    if not lens or n in lens:
        return []
    return [f"slide {i}: title counts {n} {m.group(2)} but the slide lists {lens[0]}: make them agree, or say "
            f"which {n} you mean"]


def validate(spec: dict) -> tuple[list[str], list[str]]:
    """Return (blockers, notes). Blockers stop a strict build; notes are always advisory."""
    blockers, notes = [], []
    facts_raw = spec.get("_facts_raw", {})
    has_facts = bool(facts_raw)
    meta = spec.get("fact_meta", {})
    evidence = spec.get("evidence", {})
    # evidence register and fact classification
    for eid, e in evidence.items():
        st = e.get("status", "missing")
        if st not in EVIDENCE_STATUS:
            blockers.append(f"evidence '{eid}': status must be one of {sorted(EVIDENCE_STATUS)}")
        elif st != "verified":
            blockers.append(f"evidence '{eid}' is {st}: verify it (source exists AND supports the claim) or drop "
                            "the claims that rest on it")
        if not e.get("source"):
            blockers.append(f"evidence '{eid}' has no source")
    unclassified = []
    for name, v in facts_raw.items():
        derived = isinstance(v, str) and v.startswith("=")
        m = meta.get(name, {})
        kind = m.get("kind", "calculated" if derived else None)
        if kind is None:
            unclassified.append(name)
            continue
        if kind not in FACT_KINDS:
            blockers.append(f"fact '{name}': unknown kind '{kind}'")
        if kind == "observed":
            eid = m.get("evidence")
            if not eid or eid not in evidence:
                blockers.append(f"fact '{name}' is observed but names no evidence entry")
    if unclassified:
        blockers.append(f"{len(unclassified)} raw fact(s) have no kind in fact_meta ({', '.join(unclassified[:6])}"
                        f"{'…' if len(unclassified) > 6 else ''}); kinds: "
                        f"{', '.join(sorted(FACT_KINDS - {'calculated'}))}")
    illustrative = [n for n, m in meta.items() if m.get("kind") == "illustrative"]
    if illustrative:
        notes.append(f"illustrative facts ({', '.join(illustrative[:5])}): every slide that shows them needs an "
                     "'Illustrative' tag or footer")
    for i, s in enumerate(spec.get("slides", []), 1):
        status = s.get("data_status")
        if status and status not in DATA_STATUS:
            blockers.append(f"slide {i}: data_status must be 'sourced' or 'illustrative'")
        if status == "sourced" and not s.get("source"):
            blockers.append(f"slide {i}: data_status 'sourced' needs a source line")
        if status == "illustrative" and "illustr" not in (s.get("tag", "") + spec.get("footer", "")).lower():
            blockers.append(f"slide {i}: data_status 'illustrative' needs an 'Illustrative' tag or footer")
        texts = list(slide_strings(s))
        for t in texts:
            if PLACEHOLDER.search(t):
                blockers.append(f"slide {i}: placeholder left on the slide: '{t[:50]}'")
                break
        notes += _count_issues(i, s)
        if s.get("type") == "custom":
            notes.append(f"slide {i}: custom layout; the final PPTX needs this slide built by hand (lint fails until then)")
        if has_facts and not status:
            for t in s.get("_raw_text", []):
                m = _HAND.search(re.sub(r"\{=[^}]*\}", "", t))
                if m:
                    blockers.append(f"slide {i}: hand-typed figure '{m.group(0)}': derive it from facts ({{=expr}}) "
                                    "or set data_status")
                    break
            for path, v in _raw_numbers(s.get("_raw", {})):
                if s.get("type") == "matrix" and path.startswith(".items"):
                    continue  # positions on a judgement grid, not data
                blockers.append(f"slide {i}: literal number(s) in {path.lstrip('.')} = {v}: use \"=fact\" or set "
                                "data_status")
                break
    return blockers, notes


def load_spec(path: str) -> dict:
    """Read a spec, resolve facts, run checks, render tokens. Keeps raw slides for validation."""
    with open(path, encoding="utf-8") as fh:
        spec = json.load(fh)
    facts = spec.get("facts", {})
    spec["_facts_raw"] = dict(facts)
    resolved = {}
    for k, v in facts.items():
        resolved[k] = render_tokens(v, resolved) if isinstance(v, str) else v
    spec["facts"] = resolved
    failures = []
    for chk in spec.get("checks", []):
        try:
            ok = safe_eval(chk, resolved)
        except SpecError:
            raise
        except Exception as e:  # noqa: BLE001
            raise SpecError(f"check '{chk}' could not run: {e}")
        if not ok:
            failures.append(chk)
    if failures:
        raise SpecError("fact checks failed (fix the numbers before building):\n  " + "\n  ".join(failures))
    raw_slides = spec["slides"]
    spec["slides"] = [render_tokens(s, resolved) for s in raw_slides]
    for s, raw in zip(spec["slides"], raw_slides):
        s["_raw"] = raw
        s["_raw_text"] = list(slide_strings(raw))
    blockers, notes = validate(spec)
    spec["_blockers"], spec["_notes"] = blockers, notes
    # backwards-compatible name used by the builders' `check` lines
    spec["_handtyped"] = [b for b in blockers if "hand-typed" in b or "literal number" in b]
    return spec


def report(spec: dict, strict: bool, out=print) -> int:
    """Print validation lines; return 2 when strict and anything blocks the final build."""
    tag = "error" if strict else "check"
    for b in spec.get("_blockers", []):
        out(f"  {tag} {b}")
    for n in spec.get("_notes", []):
        out(f"  note  {n}")
    if strict and spec.get("_blockers"):
        out(f"  STRICT: {len(spec['_blockers'])} release blocker(s); fix them before the final build")
        return 2
    if not strict and spec.get("_blockers"):
        out(f"  draft: {len(spec['_blockers'])} item(s) would block the final build (--strict)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    try:
        spec = load_spec(a.spec)
    except SpecError as e:
        print(f"SPEC ERROR: {e}", file=sys.stderr)
        return 2
    rc = report(spec, a.strict)
    if rc == 0 and not spec.get("_blockers"):
        print("  ok    no release blockers")
    return rc


if __name__ == "__main__":
    sys.exit(main())

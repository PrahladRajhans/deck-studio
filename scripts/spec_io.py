#!/usr/bin/env python3
"""Load and validate a deck-studio spec. Shared by the HTML draft builder and the PPTX builder.

No PowerPoint dependency: drafting needs only this module, _common.py and build_html.py.

    python3 spec_io.py spec.json            # validation report (draft rules)
    python3 spec_io.py spec.json --strict   # release gate: exit 2 if anything blocks a final build

Draft mode reports problems as `check` lines and carries on, so iteration stays cheap.
Strict mode validates provenance records, labels, placeholders and reviewed claim inventories.
It does not retrieve sources or prove natural-language claims. Source support and inventory
completeness require a semantic review before release. Drafts report blockers without stopping.
"""
from __future__ import annotations

import argparse
import ast
from html.parser import HTMLParser
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
# Include counts and years, not only currencies/percentages. Administrative exceptions
# must name the exact text and a reason; classification is never inferred from typography.
_HAND = re.compile(r"(?<![\w])[-+]?\d[\d,]*(?:\.\d+)?(?:%|x\b|×)?")
CLAIM_KINDS = {"observed", "quotation", "calculated", "estimate", "forecast", "assumption",
               "target", "hypothesis", "recommendation", "illustrative"}
_VALIDATION_SKIP = {"_raw", "_raw_text", "claims", "non_factual_reason", "number_exceptions",
                    "evidence_ids", "voice_ok", "path", "image", "photo", "id", "type", "kind",
                    "style", "direction", "frame", "icon", "number_format", "pptx_note"}


class _VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "template"}:
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "template"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, text):
        if not self.hidden:
            self.parts.append(text)


def validation_strings(obj, *, numbers=False):
    """Evidence/placeholder traversal is independent of editorial exemptions.

    Quotes, references, source lines and speaker notes must not hide placeholders.
    Code and citation metadata are exempt only from numerical provenance scanning.
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in _VALIDATION_SKIP or key.startswith("_"):
                continue
            if numbers and key in {"code", "source", "sources", "credit", "alt"}:
                continue
            if key == "html" and isinstance(value, str):
                parser = _VisibleHTML()
                parser.feed(value)
                yield " ".join(parser.parts)
            else:
                yield from validation_strings(value, numbers=numbers)
    elif isinstance(obj, list):
        for value in obj:
            yield from validation_strings(value, numbers=numbers)
    elif isinstance(obj, str) and not obj.startswith("="):
        yield obj


def _expression_names(obj):
    """Fact names used by expressions, including nested chart arrays and text tokens."""
    names = set()
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key not in _VALIDATION_SKIP:
                names.update(_expression_names(value))
    elif isinstance(obj, list):
        for value in obj:
            names.update(_expression_names(value))
    elif isinstance(obj, str):
        exprs = [obj[1:]] if obj.startswith("=") else re.findall(r"\{=([^}|]+)(?:\|[^}]*)?\}", obj)
        for expr in exprs:
            try:
                names.update(n.id for n in ast.walk(ast.parse(expr.strip(), mode="eval")) if isinstance(n, ast.Name))
            except SyntaxError:
                pass  # load_spec reports invalid expressions before validation
    return names


def _labelled_illustrative(spec, slide):
    return bool(re.search(r"\billustrative\b", slide.get("tag", "") + " " + spec.get("footer", ""), re.I))


def _claim_issues(index, slide, evidence, illustrative):
    """Validate a semantically reviewed claim inventory, not the truth of natural language."""
    errors = []
    claims = slide.get("claims", [])
    if not isinstance(claims, list):
        return [f"slide {index}: claims must be a list"]
    if not claims and not illustrative and not str(slide.get("non_factual_reason", "")).strip():
        errors.append(f"slide {index}: missing claims inventory; record factual claims or a non_factual_reason")
    visible = " ".join(validation_strings(slide))
    normal = lambda text: " ".join(strip_markup(str(text)).split())
    for claim in claims:
        if not isinstance(claim, dict):
            errors.append(f"slide {index}: each claim must be an object")
            continue
        text, kind = claim.get("text", ""), claim.get("kind")
        if not text or normal(text) not in normal(visible):
            errors.append(f"slide {index}: claim text must match text on the slide or in its notes")
        if kind not in CLAIM_KINDS:
            errors.append(f"slide {index}: unknown claim kind '{kind}'")
        if claim.get("status") != "reviewed":
            errors.append(f"slide {index}: claim '{str(text)[:45]}' needs semantic review (status 'reviewed')")
        refs = claim.get("evidence_ids", [])
        if not isinstance(refs, list) or any(not isinstance(x, str) for x in refs):
            errors.append(f"slide {index}: claim evidence_ids must be a list of evidence IDs")
            refs = []
        if kind in {"observed", "quotation"} and not refs:
            errors.append(f"slide {index}: {kind} claim needs linked evidence")
        for eid in refs:
            if eid not in evidence:
                errors.append(f"slide {index}: claim links unknown evidence '{eid}'")
        if kind not in {"observed", "quotation", "illustrative"} and not str(claim.get("basis", "")).strip():
            errors.append(f"slide {index}: {kind} claim needs its analysis, assumptions or calculation in basis")
        if kind == "illustrative" and not illustrative:
            errors.append(f"slide {index}: illustrative claim needs data_status 'illustrative' and a visible label")
    return errors


_NUMWORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
# list fields whose length a title count can refer to
_COUNTABLE = ("items", "points", "steps", "columns", "spokes", "stages", "levels", "tiers", "people",
              "branches", "lanes", "milestones", "rows", "options")


def _raw_numbers(obj, path=""):
    """Find numeric primitives, including table cells and mixed nested arrays.

    Skip only known layout/index settings and provenance records. Semantic exceptions
    such as matrix judgement positions are handled explicitly by validate().
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.startswith("_") or key in {
                "claims", "number_exceptions", "evidence_ids", "theme", "id", "highlight",
                "recommended", "start", "end", "number", "feeling", "image_width",
                "highlight_row", "active", "widths", "totals", "min", "max",
            }:
                continue
            yield from _raw_numbers(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from _raw_numbers(value, f"{path}[{index}]")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        yield path, obj


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
        if not str(e.get("locator", "")).strip():
            blockers.append(f"evidence '{eid}' has no locator (page, table, cell, section or precise URL)")
        if PLACEHOLDER.search(str(e)):
            blockers.append(f"evidence '{eid}' contains a placeholder")
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
        if kind == "calculated" and not derived:
            blockers.append(f"fact '{name}': calculated facts must be '=expression', not raw values")
        if kind == "observed":
            eid = m.get("evidence")
            if not eid or eid not in evidence:
                blockers.append(f"fact '{name}' is observed but names no evidence entry")
    if unclassified:
        blockers.append(f"{len(unclassified)} raw fact(s) have no kind in fact_meta ({', '.join(unclassified[:6])}"
                        f"{'…' if len(unclassified) > 6 else ''}); kinds: "
                        f"{', '.join(sorted(FACT_KINDS - {'calculated'}))}")
    illustrative_facts = {n for n, m in meta.items() if m.get("kind") == "illustrative"}
    # Derived values retain illustrative provenance, even through multiple calculations.
    for _ in facts_raw:
        expanded = illustrative_facts | {n for n, v in facts_raw.items()
                                         if _expression_names(v) & illustrative_facts}
        if expanded == illustrative_facts:
            break
        illustrative_facts = expanded
    for field in ("footer", "sources", "title"):
        if PLACEHOLDER.search(str(spec.get(field, ""))):
            blockers.append(f"deck {field} contains a placeholder")
    for i, s in enumerate(spec.get("slides", []), 1):
        status = s.get("data_status")
        if status and status not in DATA_STATUS:
            blockers.append(f"slide {i}: data_status must be 'sourced' or 'illustrative'")
        refs = s.get("evidence_ids", [])
        if not isinstance(refs, list) or any(not isinstance(x, str) for x in refs):
            blockers.append(f"slide {i}: evidence_ids must be a list of evidence IDs")
            refs = []
        for eid in refs:
            if eid not in evidence:
                blockers.append(f"slide {i}: unknown evidence '{eid}'")
        if status == "sourced":
            if not s.get("source"):
                blockers.append(f"slide {i}: data_status 'sourced' needs a source line")
            if not refs:
                blockers.append(f"slide {i}: data_status 'sourced' needs linked evidence_ids, not just a source string")
        illustrative = status == "illustrative"
        s["_illustrative"] = bool(illustrative or _expression_names(s.get("_raw", s)) & illustrative_facts)
        if s["_illustrative"]:
            if not _labelled_illustrative(spec, s):
                blockers.append(f"slide {i}: illustrative content needs an 'Illustrative' tag or footer")
            if spec.get("illustrative_authorized") is not True:
                blockers.append(f"slide {i}: illustrative content needs recorded user agreement (illustrative_authorized: true)")
        for t in validation_strings(s):
            if PLACEHOLDER.search(t):
                blockers.append(f"slide {i}: placeholder left in deliverable text: '{t[:50]}'")
                break
        blockers += _claim_issues(i, s, evidence, illustrative)
        notes += _count_issues(i, s)
        if s.get("type") == "custom":
            notes.append(f"slide {i}: custom layout; preserve its PPTX reconstruction script alongside the spec")
        if not status:
            exceptions = s.get("number_exceptions", [])
            if not isinstance(exceptions, list):
                blockers.append(f"slide {i}: number_exceptions must be a list")
                exceptions = []
            for exception in exceptions:
                if (not isinstance(exception, dict) or not exception.get("text")
                        or not str(exception.get("reason", "")).strip()):
                    blockers.append(f"slide {i}: number exception requires exact text and an administrative reason")
            for t in validation_strings(s.get("_raw", s), numbers=True):
                clean = re.sub(r"\{=[^}]*\}", "", t)
                for exception in exceptions:
                    if isinstance(exception, dict) and exception.get("text") and exception.get("reason"):
                        clean = re.sub(r"(?<!\w)" + re.escape(str(exception["text"])) + r"(?!\w)", "", clean)
                match = _HAND.search(clean)
                if match:
                    blockers.append(f"slide {i}: hand-typed figure '{match.group(0)}': derive it from facts ({{=expr}}) "
                                    "or classify and evidence it with data_status")
                    break
            for path, v in _raw_numbers(s.get("_raw", s)):
                if s.get("type") == "matrix" and path.startswith(".items"):
                    continue
                blockers.append(f"slide {i}: literal number(s) in {path.lstrip('.')} = {v}: use \"=fact\" or set "
                                "data_status with its required evidence or illustrative label")
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

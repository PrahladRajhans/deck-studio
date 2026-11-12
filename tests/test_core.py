"""Unit tests for the parts that must never silently go wrong: arithmetic, validation, style checks."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")
sys.path.insert(0, SCRIPTS)

from _common import SpecError, ai_tells, safe_eval, resolve_theme  # noqa: E402
from spec_io import load_spec  # noqa: E402


def spec_file(spec):
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as fh:
        json.dump(spec, fh)
    return path


class Arithmetic(unittest.TestCase):
    def test_unequal_vectors_fail(self):
        for e in ("vadd([10,20,30],[1,2])", "vsub([1],[1,2])", "wavg([10],[1,9])"):
            with self.assertRaises(SpecError):
                safe_eval(e, {})

    def test_wavg_needs_valid_weights(self):
        with self.assertRaises(SpecError):
            safe_eval("wavg([1,2],[0,0])", {})
        self.assertEqual(safe_eval("wavg([1,3],[1,1])", {}), 2.0)

    def test_not_reached_cannot_become_a_year(self):
        self.assertIsNone(safe_eval("first_at_least([1,2],5)", {}))
        self.assertFalse(safe_eval("reached(first_at_least([1,2],5))", {}))
        with self.assertRaises(SpecError):
            safe_eval("[2024,2025][first_at_least([1,2],5)]", {})
        self.assertEqual(safe_eval("[2024,2025][first_at_least([1,2],2)]", {}), 2025)


class Validation(unittest.TestCase):
    def test_literal_chart_value_blocks_strict(self):
        p = spec_file({"facts": {"revenue": 10}, "fact_meta": {"revenue": {"kind": "illustrative"}},
                       "slides": [{"type": "chart", "title": "Revenue grew", "chart": {
                           "kind": "column", "categories": ["A"], "series": [{"name": "r", "values": [999]}]}}]})
        spec = load_spec(p)
        self.assertTrue(any("literal number" in b for b in spec["_blockers"]))

    def test_hand_typed_figure_in_nested_text_blocks_strict(self):
        p = spec_file({"facts": {"x": 1}, "fact_meta": {"x": {"kind": "target"}},
                       "slides": [{"type": "cards", "title": "Plan", "items": [{"heading": "A", "body": "Up 40%"}]}]})
        self.assertTrue(any("hand-typed" in b for b in load_spec(p)["_blockers"]))

    def test_unverified_evidence_and_unclassified_facts_block(self):
        p = spec_file({"facts": {"share": 34, "size": 10},
                       "fact_meta": {"share": {"kind": "observed", "evidence": "e1"}},
                       "evidence": {"e1": {"source": "Panel data 2026", "status": "unverified"}},
                       "slides": [{"type": "statement", "claim": "Share is {=share}%"}]})
        b = load_spec(p)["_blockers"]
        self.assertTrue(any("unverified" in x for x in b))
        self.assertTrue(any("no kind" in x for x in b))

    def test_data_status_classifies_literals(self):
        p = spec_file({"facts": {"x": 1}, "fact_meta": {"x": {"kind": "illustrative"}}, "footer": "Illustrative", "illustrative_authorized": True,
                       "slides": [{"type": "chart", "title": "T", "data_status": "illustrative", "chart": {
                           "kind": "column", "categories": ["A"], "series": [{"name": "r", "values": [9]}]}}]})
        self.assertEqual(load_spec(p)["_blockers"], [])

    def test_count_mismatch_is_reported(self):
        p = spec_file({"slides": [{"type": "risks", "title": "Three limits matter",
                                   "rows": [{"risk": "a", "mitigation": "m"}, {"risk": "b", "mitigation": "m"}]}]})
        self.assertTrue(any("counts 3" in n for n in load_spec(p)["_notes"]))

    def test_examples_pass_strict(self):
        ex = os.path.join(HERE, "..", "assets", "examples")
        for f in sorted(os.listdir(ex)):
            if f.endswith(".json") and not f.startswith("chart-"):
                with self.subTest(f=f):
                    self.assertEqual(load_spec(os.path.join(ex, f))["_blockers"], [])


class Style(unittest.TestCase):
    def test_technical_terms_survive(self):
        for t in ("Use robust standard errors.", "Financial leverage increased to 2.4x.",
                  "The landscape photograph shows the pipeline route."):
            self.assertEqual(ai_tells(t), [], t)

    def test_stock_phrasing_is_prompted_and_can_be_kept(self):
        self.assertTrue(ai_tells("Our robust platform empowers teams"))
        self.assertEqual(ai_tells("No pressure. No flow.", keep=["no pressure"]), [])


class Builders(unittest.TestCase):
    def test_html_draft_needs_no_pptx(self):
        code = ("import sys; sys.modules['pptx'] = None; sys.path.insert(0, %r); import build_html" % SCRIPTS)
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_negative_stacks_have_no_negative_sizes(self):
        import re
        from build_html import chart_svg
        t = resolve_theme("consulting-navy", None)
        for kind in ("stacked", "stacked_bar"):
            svg = chart_svg({"kind": kind, "categories": ["A", "B"],
                             "series": [{"name": "x", "values": [5, -3]}, {"name": "y", "values": [2, -4]}]}, t)
            self.assertEqual(re.findall(r'(?:width|height)="-', svg), [], kind)


class Sandbox(unittest.TestCase):
    def test_draft_runs_in_a_sandboxed_preview(self):
        """claude.ai previews HTML in a sandboxed about:srcdoc frame, where touching the URL throws."""
        import html as _html
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.skipTest("playwright not installed")
        out = os.path.join(tempfile.mkdtemp(), "d.html")
        spec = os.path.join(HERE, "..", "assets", "examples", "personal-story.json")
        subprocess.run([sys.executable, os.path.join(SCRIPTS, "build_html.py"), spec, "-o", out],
                       check=True, capture_output=True)
        doc = open(out, encoding="utf-8").read()
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.set_content('<iframe sandbox="allow-scripts" srcdoc="%s"></iframe>' % _html.escape(doc, quote=True))
            pg.wait_for_timeout(1200)
            frame = pg.frames[1]
            frame.evaluate("window.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight'}))")
            pg.wait_for_timeout(200)
            idx = frame.evaluate("[...document.querySelectorAll('.slide')].findIndex(s=>s.classList.contains('active'))")
            b.close()
        self.assertEqual(errors, [])
        self.assertEqual(idx, 1)


if __name__ == "__main__":
    unittest.main()

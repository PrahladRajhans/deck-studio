"""Custom composition must preserve evidence, notes and provenance at export boundaries."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_html import HtmlDeck
from spec_io import load_spec


class CreativeComposition(unittest.TestCase):
    def load(self, spec):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'spec.json'
            path.write_text(json.dumps(spec))
            return load_spec(str(path))

    def illustration(self, full_bleed):
        return {'footer': 'Illustrative', 'illustrative_authorized': True, 'slides': [{
            'type': 'custom', 'title': 'A planning title', 'full_bleed': full_bleed,
            'html': '<div style="font-size:60px">The handoff is the question.</div>',
            'source': 'Illustrative workflow example.', 'data_status': 'illustrative',
            'notes': {'say': 'Locate the queue before claiming its cause.'}}]}

    def test_full_stage_preserves_source_notes_and_visible_provenance(self):
        spec = self.load(self.illustration(True))
        self.assertEqual(spec['_blockers'], [])
        html = HtmlDeck(spec, '.').build()
        self.assertIn('class="custom-stage"', html)
        self.assertIn('class="custom-source"', html)
        self.assertIn('Illustrative workflow example.', html)
        self.assertIn('Locate the queue before claiming its cause.', html)
        self.assertIn('class="provenance-label"', html)
        self.assertIn('The handoff is the question.', html)
        self.assertNotIn('<h1 class="title"', html)

    def test_standard_custom_chrome_is_retained_by_default(self):
        html = HtmlDeck(self.load(self.illustration(False)), '.').build()
        self.assertNotIn('class="custom-stage"', html)
        self.assertIn('A planning title', html)
        self.assertIn('The handoff is the question.', html)

    def test_unrendered_planning_title_cannot_satisfy_claim_inventory(self):
        spec = self.illustration(True)
        spec['slides'][0]['claims'] = [{'text': 'A planning title', 'kind': 'recommendation',
                                      'status': 'reviewed', 'basis': 'A design rationale'}]
        self.assertTrue(any('must match text' in b for b in self.load(spec)['_blockers']))

    def test_creative_example_keeps_counted_units_consistent(self):
        path = ROOT / 'assets' / 'creative-examples' / 'queue-review.json'
        spec = load_spec(str(path))
        self.assertEqual(spec['_blockers'], [])
        self.assertEqual(spec['facts']['packed'] + spec['facts']['waiting'], spec['facts']['total'])
        deck = HtmlDeck(spec, str(path.parent))
        html = deck.build()
        self.assertEqual(deck.pages_seen, {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4})
        self.assertEqual(html.count('class="provenance-label"'), len(spec['slides']))
        self.assertEqual(html.count('data-order-unit="true"'), spec['facts']['total'])
        self.assertIn('6 / 10', html)
        self.assertIn('4 / 10', html)
        self.assertIn('This locates the queue. It does not explain why.', html)


if __name__ == '__main__':
    unittest.main()

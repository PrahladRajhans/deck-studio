"""Adversarial and positive release-gate tests. No network or rendering required."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from spec_io import load_spec, report


class ReleaseGate(unittest.TestCase):
    def load(self, spec):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'spec.json'
            path.write_text(json.dumps(spec))
            return load_spec(str(path))

    def blocked(self, spec, message):
        result = self.load(spec)
        self.assertEqual(report(result, True, out=lambda _: None), 2)
        self.assertTrue(any(message in b for b in result['_blockers']), result['_blockers'])

    def observed(self):
        return {
            'facts': {'patients': 12},
            'fact_meta': {'patients': {'kind': 'observed', 'evidence': 'trial'}},
            'evidence': {'trial': {'source': 'User-supplied trial report', 'locator': 'Table 1, row enrolled',
                                   'status': 'verified'}},
            'slides': [{'type': 'statement', 'claim': 'We enrolled {=patients} participants',
                        'claims': [{'text': 'We enrolled {=patients} participants', 'kind': 'observed',
                                    'status': 'reviewed', 'evidence_ids': ['trial']}]}]}

    def test_no_facts_does_not_disable_numeric_gate(self):
        self.blocked({'slides': [{'type': 'statement', 'claim': 'Revenue rose 99% in 2026'}]}, 'hand-typed')

    def test_plain_counts_are_checked(self):
        spec = self.observed()
        spec['slides'][0]['claim'] = 'We enrolled 999 participants'
        self.blocked(spec, 'hand-typed')

    def test_source_string_is_not_evidence(self):
        self.blocked({'slides': [{'type': 'statement', 'claim': 'Revenue rose 99%',
                                  'data_status': 'sourced', 'source': 'Invented Report 2026'}]}, 'linked evidence_ids')

    def test_qualitative_claim_needs_review_inventory(self):
        self.blocked({'slides': [{'type': 'statement', 'claim': 'Our treatment cures every patient'}]},
                     'missing claims inventory')

    def test_placeholder_traversal_is_not_style_traversal(self):
        for key in ('quote', 'code', 'source', 'credit', 'notes'):
            with self.subTest(key=key):
                self.blocked({'slides': [{'type': 'quote', key: '[CONFIRM: exact wording]'}]}, 'placeholder')
        self.blocked({'slides': [{'type': 'references', 'items': ['[TBD]']}]}, 'placeholder')
        for field in ('footer', 'sources', 'title'):
            self.blocked({field: '[TBD]', 'slides': []}, 'placeholder')

    def test_observed_fact_and_matching_claim_pass(self):
        self.assertEqual(self.load(self.observed())['_blockers'], [])

    def test_source_locator_is_required(self):
        spec = self.observed()
        del spec['evidence']['trial']['locator']
        self.blocked(spec, 'locator')

    def test_unverified_evidence_cannot_release(self):
        spec = self.observed()
        spec['evidence']['trial']['status'] = 'unverified'
        self.blocked(spec, 'unverified')

    def test_unknown_slide_and_claim_evidence_fail(self):
        spec = self.observed()
        spec['slides'][0]['evidence_ids'] = ['unknown']
        spec['slides'][0]['claims'][0]['evidence_ids'] = ['unknown']
        self.blocked(spec, 'unknown evidence')

    def test_raw_value_is_not_a_calculation(self):
        spec = self.observed()
        spec['fact_meta']['patients']['kind'] = 'calculated'
        self.blocked(spec, "must be '=expression'")

    def test_illustrative_provenance_propagates_through_calculations(self):
        spec = {'facts': {'a': 5, 'b': '=a*2', 'c': '=b*2'},
                'fact_meta': {'a': {'kind': 'illustrative'}},
                'slides': [{'type': 'statement', 'claim': 'Total {=c}',
                            'non_factual_reason': 'Layout exercise'}]}
        self.blocked(spec, "'Illustrative' tag or footer")
        spec['footer'] = 'Illustrative'
        self.blocked(spec, 'recorded user agreement')

    def test_authorized_labelled_illustration_passes(self):
        spec = {'footer': 'Illustrative', 'illustrative_authorized': True,
                'slides': [{'type': 'statement', 'claim': 'Revenue rose 99%', 'data_status': 'illustrative'}]}
        self.assertEqual(self.load(spec)['_blockers'], [])

    def test_review_inventory_is_bound_to_presented_text(self):
        spec = self.observed()
        spec['slides'][0]['claims'][0]['text'] = 'A different claim'
        self.blocked(spec, 'must match text')

    def test_claim_review_and_recommendation_basis_required(self):
        spec = self.observed()
        claim = spec['slides'][0]['claims'][0]
        claim['status'] = 'unreviewed'
        self.blocked(spec, 'needs semantic review')
        claim.update(status='reviewed', kind='recommendation')
        self.blocked(spec, 'needs its analysis')

    def test_quotation_requires_evidence(self):
        self.blocked({'slides': [{'type': 'quote', 'quote': 'Listen first', 'claims': [
            {'text': 'Listen first', 'kind': 'quotation', 'status': 'reviewed'}]}]}, 'needs linked evidence')

    def test_mixed_chart_array_cannot_hide_a_literal(self):
        spec = self.observed()
        spec['slides'][0]['chart'] = {'series': [{'values': ['=patients', 999]}]}
        self.blocked(spec, 'literal number')

    def test_administrative_exception_requires_reason(self):
        spec = {'slides': [{'type': 'divider', 'title': 'Part 2', 'non_factual_reason': 'Section navigation',
                            'number_exceptions': [{'text': '2', 'reason': 'Section number'}]}]}
        self.assertEqual(self.load(spec)['_blockers'], [])
        spec['slides'][0]['number_exceptions'][0].pop('reason')
        self.blocked(spec, 'administrative reason')

    def test_numeric_table_cells_are_checked(self):
        self.blocked({'slides': [{'type': 'table', 'title': 'Participants',
                                  'headers': ['Group', 'Count'], 'rows': [['A', 999]],
                                  'non_factual_reason': 'Does not exempt numerical data'}]}, 'literal number')

    def test_administrative_exception_does_not_remove_substrings(self):
        self.blocked({'slides': [{'type': 'statement', 'claim': 'We enrolled 222 patients',
                                  'number_exceptions': [{'text': '2', 'reason': 'Section number'}]}]}, 'hand-typed')

    def test_custom_html_checks_text_not_css_dimensions(self):
        spec = {'slides': [{'type': 'custom', 'title': 'Introduction', 'non_factual_reason': 'Navigation',
                            'html': '<div style="width:400px">Welcome</div>'}]}
        self.assertEqual(self.load(spec)['_blockers'], [])
        spec['slides'][0]['html'] = '<div>Revenue rose 99%</div>'
        self.blocked(spec, 'hand-typed')

    def test_illustrative_cover_has_visible_html_badge(self):
        from build_html import HtmlDeck
        spec = self.load({'footer': 'Illustrative', 'illustrative_authorized': True,
                          'slides': [{'type': 'cover', 'title': 'Revenue rose 99%',
                                      'data_status': 'illustrative'}]})
        output = HtmlDeck(spec, '.').build()
        self.assertIn('class="provenance-label"', output)
        self.assertIn('>Illustrative</span></section>', output)

    def test_illustrative_cover_has_native_pptx_badge(self):
        try:
            from build_deck import Builder
        except ModuleNotFoundError:
            self.skipTest('python-pptx/Pillow not installed')
        spec = self.load({'footer': 'Illustrative', 'illustrative_authorized': True,
                          'slides': [{'type': 'cover', 'title': 'Revenue rose 99%',
                                      'data_status': 'illustrative'}]})
        deck = Builder(spec, '.').build()
        labels = [shape.text for shape in deck.slides[0].shapes
                  if shape.name == 'provenance-label']
        self.assertEqual(labels, ['Illustrative'])

    def test_strict_html_refuses_before_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            spec, out = Path(folder) / 'spec.json', Path(folder) / 'final.html'
            spec.write_text(json.dumps({'slides': [{'type': 'statement', 'claim': '[CONFIRM: finding]'}]}))
            script = Path(__file__).resolve().parents[1] / 'scripts' / 'build_html.py'
            result = subprocess.run([sys.executable, str(script), str(spec), '--strict', '-o', str(out)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(out.exists())
            # Draft iteration remains possible while evidence gaps are unresolved.
            draft = subprocess.run([sys.executable, str(script), str(spec), '-o', str(out)],
                                   capture_output=True, text=True)
            self.assertEqual(draft.returncode, 0, draft.stderr)
            self.assertTrue(out.exists())


if __name__ == '__main__':
    unittest.main()

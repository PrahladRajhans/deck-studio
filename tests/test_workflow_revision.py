"""Reachable provenance, assurance profiles and dependency-free authoring commands."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from spec_io import load_spec
from _common import slide_seconds


class WorkflowRevision(unittest.TestCase):
    def load(self, spec):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'spec.json'
            p.write_text(json.dumps(spec))
            return load_spec(str(p))

    def observed(self):
        return {'facts': {'a': 4, 'b': '=a*2'},
                'fact_meta': {'a': {'kind': 'observed', 'evidence': 'brief'}},
                'evidence': {'brief': {'source': 'Supplied brief', 'locator': 'Paragraph 1', 'status': 'verified'}},
                'slides': [{'type': 'statement', 'claim': 'Count {=b}',
                            'claims': [{'text': 'Count {=b}', 'kind': 'observed', 'status': 'reviewed'}]}]}

    def test_fact_tokens_inherit_evidence_through_calculations(self):
        self.assertEqual(self.load(self.observed())['_blockers'], [])

    def test_inherited_evidence_must_still_be_verified(self):
        spec = self.observed()
        spec['evidence']['brief']['status'] = 'unverified'
        self.assertTrue(any('unverified' in b for b in self.load(spec)['_blockers']))

    def test_inherited_provenance_does_not_waive_semantic_review(self):
        spec = self.observed()
        spec['slides'][0]['claims'][0]['status'] = 'unreviewed'
        self.assertTrue(any('semantic review' in b for b in self.load(spec)['_blockers']))

    def test_unused_research_gap_is_retained_as_advisory(self):
        spec = self.observed()
        spec['facts']['unknown_market_size'] = '[TBD]'
        spec['evidence']['unused'] = {'source': 'Source: missing', 'status': 'missing'}
        result = self.load(spec)
        self.assertEqual(result['_blockers'], [])
        self.assertTrue(any('unused research history' in n for n in result['_notes']))
        self.assertIn('unused', result['evidence'])

    def test_used_gap_cannot_be_relabelled_unused(self):
        spec = self.observed()
        spec['evidence']['brief']['status'] = 'missing'
        self.assertTrue(any("'brief' is missing" in b for b in self.load(spec)['_blockers']))

    def test_brief_assurance_requires_supplied_evidence_or_nonfactual_reason(self):
        spec = self.observed()
        spec['assurance'] = 'brief'
        spec['slides'][0].pop('claims')
        spec['slides'][0]['evidence_ids'] = ['brief']
        self.assertEqual(self.load(spec)['_blockers'], [])
        spec['slides'][0].pop('evidence_ids')
        self.assertTrue(any('missing claims' in b for b in self.load(spec)['_blockers']))

    def test_standard_and_high_do_not_accept_slide_citation_as_claim_review(self):
        for level in ('standard', 'high'):
            spec = self.observed()
            spec['assurance'] = level
            spec['slides'][0].pop('claims')
            spec['slides'][0]['evidence_ids'] = ['brief']
            self.assertTrue(any('missing claims' in b for b in self.load(spec)['_blockers']))

    def test_brief_assurance_does_not_waive_placeholder_rules(self):
        spec = self.observed()
        spec['assurance'] = 'brief'
        spec['slides'][0]['source'] = 'Source: to be added'
        self.assertTrue(any('placeholder' in b for b in self.load(spec)['_blockers']))

    def test_schema_and_outline_need_no_pptx(self):
        for args in (['--schema'], [str(ROOT / 'assets/examples/personal-story.json'), '--outline']):
            code = ('import sys;sys.modules["pptx"]=None;sys.path.insert(0,%r);'
                    'import spec_io;sys.exit(spec_io.main(%r))' % (str(ROOT / 'scripts'), args))
            r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(r.stdout.strip())

    def test_explicit_timings_override_complexity_estimates(self):
        slides = [{'type': 'cover'}, {'type': 'chart'}, {'type': 'statement'}, {'type': 'table', 'seconds': 70}]
        spec = {'minutes': 5, 'slides': slides}
        self.assertEqual(slide_seconds(spec, slides[0]), 8)
        self.assertEqual(slide_seconds(spec, slides[3]), 70)
        self.assertGreater(slide_seconds(spec, slides[1]), slide_seconds(spec, slides[2]))

    def test_invalid_timing_is_blocked(self):
        spec = self.observed()
        for value in (-1, float('inf'), float('nan')):
            spec['slides'][0]['seconds'] = value
            self.assertTrue(any('seconds' in b for b in self.load(spec)['_blockers']))


if __name__ == '__main__':
    unittest.main()

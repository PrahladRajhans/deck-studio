"""Retained context, worked examples and explicit native reconstruction."""
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from spec_io import load_spec
from visual_elements import process_body, table_base
from _common import SpecError
from build_html import HtmlDeck


class Completeness(unittest.TestCase):
    def test_new_samples_are_strict_ready_and_reconcile(self):
        for name in ('decision-tradeoffs','unit-economics','cash-flow-teaching'):
            spec=load_spec(str(ROOT/f'assets/examples/{name}.json'))
            self.assertFalse(spec['_blockers'],spec['_blockers'])
        economics=load_spec(str(ROOT/'assets/examples/unit-economics.json'))
        teaching=load_spec(str(ROOT/'assets/examples/cash-flow-teaching.json'))
        self.assertEqual(economics['facts']['cm3'],20)
        self.assertEqual(teaching['facts']['operating'],20)
        self.assertEqual(teaching['facts']['closing'],15)
        self.assertNotIn('ltv',economics['facts'])

    def test_rag_sample_includes_unknown_and_real_tradeoffs(self):
        spec=load_spec(str(ROOT/'assets/examples/decision-tradeoffs.json'))
        rows=spec['slides'][1]['rows']
        # Preferred pilot has a weakness; alternatives each retain an actual advantage.
        for row in rows:
            self.assertTrue(any(isinstance(cell,dict) and cell.get('status')=='green' for cell in row))
        self.assertTrue(any(cell.get('status')=='amber' for cell in rows[1] if isinstance(cell,dict)))
        self.assertIn('unknown',json.dumps(spec['slides'][2]))

    def test_process_defect_and_dropoff_metrics_are_explicit(self):
        body=process_body({'defect_rate':'2% of inspected','drop_off':'20% of received'})
        self.assertIn('Defect rate: 2% of inspected',body)
        self.assertIn('Drop-off: 20% of received',body)
        self.assertNotIn('Volume',body)

    def test_sensitivity_crosshair_preserves_explicit_base_label(self):
        spec=load_spec(str(ROOT/'assets/examples/visual-components.json'))
        deck=HtmlDeck(spec,str(ROOT/'assets/examples'))
        doc=deck.s_table(spec['slides'][2])
        self.assertIn('(base)',doc)
        self.assertIn('outline:2px solid',doc)
        self.assertGreaterEqual(doc.count('background:#'),5)

    def test_bad_base_markers_are_controlled_spec_errors(self):
        for marker in ([],[1],[True,0],[-1,0],[0,2],'0,0'):
            with self.assertRaises(SpecError):
                table_base(marker, [['a','b']], ['x','y'])
        with tempfile.TemporaryDirectory() as folder:
            original=json.loads((ROOT/'assets/examples/visual-components.json').read_text())
            original['slides'][2]['base_cell']=[1]
            path=Path(folder)/'invalid.json'
            path.write_text(json.dumps(original))
            result=load_spec(str(path))
            self.assertTrue(any('base_cell' in b for b in result['_blockers']))

    def test_native_brand_recipe_preserves_copy_and_notes(self):
        try:
            import pptx
        except ImportError:
            self.skipTest('python-pptx not installed')
        recipe=ROOT/'assets/forward-tests/rebuild_brand.py'
        module=runpy.run_path(str(recipe))
        spec=load_spec(str(ROOT/'assets/forward-tests/brand.json'))
        with tempfile.TemporaryDirectory() as folder:
            dest=Path(folder)/'brand-native.pptx'
            result=subprocess.run([sys.executable,str(recipe),'-o',str(dest)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            deck=pptx.Presentation(dest)
            self.assertEqual(len(deck.slides),4)
            for source,slide in zip(spec['slides'],deck.slides):
                text=' '.join(' '.join(sp.text.split()) for sp in slide.shapes if sp.has_text_frame)
                for part in module['Copy'](source['html']).parts:
                    self.assertIn(' '.join(part.split()),text)
                self.assertIn(source['source'],text)
                self.assertIn(source['notes']['say'],slide.notes_slide.notes_text_frame.text)
                self.assertFalse(any(sp.shape_type==13 for sp in slide.shapes))
            for edit in ('append','same_count_structure','layout_style'):
                changed=json.loads((ROOT/'assets/forward-tests/brand.json').read_text())
                if edit=='append':
                    changed['slides'][0]['html']+='<p>Extra copy requiring a revised composition.</p>'
                elif edit=='same_count_structure':
                    changed['slides'][0]['html']=changed['slides'][0]['html'].replace('<br>','</h1><h1>')
                else:
                    changed['slides'][0]['html']=changed['slides'][0]['html'].replace('right:125px','right:150px')
                bad=Path(folder)/(edit+'.json')
                bad.write_text(json.dumps(changed))
                rejected=Path(folder)/(edit+'.pptx')
                result=subprocess.run([sys.executable,str(recipe),'--spec',str(bad),'-o',str(rejected)],capture_output=True,text=True)
                self.assertEqual(result.returncode,2,result.stderr)
                self.assertFalse(rejected.exists())

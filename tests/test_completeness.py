"""Retained context, worked examples and explicit native reconstruction."""
from pathlib import Path
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
import zipfile

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

    def test_upload_zip_preserves_source_and_rejects_tampering(self):
        from package_skill import build, verify
        with tempfile.TemporaryDirectory() as folder:
            dest=Path(folder)/'deck-studio.zip'
            manifest=build(ROOT,dest,revision='test-source')
            self.assertEqual(manifest['skill'],'deck-studio')
            self.assertEqual(verify(ROOT,dest,expected_revision='test-source')['revision'],'test-source')
            with self.assertRaises(ValueError):verify(ROOT,dest,expected_revision='different-source')
            self.assertIn('references/human-voice.md',manifest['files'])
            for path in ('agents/openai.yaml', 'references/host-chatgpt.md', 'references/host-claude.md'):
                self.assertIn(path,manifest['files'])
            self.assertIn('assets/icons/feather/LICENSE',manifest['files'])
            self.assertIn('licence.txt',manifest['files'])
            self.assertIn('tests/fixtures/marketing.json',manifest['files'])
            self.assertIn('tests/evaluations/2026-11-14-feedback-coverage.md',manifest['files'])
            with zipfile.ZipFile(dest) as z:
                self.assertTrue(all(p.startswith('deck-studio/') for p in z.namelist()))
                data={p:z.read(p) for p in z.namelist()}
            self.assertIn(b'Copyright (c) 2026 Prahlad Rajhans',data['deck-studio/licence.txt'])
            self.assertIn(b'Cole Bemis',data['deck-studio/assets/icons/feather/LICENSE'])
            bad=Path(folder)/'tampered.zip'
            data['deck-studio/SKILL.md']+=b'Altered after verification'
            with zipfile.ZipFile(bad,'w') as z:
                for path,content in data.items():z.writestr(path,content)
            with self.assertRaises(ValueError):verify(ROOT,bad)
            metadata=json.loads(data['deck-studio/bundle-manifest.json'])
            metadata['schema_version']=999
            data['deck-studio/bundle-manifest.json']=json.dumps(metadata).encode()
            data['deck-studio/SKILL.md']=data['deck-studio/SKILL.md'].removesuffix(b'Altered after verification')
            with zipfile.ZipFile(bad,'w') as z:
                for path,content in data.items():z.writestr(path,content)
            with self.assertRaises(ValueError):verify(ROOT,bad)
            from package_skill import inputs
            # A missing adapter must fail packaging rather than silently omit host support.
            requiredroot=Path(folder)/'missing-adapter'
            requiredroot.mkdir()
            for name in ('SKILL.md','requirements.txt','scripts/spec_io.py','scripts/build_html.py',
                         'scripts/build_deck.py','references/creative-direction.md',
                         'agents/openai.yaml','references/host-claude.md','licence.txt'):
                source=requiredroot/name
                source.parent.mkdir(parents=True,exist_ok=True)
                source.write_bytes((ROOT/name).read_bytes())
            with self.assertRaisesRegex(ValueError,'host-chatgpt'):inputs(requiredroot)
            (requiredroot/'references/host-chatgpt.md').write_bytes((ROOT/'references/host-chatgpt.md').read_bytes())
            (requiredroot/'licence.txt').unlink()
            with self.assertRaisesRegex(ValueError,'licence.txt'):inputs(requiredroot)
            linkroot=Path(folder)/'source'
            linkroot.mkdir()
            (linkroot/'assets').symlink_to(ROOT/'assets',target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'symlinks'):inputs(linkroot)

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

"""Visual semantics and targeted geometry; renderer integration runs with optional dependencies."""
import html
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from _common import SpecError
from visual_elements import table_cell, process_body, status_color
from geometry_checks import review
from icons import svg, foreground
from spec_io import load_spec
from build_html import HtmlDeck


class VisualRevision(unittest.TestCase):
    def test_status_is_not_colour_only(self):
        self.assertEqual(table_cell({'kind':'status','status':'amber'}), ('● At risk','rag_amber'))
        self.assertEqual(status_color('rag_amber',{'bg':'FFFFFF','accent':'0000FF'}),'8A5700')
        self.assertIn('Supplier', table_cell({'kind':'status','status':'red','label':'Supplier late'})[0])
        with self.assertRaises(SpecError): table_cell({'kind':'status','status':'purple'})

    def test_harvey_has_fraction_and_validates_score(self):
        self.assertIn('3/4', table_cell({'kind':'harvey','score':3})[0])
        for score in (-1,5,True,1.5):
            with self.assertRaises(SpecError): table_cell({'kind':'harvey','score':score})

    def test_process_metrics_do_not_fill_missing_values(self):
        self.assertEqual(process_body({'heading':'Inspect','volume':'80 items','duration':'2 hours'}), 'Volume: 80 items\nTime: 2 hours')
        self.assertEqual(process_body({'body':'Listen'}),'Listen')

    def test_pinned_icons_render_offline_and_reject_paths(self):
        self.assertEqual(len(list((ROOT/'assets/icons/feather').glob('*.svg'))),12)
        self.assertIn('MIT', (ROOT/'assets/icons/feather/LICENSE').read_text())
        self.assertIn('#123ABC',svg('feather:clock','123ABC'))
        self.assertEqual(foreground('FFFFFF'),'000000')
        self.assertEqual(foreground('000000'),'FFFFFF')
        for name in ('feather:../../secret','clock','feather:missing'):
            with self.assertRaises(SpecError): svg(name)
        with self.assertRaises(SpecError): svg('feather:clock','red;opacity:0')

    def test_alignment_checks_real_boxes_and_narrow_pair_waivers(self):
        boxes=[('A',0,0,10,10),('B',20,3,10,10),('C',30,0,10,10)]
        issues,allowed=review(boxes,{'alignment_groups':[{'shapes':['A','B'],'edge':'top','tolerance_pt':2}], 'intentional_overlaps':[{'shapes':['A','B'],'reason':'Inspected layering'}]})
        self.assertEqual(issues[0][0],'alignment')
        self.assertIn(frozenset(('A','B')),allowed)
        self.assertNotIn(frozenset(('A','C')),allowed)
        issues,allowed=review(boxes,{'intentional_overlaps':[{'shapes':['A','missing'],'reason':'x'},{'shapes':['A','B']}]})
        self.assertEqual(len(issues),2)
        self.assertEqual(allowed,set())

    def test_malformed_annotations_warn_instead_of_crashing(self):
        for annotation in ({'intentional_overlaps':None}, {'intentional_overlaps':[None]}, {'alignment_groups':[None]}, {'intentional_overlaps':[{'shapes':[{},'A'],'reason':'x'}]}):
            issues, allowed = review([('A',0,0,1,1)], annotation)
            self.assertTrue(issues)
            self.assertFalse(allowed)

    def test_duplicate_shape_names_cannot_waive_collisions(self):
        issues,allowed=review([('A',0,0,1,1),('A',1,1,1,1),('B',0,0,1,1)], {'intentional_overlaps':[{'shapes':['A','B'],'reason':'x'}]})
        self.assertTrue(issues)
        self.assertFalse(allowed)

    def test_fixed_missing_evidence_is_draft_only(self):
        for name in ('executive','marketing','brand','incomplete'):
            spec=load_spec(str(ROOT/f'assets/benchmarks/{name}.json'))
            self.assertEqual(bool(spec['_blockers']),name=='incomplete',spec['_blockers'])
        self.assertIsNone(json.loads((ROOT/'tests/fixtures/marketing.json').read_text())['material']['control_group'])

    def test_html_structured_components_are_visible(self):
        spec=load_spec(str(ROOT/'assets/examples/visual-components.json'))
        deck=HtmlDeck(spec,str(ROOT/'assets/examples'))
        doc=deck.build()
        self.assertIn('<svg',doc)
        self.assertIn('stroke="#FFFFFF"',doc)
        self.assertIn('3/4',doc)
        self.assertIn('Approval pending',doc)
        self.assertIn('(base)',doc)
        self.assertIn('Volume: 100 items',doc)
        self.assertNotIn("'kind': 'status'",doc)

    def test_full_stage_copy_review_ignores_planning_and_html_code(self):
        from _common import slide_strings
        slide = {'type':'custom','full_bleed':True,'title':'Planning title hidden',
                 'html':'<h1 style="font-size:100px">Visible claim</h1><style>.thing {color:red}</style><template>Hidden notes</template>',
                 'pptx_note':'Rebuild these editable objects with exact coordinates',
                 'layout_review':{'alignment_groups':[{'shapes':['Metadata A','Metadata B'],'edge':'top'}]}}
        text=' '.join(slide_strings(slide))
        self.assertEqual(text.strip(),'Visible claim')

    def test_native_components_remain_editable(self):
        try:
            import pptx
            import cairosvg
        except ImportError:
            self.skipTest('PPTX/icon dependencies not installed')
        with tempfile.TemporaryDirectory() as folder:
            dest=Path(folder)/'components.pptx'
            r=subprocess.run([sys.executable,str(ROOT/'scripts/build_deck.py'),str(ROOT/'assets/examples/visual-components.json'),'--strict','-o',str(dest)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            deck=pptx.Presentation(dest)
            self.assertTrue(any(sp.shape_type==13 for sp in deck.slides[0].shapes))
            table=next(sp.table for sp in deck.slides[1].shapes if sp.has_table)
            self.assertIn('3/4',table.cell(1,2).text)
            self.assertIn('Approval pending',table.cell(2,1).text)

    def test_chart_extensions_render_negative_outcomes(self):
        try:
            import matplotlib
        except ImportError:
            self.skipTest('matplotlib not installed')
        from chart_images import render
        with tempfile.TemporaryDirectory() as folder:
            for kind in ('tornado','sensitivity'):
                spec=json.loads((ROOT/f'assets/examples/chart-{kind}.json').read_text())
                path=Path(folder)/f'{kind}.png'
                render(spec,str(path))
                self.assertGreater(path.stat().st_size,1000)
            with self.assertRaises(SpecError): render({'kind':'tornado','base':10,'items':[{'label':'x','low':11,'high':20}]},str(path))
            with self.assertRaises(SpecError): render({'kind':'sensitivity','rows':['a'],'cols':['b'],'values':[[1]],'base_cell':[2,0]},str(path))

    def test_fallback_controls_work_in_sandbox(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.skipTest('playwright not installed')
        doc=(ROOT/'assets/html-stage/stage-template.html').read_text()
        with sync_playwright() as p:
            browser=p.chromium.launch()
            page=browser.new_page()
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content('<iframe sandbox="allow-scripts" srcdoc="'+html.escape(doc,quote=True)+'"></iframe>')
            frame=page.frames[1]
            for key in ('ArrowRight','n','g'):
                frame.evaluate('(key)=>window.dispatchEvent(new KeyboardEvent("keydown",{key}))',key)
            self.assertEqual(frame.locator('#notes').evaluate('(el)=>el.style.display'),'block')
            self.assertEqual(frame.locator('#grid').evaluate('(el)=>el.style.display'),'grid')
            frame.locator('#grid button').nth(3).click()
            self.assertEqual(frame.locator('#stage > .slide.active').count(),1)
            self.assertEqual(frame.locator('#stage > .slide').nth(3).get_attribute('class'),'slide active')
            self.assertFalse(errors)
            browser.close()

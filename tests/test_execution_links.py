"""Real timeout/cleanup regressions, dependency isolation and structural link checks."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from execution import Deadline, ExecutionTimeout, positive_seconds, run_bounded
import check_links
import env_check


class ExecutionAndLinks(unittest.TestCase):
    def test_success_and_command_failure_preserve_exit_semantics(self):
        result=run_bounded([sys.executable,'-c','print("ready")'],timeout=3,capture_output=True,text=True)
        self.assertEqual(result.stdout.strip(),'ready')
        with self.assertRaises(subprocess.CalledProcessError):
            run_bounded([sys.executable,'-c','raise SystemExit(7)'],timeout=3,check=True)

    def test_hanging_process_exits_with_a_timeout(self):
        start=time.monotonic()
        with self.assertRaises(ExecutionTimeout):
            run_bounded([sys.executable,'-c','import time;time.sleep(60)'],timeout=.15,capture_output=True)
        self.assertLess(time.monotonic()-start,5)

    @unittest.skipUnless(os.name=='posix','process group cleanup is POSIX-specific')
    def test_timeout_stops_descendants_as_well_as_parent(self):
        with tempfile.TemporaryDirectory() as folder:
            marker=Path(folder)/'orphan-finished'
            child='import pathlib,sys,time;time.sleep(.8);pathlib.Path(sys.argv[1]).write_text("orphan")'
            parent='import subprocess,sys,time;subprocess.Popen([sys.executable,"-c",sys.argv[1],sys.argv[2]]);time.sleep(60)'
            with self.assertRaises(ExecutionTimeout):
                run_bounded([sys.executable,'-c',parent,child,str(marker)],timeout=.2,capture_output=True)
            time.sleep(.9)
            self.assertFalse(marker.exists(),'a descendant survived the timeout')

    @unittest.skipUnless(os.name=='posix','nested process-group ownership is POSIX-specific')
    def test_nested_timeout_cleans_converter_and_owned_workspace(self):
        for outer,inner in ((.2,5),(3,.2)):
            with tempfile.TemporaryDirectory() as folder:
                marker=Path(folder)/'converter-finished'
                workspace=Path(folder)/'workspace-path'
                child='import pathlib,sys,time;time.sleep(.8);pathlib.Path(sys.argv[1]).write_text("orphan")'
                nested=('import os,pathlib,sys;sys.path.insert(0,sys.argv[1]);'
                        'from execution import run_bounded;'
                        'pathlib.Path(sys.argv[2]).write_text(os.environ["_DECK_STUDIO_EXEC_CONTEXT"]);'
                        'run_bounded([sys.executable,"-c",sys.argv[3],sys.argv[4]],timeout=float(sys.argv[5]))')
                start=time.monotonic()
                with self.assertRaises(ExecutionTimeout):
                    run_bounded([sys.executable,'-c',nested,str(ROOT/'scripts'),str(workspace),child,str(marker),str(inner)],timeout=outer,capture_output=True,text=True)
                self.assertLess(time.monotonic()-start,.75)
                time.sleep(.9)
                self.assertFalse(marker.exists())
                self.assertFalse(Path(workspace.read_text()).exists())

    def test_deadline_is_shared_across_steps(self):
        with patch('execution.time.monotonic',side_effect=[100,105,111]):
            budget=Deadline(10)
            self.assertEqual(budget.remaining(8),5)
            with self.assertRaises(ExecutionTimeout):budget.remaining()

    def test_invalid_time_limits_are_rejected(self):
        for value in (0,-1,float('inf'),float('nan'),True,'bad'):
            with self.assertRaises(ValueError):positive_seconds(value)

    def test_preview_stops_before_next_child_when_total_budget_is_used(self):
        import preview_directions
        with tempfile.TemporaryDirectory() as folder, patch('preview_directions.Deadline') as budget, patch('preview_directions.run_bounded') as run:
            budget.return_value.remaining.side_effect=[1,ExecutionTimeout('budget exhausted')]
            run.return_value=subprocess.CompletedProcess([],0,'','')
            with self.assertRaises(ExecutionTimeout):
                preview_directions.main(['unused.json','--directions','consulting-navy','--out',folder])
            self.assertEqual(run.call_count,1)

    def test_optional_pdf_fallback_runs_as_a_bounded_worker(self):
        try:
            from PIL import Image
            import fitz
        except ImportError:
            self.skipTest('Pillow or optional PyMuPDF not installed')
        import render
        with tempfile.TemporaryDirectory() as folder:
            pdf=Path(folder)/'input.pdf'
            Image.new('RGB',(32,32),'white').save(pdf,'PDF')
            with patch('render.shutil.which',return_value=None):
                images=render.to_pngs(str(pdf),folder,96,timeout=20)
            self.assertEqual(len(images),1)
            with Image.open(images[0]) as image:self.assertGreater(image.width,0)

    def test_missing_optional_packages_do_not_crash_or_block_html_authoring(self):
        unavailable={'ok':False,'detail':'missing in test environment'}
        with patch('env_check.probe',return_value=unavailable), patch('env_check.run_bounded',return_value=subprocess.CompletedProcess([],1,'','')), patch('env_check.soffice_bin',side_effect=SystemExit()), patch('env_check.shutil.which',return_value=None), patch('env_check._pil_font',side_effect=AssertionError('must not load absent Pillow')):
            report=env_check.collect('consulting-navy')
        self.assertTrue(report['features']['html_draft'])
        self.assertFalse(report['features']['pptx_icons'])
        self.assertFalse(report['features']['html_render'])
        self.assertIn('cairosvg',report['dependencies'])

    def test_required_feature_gate_reports_failure(self):
        from contextlib import redirect_stdout
        from io import StringIO
        fake={'features':{'html_draft':True,'pptx_icons':False}}
        with patch('env_check.collect',return_value=fake), redirect_stdout(StringIO()) as output:
            result=env_check.main(['--json','--require','pptx_icons'])
        self.assertEqual(result,1)
        self.assertEqual(json.loads(output.getvalue())['missing_required'],['pptx_icons'])

    def test_full_bundle_reference_graph_is_resolved(self):
        self.assertEqual(check_links.check(ROOT)['errors'],[])

    def test_checker_detects_missing_targets_sections_and_import_cycles(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'scripts').mkdir()
            (root/'references').mkdir()
            (root/'SKILL.md').write_text('See missing.md and guide.md §9. [Bad](references/absent.md)')
            (root/'references/guide.md').write_text('## 1. Valid section\n')
            (root/'scripts/a.py').write_text('import b\n')
            (root/'scripts/b.py').write_text('import a\n')
            errors='\n'.join(check_links.check(root)['errors'])
            self.assertIn('missing.md',errors)
            self.assertIn('guide.md §9',errors)
            self.assertIn('circular local import',errors)

    def test_chart_registry_is_discoverable_in_route_reference(self):
        from chart_images import KINDS
        route=(ROOT/'references/routes.md').read_text().split('## G. Chart images',1)[1].split('## H.',1)[0].lower()
        for kind in KINDS:self.assertIn(kind,route)

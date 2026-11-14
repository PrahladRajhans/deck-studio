#!/usr/bin/env python3
"""Report feature dependencies, fonts and actual renderer readiness.

Missing optional features do not block dependency-free HTML authoring. Use --require FEATURE
for a route-specific readiness gate, or --json for a machine-readable report.
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import sys

from _common import DIRECTIONS, FONT_FALLBACKS, _FONT_FILES, _find_font_file, _pil_font
from execution import Deadline, ExecutionTimeout, run_bounded
from render import soffice_bin

HERE = os.path.dirname(os.path.abspath(__file__))
DEPENDENCIES = {'pptx': 'python-pptx', 'PIL': 'Pillow', 'matplotlib': 'matplotlib',
                'numpy': 'NumPy (installed with matplotlib)', 'playwright': 'Playwright',
                'cairosvg': 'CairoSVG/native Cairo (PPTX Feather icons)', 'fitz': 'PyMuPDF (optional fallback)'}
PROBE = "import importlib,sys;importlib.import_module(sys.argv[1])"


def probe(module, deadline):
    command = [sys.executable, '-c', PROBE, module]
    if module == 'PIL':
        command = [sys.executable, '-c', 'from PIL import ImageFont;ImageFont.load_default()']
    if module == 'cairosvg':
        command = [sys.executable, '-c',
                   "import sys;sys.path.insert(0,sys.argv[1]);from icons import png;png('feather:clock')", HERE]
    try:
        result = run_bounded(command, timeout=deadline.remaining(15), capture_output=True, text=True)
    except ExecutionTimeout:
        return {'ok': False, 'detail': 'probe timed out; no retry'}
    detail = 'ok' if result.returncode == 0 else ((result.stderr or 'dependency unavailable').strip().splitlines()[-1])
    return {'ok': result.returncode == 0, 'detail': detail[:200]}


def collect(direction=None):
    deadline = Deadline(120)
    dependencies = {module: probe(module, deadline) for module in DEPENDENCIES}
    code = ('from playwright.sync_api import sync_playwright;'
            'p=sync_playwright().start();b=p.chromium.launch(timeout=15000);b.close();p.stop()')
    try:
        result = run_bounded([sys.executable, '-c', code], timeout=deadline.remaining(20), capture_output=True, text=True)
        chromium = result.returncode == 0
    except ExecutionTimeout:
        chromium = False
    try:
        office = soffice_bin()
    except SystemExit:
        office = None
    poppler = shutil.which('pdftoppm')
    fonts = []
    dirs = [direction] if direction else DIRECTIONS
    for family in sorted({DIRECTIONS[d][k] for d in dirs for k in ('heading_font','body_font')}):
        for bold in (False,True):
            want = _FONT_FILES.get((family.lower(),bold))
            path = _find_font_file(want) if want else None
            if dependencies['PIL']['ok']:
                _pil_font(family,bold,20)
            fonts.append({'family':family,'bold':bold,'file':path,
                          'measurement':('Pillow unavailable; measurement unverified' if not dependencies['PIL']['ok'] else ('font file' if path else FONT_FALLBACKS.get((family.lower(),bold),'substitute')))})
    ok = lambda name: dependencies[name]['ok']
    features = {'html_draft':True, 'html_render':ok('PIL') and chromium,
                'pptx_build':ok('pptx') and ok('PIL'),
                'pptx_render':ok('PIL') and bool(office) and bool(poppler or ok('fitz')),
                'chart_images':ok('matplotlib') and ok('numpy'), 'pptx_icons':ok('cairosvg')}
    return {'dependencies':dependencies,'chromium':chromium,'libreoffice':office,
            'poppler':poppler,'fonts':fonts,'features':features}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--direction', choices=sorted(DIRECTIONS))
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--require', action='append', default=[],
                        choices=['html_draft','html_render','pptx_build','pptx_render','chart_images','pptx_icons'])
    args = parser.parse_args(argv)
    report = collect(args.direction)
    report['missing_required'] = [f for f in args.require if not report['features'][f]]
    if args.json:
        print(json.dumps(report,indent=2))
    else:
        print('Dependencies (missing optional features do not block other routes):')
        for module, status in report['dependencies'].items():
            print(f"  {DEPENDENCIES[module]}: {status['detail']}")
        print('Feature readiness:')
        for feature, ready in report['features'].items():
            print(f"  {feature}: {'ready' if ready else 'unavailable'}")
        print('Fonts (check wrapping with the final renderer):')
        for font in report['fonts']:
            print(f"  {font['family']}{' bold' if font['bold'] else ''}: {font['measurement']}" + (f" ({font['file']})" if font['file'] else ''))
        print(f"  LibreOffice: {report['libreoffice'] or 'MISSING'}")
        print(f"  poppler: {report['poppler'] or 'MISSING; optional PyMuPDF fallback'}")
        if report['missing_required']:
            print('Required features unavailable: '+', '.join(report['missing_required']))
    return 1 if report['missing_required'] else 0


if __name__ == '__main__':
    sys.exit(main())

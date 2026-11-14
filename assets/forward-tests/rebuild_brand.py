#!/usr/bin/env python3
"""Native editable reconstruction of brand.json, not a general HTML converter.

The recipe uses the reviewed composition's fixed geometry and extracts resolved copy from the
same spec. If its structure changes, refuse rather than guessing. Adapt the recipe deliberately,
render it and reconcile before using it for a different design. No full-slide images are used.
"""
from html.parser import HTMLParser
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from _common import SLIDE_W, SLIDE_H, SpecError
from spec_io import load_spec, report
from build_deck import Builder
from pptx.enum.shapes import MSO_SHAPE


class Copy(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.parts = []
        self.structure = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        self.structure.append(['start', tag, sorted(attrs)])

    def handle_endtag(self, tag):
        self.structure.append(['end', tag])

    def handle_startendtag(self, tag, attrs):
        self.structure.append(['empty', tag, sorted(attrs)])

    def signature(self):
        return hashlib.sha256(json.dumps(self.structure).encode()).hexdigest()

    def handle_data(self, text):
        if text.strip():
            self.parts.append(text.strip())


class BrandRecipe(Builder):
    def s_custom(self, s):
        index = self.cur_idx - 1
        copy = Copy(s['html'])
        parts = copy.parts
        signatures = ['5208cb057440d508d4045e365577e899ad25722059eebe6a2f9eaf0a42fc2ac4', '2b3d3c2c8e5ac0ad0c9ffb015e9a3851d9e6fffb7de9ade08057909646d515fc', '319c5a37f477c2b3529e66a96824689a374061d0737b607a09edca06e17e5032', '946108eca543d45b063a0a07398423afe2f4dc16c84af01a5813b7f2dc244719']
        if copy.signature() != signatures[index]:
            raise SpecError('brand recipe markup/layout changed; revise and review the native recipe')
        counts = [4, 8, 8, 6]
        if len(parts) != counts[index]:
            raise SpecError('brand recipe content structure changed; revise and review the native recipe')
        dark, paper, acid = '151515', 'F4F0E6', 'E3FF55'
        bg = [dark, acid, paper, dark][index]
        ink = paper if index in (0, 3) else dark
        slide = self.new_slide()
        self.rect(slide, 0, 0, SLIDE_W, SLIDE_H, fill=bg, name='Background')

        def text(name, x, y, w, h, value, size, color=ink, bold=False):
            # HTML pixels / 144 -> inches; pixels / 2 -> points for this fixed canvas.
            return self.text(slide, x/144, y/144, w/144, h/144, value, size/2, color,
                             font='Arial', bold=bold, min_size=size/2, name=name,
                             line_spacing=1.05, para_space=0)

        def rule(name, x, y, w):
            self.line(slide, x/144, y/144, (x+w)/144, y/144, dark, width=1.5, name=name)

        text('Kicker', 120, 105, 1650, 65, parts[0], 28, acid if index == 3 else ink)
        if index == 0:
            self.rect(slide, 1305/144, 240/144, 490/144, 490/144,
                      line=acid, line_w=1, shape=MSO_SHAPE.OVAL, name='Conceptual spotlight')
            text('Festival name', 120, 250, 1100, 530, '\n'.join(parts[1:3]), 180, acid, True)
            text('Headline', 120, 850, 1600, 90, parts[3], 48)
        elif index == 1:
            text('Headline', 120, 220, 1640, 150, parts[1], 100, bold=True)
            rule('Section rule', 120, 390, 1680)
            text('Kicker left', 120, 455, 690, 65, parts[2], 28)
            text('Stay', 120, 565, 660, 180, parts[3], 105, bold=True)
            self.line(slide, 830/144, 445/144, 830/144, 800/144, dark, width=1.5, name='Experience threshold')
            text('Kicker right', 900, 455, 850, 65, parts[4], 28)
            text('Make', 900, 565, 850, 260, '\n'.join(parts[5:7]), 105, bold=True)
            text('Proposal', 120, 900, 1650, 100, parts[7], 36)
        elif index == 2:
            text('Headline', 120, 210, 1600, 250, '\n'.join(parts[1:3]), 100, bold=True)
            rule('Left rule', 120, 500, 780)
            rule('Right rule', 990, 500, 780)
            text('Artists', 120, 550, 780, 90, parts[3], 52, bold=True)
            text('Workshop', 120, 665, 780, 130, parts[4], 36)
            text('Choice', 990, 550, 780, 90, parts[5], 52, bold=True)
            text('Participation', 990, 665, 780, 130, parts[6], 36)
            text('Caveat', 120, 895, 1650, 110, parts[7], 36)
        else:
            text('Headline', 120, 210, 1600, 260, '\n'.join(parts[1:3]), 100, bold=True)
            text('Support ask', 120, 530, 1650, 180, parts[3], 150, acid, True)
            text('Scope', 120, 755, 1650, 100, parts[4], 36)
            self.line(slide, 120/144, 875/144, 1800/144, 875/144, '444444', width=1, name='Scope rule')
            text('Caveat', 120, 910, 1650, 100, parts[5], 32)
        self.rect(slide, .80, 7.12, 11.8, .25, fill='FFFFFF', name='Source surface')
        self.text(slide, .83, 7.14, 11.6, .20, s.get('source', ''), 9, '111111',
                  font='Arial', min_size=9, name='Source', para_space=0)
        return slide


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', default=str(Path(__file__).with_name('brand.json')))
    parser.add_argument('-o', '--out', required=True)
    args = parser.parse_args(argv)
    try:
        spec = load_spec(args.spec)
        if report(spec, True):
            return 2
        if len(spec['slides']) != 4 or any(s.get('type') != 'custom' or not s.get('full_bleed') for s in spec['slides']):
            raise SpecError('recipe supports only the reviewed four-slide full-stage brand composition')
        builder = BrandRecipe(spec, str(Path(args.spec).resolve().parent))
        deck = builder.build()
        hard = [w for w in builder.warnings if 'does not fit' in w or 'placeholder' in w]
        if hard:
            for warning in hard:
                print(warning, file=sys.stderr)
            return 3
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        deck.save(out)
        print(f'built {out}: native editable text/shapes, controlled reconstruction of reviewed brand HTML')
        return 0
    except SpecError as exc:
        print(f'SPEC ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())

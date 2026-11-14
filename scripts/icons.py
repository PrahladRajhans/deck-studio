"""Pinned, licensed Feather icons. Rendering is offline and independent of Office fonts."""
from io import BytesIO
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from _common import SpecError

ROOT = Path(__file__).resolve().parents[1] / 'assets/icons/feather'


def svg(name, color='FFFFFF'):
    if not re.fullmatch(r'feather:[a-z0-9-]+', str(name)):
        raise SpecError('icons must use a bundled feather:name identifier')
    if not re.fullmatch(r'[0-9a-fA-F]{6}', color):
        raise SpecError('icon colour must be six hexadecimal digits')
    path = ROOT / (name.split(':', 1)[1] + '.svg')
    if not path.is_file():
        raise SpecError(f'icon is not bundled: {name}')
    text = path.read_text(encoding='utf-8')
    ET.fromstring(text)
    return text.replace('currentColor', '#' + color)


def foreground(background):
    """Choose the more legible monochrome icon stroke for the actual badge fill."""
    channels = [int(background[i:i+2], 16)/255 for i in (0, 2, 4)]
    linear = [c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in channels]
    lum = sum(c*w for c, w in zip(linear, (.2126, .7152, .0722)))
    return 'FFFFFF' if 1.05/(lum+.05) >= (lum+.05)/.05 else '000000'


def png(name, color='FFFFFF'):
    import cairosvg
    return BytesIO(cairosvg.svg2png(bytestring=svg(name, color).encode(), output_width=192, output_height=192))

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


def png(name, color='FFFFFF'):
    import cairosvg
    return BytesIO(cairosvg.svg2png(bytestring=svg(name, color).encode(), output_width=192, output_height=192))

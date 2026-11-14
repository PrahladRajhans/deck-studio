"""Shared, deterministic table and process semantics for both output formats."""
from _common import SpecError

STATUS = {'green': ('rag_green', 'On track'), 'amber': ('rag_amber', 'At risk'),
          'red': ('rag_red', 'Off track'), 'unknown': ('rag_unknown', 'Unknown')}
BALLS = ('○', '◔', '◑', '◕', '●')


def table_cell(value):
    """Return visible text and optional colour token. Never communicate status by colour alone."""
    if not isinstance(value, dict):
        return str(value), None
    kind = value.get('kind')
    label = value.get('label', '')
    if kind == 'status':
        status = value.get('status', 'unknown')
        if status not in STATUS:
            raise SpecError(f'unknown table status: {status}')
        token, default = STATUS[status]
        return f'● {label or default}', token
    if kind == 'harvey':
        score = value.get('score')
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 4:
            raise SpecError('Harvey score must be an integer from 0 to 4')
        return f'{BALLS[score]} {score}/4' + (f' {label}' if label else ''), None
    raise SpecError(f'unknown structured table cell: {kind}')


def process_body(step):
    """Optional explicit metrics; no inferred throughput, costs or conversions."""
    parts = [str(step.get('body', ''))] if step.get('body') else []
    for key, label in (('volume', 'Volume'), ('duration', 'Time'), ('cost', 'Cost'), ('conversion', 'Conversion'),
                       ('defect_rate', 'Defect rate'), ('drop_off', 'Drop-off')):
        if key in step:
            parts.append(f'{label}: {step[key]}')
    return '\n'.join(parts)


def status_color(token, theme, background=None):
    """Semantic RAG hues, with readable foregrounds on the actual table surface."""
    palette = {'rag_green': ('157347','75D8A3'), 'rag_amber': ('8A5700','FFD166'),
               'rag_red': ('B42318','FF9999'), 'rag_unknown': ('52606D','BCC8D3')}
    bg = background or theme['bg']
    def lum(h):
        c = [int(h[i:i+2],16)/255 for i in (0,2,4)]
        c = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in c]
        return sum(v*w for v,w in zip(c,(.2126,.7152,.0722)))
    def ratio(fg):
        a,b = sorted((lum(fg),lum(bg)))
        return (b+.05)/(a+.05)
    for color in palette[token]:
        if ratio(color) >= 4.5:
            return color
    return max(('000000','FFFFFF'), key=ratio)


def table_base(base_cell, rows, columns):
    """Reject malformed or out-of-range base markers before indexing the crosshair."""
    if base_cell is None:
        return None
    if not isinstance(base_cell, list) or len(base_cell) != 2 or any(isinstance(v, bool) or not isinstance(v, int) for v in base_cell):
        raise SpecError('base_cell must be [row, column] with integer indices')
    row, col = base_cell
    if not 0 <= row < len(rows) or not 0 <= col < len(columns):
        raise SpecError('base_cell lies outside the table')
    return base_cell

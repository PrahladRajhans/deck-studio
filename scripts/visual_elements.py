"""Shared, deterministic table and process semantics for both output formats."""
from _common import SpecError

STATUS = {'green': ('pos', 'On track'), 'amber': ('accent', 'At risk'),
          'red': ('neg', 'Off track'), 'unknown': ('muted', 'Unknown')}
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
    for key, label in (('volume', 'Volume'), ('duration', 'Time'), ('cost', 'Cost'), ('conversion', 'Conversion')):
        if key in step:
            parts.append(f'{label}: {step[key]}')
    return '\n'.join(parts)

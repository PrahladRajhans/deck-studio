"""Narrow checks against actual named shapes; all dimensions use one caller-supplied unit."""
import math
from collections import Counter


def review(boxes, annotations=None, points_per_unit=1):
    annotations = {} if annotations is None else annotations
    counts = Counter(b[0] for b in boxes)
    unique = {b[0]: b[1:] for b in boxes if counts[b[0]] == 1}
    findings, allowed = [], set()
    if not isinstance(annotations, dict):
        return [('layout_annotation', 'layout_review must be an object')], allowed
    overlaps = annotations.get('intentional_overlaps', [])
    groups = annotations.get('alignment_groups', [])
    if not isinstance(overlaps, list) or not isinstance(groups, list):
        return [('layout_annotation', 'annotation groups must be lists')], allowed
    for item in overlaps:
        if not isinstance(item, dict):
            findings.append(('layout_annotation', 'overlap exception must be an object'))
            continue
        names = item.get('shapes', [])
        if not isinstance(names, list) or any(not isinstance(n, str) for n in names) or len(names) != 2 or len(set(names)) != 2 or not isinstance(item.get('reason'), str) or not item.get('reason', '').strip() or any(n not in unique for n in names):
            findings.append(('layout_annotation', 'overlap exception needs two unique existing shape names and a reason'))
        else:
            allowed.add(frozenset(names))
    edges = {'left': lambda b: b[0], 'right': lambda b: b[0]+b[2],
             'top': lambda b: b[1], 'bottom': lambda b: b[1]+b[3],
             'center_x': lambda b: b[0]+b[2]/2, 'center_y': lambda b: b[1]+b[3]/2}
    for group in groups:
        if not isinstance(group, dict):
            findings.append(('layout_annotation', 'alignment group must be an object'))
            continue
        names, edge = group.get('shapes', []), group.get('edge')
        tol = group.get('tolerance_pt', 2)
        if not isinstance(names, list) or any(not isinstance(n, str) for n in names) or not isinstance(edge, str) or edge not in edges or len(names) < 2 or len(set(names)) != len(names) or any(n not in unique for n in names) or isinstance(tol, bool) or not isinstance(tol, (float, int)) or not math.isfinite(tol) or not 0 <= tol <= 6:
            findings.append(('layout_annotation', 'alignment group needs unique existing shapes, valid edge and tolerance_pt from 0 to 6'))
            continue
        vals = [edges[edge](unique[n]) * points_per_unit for n in names]
        if max(vals)-min(vals) > tol:
            findings.append(('alignment', f'{edge} alignment differs by {max(vals)-min(vals):.1f} pt: {names}'))
    return findings, allowed

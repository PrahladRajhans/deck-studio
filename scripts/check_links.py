#!/usr/bin/env python3
"""Check internal document/file/section pointers and circular local Python imports."""
import argparse
import ast
import json
from pathlib import Path
import re
from urllib.parse import unquote


def check(root):
    root = Path(root)
    documents = list(root.glob('*.md')) + list(root.glob('references/*.md')) + list(root.glob('tests/**/*.md'))
    index = {}
    for path in root.rglob('*.md'):
        if '.git' not in path.parts:
            index.setdefault(path.name, []).append(path)
    errors, count = [], 0
    for path in documents:
        text = path.read_text(encoding='utf-8')
        label = str(path.relative_to(root))
        for target in re.findall(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)',text):
            if target.startswith(('https:', 'http:', '#', 'mailto:')):
                continue
            count += 1
            local = unquote(target.split('#')[0])
            if not (path.parent/local).exists():
                errors.append(f'{label}: missing link target {local}')
        for target in re.findall(r'(?<![\w/.])((?:scripts|references|assets|tests)/[\w./-]+)',text):
            count += 1
            local = target.rstrip('.;,:')
            if not (root/local).exists():
                errors.append(f'{label}: missing path {local}')
        for match in re.finditer(r'(?<![\w/.-])([\w-]+\.md)(?:\s+§([A-Z]|\d+[a-z]?))?',text):
            name, section = match.groups()
            count += 1
            if name not in index:
                errors.append(f'{label}: missing referenced document {name}')
            elif section and not any(re.search(r'^#{1,6}\s+'+re.escape(section)+r'(?:[. ·:]|\s|$)',p.read_text(),re.M) for p in index[name]):
                errors.append(f'{label}: missing section {name} §{section}')
    modules = {p.stem:p for p in (root/'scripts').glob('*.py')}
    graph = {name:set() for name in modules}
    for name,path in modules.items():
        for node in ast.walk(ast.parse(path.read_text(),filename=str(path))):
            imports = [a.name.split('.')[0] for a in node.names] if isinstance(node,ast.Import) else ([node.module.split('.')[0]] if isinstance(node,ast.ImportFrom) and node.module else [])
            graph[name].update(module for module in imports if module in modules)
    done = set()
    def visit(name, stack):
        if name in stack:
            errors.append('circular local import: '+' -> '.join(stack[stack.index(name):]+[name]))
            return
        if name in done:
            return
        for dependency in sorted(graph[name]):
            visit(dependency,stack+[name])
        done.add(name)
    for name in sorted(graph):
        visit(name,[])
    return {'references_checked':count,'modules_checked':len(graph),'errors':sorted(set(errors))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    report = check(args.root)
    if args.json:
        print(json.dumps(report,indent=2))
    else:
        print(f"checked {report['references_checked']} internal pointers and {report['modules_checked']} local modules")
        for error in report['errors']:
            print('ERROR: '+error)
        if not report['errors']:
            print('internal references and local import graph: clean')
    return 1 if report['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())

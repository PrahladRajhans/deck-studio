#!/usr/bin/env python3
"""Build and verify an upload ZIP rooted at the skill name, preserving source and context."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

INCLUDE = ('SKILL.md', 'README.md', 'CHANGELOG.md', 'requirements.txt', 'LICENSE',
           'scripts', 'references', 'assets', 'tests')
REQUIRED = ('SKILL.md', 'requirements.txt', 'scripts/spec_io.py', 'scripts/build_html.py',
            'scripts/build_deck.py', 'references/creative-direction.md')
MANIFEST = 'bundle-manifest.json'


def inputs(root):
    files = {}
    for entry in INCLUDE:
        path = root / entry
        if path.is_symlink():
            raise ValueError(f'bundle does not follow symlinks: {entry}')
        candidates = [path] if path.is_file() else (path.rglob('*') if path.is_dir() else [])
        for source in candidates:
            relative = source.relative_to(root)
            if any(part.startswith('.') or part == '__pycache__' for part in relative.parts) or source.suffix in {'.pyc', '.pyo'}:
                continue
            if source.is_symlink():
                raise ValueError(f'bundle does not follow symlinks: {relative}')
            if source.is_file():
                files[relative.as_posix()] = source.read_bytes()
    for name in REQUIRED:
        if name not in files:
            raise ValueError(f'required skill file missing: {name}')
    return files


def skill_name(files):
    header = re.match(r'---\s*\n(.*?)\n---', files['SKILL.md'].decode(), re.S)
    match = re.search(r'^name:\s*([a-z0-9-]+)\s*$', header[1], re.M) if header else None
    if not match or len(match[1]) > 64:
        raise ValueError('SKILL.md needs a valid lowercase skill name')
    return match[1]


def build(root, out, revision='unspecified'):
    root, out = Path(root).resolve(), Path(out).resolve()
    files = inputs(root)
    name = skill_name(files)
    manifest = {'schema_version': 1, 'skill': name, 'revision': revision,
                'files': {p: hashlib.sha256(data).hexdigest() for p, data in sorted(files.items())}}
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'w') as archive:
        for path, data in sorted({**files, MANIFEST: (json.dumps(manifest, indent=2)+'\n').encode()}.items()):
            item = zipfile.ZipInfo(f'{name}/{path}', date_time=(1980,1,1,0,0,0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = (0o100644 << 16)
            archive.writestr(item, data)
    verify(root, out)
    return manifest


def verify(root, out, expected_revision=None):
    expected = inputs(Path(root).resolve())
    name = skill_name(expected)
    with zipfile.ZipFile(out) as archive:
        names = archive.namelist()
        wanted = {f'{name}/{p}' for p in expected} | {f'{name}/{MANIFEST}'}
        if len(names) != len(set(names)) or set(names) != wanted or any('..' in PurePosixPath(p).parts for p in names):
            raise ValueError('ZIP must contain exactly one correctly named skill folder and its source files')
        manifest = json.loads(archive.read(f'{name}/{MANIFEST}'))
        if manifest.get('schema_version') != 1 or not isinstance(manifest.get('revision'),str):
            raise ValueError('unsupported manifest schema or revision metadata')
        if expected_revision is not None and manifest['revision'] != expected_revision:
            raise ValueError('bundle revision differs from the expected source commit')
        hashes = {p: hashlib.sha256(data).hexdigest() for p, data in expected.items()}
        if manifest.get('skill') != name or manifest.get('files') != hashes:
            raise ValueError('bundle manifest differs from the source')
        for path, data in expected.items():
            if archive.read(f'{name}/{path}') != data:
                raise ValueError(f'bundled file differs from source: {path}')
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--out', required=True)
    parser.add_argument('--revision')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args(argv)
    manifest = verify(args.root, args.out, expected_revision=args.revision) if args.verify_only else build(args.root, args.out, args.revision or 'unspecified')
    print(f'verified {args.out}: {manifest["skill"]}/, {len(manifest["files"])} source files, revision {manifest["revision"]}')


if __name__ == '__main__':
    main()

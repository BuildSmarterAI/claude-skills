#!/usr/bin/env python3
"""Deterministic, manifest-driven skill deployment.

    canonical claude-skills repo  ->  ~/.claude/skills   (Claude Code)
                                  ->  ~/.agents/skills   (Codex CLI, root `r0`)

The runtime stores are DEPLOYMENT OUTPUTS. Do not hand-edit them; edit the
canonical source and redeploy.

Usage
-----
    python scripts/deploy-skills.py --check      # report drift, change nothing (exit 1 on drift)
    python scripts/deploy-skills.py --dry-run    # describe exactly what --deploy would do
    python scripts/deploy-skills.py --deploy     # copy/update runtime stores
    ... [--runtime claude|codex|all] [--skill NAME] [--json PATH]
    ... [--claude-root DIR] [--codex-root DIR]   # for sandbox testing

Safety properties
-----------------
* Idempotent: deploying twice is a no-op.
* Hash-based: decisions come from SHA-256 of file bytes, never mtime or size.
* COPY/UPDATE ONLY. It never deletes a runtime skill. Runtime-only skills are
  reported as EXTRA so they can be reviewed, never silently removed.
* Refuses to run if the manifest is missing/unparseable, or if a declared source
  is absent.
* Never touches `pre-consolidation/` (the preservation archive) or `scripts/`,
  `docs/`, `manifests/`.
* Preserves bytes exactly, including line endings.
* Exit codes: 0 clean, 1 drift found (--check), 2 refused/error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(REPO, 'manifests', 'skills.json')

NEVER_DEPLOY = {'pre-consolidation', 'scripts', 'docs', 'manifests', '.git', '.github'}
EXCLUDE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', '.cache'}
EXCLUDE_SUFFIX = ('.pyc', '.pyo', '.log', '.tmp', '.pem', '.key')
EXCLUDE_NAMES = {'.env', '.DS_Store', 'Thumbs.db'}

DEPLOYABLE_MODES = {'IDENTICAL', 'CLAUDE_ONLY', 'CODEX_ONLY'}


def sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def walk(root: str):
    """Relative paths of deployable files under a skill directory."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn in EXCLUDE_NAMES or fn.lower().endswith(EXCLUDE_SUFFIX):
                continue
            full = os.path.join(dirpath, fn)
            out.append(os.path.relpath(full, root).replace('\\', '/'))
    return sorted(out)


def load_manifest(path):
    if not os.path.isfile(path):
        sys.exit(f'REFUSED: manifest not found at {path}')
    try:
        return json.load(open(path, encoding='utf-8'))
    except Exception as exc:
        sys.exit(f'REFUSED: manifest is not valid JSON ({exc})')


def plan(manifest, roots, only_skill=None):
    """Compute the deployment plan without touching anything."""
    actions, extras, problems = [], [], []
    declared = {rt: set() for rt in roots}

    for entry in manifest['skills']:
        name = entry['skill']
        if only_skill and name != only_skill:
            continue
        if entry['mode'] not in DEPLOYABLE_MODES:
            continue
        if entry.get('status') != 'active':
            continue
        if name in NEVER_DEPLOY:
            problems.append({'skill': name, 'issue': 'name collides with a reserved directory'})
            continue

        src = os.path.join(REPO, entry.get('source') or name)
        if not os.path.isdir(src):
            problems.append({'skill': name, 'issue': f'declared source missing: {src}'})
            continue

        for rt in entry.get('targets', []):
            if rt not in roots:
                continue
            declared[rt].add(name)
            dst = os.path.join(roots[rt], name)
            for rel in walk(src):
                s = os.path.join(src, rel)
                d = os.path.join(dst, rel)
                if not os.path.exists(d):
                    actions.append({'action': 'CREATE', 'runtime': rt, 'skill': name,
                                    'path': rel, 'src': s, 'dst': d})
                elif sha(s) != sha(d):
                    actions.append({'action': 'UPDATE', 'runtime': rt, 'skill': name,
                                    'path': rel, 'src': s, 'dst': d})
            # files present in the runtime but not in source -> report only
            if os.path.isdir(dst):
                for rel in set(walk(dst)) - set(walk(src)):
                    extras.append({'runtime': rt, 'skill': name, 'path': rel,
                                   'kind': 'file-not-in-source'})

    # whole skills present at runtime but never declared -> report only, never delete
    for rt, root in roots.items():
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            if name.startswith('.') or name in NEVER_DEPLOY:
                continue
            if not os.path.isdir(os.path.join(root, name)):
                continue
            if name not in declared[rt]:
                extras.append({'runtime': rt, 'skill': name, 'path': '',
                               'kind': 'skill-not-declared-active'})
    return actions, extras, problems


def apply(actions):
    done = 0
    for a in actions:
        os.makedirs(os.path.dirname(a['dst']), exist_ok=True)
        shutil.copyfile(a['src'], a['dst'])       # byte-exact, preserves line endings
        done += 1
    return done


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--check', action='store_true')
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--deploy', action='store_true')
    ap.add_argument('--runtime', choices=['claude', 'codex', 'all'], default='all')
    ap.add_argument('--skill')
    ap.add_argument('--json')
    ap.add_argument('--manifest', default=MANIFEST)
    ap.add_argument('--claude-root', default=os.path.expanduser('~/.claude/skills'))
    ap.add_argument('--codex-root', default=os.path.expanduser('~/.agents/skills'))
    args = ap.parse_args()

    roots = {}
    if args.runtime in ('claude', 'all'):
        roots['claude'] = args.claude_root.replace('\\', '/')
    if args.runtime in ('codex', 'all'):
        roots['codex'] = args.codex_root.replace('\\', '/')

    manifest = load_manifest(args.manifest)
    actions, extras, problems = plan(manifest, roots, args.skill)

    print(f'canonical source : {REPO}')
    for rt, r in roots.items():
        print(f'runtime {rt:<7} : {r}')
    print(f'manifest         : {args.manifest}')
    print()
    print(f'  to CREATE : {sum(1 for a in actions if a["action"] == "CREATE")}')
    print(f'  to UPDATE : {sum(1 for a in actions if a["action"] == "UPDATE")}')
    print(f'  EXTRA at runtime (never auto-removed): {len(extras)}')
    print(f'  PROBLEMS  : {len(problems)}')

    for p in problems[:10]:
        print(f'    ! {p["skill"]}: {p["issue"]}')
    for a in actions[:25]:
        print(f'    {a["action"]:<7} [{a["runtime"]}] {a["skill"]}/{a["path"]}')
    if len(actions) > 25:
        print(f'    ... and {len(actions) - 25} more')

    report = {'actions': actions, 'extras': extras, 'problems': problems,
              'counts': {'create': sum(1 for a in actions if a['action'] == 'CREATE'),
                         'update': sum(1 for a in actions if a['action'] == 'UPDATE'),
                         'extra': len(extras), 'problems': len(problems)}}
    if args.json:
        json.dump(report, open(args.json, 'w', encoding='utf-8'), indent=1)

    if problems:
        print('\nREFUSED: fix the problems above before deploying.')
        return 2
    if args.check:
        if actions:
            print('\nDRIFT DETECTED (--check)')
            return 1
        print('\nCLEAN: every declared skill matches the canonical source.')
        return 0
    if args.dry_run:
        print('\nDRY RUN: nothing was written.')
        return 0
    n = apply(actions)
    print(f'\nDEPLOYED: {n} file(s) written. No file was deleted.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

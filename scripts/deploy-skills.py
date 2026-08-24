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
import datetime
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
# Delivery is governed by mode and targets; exposure is a separate axis.
# `on-demand` means installed but not auto-loaded - all 105 skills switched off
# via skillOverrides are still present on disk - so withholding the file would
# make it impossible to load on demand at all. `hold` stays out: that flags
# unsettled content, which is a statement about the bytes, not about exposure.
DELIVERABLE_STATUS = {'active', 'on-demand'}


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
        if entry.get('status') not in DELIVERABLE_STATUS:
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


def _catalog_version():
    """Read catalog-version.json if present. Absent is fine - the deployer
    predates versioning and must keep working on trees that have none."""
    p = os.path.join(REPO, 'catalog-version.json')
    try:
        with open(p, encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _canonical_commit():
    """Best-effort source commit. Degrades to None rather than failing a deploy:
    the catalog must remain deployable from an export with no git metadata."""
    try:
        import subprocess
        r = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True,
                           text=True, timeout=10)
        head = r.stdout.strip()               # not `sha` - that shadows the hash helper
        if r.returncode == 0 and len(head) == 40:
            dirty = subprocess.run(['git', 'status', '--porcelain'], cwd=REPO,
                                   capture_output=True, text=True, timeout=10).stdout.strip()
            return head, bool(dirty)
    except Exception:
        pass
    return None, None


def write_deployment_state(roots, actions, manifest_path, when):
    """Record what each runtime was deployed FROM.

    Commit identity alone is insufficient: a dirty tree, an export, or a
    hand-edit all share a commit SHA while shipping different bytes. Pairing the
    commit with the manifest's own SHA-256 and the catalog version makes the
    deployed runtime attributable to an actual catalog state.

    Only ever called on --deploy, and never fabricates history for a runtime
    this invocation did not write.
    """
    ver = _catalog_version()
    commit, dirty = _canonical_commit()   # not `sha` - that shadows the hash helper
    mhash = sha(manifest_path)
    written = []
    for rt, root in roots.items():
        if not os.path.isdir(root):
            continue
        state = {
            'deployment_state_schema_version': ver.get('deployment_state_schema_version', 1),
            'catalog_version': ver.get('catalog_version'),
            'canonical_repo': ver.get('canonical_repo'),
            'canonical_commit': commit,
            'canonical_tree_dirty': dirty,
            'manifest_path': os.path.relpath(manifest_path, REPO).replace('\\', '/'),
            'manifest_sha256': mhash,
            'runtime': rt,
            'runtime_root': root,
            'deployed_at': when,
            'deployed_by': 'scripts/deploy-skills.py',
            'files_written_this_run': sum(1 for a in actions if a['runtime'] == rt),
            'note': ('Generated by the deployer. Attribution is catalog_version + '
                     'canonical_commit + manifest_sha256; a commit alone does not '
                     'identify the bytes. Do not hand-edit.'),
        }
        p = os.path.join(root, '.deployment-state.json')
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump(state, fh, indent=1)
        written.append(rt)
    return written


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
    stamped = write_deployment_state(
        roots, actions, args.manifest,
        datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat())
    if stamped:
        ver = _catalog_version().get('catalog_version') or 'unversioned'
        print(f'STATE: .deployment-state.json written for {", ".join(stamped)} '
              f'(catalog {ver})')
    return 0


if __name__ == '__main__':
    sys.exit(main())

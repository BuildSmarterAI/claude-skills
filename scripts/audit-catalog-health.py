#!/usr/bin/env python3
"""Catalog health audit: does the policy record still describe the world?

`check-skill-consistency.py` is the CI gate. It is repository-only by contract -
no network, no runtime stores - so it can prove the catalog is *internally*
correct and nothing more. This audit asks the complementary question:

    the record says X. is X still true?

Three ways the record silently stops describing reality:

1. **Runtime drift.** `~/.claude/skills` is a deployment *output* governed by
   `manifests/skills.json`, but third-party installers write into it directly.
   Observed 2026-08-21: an installer overwrote `code-review/SKILL.md` mid-session
   and `deploy-skills.py --check` reported an UPDATE no session had caused. This
   audit reports drift **with the side attributed**, because "canonical changed"
   and "something else overwrote the runtime" need opposite responses.

2. **Retention record versus remote.** A branch named in `manifests/retention.json`
   can be deleted or moved. A missing PERMANENT-PRESERVATION branch is not
   routine cleanup - it is irreversible loss of the only copy.

3. **Expiry.** A retention window passes with nobody noticing.

Severity
--------
**violations** block (exit 1). **notices** inform (exit 0). "Due for retirement"
is a notice: filing it as a violation would fail every build from the expiry date
onward for a condition no commit caused and no commit can fix.

Skips are loud
--------------
A CI runner has no runtime stores, so the drift section cannot run there. A
*silent* skip yields exit 0 that is byte-identical to a run which checked
everything - the commonest false green. Every section that cannot run records
itself in `skipped` with a reason, and that reason is printed and carried into
`--json`.

Usage
-----
    python scripts/audit-catalog-health.py
    python scripts/audit-catalog-health.py --json
    python scripts/audit-catalog-health.py --no-runtime   # repo/remote only

Exit codes: 0 healthy (notices allowed), 1 violations, 2 refused.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

REPO_DEFAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RETENTION_FILE = os.path.join('manifests', 'retention.json')
MANIFEST_FILE = os.path.join('manifests', 'skills.json')

DEPLOYABLE_MODES = {'IDENTICAL', 'CLAUDE_ONLY', 'CODEX_ONLY'}
# Classes whose disappearance is loss, not cleanup.
PRESERVATION_CLASSES = {'PERMANENT-PRESERVATION'}

DEFAULT_RUNTIME_ROOTS = {
    'claude': os.path.join(os.path.expanduser('~'), '.claude', 'skills'),
    'codex': os.path.join(os.path.expanduser('~'), '.agents', 'skills'),
}

LEADING_DATE = re.compile(r'^\s*(\d{4})-(\d{2})-(\d{2})')


class Report:
    def __init__(self):
        self.violations = defaultdict(list)
        self.notices = defaultdict(list)
        self.counts = defaultdict(int)
        self.skipped = {}

    def add(self, kind, offender):
        self.violations[kind].append(offender)

    def notice(self, kind, offender):
        self.notices[kind].append(offender)

    def skip(self, section, why):
        self.skipped[section] = why

    @property
    def ok(self):
        return not self.violations

    def as_dict(self):
        return {
            'ok': self.ok,
            'counts': dict(self.counts),
            'skipped': dict(self.skipped),
            'violations': {k: sorted(v) for k, v in sorted(self.violations.items())},
            'notices': {k: sorted(v) for k, v in sorted(self.notices.items())},
        }


def sha256_file(path):
    with open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _git(repo, *args):
    r = subprocess.run(('git',) + args, cwd=repo, capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    return r.stdout if r.returncode == 0 else ''


def remote_refs_from_git(repo):
    """{branch_name: sha} for origin's branches, from local remote-tracking refs."""
    out = {}
    text = _git(repo, 'for-each-ref', '--format=%(refname:short) %(objectname)',
                'refs/remotes/origin')
    for line in text.split('\n'):
        parts = line.split()
        if len(parts) == 2 and parts[0] != 'origin/HEAD':
            out[parts[0][len('origin/'):]] = parts[1]
    return out


def canonical_mtimes_from_git(repo):
    """{skill_dir: last commit unix time} in ONE git pass.

    Commit time, not file mtime: a fresh clone rewrites every file mtime to
    checkout time, which would make canonical look newer than every runtime copy
    and attribute all drift to "undeployed".
    """
    text = _git(repo, 'log', '--format=%ct', '--name-only', '--no-renames')
    out, ts = {}, None
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.isdigit():
            ts = int(line)
            continue
        top = line.split('/', 1)[0]
        if ts is not None and top not in out:
            out[top] = ts
    return out


def parse_expiry(value):
    """('indefinite'|'expired'|date|None) from a retention string."""
    text = str(value or '').strip()
    if not text:
        return None
    low = text.lower()
    if low.startswith('indefinite'):
        return 'indefinite'
    if low.startswith('expired'):
        return 'expired'
    m = LEADING_DATE.match(text)
    if m:
        try:
            return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    return None


def dirty_top_dirs(repo):
    """Top-level directories with uncommitted changes, in one git call.

    Attribution otherwise compares two different snapshots: `expected_sha256` is
    read from the WORKING-TREE manifest while timestamps come from COMMITTED
    history. On any machine mid-edit that gap makes canonical look old, so the
    audit blames an external writer for the developer's own change - the exact
    misdiagnosis this attribution exists to prevent, inverted.
    """
    out = set()
    for line in _git(repo, 'status', '--porcelain').split('\n'):
        path = line[3:].strip() if len(line) > 3 else ''
        if ' -> ' in path:
            path = path.split(' -> ', 1)[1]
        path = path.strip('"')
        if path:
            out.add(path.split('/', 1)[0])
    return out


def _audit_runtime(rep, root, entries, runtime_roots, canonical_mtimes):
    configured = dict(runtime_roots or {})
    present = {t: p for t, p in configured.items() if os.path.isdir(p)}
    if not present:
        named = ', '.join(sorted(configured.values())) or '<none configured>'
        rep.skip('runtime', f'no runtime store present ({named}) - '
                            'expected on a CI runner; drift is a local question')
        return

    # One present root must not mask a wholly unchecked second runtime. Without
    # this, entries targeting the absent root fall through silently and the
    # output reads as complete while half the catalog went unverified.
    for target, path in sorted(configured.items()):
        if target not in present:
            rep.skip(f'runtime:{target}',
                     f'{path} is absent, so no {target} target was verified')

    if canonical_mtimes is None:
        canonical_mtimes = canonical_mtimes_from_git(root)
    dirty = dirty_top_dirs(root)

    for e in entries:
        if e.get('mode') not in DEPLOYABLE_MODES:
            continue
        name = e.get('skill')
        expected = e.get('expected_sha256')
        if not name or not expected:
            continue
        src_dir = e.get('source') or name
        for target in (e.get('targets') or []):
            rt_root = present.get(target)
            if not rt_root:
                # Disclosed at section level above; counted so the anti-vacuity
                # signal cannot overstate what was actually verified.
                rep.counts['runtime_targets_unchecked'] += 1
                continue
            rt_file = os.path.join(rt_root, name, 'SKILL.md')
            if not os.path.isfile(rt_file):
                # Exposure and deployment are independent. `status` controls
                # what a runtime LOADS; mode and targets control what it
                # RECEIVES. A deployable entry targeting a runtime that is
                # present on disk must therefore exist there whatever its
                # status - `on-demand` means installed but not auto-loaded, not
                # withheld. Settled 2026-08-24; previously split by severity
                # because two documents disagreed and the catalog had a single
                # on-demand entry to test them against.
                rep.add('runtime_missing',
                        f'[{target}] {name}: not deployed (status='
                        f'{e.get("status")!r}; exposure does not affect delivery)')
                continue

            rep.counts['runtime_files_compared'] += 1
            actual = sha256_file(rt_file)
            if actual == expected:
                continue

            # Attribute the side. This is what turns a recurring, apparently
            # new finding into a known one.
            rt_mtime = os.path.getmtime(rt_file)
            canon_mtime = canonical_mtimes.get(src_dir)
            if src_dir in dirty:
                # Canonical has uncommitted changes for this skill, so the
                # committed timestamp understates it. This is our own edit.
                side = ('UNDEPLOYED canonical change - canonical has uncommitted '
                        'changes for this skill, so the runtime is behind')
            elif canon_mtime is None:
                rep.skip('attribution',
                         'no canonical timestamp available (no git history for '
                         'these paths), so drift could not be attributed to a side')
                side = 'unknown side (no canonical timestamp available)'
            elif rt_mtime > canon_mtime:
                side = ('EXTERNAL writer - the runtime copy is newer than the '
                        'canonical commit, so something outside this repo wrote it')
            else:
                side = ('UNDEPLOYED canonical change - canonical is newer, so this '
                        'repo changed and the runtime has not been updated')
            rep.add('runtime_drift', f'[{target}] {name}: {side}')


def _audit_retention(rep, root, remote_refs, today):
    rpath = os.path.join(root, RETENTION_FILE)
    if not os.path.isfile(rpath):
        rep.skip('retention', f'{RETENTION_FILE} not present in this tree')
        return
    try:
        with open(rpath, encoding='utf-8') as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        # A corrupt policy record is a finding, never "nothing to check".
        rep.add('retention_unreadable', f'{RETENTION_FILE}: {exc}')
        return

    branches = data.get('branches')
    if not isinstance(branches, dict):
        rep.add('retention_unreadable', f'{RETENTION_FILE}: missing branches map')
        return

    # Auto-discovered refs are only believed when discovery actually found
    # something. An empty result means we could not look - `actions/checkout`
    # fetches no remote branch refs by default - and reporting that as "every
    # branch is gone" would fire the preservation alarm on pure noise. An
    # explicitly supplied mapping is always trusted, empty or not.
    existence_known = True
    if remote_refs is None:
        remote_refs = remote_refs_from_git(root)
        if not remote_refs:
            existence_known = False
            rep.skip('retention_remote',
                     'could not enumerate origin refs (no remote-tracking refs '
                     'present); branch existence and tip checks were not run')

    for name, meta in sorted(branches.items()):
        if not isinstance(meta, dict):
            rep.add('retention_unreadable', f'{name}: not an object')
            continue
        rep.counts['retention_branches_checked'] += 1
        cls = meta.get('class')

        if existence_known:
            if name not in remote_refs:
                if cls in PRESERVATION_CLASSES:
                    rep.add('preservation_branch_missing',
                            f'{name}: class {cls} promises indefinite retention, '
                            f'but the branch is absent from origin')
                else:
                    rep.add('retention_branch_missing',
                            f'{name}: recorded as {cls}, absent from origin')
            else:
                recorded_tip = (meta.get('tip') or '').strip()
                actual_tip = remote_refs[name]
                if not recorded_tip:
                    # The count is an anti-vacuity signal; an entry with no tip
                    # had nothing compared and must not inflate it.
                    rep.notice('retention_incomplete',
                               f'{name}: no tip recorded, so nothing was verified '
                               f'against origin')
                else:
                    rep.counts['retention_tips_verified'] += 1
                    if recorded_tip != actual_tip:
                        rep.add('retention_tip_moved',
                                f'{name}: record says {recorded_tip[:8]}, '
                                f'origin has {actual_tip[:8]}')

        raw_retention = str(meta.get('retention') or '').strip()
        expiry = parse_expiry(raw_retention)
        if not raw_retention:
            rep.notice('retention_incomplete',
                       f'{name}: no retention window recorded')
        elif expiry is None:
            # An unreadable expiry must not be indistinguishable from "no expiry
            # configured" - silence there means a window can pass unnoticed.
            rep.notice('retention_unparseable_expiry',
                       f'{name}: cannot read a date from {raw_retention!r}')
        if expiry == 'expired':
            rep.notice('retention_expired', f'{name}: recorded as already expired')
        elif isinstance(expiry, datetime.date) and today is not None \
                and today >= expiry:
            rep.notice('retention_expired',
                       f'{name}: retention window ended {expiry.isoformat()}')


def audit(repo, runtime_roots=None, today=None, remote_refs=None,
          canonical_mtimes=None):
    """Audit the catalog against live reality. Report only - never repairs."""
    rep = Report()

    try:
        with open(os.path.join(repo, MANIFEST_FILE), encoding='utf-8') as fh:
            entries = json.load(fh)['skills']
    except (OSError, ValueError, KeyError) as exc:
        rep.add('manifest_unreadable', f'{MANIFEST_FILE}: {exc}')
        return rep

    rep.counts['manifest_entries'] = len(entries)
    _audit_runtime(rep, repo, entries, runtime_roots, canonical_mtimes)
    _audit_retention(rep, repo, remote_refs, today)
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--no-runtime', action='store_true',
                    help='skip the runtime drift section entirely')
    ap.add_argument('--claude-root', default=DEFAULT_RUNTIME_ROOTS['claude'])
    ap.add_argument('--codex-root', default=DEFAULT_RUNTIME_ROOTS['codex'])
    args = ap.parse_args(argv)

    roots = {} if args.no_runtime else {'claude': args.claude_root,
                                        'codex': args.codex_root}
    rep = audit(args.repo, runtime_roots=roots, today=datetime.date.today())

    if args.json:
        json.dump(rep.as_dict(), sys.stdout, indent=1, sort_keys=True)
        sys.stdout.write('\n')
    else:
        print(f'Catalog health: {"PASS" if rep.ok else "FAIL"}')
        print(f'  manifest entries        : {rep.counts["manifest_entries"]}')
        print(f'  runtime files compared  : {rep.counts["runtime_files_compared"]}')
        print(f'  retention branches      : {rep.counts["retention_branches_checked"]}')
        for section, why in sorted(rep.skipped.items()):
            print(f'  SKIPPED [{section}]: {why}')
        for kind, items in sorted(rep.violations.items()):
            print(f'\n{kind}:  [{len(items)}]')
            for o in sorted(items)[:25]:
                print(f'  - {o}')
            if len(items) > 25:
                print(f'  ... {len(items) - 25} more')
        for kind, items in sorted(rep.notices.items()):
            print(f'\nnotice {kind}:  [{len(items)}]')
            for o in sorted(items)[:25]:
                print(f'  - {o}')

    if 'manifest_unreadable' in rep.violations:
        return 2
    return 0 if rep.ok else 1


if __name__ == '__main__':
    sys.exit(main())

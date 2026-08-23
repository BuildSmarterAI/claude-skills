#!/usr/bin/env python3
"""Prove a branch's content is preserved on main - by BLOB, not by ancestry.

Run this immediately before retiring a branch. It answers one question:

    if this branch were deleted right now, would any content be lost?

Why not `git branch --merged`
-----------------------------
Every pull request in this repository is squash-merged. A squash merge copies
the TREE onto main and discards the commits, so the branch is not an ancestor of
main even though every byte it contributed is preserved. `git branch --merged`
and `git merge-base --is-ancestor` are therefore wrong here - measured wrong for
4 of the 5 branches inventoried in docs/consolidation/branch-retention-inventory.md.

The method
----------
Collect every blob reachable from the branch, across all of its own commits, and
test membership against every blob reachable from the base ref. A branch-only
blob matters **only if a path in the branch tip tree still carries it**;
otherwise it is an intermediate state the branch itself superseded before merge,
and deleting the branch loses nothing.

Guarantees
----------
- **Read-only.** Every git invocation is checked against an allow-list, so this
  script is structurally incapable of moving a ref. It runs next to a
  destructive action and must never become part of one.
- **Never vacuous.** With nothing to check it REFUSES (exit 2) rather than
  reporting success. A run that inspected zero branches has made no claim.
- **Recomputed, never recalled.** Containment is measured against the base ref
  as it is right now. A stored measurement goes stale the moment main moves.

Usage
-----
    python scripts/verify-branch-containment.py --branch NAME [--branch NAME ...]
    python scripts/verify-branch-containment.py            # every deletable
                                                           # branch in retention.json
    python scripts/verify-branch-containment.py --json

Severity
--------
**violation** (exit 1): a tip path exists nowhere in the base ref, so deleting
the branch destroys the only copy. This is the invariant.

**notice** (exit 0): a tip path still exists on the base ref carrying different
content, so deleting drops an older revision. Nearly every squash-merged branch
that was revised in place produces these; blocking on them would fire the gate on
every legitimate retirement until people stopped reading it. Review before
deleting - the retirement checklist in docs/consolidation/RETENTION.md is where
that acknowledgement belongs.

Exit codes: 0 nothing would be orphaned (notices allowed), 1 content would be
orphaned, 2 refused.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict

REPO_DEFAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RETENTION_FILE = os.path.join('manifests', 'retention.json')

# Read-only porcelain/plumbing only. `fetch` and `checkout` are absent
# deliberately: both move refs or the working tree.
READONLY_GIT = frozenset({
    'rev-list', 'ls-tree', 'rev-parse', 'cat-file', 'for-each-ref', 'show-ref',
})


class NotReadOnly(Exception):
    """A mutating git subcommand was attempted. This script never mutates."""


class GitError(Exception):
    """A read-only git invocation failed (usually an unresolvable ref)."""


def git(repo, *args, check=True):
    """Run one read-only git subcommand.

    The allow-list is the guarantee, not a convention: a future edit that reaches
    for `git branch -D` raises instead of deleting.
    """
    if not args or args[0] not in READONLY_GIT:
        raise NotReadOnly(
            f'refusing non-read-only git subcommand: {args[0] if args else "<none>"}')
    r = subprocess.run(('git',) + args, cwd=repo, capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    if check and r.returncode != 0:
        raise GitError(f'git {" ".join(args)}: {r.stderr.strip()}')
    return r.stdout


def resolve(repo, ref):
    """Return the commit SHA for a ref, or None if it does not resolve."""
    try:
        out = git(repo, 'rev-parse', '--verify', '--quiet', f'{ref}^{{commit}}')
    except GitError:
        return None
    return out.strip() or None


def _blobs_of_tree(repo, rev):
    """{path: blob_sha} for one revision's full tree."""
    out = {}
    for line in git(repo, 'ls-tree', '-r', rev).split('\n'):
        if not line.strip():
            continue
        meta, path = line.split('\t', 1)
        parts = meta.split()
        if len(parts) >= 3 and parts[1] == 'blob':
            out[path] = parts[2]
    return out


def history_index(repo, ref):
    """(every blob reachable from ref, every path ever seen, commits walked).

    Walks each commit's full tree rather than its diff: a blob introduced and
    later overwritten must still count as present in history, which is exactly
    what makes a squashed merge detectable. Paths are collected alongside so a
    missing blob can be classified as superseded rather than orphaned.
    """
    blobs, paths = set(), set()
    revs = [r for r in git(repo, 'rev-list', ref).split('\n') if r.strip()]
    for rev in revs:
        tree = _blobs_of_tree(repo, rev)
        blobs.update(tree.values())
        paths.update(tree.keys())
    return blobs, paths, len(revs)


def blobs_in_history(repo, ref):
    """(set of every blob reachable from ref, number of commits walked)."""
    blobs, _paths, n = history_index(repo, ref)
    return blobs, n


def blobs_at_tip(repo, ref):
    """{path: blob_sha} for the branch tip tree only."""
    return _blobs_of_tree(repo, ref)


def containment(repo, branch, base='origin/main', base_index=None):
    """Measure whether `branch` content is preserved in `base` history."""
    if base_index is None:
        base_index = history_index(repo, base)[:2]
    base_blobs, base_paths = base_index

    branch_blobs, _branch_paths, commits = history_index(repo, branch)
    tree = blobs_at_tip(repo, branch)

    missing = branch_blobs - base_blobs
    # THE RULE: a branch-only blob matters only if a tip path still carries it.
    missing_paths = sorted(p for p, sha in tree.items() if sha in missing)

    # Severity split. This adds evidence; it never downgrades a violation.
    #
    # BOTH categories lose unique bytes - every path here carries a blob that
    # exists nowhere in base history. The split says only whether the PATH
    # survives:
    #   divergent -> base has this path, carrying different content
    #   orphan    -> base has no such path at all
    # "divergent" deliberately avoids the word "superseded", which
    # branch-retention-inventory.md already uses for a different thing: an
    # intermediate state a branch overwrote *itself* before merge. Those never
    # reach this list, because they hold no tip path.
    divergent = [p for p in missing_paths if p in base_paths]
    orphan = [p for p in missing_paths if p not in base_paths]

    return {
        'branch': branch,
        'base': base,
        'commits': commits,
        'blobs': len(branch_blobs),
        'files': len(tree),
        'missing_blobs': len(missing),
        'missing_tip_paths': len(missing_paths),
        'missing_paths': missing_paths,
        'divergent_paths': divergent,
        'orphan_paths': orphan,
        'contained': not missing_paths,
    }


class Report:
    """Violations block (exit 1). Notices inform (exit 0).

    The split is the difference between "this deletion destroys the only copy of
    something" and "this deletion drops an older revision of a file main still
    carries". The first is the invariant; the second happens on essentially every
    squash-merged branch, and treating it as a defect would make the gate fire on
    every legitimate retirement until people stopped reading it.
    """

    def __init__(self):
        self.violations = defaultdict(list)
        self.notices = defaultdict(list)
        self.counts = defaultdict(int)
        self.results = []
        self.refused = False

    def add(self, kind, offender):
        self.violations[kind].append(offender)

    def notice(self, kind, offender):
        self.notices[kind].append(offender)

    @property
    def ok(self):
        return not self.violations and not self.refused

    def as_dict(self):
        return {
            'ok': self.ok,
            'refused': self.refused,
            'counts': dict(self.counts),
            'violations': {k: sorted(v) for k, v in sorted(self.violations.items())},
            'notices': {k: sorted(v) for k, v in sorted(self.notices.items())},
            'results': self.results,
        }


def deletable_branches(repo):
    """Branches retention.json marks deletable. Absent file -> empty list."""
    path = os.path.join(repo, RETENTION_FILE)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return []
    return sorted(name for name, meta in (data.get('branches') or {}).items()
                  if isinstance(meta, dict) and meta.get('deletable') is True)


def verify(repo, branches=None, base='origin/main', ref_prefix=None):
    """Verify every named branch is contained in `base`.

    `ref_prefix` is prepended to every name before resolving. It defaults to
    `origin/` whenever the names come from retention.json, because that record
    describes REMOTE branches: its `tip` values are origin tips, and a bare name
    would otherwise resolve to a same-named local branch that may lag origin -
    measuring containment against a tree nobody asked about. Explicitly supplied
    `--branch` names are used verbatim.
    """
    rep = Report()

    if branches is None:
        branches = deletable_branches(repo)
        rep.counts['source_retention_json'] = 1
        if ref_prefix is None:
            ref_prefix = 'origin/'
    ref_prefix = ref_prefix or ''

    if not branches:
        # Not a pass. Nothing was inspected, so nothing has been established.
        rep.refused = True
        rep.add('nothing_to_check',
                'no branches supplied and none marked deletable in retention.json')
        return rep

    base_sha = resolve(repo, base)
    if base_sha is None:
        rep.refused = True
        rep.add('unresolvable_ref', f'base {base}')
        return rep
    rep.counts['base_commits'] = 0

    base_blobs, base_paths, base_commits = history_index(repo, base)
    rep.counts['base_commits'] = base_commits
    rep.counts['base_blobs'] = len(base_blobs)

    for name in branches:
        ref = f'{ref_prefix}{name}'
        if resolve(repo, ref) is None:
            # A ref that does not resolve must never be reported as safe.
            rep.refused = True
            rep.add('unresolvable_ref', ref)
            continue

        c = containment(repo, ref, base=base, base_index=(base_blobs, base_paths))
        rep.results.append(c)
        rep.counts['branches_checked'] += 1
        rep.counts['blobs_inspected'] += c['blobs']
        rep.counts['files_inspected'] += c['files']
        rep.counts['orphan_paths'] += len(c['orphan_paths'])
        rep.counts['divergent_paths'] += len(c['divergent_paths'])

        # Only-copy loss blocks. Older-version loss informs.
        if c['orphan_paths']:
            rep.add('would_orphan_content',
                    f'{ref}: {len(c["orphan_paths"])} path(s) exist nowhere in '
                    f'{base} - deleting this branch destroys the only copy')
        if c['divergent_paths']:
            rep.notice('would_lose_older_version',
                       f'{ref}: {len(c["divergent_paths"])} path(s) still exist on '
                       f'{base} with different content - review before deleting')

    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--branch', action='append', dest='branches',
                    help='branch to verify (repeatable); default: retention.json')
    ap.add_argument('--base', default='origin/main')
    ap.add_argument('--json', action='store_true')
    args = ap.parse_args(argv)

    rep = verify(args.repo, branches=args.branches, base=args.base)

    if args.json:
        json.dump(rep.as_dict(), sys.stdout, indent=1, sort_keys=True)
        sys.stdout.write('\n')
    elif rep.refused:
        print('Branch containment: REFUSED')
        for kind, offenders in sorted(rep.violations.items()):
            for o in sorted(offenders):
                print(f'  {kind}: {o}')
        print('  (no claim has been made about any branch)')
    else:
        status = 'PASS' if rep.ok else 'FAIL'
        print(f'Branch containment: {status}')
        print(f'  base                 : {rep.counts["base_commits"]} commits, '
              f'{rep.counts["base_blobs"]} blobs')
        print(f'  branches checked     : {rep.counts["branches_checked"]}')
        print(f'  blobs inspected      : {rep.counts["blobs_inspected"]}')
        for c in rep.results:
            mark = 'contained' if c['contained'] else 'NOT CONTAINED'
            print(f'  - {c["branch"]}: {mark} '
                  f'({c["missing_blobs"]} blob(s) absent, '
                  f'{c["missing_tip_paths"]} on live tip paths '
                  f'= {len(c["orphan_paths"])} orphaned, '
                  f'{len(c["divergent_paths"])} divergent)')
            for p in c['orphan_paths'][:10]:
                print(f'      orphaned  (base has no such path): {p}')
            if len(c['orphan_paths']) > 10:
                print(f'      ... {len(c["orphan_paths"]) - 10} more orphaned')
            for p in c['divergent_paths'][:5]:
                print(f'      divergent (base path differs)    : {p}')
            if len(c['divergent_paths']) > 5:
                print(f'      ... {len(c["divergent_paths"]) - 5} more divergent')
        for kind, items in sorted(rep.violations.items()):
            print(f'\n{kind}:  [{len(items)}]')
            for o in sorted(items):
                print(f'  - {o}')
        for kind, items in sorted(rep.notices.items()):
            print(f'\nnotice {kind}:  [{len(items)}]')
            for o in sorted(items):
                print(f'  - {o}')
        if rep.violations or rep.notices:
            print('\n  Both categories lose unique bytes. "divergent" means only that')
            print('  the path still exists on the base ref with other content.')

    if rep.refused:
        return 2
    return 0 if rep.ok else 1


if __name__ == '__main__':
    sys.exit(main())

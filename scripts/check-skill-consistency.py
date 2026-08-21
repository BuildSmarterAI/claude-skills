#!/usr/bin/env python3
"""Repository-only canonical skill consistency checker.

This answers ONE question: **is the canonical repository internally correct?**
It reads nothing outside the repo - no `~/.claude/skills`, no `~/.agents/skills`,
no network, no secrets, no environment state - so it runs identically on a clean
CI runner and on a developer machine.

    canonical files -> check-skill-consistency.py -> GitHub Actions gate
    canonical files -> deploy-skills.py --check   -> THIS MACHINE's runtime parity

Those are different questions. `deploy-skills.py --check` compares canonical
against the live runtime stores; on a runner that has no runtime stores it
reports every declared skill as a false CREATE (measured: 246). It must never
run in CI. See docs/consolidation/README.md.

Usage
-----
    python scripts/check-skill-consistency.py            # human-readable
    python scripts/check-skill-consistency.py --json     # machine-readable
    python scripts/check-skill-consistency.py --repo DIR # check another tree

Exit codes: 0 all invariants hold, 1 violations found, 2 refused (unreadable
manifest - the checker cannot make a claim either way).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict

REPO_DEFAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directories that are never skills. `pre-consolidation` is the 1,214-file
# preservation archive: historical rollback evidence, not deploy input, and
# deliberately not validated or hashed on every run.
NOT_SKILLS = {'pre-consolidation', 'scripts', 'docs', 'manifests', 'tests',
              '.git', '.github', '.venv', 'node_modules', '__pycache__'}

VALID_MODES = {'IDENTICAL', 'CLAUDE_ONLY', 'CODEX_ONLY', 'ADAPTER',
               'VENDORED', 'REPO_LOCAL', 'DISABLED'}
VALID_STATUS = {'active', 'on-demand', 'repo-local', 'hold'}
VALID_TARGETS = {'claude', 'codex'}

# Modes whose bytes this repository deploys, so it must own a verified copy.
DEPLOYABLE_MODES = {'IDENTICAL', 'CLAUDE_ONLY', 'CODEX_ONLY'}
# Modes that are deliberately not uniform across runtimes and must say why.
DIVERGENT_MODES = {'CLAUDE_ONLY', 'CODEX_ONLY', 'ADAPTER'}

# Ownership placeholders that are not owners. D4.2 removed 20 entries reading
# "belongs to a product repo" while no repository contained any of them; this
# rejects the phrasing so it cannot come back.
PLACEHOLDER = re.compile(r'belongs to|product repo|a repo|tbd|unknown|todo|n/?a', re.I)

# YAML permits `name: thing`, `name: "thing"` and `name: 'thing'` - 32 canonical
# skills use the quoted form. The quotes are syntax, not part of the identifier.
FRONTMATTER_NAME = re.compile(r'''(?m)^name:\s*(?:"([^"]+)"|'([^']+)'|(\S+))\s*$''')
FRONTMATTER_DESC = re.compile(r'(?m)^description:\s*(\S)')


class Report:
    def __init__(self):
        self.violations = defaultdict(list)
        self.counts = defaultdict(int)

    def add(self, kind, offender):
        self.violations[kind].append(offender)

    @property
    def ok(self):
        return not self.violations

    def as_dict(self):
        return {'ok': self.ok,
                'counts': dict(self.counts),
                'violations': {k: sorted(v) for k, v in sorted(self.violations.items())}}


def sha256_file(path):
    """Hash raw bytes. Line endings are part of the identity - the repo pins
    `* -text` in .gitattributes precisely so CRLF never silently rewrites them."""
    with open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def read_frontmatter(path):
    """Return (ok, name, has_description). Deliberately a narrow reader rather
    than a YAML dependency: stdlib only, and frontmatter here is flat."""
    try:
        with open(path, encoding='utf-8', errors='replace') as fh:
            text = fh.read(8192).replace('\r\n', '\n')
    except OSError:
        return False, None, False
    if not text.startswith('---'):
        return False, None, False
    end = text.find('\n---', 3)
    if end == -1:
        return False, None, False
    block = text[3:end]
    m = FRONTMATTER_NAME.search(block)
    name = next((g for g in m.groups() if g), None) if m else None
    return True, name, bool(FRONTMATTER_DESC.search(block))


def canonical_skill_dirs(root):
    out = []
    for name in sorted(os.listdir(root)):
        if name.startswith('.') or name in NOT_SKILLS:
            continue
        d = os.path.join(root, name)
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'SKILL.md')):
            out.append(name)
    return out


def check_repo(root):
    """Evaluate every invariant against a canonical repository tree."""
    rep = Report()
    mpath = os.path.join(root, 'manifests', 'skills.json')
    try:
        with open(mpath, encoding='utf-8') as fh:
            manifest = json.load(fh)
        entries = manifest['skills']
    except (OSError, ValueError, KeyError) as exc:
        rep.add('manifest_unreadable', f'{mpath}: {exc}')
        return rep

    # --- A. manifest validity -------------------------------------------------
    if not entries:
        rep.add('empty_manifest', mpath)
        return rep

    seen = set()
    declared = set()
    for e in entries:
        name = e.get('skill')
        if not name:
            rep.add('missing_required_field', f'<unnamed>: skill')
            continue
        if name in seen:
            rep.add('duplicate_skill_id', name)
        seen.add(name)
        declared.add(name)
        rep.counts['skills'] += 1

        for field in ('mode', 'status'):
            if not e.get(field):
                rep.add('missing_required_field', f'{name}: {field}')

        mode, status = e.get('mode'), e.get('status')
        if mode and mode not in VALID_MODES:
            rep.add('invalid_mode', f'{name}: {mode}')
        if status and status not in VALID_STATUS:
            rep.add('invalid_status', f'{name}: {status}')
        for t in (e.get('targets') or []):
            if t not in VALID_TARGETS:
                rep.add('invalid_target', f'{name}: {t}')

        # --- E. state contradictions -----------------------------------------
        # An entry cannot be exposed and deploy nowhere. D4 found 11 of these;
        # each would have been miscounted as active by the activation step.
        if status == 'active' and mode == 'DISABLED':
            rep.add('active_disabled_conflict', name)
        if mode in DEPLOYABLE_MODES and not (e.get('targets') or []):
            rep.add('deployable_without_target', name)

        # --- F. holds ---------------------------------------------------------
        # Holds stay possible - adjudication is legitimate - but never silent.
        if status == 'hold' and not (e.get('hold_reason') or '').strip():
            rep.add('hold_without_reason', name)

        # --- G. intentional divergence ----------------------------------------
        if mode in DIVERGENT_MODES:
            why = (e.get('intentional_divergence') or e.get('divergence_reason') or '')
            if not why.strip():
                rep.add('undocumented_divergence', f'{name}: {mode}')
            else:
                rep.counts['divergences_documented'] += 1

        # --- D. ownership invariant -------------------------------------------
        is_repo_local = (e.get('ownership_class') == 'REPO-LOCAL'
                         or mode == 'REPO_LOCAL' or status == 'repo-local')
        if is_repo_local:
            owner_repo = (e.get('owner_repo') or '').strip()
            owner_path = (e.get('owner_path') or '').strip()
            if (not owner_repo or not owner_path
                    or PLACEHOLDER.search(owner_repo) or PLACEHOLDER.search(owner_path)):
                rep.add('repo_local_missing_owner', name)
            else:
                rep.counts['ownership_verified'] += 1

        # --- B. hash integrity + source presence ------------------------------
        src = os.path.join(root, e.get('source') or name, 'SKILL.md')
        present = os.path.isfile(src)
        must_have_source = mode in DEPLOYABLE_MODES or e.get('source_present_in_canonical')

        if must_have_source and not present:
            rep.add('missing_source', f'{name}: {os.path.relpath(src, root)}')
        elif present:
            expected = e.get('expected_sha256')
            if mode in DEPLOYABLE_MODES and not expected:
                rep.add('missing_expected_sha256', name)
            elif expected:
                if sha256_file(src) != expected:
                    rep.add('hash_mismatch', name)
                rep.counts['hashes_checked'] += 1

            # --- C. frontmatter validity --------------------------------------
            ok, fm_name, has_desc = read_frontmatter(src)
            rep.counts['frontmatter_checked'] += 1
            if not ok or not fm_name or not has_desc:
                missing = ('no frontmatter' if not ok
                           else 'no name' if not fm_name else 'no description')
                rep.add('frontmatter_invalid', f'{name}: {missing}')
            elif fm_name != name and not e.get('frontmatter_name_exception'):
                rep.add('frontmatter_name_mismatch', f'{name}: declares {fm_name}')

    # --- drift in the other direction: on disk but undeclared -----------------
    for name in canonical_skill_dirs(root):
        if name not in declared:
            rep.add('undeclared_canonical_skill', name)

    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--repo', default=REPO_DEFAULT)
    ap.add_argument('--json', action='store_true', help='machine-readable output')
    args = ap.parse_args(argv)

    rep = check_repo(args.repo)

    if args.json:
        json.dump(rep.as_dict(), sys.stdout, indent=1, sort_keys=True)
        sys.stdout.write('\n')
    elif rep.ok:
        print('Skill consistency: PASS')
        print(f'  skills                 : {rep.counts["skills"]}')
        print(f'  hashes checked         : {rep.counts["hashes_checked"]}')
        print(f'  frontmatter checked    : {rep.counts["frontmatter_checked"]}')
        print(f'  ownership verified     : {rep.counts["ownership_verified"]}')
        print(f'  divergences documented : {rep.counts["divergences_documented"]}')
        print('  ownership violations   : 0')
        print('  state violations       : 0')
        print('  undocumented divergences: 0')
    else:
        print('Skill consistency: FAIL')
        print(f'  (inspected {rep.counts["skills"]} skills, '
              f'{rep.counts["hashes_checked"]} hashes)')
        for kind, offenders in sorted(rep.violations.items()):
            print(f'\n{kind}:  [{len(offenders)}]')
            for o in sorted(offenders)[:25]:
                print(f'  - {o}')
            if len(offenders) > 25:
                print(f'  ... {len(offenders) - 25} more')

    if 'manifest_unreadable' in rep.violations:
        return 2
    return 0 if rep.ok else 1


if __name__ == '__main__':
    sys.exit(main())

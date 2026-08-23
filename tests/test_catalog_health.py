"""Tests for the branch-containment verifier and the catalog health audit.

Risk class: deterministic guardrail / evaluator (risk-based-tdd §2.16) and a
retention invariant (§2.14) -> test-first is mandatory, and §6 mutation testing
applies because these gates guard a destructive action (branch deletion).

Two failure modes dominate here and both look like success:

1. **Vacuous pass.** A gate that inspects zero branches exits 0 and is byte-for-byte
   indistinguishable from a gate that inspected everything and found nothing wrong.
   Every check below asserts a non-zero inspected count, and the verifier is
   required to REFUSE (exit 2) rather than pass when it has nothing to check.

2. **Ancestry mistaken for containment.** Every PR in this repository is
   squash-merged, which preserves the tree and discards the commits. `git branch
   --merged` and `merge-base --is-ancestor` therefore report merged branches as
   unmerged - measured wrong for 4 of 5 branches. `test_squash_merge_defeats_
   ancestry_but_not_blob_containment` builds that exact situation from scratch so
   the distinction is enforced, not merely documented.
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)


def _load(script_name, module_name):
    """Scripts are hyphenated (CLI convention), so load them by path."""
    target = os.path.join(_ROOT, 'scripts', script_name)
    spec = importlib.util.spec_from_file_location(module_name, target)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vbc = _load('verify-branch-containment.py', 'verify_branch_containment')


class GitRepo:
    """A throwaway git repository. Never touches the real working tree."""

    def __init__(self):
        self.path = tempfile.mkdtemp(prefix='containment-')
        self._run('init', '-b', 'main')
        # Determinism: autocrlf would rewrite bytes and change blob identity,
        # which is exactly what this verifier reasons about.
        self._run('config', 'core.autocrlf', 'false')
        self._run('config', 'user.email', 'test@example.invalid')
        self._run('config', 'user.name', 'Test')

    def _run(self, *args):
        r = subprocess.run(('git',) + args, cwd=self.path, capture_output=True,
                           text=True, encoding='utf-8', errors='replace')
        if r.returncode != 0:
            raise RuntimeError(f'git {" ".join(args)} failed: {r.stderr}')
        return r.stdout

    def write(self, relpath, content):
        full = os.path.join(self.path, relpath)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'wb') as fh:
            fh.write(content.encode('utf-8'))

    def commit(self, message, files):
        for relpath, content in files.items():
            self.write(relpath, content)
        self._run('add', '-A')
        self._run('commit', '-m', message)
        return self._run('rev-parse', 'HEAD').strip()

    def checkout(self, ref, create=False):
        self._run('checkout', *(('-b', ref) if create else (ref,)))

    def destroy(self):
        shutil.rmtree(self.path, ignore_errors=True)


class ContainmentTestCase(unittest.TestCase):
    def setUp(self):
        self.r = GitRepo()
        self.addCleanup(self.r.destroy)

    def is_ancestor(self, ref, of):
        """What `git branch --merged` would conclude."""
        p = subprocess.run(('git', 'merge-base', '--is-ancestor', ref, of),
                           cwd=self.r.path, capture_output=True)
        return p.returncode == 0


class TestSquashMergeSemantics(ContainmentTestCase):
    def test_squash_merge_defeats_ancestry_but_not_blob_containment(self):
        """The single most important behaviour in this file.

        A squash merge copies the TREE onto main and throws the commits away.
        Ancestry therefore says "not merged" while every byte is in fact
        preserved. Deleting on the ancestry answer would be safe here but
        refusing on it would block every legitimate retirement; the verifier
        must reason about blobs.
        """
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('feature work', {'feat.txt': 'FEATURE CONTENT\n'})
        self.r.checkout('main')
        # Squash-merge: same file content, brand new commit, no shared history.
        self.r.commit('squash: feature work', {'feat.txt': 'FEATURE CONTENT\n'})

        self.assertFalse(self.is_ancestor('feature', 'main'),
                         'precondition: ancestry must report feature as unmerged')

        c = vbc.containment(self.r.path, 'feature', base='main')
        self.assertTrue(c['contained'],
                        f'blob containment must see the content on main; got {c}')
        self.assertEqual(c['missing_tip_paths'], 0)

    def test_counts_are_non_vacuous(self):
        """A containment result that inspected nothing must not read as success."""
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('work', {'a.txt': 'a\n'})
        c = vbc.containment(self.r.path, 'feature', base='main')
        self.assertGreater(c['commits'], 0, 'must report commits inspected')
        self.assertGreater(c['blobs'], 0, 'must report blobs inspected')
        self.assertGreater(c['files'], 0, 'must report tip files inspected')


class TestUncontainedContent(ContainmentTestCase):
    def test_branch_with_unique_tip_content_is_not_contained(self):
        """The case that must block a deletion: content that exists nowhere else."""
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('unique', {'only-here.txt': 'IRREPLACEABLE\n'})

        c = vbc.containment(self.r.path, 'feature', base='main')
        self.assertFalse(c['contained'])
        self.assertGreater(c['missing_tip_paths'], 0)
        self.assertIn('only-here.txt', c['missing_paths'])

    def test_superseded_intermediate_blob_is_not_a_violation(self):
        """The tip-tree-path rule, stated exactly.

        A branch-only blob matters ONLY if a path in the branch tip tree still
        carries it. An intermediate state that the branch itself overwrote is
        not content loss - main has the final state, which is what shipped.
        Without this rule every multi-commit branch would look uncontained.
        """
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('v1', {'f.txt': 'VERSION ONE\n'})
        self.r.commit('v2', {'f.txt': 'VERSION TWO\n'})
        self.r.checkout('main')
        self.r.commit('squash: only the final state', {'f.txt': 'VERSION TWO\n'})

        c = vbc.containment(self.r.path, 'feature', base='main')
        self.assertGreater(c['missing_blobs'], 0,
                           'precondition: the v1 blob is genuinely absent from main')
        self.assertEqual(c['missing_tip_paths'], 0,
                         'but no tip path carries it, so nothing would be lost')
        self.assertTrue(c['contained'])


class TestDivergentVersusOrphaned(ContainmentTestCase):
    """Two ways a tip path can hold content absent from base.

    **Both lose unique bytes.** Every path in either list carries a blob that
    exists nowhere in base history. The split reports only whether the PATH
    survives:

    - **divergent**: base has this path, carrying different content.
    - **orphaned**: base has no such path at all.

    `contained` stays False for both - this adds evidence, it never downgrades
    a violation. The distinction matters because a gate that reports a 913-path
    preservation archive and a single stale doc revision at identical severity
    is a gate operators learn to ignore.

    The word "superseded" is deliberately avoided: branch-retention-inventory.md
    already uses it for an intermediate state a branch overwrote *itself*, which
    never appears here because such a state holds no tip path.
    """

    def test_divergent_path_is_classified_divergent_not_orphan(self):
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('old revision', {'doc.md': 'OLD VERSION\n'})
        self.r.checkout('main')
        self.r.commit('newer revision landed', {'doc.md': 'NEW VERSION\n'})

        c = vbc.containment(self.r.path, 'feature', base='main')
        self.assertFalse(c['contained'], 'strict boolean must stay False')
        self.assertIn('doc.md', c['divergent_paths'])
        self.assertEqual(c['orphan_paths'], [],
                         'main still has this path, so nothing is orphaned')

    def test_orphaned_path_is_classified_orphan(self):
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('only copy', {'archive/only-here.txt': 'IRREPLACEABLE\n'})

        c = vbc.containment(self.r.path, 'feature', base='main')
        self.assertFalse(c['contained'])
        self.assertIn('archive/only-here.txt', c['orphan_paths'])
        self.assertEqual(c['divergent_paths'], [])

    def test_divergent_paths_still_hold_bytes_absent_from_base(self):
        """The label must never be readable as 'redundant, safe to drop'."""
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('old revision', {'doc.md': 'OLD VERSION\n'})
        self.r.checkout('main')
        self.r.commit('newer revision landed', {'doc.md': 'NEW VERSION\n'})

        c = vbc.containment(self.r.path, 'feature', base='main')
        self.assertGreater(c['missing_blobs'], 0,
                           'a divergent path still carries a blob absent from base')

    def test_classification_partitions_missing_paths_exactly(self):
        """No missing path may be dropped or double-counted by the split."""
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('mixed', {'doc.md': 'OLD\n', 'gone.txt': 'ONLY\n'})
        self.r.checkout('main')
        self.r.commit('newer doc only', {'doc.md': 'NEW\n'})

        c = vbc.containment(self.r.path, 'feature', base='main')
        self.assertEqual(
            sorted(c['divergent_paths'] + c['orphan_paths']),
            sorted(c['missing_paths']),
            'divergent + orphan must partition missing_paths exactly')
        self.assertEqual(len(c['divergent_paths']) + len(c['orphan_paths']),
                         c['missing_tip_paths'])


class TestReadOnlyGuarantee(ContainmentTestCase):
    """This script runs immediately before someone deletes a branch. It must be
    structurally incapable of mutating the repository it is judging."""

    def test_mutating_subcommands_are_refused(self):
        for bad in ('push', 'branch', 'commit', 'reset', 'checkout', 'gc',
                    'update-ref', 'fetch', 'clean', 'tag'):
            with self.assertRaises(vbc.NotReadOnly, msg=f'{bad} must be refused'):
                vbc.git(self.r.path, bad, '--help')

    def test_readonly_subcommands_are_allowed(self):
        self.r.commit('base', {'base.txt': 'base\n'})
        out = vbc.git(self.r.path, 'rev-parse', 'HEAD')
        self.assertEqual(len(out.strip()), 40)

    def test_repository_is_unchanged_by_a_verification_run(self):
        """Belt and braces: compare full ref state before and after."""
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('work', {'a.txt': 'a\n'})
        before = self.r._run('for-each-ref', '--format=%(refname) %(objectname)')
        vbc.verify(self.r.path, branches=['feature'], base='main')
        after = self.r._run('for-each-ref', '--format=%(refname) %(objectname)')
        self.assertEqual(before, after, 'verification must not move or create refs')


class TestRefusalRatherThanVacuousPass(ContainmentTestCase):
    def test_no_branches_to_check_is_refused_not_passed(self):
        """Exit 2, not 0. A run that checked nothing has made no claim."""
        self.r.commit('base', {'base.txt': 'base\n'})
        rep = vbc.verify(self.r.path, branches=[], base='main')
        self.assertTrue(rep.refused, 'empty branch set must refuse')
        self.assertEqual(rep.counts['branches_checked'], 0)

    def test_nonexistent_branch_is_refused_not_reported_contained(self):
        """A typo'd branch name must never come back as 'safe to delete'."""
        self.r.commit('base', {'base.txt': 'base\n'})
        rep = vbc.verify(self.r.path, branches=['no-such-branch'], base='main')
        self.assertTrue(rep.refused)
        self.assertIn('unresolvable_ref', rep.violations)

    def test_nonexistent_base_is_refused(self):
        self.r.commit('base', {'base.txt': 'base\n'})
        rep = vbc.verify(self.r.path, branches=['main'], base='origin/nope')
        self.assertTrue(rep.refused)


class TestRetentionSourcedNamesResolveAgainstOrigin(ContainmentTestCase):
    """retention.json records REMOTE branches, so bare names must resolve to
    `origin/<name>` and never to a same-named local branch.

    Both halves of this matter and the quiet one is worse:

    - A retention name with no local branch makes the verifier REFUSE, which
      turns CI red for a branch that is perfectly fine on origin.
    - A retention name that DOES have a stale local branch resolves silently to
      the wrong commit, and containment is then measured against a tree nobody
      asked about - producing confident numbers about the wrong thing.
    """

    def _make_remote_ref(self, name, sha):
        self.r._run('update-ref', f'refs/remotes/origin/{name}', sha)

    def test_retention_name_resolves_to_origin_not_a_stale_local_branch(self):
        base = self.r.commit('base', {'base.txt': 'base\n'})

        # The local branch is stale and holds content that is NOT on main.
        self.r.checkout('feat', create=True)
        self.r.commit('stale local work', {'stale.txt': 'NOT ON MAIN\n'})

        # origin/feat is the real branch, and it was squash-merged into main.
        self.r.checkout('main')
        merged = self.r.commit('squash: real feat work', {'real.txt': 'REAL\n'})
        self._make_remote_ref('feat', merged)

        rep = vbc.verify(self.r.path, branches=['feat'], base='main',
                         ref_prefix='origin/')
        self.assertFalse(rep.refused, f'origin/feat exists; got {dict(rep.violations)}')
        self.assertTrue(rep.ok,
                        'origin/feat is contained in main; the stale local '
                        f'branch must not be consulted. got {dict(rep.violations)}')

    def test_missing_local_branch_does_not_refuse_when_origin_has_it(self):
        base = self.r.commit('base', {'base.txt': 'base\n'})
        self._make_remote_ref('only-on-origin', base)
        rep = vbc.verify(self.r.path, branches=['only-on-origin'], base='main',
                         ref_prefix='origin/')
        self.assertFalse(rep.refused)
        self.assertEqual(rep.counts['branches_checked'], 1)

    def test_retention_json_names_are_prefixed_automatically(self):
        """Reading from retention.json must apply the origin/ prefix itself."""
        base = self.r.commit('base', {'base.txt': 'base\n'})
        self._make_remote_ref('recorded', base)
        os.makedirs(os.path.join(self.r.path, 'manifests'), exist_ok=True)
        with open(os.path.join(self.r.path, 'manifests', 'retention.json'), 'w',
                  encoding='utf-8') as fh:
            json.dump({'schema': 1, 'branches': {
                'recorded': {'class': 'MERGED-IMPLEMENTATION', 'tip': base,
                             'deletable': True, 'retention': '2026-09-20'}}}, fh)

        rep = vbc.verify(self.r.path, base='main')  # branches=None -> retention.json
        self.assertFalse(rep.refused,
                         f'bare name must resolve via origin/; got {dict(rep.violations)}')
        self.assertEqual(rep.counts['branches_checked'], 1)


class TestVerifyReport(ContainmentTestCase):
    def test_orphaned_content_produces_violation_and_exit_1(self):
        """Only-copy loss is the invariant this gate exists to enforce."""
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('unique', {'only-here.txt': 'IRREPLACEABLE\n'})
        rep = vbc.verify(self.r.path, branches=['feature'], base='main')
        self.assertFalse(rep.ok)
        self.assertFalse(rep.refused)
        self.assertIn('would_orphan_content', rep.violations)
        self.assertEqual(rep.counts['branches_checked'], 1)

    def test_divergent_only_content_is_a_notice_not_a_violation(self):
        """Losing an older version of a path main still carries is a judgement
        call, not an automatic defect.

        Every squash-merged branch that was revised in place produces divergent
        paths. Blocking on them would fire on every legitimate retirement, and a
        gate that always fires is a gate operators route around. The only-copy
        invariant is untouched - see the orphan test above.
        """
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('old revision', {'doc.md': 'OLD\n'})
        self.r.checkout('main')
        self.r.commit('newer revision', {'doc.md': 'NEW\n'})

        rep = vbc.verify(self.r.path, branches=['feature'], base='main')
        self.assertIn('would_lose_older_version', rep.notices)
        self.assertNotIn('would_orphan_content', rep.violations)
        self.assertTrue(rep.ok, 'a divergent-only branch must not fail the run')

    def test_orphan_wins_when_a_branch_has_both(self):
        """A branch with any orphaned path blocks, whatever else it also has."""
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('mixed', {'doc.md': 'OLD\n', 'gone.txt': 'ONLY\n'})
        self.r.checkout('main')
        self.r.commit('newer doc only', {'doc.md': 'NEW\n'})

        rep = vbc.verify(self.r.path, branches=['feature'], base='main')
        self.assertIn('would_orphan_content', rep.violations)
        self.assertIn('would_lose_older_version', rep.notices)
        self.assertFalse(rep.ok)

    def test_contained_branch_passes_with_non_zero_counts(self):
        self.r.commit('base', {'base.txt': 'base\n'})
        self.r.checkout('feature', create=True)
        self.r.commit('work', {'feat.txt': 'X\n'})
        self.r.checkout('main')
        self.r.commit('squash', {'feat.txt': 'X\n'})
        rep = vbc.verify(self.r.path, branches=['feature'], base='main')
        self.assertTrue(rep.ok, f'got {dict(rep.violations)}')
        self.assertEqual(rep.counts['branches_checked'], 1)
        self.assertGreater(rep.counts['blobs_inspected'], 0)


if __name__ == '__main__':
    unittest.main()

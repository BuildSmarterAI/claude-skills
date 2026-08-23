"""Tests for the catalog health audit: the policy record versus live reality.

Risk class: deterministic guardrail / evaluator (risk-based-tdd §2.16) plus a
retention invariant (§2.14) -> test-first is mandatory.

`check-skill-consistency.py` validates the retention POLICY RECORD statically and
offline, and is deliberately forbidden from reading the network or the runtime
stores. This audit asks the complementary question that gate structurally cannot:
**does the record still describe the world?** A branch can vanish, a tip can move,
an expiry can pass, and a third-party installer can overwrite a manifest-governed
runtime file - none of which changes a single byte in the repository.

The dominant failure mode here is the *invisible skip*. On a CI runner there are
no runtime stores, so the drift section cannot run; a silent skip produces exit 0
that is byte-identical to a run which checked everything. Every section therefore
records itself in `report.skipped` with a reason, and the tests below pin that
behaviour rather than trusting it.
"""
from __future__ import annotations

import datetime
import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)


def _load(script_name, module_name):
    target = os.path.join(_ROOT, 'scripts', script_name)
    spec = importlib.util.spec_from_file_location(module_name, target)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ach = _load('audit-catalog-health.py', 'audit_catalog_health')

AUG_22 = datetime.date(2026, 8, 22)


class AuditTestCase(unittest.TestCase):
    """Builds a canonical tree plus fake runtime stores, all disposable."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='audit-')
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        os.makedirs(os.path.join(self.root, 'manifests'))
        self.claude = os.path.join(self.root, '_rt_claude')
        self.codex = os.path.join(self.root, '_rt_codex')

    def add_skill(self, name, content, *, targets=('claude',), mode='IDENTICAL'):
        d = os.path.join(self.root, name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'SKILL.md'), 'wb') as fh:
            fh.write(content.encode('utf-8'))
        return {'skill': name, 'source': name, 'targets': list(targets),
                'mode': mode, 'status': 'active',
                'expected_sha256': hashlib.sha256(content.encode('utf-8')).hexdigest()}

    def write_manifest(self, entries):
        with open(os.path.join(self.root, 'manifests', 'skills.json'), 'w',
                  encoding='utf-8') as fh:
            json.dump({'skills': entries}, fh)

    def write_retention(self, branches):
        with open(os.path.join(self.root, 'manifests', 'retention.json'), 'w',
                  encoding='utf-8') as fh:
            json.dump({'schema': 1, 'branches': branches}, fh)

    def deploy(self, root, name, content, *, mtime=None):
        d = os.path.join(root, name)
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, 'SKILL.md')
        with open(p, 'wb') as fh:
            fh.write(content.encode('utf-8'))
        if mtime is not None:
            os.utime(p, (mtime, mtime))
        return p

    def roots(self):
        return {'claude': self.claude, 'codex': self.codex}


class TestRuntimeDrift(AuditTestCase):
    def test_matching_runtime_is_not_drift(self):
        self.write_manifest([self.add_skill('alpha', 'BODY\n')])
        self.deploy(self.claude, 'alpha', 'BODY\n')
        rep = ach.audit(self.root, runtime_roots=self.roots())
        self.assertNotIn('runtime_drift', rep.violations)
        self.assertGreater(rep.counts['runtime_files_compared'], 0,
                           'a clean drift check must still prove it compared something')

    def test_drift_is_detected(self):
        self.write_manifest([self.add_skill('alpha', 'CANONICAL\n')])
        self.deploy(self.claude, 'alpha', 'OVERWRITTEN BY SOMETHING ELSE\n')
        rep = ach.audit(self.root, runtime_roots=self.roots())
        self.assertIn('runtime_drift', rep.violations)

    def test_runtime_newer_is_attributed_to_an_external_writer(self):
        """The 2026-08-21 case: an installer overwrote a manifest-governed file.

        Attribution is the whole point. Without it the reflex is "redeploy and
        move on", which fixes the symptom until the installer runs again - so the
        identical finding reappears and looks new every time.
        """
        self.write_manifest([self.add_skill('alpha', 'CANONICAL\n')])
        self.deploy(self.claude, 'alpha', 'INSTALLER WROTE THIS\n', mtime=9_000_000_000)
        rep = ach.audit(self.root, runtime_roots=self.roots(),
                        canonical_mtimes={'alpha': 1_000_000_000})
        found = [v for v in rep.violations.get('runtime_drift', []) if 'alpha' in v]
        self.assertTrue(found, 'drift must be reported')
        self.assertIn('external', found[0].lower(),
                      f'runtime newer than canonical implies an external writer; got {found[0]}')

    def test_canonical_newer_is_attributed_to_an_undeployed_change(self):
        self.write_manifest([self.add_skill('alpha', 'CANONICAL EDITED HERE\n')])
        self.deploy(self.claude, 'alpha', 'OLD DEPLOYED COPY\n', mtime=1_000_000_000)
        rep = ach.audit(self.root, runtime_roots=self.roots(),
                        canonical_mtimes={'alpha': 9_000_000_000})
        found = [v for v in rep.violations.get('runtime_drift', []) if 'alpha' in v]
        self.assertTrue(found)
        self.assertIn('undeployed', found[0].lower(),
                      f'canonical newer implies we have not deployed yet; got {found[0]}')

    def test_absent_runtime_is_skipped_loudly_not_silently_passed(self):
        """A CI runner has no runtime stores. That must be visible, not invisible."""
        self.write_manifest([self.add_skill('alpha', 'BODY\n')])
        rep = ach.audit(self.root,
                        runtime_roots={'claude': os.path.join(self.root, 'nope')})
        self.assertIn('runtime', rep.skipped)
        self.assertEqual(rep.counts['runtime_files_compared'], 0)
        self.assertNotIn('runtime_drift', rep.violations, 'absence is not drift')

    def test_missing_active_skill_in_present_runtime_is_a_violation(self):
        """`active` means exposed every turn, so it must be on disk.

        Measured on the real catalog: all 63 deployable claude-targeted `active`
        entries are deployed. The meaning is unambiguous and the evidence is
        strong, so absence here is a defect.
        """
        e = self.add_skill('alpha', 'BODY\n')
        e['status'] = 'active'
        self.write_manifest([e])
        self.deploy(self.claude, 'other', 'X\n')  # store exists, alpha absent
        rep = ach.audit(self.root, runtime_roots={'claude': self.claude})
        self.assertNotIn('runtime', rep.skipped)
        self.assertIn('runtime_missing', rep.violations)

    def test_missing_on_demand_skill_is_a_notice_not_a_violation(self):
        """Whether `on-demand` is deployed-but-unloaded is NOT established.

        The repository documents both readings and they conflict:
          - RELEASING.md: active<->on-demand changes "what is *loaded*, not what
            the catalog" ships  -> implies on-demand IS deployed.
          - canonical-runtime-reconciliation.md: on-demand ones "stay held"
            -> implies on-demand is NOT deployed.

        The live catalog cannot break the tie: there is exactly one deployable
        on-demand entry (n=1). Reporting a violation on an unresolved premise
        would manufacture a defect out of an open question, so this stays a
        notice until someone settles the semantics.
        """
        e = self.add_skill('alpha', 'BODY\n')
        e['status'] = 'on-demand'
        self.write_manifest([e])
        self.deploy(self.claude, 'other', 'X\n')
        rep = ach.audit(self.root, runtime_roots={'claude': self.claude})
        self.assertIn('runtime_missing', rep.notices)
        self.assertNotIn('runtime_missing', rep.violations)
        self.assertTrue(rep.ok, 'an unresolved premise must not fail the run')


class TestRetentionVersusReality(AuditTestCase):
    BR = {'class': 'MERGED-IMPLEMENTATION', 'tip': 'a' * 40,
          'deletable': True, 'retention': '2026-09-20'}

    def test_branch_missing_from_remote_is_flagged(self):
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        self.write_retention({'chore/gone': dict(self.BR)})
        rep = ach.audit(self.root, remote_refs={}, today=AUG_22)
        self.assertIn('retention_branch_missing', rep.violations)
        self.assertGreater(rep.counts['retention_branches_checked'], 0)

    def test_tip_sha_mismatch_is_flagged(self):
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        self.write_retention({'chore/moved': dict(self.BR)})
        rep = ach.audit(self.root, remote_refs={'chore/moved': 'b' * 40}, today=AUG_22)
        self.assertIn('retention_tip_moved', rep.violations)

    def test_matching_tip_is_clean(self):
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        self.write_retention({'chore/ok': dict(self.BR)})
        rep = ach.audit(self.root, remote_refs={'chore/ok': 'a' * 40}, today=AUG_22)
        self.assertNotIn('retention_tip_moved', rep.violations)
        self.assertNotIn('retention_branch_missing', rep.violations)

    def test_past_expiry_is_an_advisory_notice_not_a_build_breaker(self):
        """"Due for retirement" is information, not a defect.

        Filing it as a violation would fail CI on 2026-09-20 for every build,
        for a condition no code change caused and no code change can fix. The
        severity split is the point: notices inform, violations block.
        """
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        self.write_retention({'chore/old': dict(self.BR)})
        rep = ach.audit(self.root, remote_refs={'chore/old': 'a' * 40},
                        today=datetime.date(2026, 10, 1))
        self.assertIn('retention_expired', rep.notices)
        self.assertNotIn('retention_expired', rep.violations)
        self.assertTrue(rep.ok, 'an advisory notice must not fail the run')

    def test_expiry_fires_on_the_date_itself(self):
        """The policy reads "retire on or after", so the boundary day counts."""
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        self.write_retention({'chore/due': dict(self.BR)})
        rep = ach.audit(self.root, remote_refs={'chore/due': 'a' * 40},
                        today=datetime.date(2026, 9, 20))
        self.assertIn('retention_expired', rep.notices)

    def test_day_before_expiry_is_not_flagged(self):
        """Boundary: the expiry date must not fire a day early."""
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        self.write_retention({'chore/young': dict(self.BR)})
        rep = ach.audit(self.root, remote_refs={'chore/young': 'a' * 40},
                        today=datetime.date(2026, 9, 19))
        self.assertNotIn('retention_expired', rep.notices)

    def test_indefinite_retention_never_expires(self):
        """A preservation branch must never be reported as due for retirement."""
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        self.write_retention({'chore/snap': {
            'class': 'PERMANENT-PRESERVATION', 'tip': 'a' * 40,
            'deletable': False, 'retention': 'indefinite'}})
        rep = ach.audit(self.root, remote_refs={'chore/snap': 'a' * 40},
                        today=datetime.date(2099, 1, 1))
        self.assertNotIn('retention_expired', rep.notices)

    def test_missing_preservation_branch_is_flagged_as_its_own_severity(self):
        """The record promises this branch is kept forever, and it is gone.

        This must not be filed under the same key as an ordinary merged branch
        going missing: one is routine cleanup, the other is irreversible loss of
        the only copy of the pre-consolidation archive.
        """
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        self.write_retention({'chore/snap': {
            'class': 'PERMANENT-PRESERVATION', 'tip': 'a' * 40,
            'deletable': False, 'retention': 'indefinite'}})
        rep = ach.audit(self.root, remote_refs={}, today=AUG_22)
        self.assertIn('preservation_branch_missing', rep.violations)

    def test_absent_retention_file_is_skipped_loudly(self):
        """retention.json lands with PR #6; until then this must announce itself."""
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        rep = ach.audit(self.root, remote_refs={})
        self.assertIn('retention', rep.skipped)
        self.assertEqual(rep.counts['retention_branches_checked'], 0)
        self.assertNotIn('retention_branch_missing', rep.violations)

    def test_unenumerable_remote_is_skipped_not_read_as_every_branch_missing(self):
        """"I could not look" must never be reported as "they are all gone".

        `actions/checkout` does not fetch remote branch refs by default. Without
        this guard a CI misconfiguration enumerates zero origin refs and the
        audit concludes every retention branch has vanished - including the
        preservation archive, which fires the single loudest alarm this tool has
        while being entirely false. An empty auto-discovered ref set is missing
        evidence, not evidence of absence.

        Passing `remote_refs={}` explicitly still means "the remote really is
        empty" and is trusted; only auto-discovery is treated as unreliable.
        """
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        self.write_retention({'chore/snap': {
            'class': 'PERMANENT-PRESERVATION', 'tip': 'a' * 40,
            'deletable': False, 'retention': 'indefinite'}})
        # self.root is not a git repository, so discovery yields nothing.
        rep = ach.audit(self.root, remote_refs=None, today=AUG_22)
        self.assertNotIn('preservation_branch_missing', rep.violations)
        self.assertNotIn('retention_branch_missing', rep.violations)
        self.assertIn('retention_remote', rep.skipped)

    def test_explicit_empty_remote_is_still_trusted(self):
        """The guard must not blind the audit when the caller really knows."""
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        self.write_retention({'chore/gone': dict(self.BR)})
        rep = ach.audit(self.root, remote_refs={}, today=AUG_22)
        self.assertIn('retention_branch_missing', rep.violations)
        self.assertNotIn('retention_remote', rep.skipped)

    def test_unparseable_retention_file_is_a_violation_not_a_skip(self):
        """A corrupt policy record must never read as 'nothing to check'."""
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        with open(os.path.join(self.root, 'manifests', 'retention.json'), 'w',
                  encoding='utf-8') as fh:
            fh.write('{ not json')
        rep = ach.audit(self.root, remote_refs={}, today=AUG_22)
        self.assertIn('retention_unreadable', rep.violations)
        self.assertNotIn('retention', rep.skipped)


class TestAuditAntiVacuity(AuditTestCase):
    def test_audit_reports_what_it_inspected(self):
        self.write_manifest([self.add_skill('alpha', 'B\n')])
        self.deploy(self.claude, 'alpha', 'B\n')
        self.write_retention({'chore/ok': {'class': 'MERGED-IMPLEMENTATION',
                                           'tip': 'a' * 40, 'deletable': True,
                                           'retention': '2026-09-20'}})
        rep = ach.audit(self.root, runtime_roots=self.roots(),
                        remote_refs={'chore/ok': 'a' * 40}, today=AUG_22)
        self.assertTrue(rep.ok, f'expected clean; got {dict(rep.violations)}')
        self.assertGreater(rep.counts['runtime_files_compared'], 0)
        self.assertGreater(rep.counts['retention_branches_checked'], 0)
        self.assertEqual(rep.skipped, {}, 'nothing should be skipped in this run')

    def test_a_run_that_inspected_nothing_says_so_in_every_section(self):
        """The false-green shape: everything skipped, exit 0, looks like a pass."""
        self.write_manifest([])
        rep = ach.audit(self.root, runtime_roots={'claude': '/definitely/absent'})
        self.assertIn('runtime', rep.skipped)
        self.assertIn('retention', rep.skipped)
        self.assertEqual(rep.counts['runtime_files_compared'], 0)
        self.assertEqual(rep.counts['retention_branches_checked'], 0)

    def test_skips_are_carried_into_machine_readable_output(self):
        """Whatever consumes --json must be able to see the skip too."""
        self.write_manifest([])
        rep = ach.audit(self.root, runtime_roots={'claude': '/definitely/absent'})
        d = rep.as_dict()
        self.assertIn('skipped', d)
        self.assertIn('runtime', d['skipped'])
        self.assertIn('counts', d)


class TestTestFilesAreActuallyDiscovered(unittest.TestCase):
    """A test file that silently never runs is indistinguishable from one that
    passes. CI runs `unittest discover -s tests`, which matches `test*.py`; this
    pins that every module is inside the discovered set rather than assuming it."""

    def test_all_test_modules_are_discovered_by_the_ci_command(self):
        loader = unittest.TestLoader()
        suite = loader.discover(start_dir=_HERE, pattern='test*.py')
        found = set()

        def walk(s):
            for item in s:
                if isinstance(item, unittest.TestSuite):
                    walk(item)
                else:
                    found.add(type(item).__module__)

        walk(suite)
        for expected in ('test_skill_consistency', 'test_catalog_health',
                         'test_catalog_audit'):
            self.assertIn(expected, found,
                          f'{expected} must be discovered by CI; found={sorted(found)}')


if __name__ == '__main__':
    unittest.main()

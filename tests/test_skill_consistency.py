"""Tests for the canonical skill-consistency checker.

Risk class: deterministic guardrail / validator gate (risk-based-tdd §2.16, §2.8)
-> test-first is mandatory.

The failure mode that matters most for a checker is passing VACUOUSLY: reporting
success because it inspected nothing, or because an invariant silently never
evaluated. Every test below therefore builds a repository that violates exactly
one invariant and asserts that specific invariant fires - never merely that the
run failed. `test_clean_repo_passes_and_is_not_vacuous` pins the other side by
asserting the counters are non-zero on a passing run.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_TARGET = os.path.join(os.path.dirname(_HERE), 'scripts', 'check-skill-consistency.py')

# The script is intentionally hyphenated (CLI convention), so load it by path.
_spec = importlib.util.spec_from_file_location('check_skill_consistency', _TARGET)
csc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(csc)


SKILL_MD = """---
name: {name}
description: A test skill used by the consistency checker's own tests.
---

# {name}

Body content.
"""


def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class RepoBuilder:
    """Builds a throwaway canonical repo. Never touches the real working tree."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix='skillci-')
        os.makedirs(os.path.join(self.root, 'manifests'))
        self.skills = []

    def add_skill(self, name, *, body=None, entry=None, write_file=True):
        if write_file:
            d = os.path.join(self.root, name)
            os.makedirs(d, exist_ok=True)
            text = body if body is not None else SKILL_MD.format(name=name)
            with open(os.path.join(d, 'SKILL.md'), 'wb') as fh:
                fh.write(text.encode('utf-8'))
            digest = sha_bytes(text.encode('utf-8'))
        else:
            digest = sha_bytes(b'placeholder')
        e = {
            'skill': name,
            'source': name,
            'source_present_in_canonical': write_file,
            'targets': ['claude', 'codex'],
            'mode': 'IDENTICAL',
            'status': 'active',
            'expected_sha256': digest,
        }
        if entry:
            e.update(entry)
        self.skills.append(e)
        return e

    def write(self):
        with open(os.path.join(self.root, 'manifests', 'skills.json'), 'w',
                  encoding='utf-8') as fh:
            json.dump({'skills': self.skills}, fh, indent=1)
        return self.root

    def destroy(self):
        shutil.rmtree(self.root, ignore_errors=True)


class ConsistencyTestCase(unittest.TestCase):
    def setUp(self):
        self.b = RepoBuilder()
        self.addCleanup(self.b.destroy)

    def run_check(self):
        return csc.check_repo(self.b.write())

    def assertViolation(self, report, kind, skill):
        """Assert this exact invariant fired for this exact skill."""
        offenders = report.violations.get(kind, [])
        names = [o.split(':')[0] if isinstance(o, str) else o for o in offenders]
        self.assertIn(skill, names,
                      f'expected {kind!r} to fire for {skill!r}; '
                      f'got violations={dict(report.violations)}')
        self.assertFalse(report.ok, 'report must not be ok when a violation fired')


class TestCleanRepo(ConsistencyTestCase):
    def test_clean_repo_passes_and_is_not_vacuous(self):
        """A passing run must prove it actually inspected something.

        This is the anti-vacuity pin: a checker that walks zero skills would
        otherwise report PASS and satisfy every other test in this file.
        """
        self.b.add_skill('alpha')
        self.b.add_skill('beta')
        r = self.run_check()
        self.assertTrue(r.ok, f'expected clean repo to pass; got {dict(r.violations)}')
        self.assertEqual(r.counts['skills'], 2)
        self.assertEqual(r.counts['hashes_checked'], 2)
        self.assertEqual(r.counts['frontmatter_checked'], 2)

    def test_empty_manifest_is_not_a_pass(self):
        """Zero declared skills means the manifest is broken, not that all is well."""
        r = self.run_check()
        self.assertFalse(r.ok)
        self.assertIn('empty_manifest', r.violations)


class TestHashIntegrity(ConsistencyTestCase):
    def test_hash_mismatch_is_detected(self):
        self.b.add_skill('alpha')
        self.b.skills[0]['expected_sha256'] = '0' * 64
        self.assertViolation(self.run_check(), 'hash_mismatch', 'alpha')

    def test_hash_is_over_raw_bytes_not_normalized_text(self):
        """CRLF vs LF must change the hash; the repo pins `* -text` for this reason."""
        crlf = SKILL_MD.format(name='alpha').replace('\n', '\r\n')
        self.b.add_skill('alpha', body=crlf)
        # entry hash was computed over the CRLF bytes, so it must pass as-is
        self.assertTrue(self.run_check().ok)
        # and an LF-normalised expectation must fail
        self.b.skills[0]['expected_sha256'] = sha_bytes(
            SKILL_MD.format(name='alpha').encode('utf-8'))
        self.assertViolation(self.run_check(), 'hash_mismatch', 'alpha')

    def test_missing_expected_sha256_on_deployable_mode(self):
        self.b.add_skill('alpha')
        del self.b.skills[0]['expected_sha256']
        self.assertViolation(self.run_check(), 'missing_expected_sha256', 'alpha')


class TestSourcePresence(ConsistencyTestCase):
    def test_declared_but_absent_source_is_detected(self):
        self.b.add_skill('ghost', write_file=False,
                         entry={'source_present_in_canonical': True})
        self.assertViolation(self.run_check(), 'missing_source', 'ghost')

    def test_repo_local_skill_absent_from_canonical_is_allowed(self):
        """REPO-LOCAL skills legitimately live in another repository."""
        self.b.add_skill('owned', write_file=False, entry={
            'source_present_in_canonical': False,
            'mode': 'REPO_LOCAL', 'status': 'repo-local', 'targets': [],
            'ownership_class': 'REPO-LOCAL',
            'owner_repo': 'some-product',
            'owner_path': 'some-product/.claude/skills/owned',
            'expected_sha256': None,
        })
        self.assertTrue(self.run_check().ok)


class TestFrontmatter(ConsistencyTestCase):
    def test_missing_frontmatter_delimiter(self):
        self.b.add_skill('alpha', body='# alpha\n\nNo frontmatter at all.\n')
        self.assertViolation(self.run_check(), 'frontmatter_invalid', 'alpha')

    def test_missing_name_field(self):
        self.b.add_skill('alpha', body='---\ndescription: no name here\n---\n\n# alpha\n')
        self.assertViolation(self.run_check(), 'frontmatter_invalid', 'alpha')

    def test_missing_description_field(self):
        self.b.add_skill('alpha', body='---\nname: alpha\n---\n\n# alpha\n')
        self.assertViolation(self.run_check(), 'frontmatter_invalid', 'alpha')

    def test_name_must_match_directory(self):
        self.b.add_skill('alpha', body=SKILL_MD.format(name='not-alpha'))
        self.assertViolation(self.run_check(), 'frontmatter_name_mismatch', 'alpha')

    def test_quoted_name_is_equivalent_to_bare_name(self):
        """YAML quoting is not a name change.

        32 canonical skills write `name: "thing"`. Treating the quotes as part
        of the identifier made the checker fire on skills whose names matched
        perfectly - a false positive that would have trained reviewers to
        ignore this invariant.
        """
        self.b.add_skill('alpha', body='---\nname: "alpha"\ndescription: quoted.\n---\n\n# alpha\n')
        r = self.run_check()
        self.assertTrue(r.ok, f'quoted name must be accepted; got {dict(r.violations)}')

    def test_single_quoted_name_is_equivalent(self):
        self.b.add_skill('alpha', body="---\nname: 'alpha'\ndescription: quoted.\n---\n\n# alpha\n")
        self.assertTrue(self.run_check().ok)

    def test_quoting_does_not_mask_a_real_mismatch(self):
        """Stripping quotes must not become a way to smuggle a wrong name past."""
        self.b.add_skill('alpha', body='---\nname: "not-alpha"\ndescription: x.\n---\n\n# a\n')
        self.assertViolation(self.run_check(), 'frontmatter_name_mismatch', 'alpha')


class TestOwnership(ConsistencyTestCase):
    def test_repo_local_without_owner_repo(self):
        self.b.add_skill('orphan', write_file=False, entry={
            'source_present_in_canonical': False,
            'mode': 'REPO_LOCAL', 'status': 'repo-local', 'targets': [],
            'ownership_class': 'REPO-LOCAL', 'expected_sha256': None,
        })
        self.assertViolation(self.run_check(), 'repo_local_missing_owner', 'orphan')

    def test_repo_local_with_owner_repo_but_no_path(self):
        self.b.add_skill('orphan', write_file=False, entry={
            'source_present_in_canonical': False,
            'mode': 'REPO_LOCAL', 'status': 'repo-local', 'targets': [],
            'ownership_class': 'REPO-LOCAL', 'owner_repo': 'a-repo',
            'expected_sha256': None,
        })
        self.assertViolation(self.run_check(), 'repo_local_missing_owner', 'orphan')

    def test_generic_owner_placeholder_is_rejected(self):
        """The exact phrasing D4.2 had to eliminate must not come back."""
        self.b.add_skill('orphan', write_file=False, entry={
            'source_present_in_canonical': False,
            'mode': 'REPO_LOCAL', 'status': 'repo-local', 'targets': [],
            'ownership_class': 'REPO-LOCAL',
            'owner_repo': 'belongs to a product repo',
            'owner_path': 'belongs to a product repo',
            'expected_sha256': None,
        })
        self.assertViolation(self.run_check(), 'repo_local_missing_owner', 'orphan')


class TestStateContradictions(ConsistencyTestCase):
    def test_active_plus_disabled_is_rejected(self):
        self.b.add_skill('alpha', entry={'status': 'active', 'mode': 'DISABLED',
                                         'targets': []})
        self.assertViolation(self.run_check(), 'active_disabled_conflict', 'alpha')

    def test_invalid_mode_enum(self):
        self.b.add_skill('alpha', entry={'mode': 'TOTALLY_MADE_UP'})
        self.assertViolation(self.run_check(), 'invalid_mode', 'alpha')

    def test_invalid_status_enum(self):
        self.b.add_skill('alpha', entry={'status': 'sort-of-active'})
        self.assertViolation(self.run_check(), 'invalid_status', 'alpha')

    def test_invalid_target_runtime(self):
        self.b.add_skill('alpha', entry={'targets': ['claude', 'emacs']})
        self.assertViolation(self.run_check(), 'invalid_target', 'alpha')

    def test_duplicate_skill_identifier(self):
        self.b.add_skill('alpha')
        self.b.add_skill('alpha')
        r = self.run_check()
        self.assertFalse(r.ok)
        self.assertIn('duplicate_skill_id', r.violations)

    def test_deployable_mode_requires_targets(self):
        self.b.add_skill('alpha', entry={'mode': 'IDENTICAL', 'targets': []})
        self.assertViolation(self.run_check(), 'deployable_without_target', 'alpha')


class TestHolds(ConsistencyTestCase):
    def test_hold_without_reason_is_rejected(self):
        self.b.add_skill('alpha', entry={'status': 'hold'})
        self.assertViolation(self.run_check(), 'hold_without_reason', 'alpha')

    def test_hold_with_documented_reason_is_allowed(self):
        """Adjudication must stay possible - a documented hold is legitimate."""
        self.b.add_skill('alpha', entry={
            'status': 'hold',
            'hold_reason': 'Canonical and runtime both hold unique material; merge owed.',
        })
        self.assertTrue(self.run_check().ok)


class TestIntentionalDivergence(ConsistencyTestCase):
    def test_claude_only_without_explanation_is_rejected(self):
        self.b.add_skill('alpha', entry={'mode': 'CLAUDE_ONLY', 'targets': ['claude']})
        self.assertViolation(self.run_check(), 'undocumented_divergence', 'alpha')

    def test_codex_only_without_explanation_is_rejected(self):
        self.b.add_skill('alpha', entry={'mode': 'CODEX_ONLY', 'targets': ['codex']})
        self.assertViolation(self.run_check(), 'undocumented_divergence', 'alpha')

    def test_adapter_without_explanation_is_rejected(self):
        self.b.add_skill('alpha', entry={'mode': 'ADAPTER'})
        self.assertViolation(self.run_check(), 'undocumented_divergence', 'alpha')

    def test_documented_divergence_is_allowed(self):
        self.b.add_skill('alpha', entry={
            'mode': 'CLAUDE_ONLY', 'targets': ['claude'],
            'intentional_divergence': 'Dispatches subagents via the Agent tool, '
                                      'which Codex has no equivalent for.',
        })
        self.assertTrue(self.run_check().ok)


class TestArchiveIsNotProcessed(ConsistencyTestCase):
    def test_preservation_archive_is_skipped(self):
        """The 1,214-file archive is rollback evidence, not deploy input."""
        self.b.add_skill('alpha')
        arch = os.path.join(self.b.root, 'pre-consolidation', 'claude-runtime',
                            'skills', 'archived-thing')
        os.makedirs(arch)
        with open(os.path.join(arch, 'SKILL.md'), 'w', encoding='utf-8') as fh:
            fh.write('# deliberately invalid: no frontmatter\n')
        r = self.run_check()
        self.assertTrue(r.ok, f'archive must not be validated; got {dict(r.violations)}')
        self.assertEqual(r.counts['skills'], 1)


class TestUndeclaredCanonicalSkill(ConsistencyTestCase):
    def test_canonical_dir_missing_from_manifest_is_reported(self):
        """A skill on disk that nothing declares is drift in the other direction."""
        self.b.add_skill('alpha')
        d = os.path.join(self.b.root, 'stowaway')
        os.makedirs(d)
        with open(os.path.join(d, 'SKILL.md'), 'w', encoding='utf-8') as fh:
            fh.write(SKILL_MD.format(name='stowaway'))
        self.assertViolation(self.run_check(), 'undeclared_canonical_skill', 'stowaway')


class TestCatalogVersion(ConsistencyTestCase):
    """Catalog release identity.

    Risk class: deterministic guardrail (risk-based-tdd s2.16). A catalog that
    misreports its own version is worse than one with no version at all - a
    runtime would be attributed to a release it was never deployed from.
    """

    def write_version(self, payload):
        import os
        p = os.path.join(self.b.root, 'catalog-version.json')
        with open(p, 'w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=1)
        return p

    VALID = {'catalog_version': '1.0.0',
             'manifest_schema_version': 1,
             'deployment_state_schema_version': 1}

    def test_valid_version_file_passes(self):
        self.b.add_skill('alpha')
        self.write_version(self.VALID)
        r = self.run_check()
        self.assertTrue(r.ok, f'valid version file must pass; got {dict(r.violations)}')
        self.assertEqual(r.counts['catalog_version_checked'], 1)

    def test_absent_version_file_is_tolerated(self):
        """Absence must not fail: the checker predates versioning and other
        trees (test fixtures, forks) legitimately have none."""
        self.b.add_skill('alpha')
        self.assertTrue(self.run_check().ok)

    def test_unparseable_version_file_is_rejected(self):
        import os
        self.b.add_skill('alpha')
        with open(os.path.join(self.b.root, 'catalog-version.json'), 'w',
                  encoding='utf-8') as fh:
            fh.write('{not json')
        r = self.run_check()
        self.assertFalse(r.ok)
        self.assertIn('catalog_version_invalid', r.violations)

    def test_non_semver_catalog_version_is_rejected(self):
        self.b.add_skill('alpha')
        bad = dict(self.VALID, catalog_version='v1')
        self.write_version(bad)
        r = self.run_check()
        self.assertFalse(r.ok)
        self.assertIn('catalog_version_invalid', r.violations)

    def test_missing_required_version_key_is_rejected(self):
        self.b.add_skill('alpha')
        bad = dict(self.VALID)
        del bad['deployment_state_schema_version']
        self.write_version(bad)
        r = self.run_check()
        self.assertFalse(r.ok)
        self.assertIn('catalog_version_invalid', r.violations)

    def test_manifest_schema_disagreement_is_rejected(self):
        """The declared manifest schema must match what the manifest says.

        This is the cross-check that makes the version file meaningful rather
        than a second place to write a number that nothing verifies.
        """
        self.b.add_skill('alpha')
        self.b.write()
        m = json.load(open(os.path.join(self.b.root, 'manifests', 'skills.json'),
                           encoding='utf-8'))
        m['schema'] = 2
        with open(os.path.join(self.b.root, 'manifests', 'skills.json'), 'w',
                  encoding='utf-8') as fh:
            json.dump(m, fh, indent=1)
        self.write_version(self.VALID)          # declares manifest_schema_version 1
        r = csc.check_repo(self.b.root)
        self.assertFalse(r.ok)
        self.assertIn('manifest_schema_mismatch', r.violations)

    def test_matching_manifest_schema_passes(self):
        self.b.add_skill('alpha')
        self.b.write()
        m = json.load(open(os.path.join(self.b.root, 'manifests', 'skills.json'),
                           encoding='utf-8'))
        m['schema'] = 1
        with open(os.path.join(self.b.root, 'manifests', 'skills.json'), 'w',
                  encoding='utf-8') as fh:
            json.dump(m, fh, indent=1)
        self.write_version(self.VALID)
        self.assertTrue(csc.check_repo(self.b.root).ok)


class TestRetentionMetadata(ConsistencyTestCase):
    """Branch retention metadata.

    Risk class: deterministic guardrail (risk-based-tdd s2.16). The failure that
    matters is a preservation branch silently marked deletable - that is how
    disaster-recovery history gets tidied away by a future cleanup pass.
    """

    VALID = {
        'schema': 1,
        'branches': {
            'archive/keepme': {'class': 'PERMANENT-PRESERVATION', 'deletable': False,
                               'retention': 'indefinite'},
            'chore/done': {'class': 'MERGED-IMPLEMENTATION', 'deletable': True,
                           'retention': '2026-09-20'},
        },
    }

    def write_retention(self, payload):
        import os
        os.makedirs(os.path.join(self.b.root, 'manifests'), exist_ok=True)
        with open(os.path.join(self.b.root, 'manifests', 'retention.json'), 'w',
                  encoding='utf-8') as fh:
            json.dump(payload, fh, indent=1)

    def test_valid_retention_passes(self):
        self.b.add_skill('alpha')
        self.b.write()
        self.write_retention(self.VALID)
        r = csc.check_repo(self.b.root)
        self.assertTrue(r.ok, f'valid retention must pass; got {dict(r.violations)}')
        self.assertEqual(r.counts['retention_branches_checked'], 2)

    def test_absent_retention_is_tolerated(self):
        self.b.add_skill('alpha')
        self.assertTrue(self.run_check().ok)

    def test_unparseable_retention_is_rejected(self):
        import os
        self.b.add_skill('alpha')
        self.b.write()
        os.makedirs(os.path.join(self.b.root, 'manifests'), exist_ok=True)
        with open(os.path.join(self.b.root, 'manifests', 'retention.json'), 'w',
                  encoding='utf-8') as fh:
            fh.write('{nope')
        r = csc.check_repo(self.b.root)
        self.assertFalse(r.ok)
        self.assertIn('retention_invalid', r.violations)

    def test_unknown_class_is_rejected(self):
        self.b.add_skill('alpha')
        self.b.write()
        bad = json.loads(json.dumps(self.VALID))
        bad['branches']['chore/done']['class'] = 'PROBABLY-FINE'
        self.write_retention(bad)
        r = csc.check_repo(self.b.root)
        self.assertFalse(r.ok)
        self.assertIn('retention_invalid', r.violations)

    def test_preservation_branch_marked_deletable_is_rejected(self):
        """The invariant this file exists for.

        A PERMANENT-PRESERVATION branch flagged deletable would let a future
        cleanup pass destroy the only copy of the pre-consolidation archive.
        """
        self.b.add_skill('alpha')
        self.b.write()
        bad = json.loads(json.dumps(self.VALID))
        bad['branches']['archive/keepme']['deletable'] = True
        self.write_retention(bad)
        r = csc.check_repo(self.b.root)
        self.assertFalse(r.ok)
        self.assertIn('preservation_marked_deletable', r.violations)
        self.assertIn('archive/keepme',
                      ' '.join(r.violations['preservation_marked_deletable']))

    def test_active_and_uncertain_may_not_be_deletable(self):
        for cls in ('ACTIVE', 'UNCERTAIN'):
            with self.subTest(cls=cls):
                b = RepoBuilder()
                self.addCleanup(b.destroy)
                b.add_skill('alpha')
                b.write()
                payload = json.loads(json.dumps(self.VALID))
                payload['branches']['chore/done'] = {'class': cls, 'deletable': True,
                                                     'retention': 'n/a'}
                import os
                os.makedirs(os.path.join(b.root, 'manifests'), exist_ok=True)
                with open(os.path.join(b.root, 'manifests', 'retention.json'), 'w',
                          encoding='utf-8') as fh:
                    json.dump(payload, fh, indent=1)
                r = csc.check_repo(b.root)
                self.assertFalse(r.ok, f'{cls} + deletable must fail')
                self.assertIn('preservation_marked_deletable', r.violations)

    def test_missing_required_branch_field_is_rejected(self):
        self.b.add_skill('alpha')
        self.b.write()
        bad = json.loads(json.dumps(self.VALID))
        del bad['branches']['chore/done']['deletable']
        self.write_retention(bad)
        r = csc.check_repo(self.b.root)
        self.assertFalse(r.ok)
        self.assertIn('retention_invalid', r.violations)


if __name__ == '__main__':
    unittest.main(verbosity=2)

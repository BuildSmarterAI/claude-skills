"""The line-ending pin must be enforced, not merely requested in a comment.

Risk class: data transformation where silent corruption is possible
(risk-based-tdd §2.13) plus a deterministic guardrail (§2.16) -> test-first.

`manifests/skills.json` records the SHA-256 of every deployed file, and
`check-skill-consistency.py` hashes RAW BYTES - its own
`test_hash_is_over_raw_bytes_not_normalized_text` pins that CRLF and LF produce
different digests. This repository also sets `core.autocrlf=input`, which
rewrites CRLF to LF on commit.

The only thing standing between those two facts is `.gitattributes` declaring
`* -text`. Measured on main at the time of writing: of 235 hashed SKILL.md
files, 129 are LF, **74 are CRLF and 32 are MIXED**. Delete the pin and the next
commit touching any of those 106 files silently rewrites its bytes, invalidating
`expected_sha256` and surfacing later as an unexplained `hash_mismatch` whose
cause is invisible in the diff.

The file itself says "Do not remove it." Nothing enforced that until this test.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_TARGET = os.path.join(os.path.dirname(_HERE), 'scripts', 'check-skill-consistency.py')
_spec = importlib.util.spec_from_file_location('check_skill_consistency_eol', _TARGET)
csc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(csc)

SKILL_MD = """---
name: {name}
description: A test skill used by the line-ending pin tests.
---

# {name}
"""

PINNED = '# comment\n* -text\n'


class PinTestCase(unittest.TestCase):
    """Minimal repo builder, independent of the main suite's fixture so this
    file cannot be broken by an unrelated change to it."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='eolpin-')
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        os.makedirs(os.path.join(self.root, 'manifests'))

    def build(self, gitattributes=PINNED, name='alpha'):
        body = SKILL_MD.format(name=name).encode('utf-8')
        os.makedirs(os.path.join(self.root, name), exist_ok=True)
        with open(os.path.join(self.root, name, 'SKILL.md'), 'wb') as fh:
            fh.write(body)
        entry = {'skill': name, 'source': name, 'targets': ['claude'],
                 'mode': 'IDENTICAL', 'status': 'active',
                 'expected_sha256': hashlib.sha256(body).hexdigest()}
        with open(os.path.join(self.root, 'manifests', 'skills.json'), 'w',
                  encoding='utf-8') as fh:
            json.dump({'skills': [entry]}, fh)
        path = os.path.join(self.root, '.gitattributes')
        if gitattributes is None:
            if os.path.exists(path):
                os.remove(path)
        else:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(gitattributes)
        return csc.check_repo(self.root)


class TestLineEndingPin(PinTestCase):
    def test_pinned_repo_passes_and_is_not_vacuous(self):
        r = self.build()
        self.assertTrue(r.ok, f'a pinned repo must pass; got {dict(r.violations)}')
        self.assertEqual(r.counts['gitattributes_checked'], 1,
                         'a pass must prove the pin was actually inspected')

    def test_missing_gitattributes_is_a_violation(self):
        """Deletion is the scenario this exists for.

        Tolerating absence would make the check useless: the file could be
        removed and CI would stay green while every future commit silently
        rewrote line endings.
        """
        r = self.build(gitattributes=None)
        self.assertFalse(r.ok)
        self.assertIn('gitattributes_missing', r.violations)

    def test_text_auto_is_rejected(self):
        """`* text=auto` is the plausible wrong fix - it ENABLES normalisation."""
        r = self.build(gitattributes='* text=auto\n')
        self.assertFalse(r.ok)
        self.assertIn('gitattributes_not_pinned', r.violations)

    def test_empty_gitattributes_is_rejected(self):
        r = self.build(gitattributes='# nothing here\n')
        self.assertFalse(r.ok)
        self.assertIn('gitattributes_not_pinned', r.violations)

    def test_pin_scoped_to_one_glob_does_not_count_as_repo_wide(self):
        """`*.md -text` protects markdown only; the manifest hashes more than that."""
        r = self.build(gitattributes='*.md -text\n')
        self.assertFalse(r.ok)
        self.assertIn('gitattributes_not_pinned', r.violations)

    def test_pin_with_additional_attributes_is_accepted(self):
        r = self.build(gitattributes='* -text -diff\n')
        self.assertTrue(r.ok, f'extra attributes are fine; got {dict(r.violations)}')

    def test_extra_whitespace_is_accepted(self):
        r = self.build(gitattributes='  *   -text  \n')
        self.assertTrue(r.ok, f'whitespace is not semantic; got {dict(r.violations)}')


class TestRealRepositoryIsPinned(unittest.TestCase):
    def test_this_repository_pins_line_endings(self):
        """The invariant asserted against the real tree, not only a fixture."""
        root = os.path.dirname(_HERE)
        path = os.path.join(root, '.gitattributes')
        self.assertTrue(os.path.isfile(path),
                        '.gitattributes is missing from this repository')
        with open(path, encoding='utf-8') as fh:
            self.assertRegex(fh.read(), csc.EOL_PIN,
                             '.gitattributes must disable end-of-line conversion')


if __name__ == '__main__':
    unittest.main()

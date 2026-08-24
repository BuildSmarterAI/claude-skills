"""--quiet exists so the audit can run on every session without adding noise.

Risk class: deterministic guardrail (risk-based-tdd §2.16). The failure mode is
specific and severe: a quiet mode that is quiet when something IS wrong turns the
drift check into a permanently green light. Silence must mean "clean", never
"suppressed".
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)


def _load(script, mod):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(_ROOT, 'scripts', script))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ach = _load('audit-catalog-health.py', 'audit_quiet')


class QuietTestCase(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='quiet-')
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        os.makedirs(os.path.join(self.root, 'manifests'))

    def manifest(self, deployed):
        body = b'---\nname: alpha\ndescription: d\n---\n'
        os.makedirs(os.path.join(self.root, 'alpha'), exist_ok=True)
        open(os.path.join(self.root, 'alpha', 'SKILL.md'), 'wb').write(body)
        rt = os.path.join(self.root, 'rt')
        os.makedirs(os.path.join(rt, 'alpha'), exist_ok=True)
        if deployed is not None:
            open(os.path.join(rt, 'alpha', 'SKILL.md'), 'wb').write(deployed)
        json.dump({'skills': [{'skill': 'alpha', 'source': 'alpha',
                               'targets': ['claude'], 'mode': 'IDENTICAL',
                               'status': 'active',
                               'expected_sha256': hashlib.sha256(body).hexdigest()}]},
                  open(os.path.join(self.root, 'manifests', 'skills.json'), 'w'))
        return rt, body

    def run_main(self, deployed, quiet):
        rt, _ = self.manifest(deployed)
        argv = ['--repo', self.root, '--claude-root', rt,
                '--codex-root', os.path.join(self.root, 'absent')]
        if quiet:
            argv.append('--quiet')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = ach.main(argv)
        return code, buf.getvalue()


class TestQuietMode(QuietTestCase):
    def test_quiet_is_silent_when_clean(self):
        body = b'---\nname: alpha\ndescription: d\n---\n'
        code, out = self.run_main(body, quiet=True)
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), '', f'clean run must print nothing; got {out!r}')

    def test_quiet_still_reports_a_violation(self):
        """Silence must mean clean, never suppressed - the whole risk here."""
        code, out = self.run_main(b'OVERWRITTEN BY SOMETHING ELSE\n', quiet=True)
        self.assertEqual(code, 1)
        self.assertIn('runtime_drift', out,
                      f'a violation must break the silence; got {out!r}')

    def test_non_quiet_prints_the_summary_when_clean(self):
        body = b'---\nname: alpha\ndescription: d\n---\n'
        code, out = self.run_main(body, quiet=False)
        self.assertEqual(code, 0)
        self.assertIn('Catalog health', out)


if __name__ == '__main__':
    unittest.main()

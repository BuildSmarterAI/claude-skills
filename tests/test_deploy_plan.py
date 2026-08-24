"""Delivery is governed by mode and targets, not by exposure.

Risk class: data transformation where silent corruption is possible
(risk-based-tdd §2.13) - this decides which files reach a runtime store.

`plan()` skipped every entry whose status was not `active`, which conflates two
independent things:

  * what a runtime RECEIVES  -> `mode` + `targets`
  * what a runtime LOADS     -> exposure

The evidence that they are independent is in the live runtime: all 105 skills
turned off via `skillOverrides` are still present on disk. Exposure is switched
by the override, never by withholding the file. `on-demand` therefore means
installed but not auto-loaded, and an on-demand entry that never reaches the
runtime cannot be loaded on demand at all.

`hold` stays excluded on purpose. It means adjudication is still pending, which
is a statement about whether the content is settled - not about exposure.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
_TARGET = os.path.join(_ROOT, 'scripts', 'deploy-skills.py')
_spec = importlib.util.spec_from_file_location('deploy_skills', _TARGET)
ds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ds)


class PlanTestCase(unittest.TestCase):
    def setUp(self):
        self.rt = tempfile.mkdtemp(prefix='deployplan-')
        self.addCleanup(shutil.rmtree, self.rt, ignore_errors=True)
        self.roots = {'claude': os.path.join(self.rt, 'claude')}

    def entry(self, name, status):
        return {'skill': name, 'source': name, 'mode': 'IDENTICAL',
                'status': status, 'targets': ['claude']}

    def planned(self, status, name='ads-audit'):
        """Use a skill that really exists in the repo, so `plan` reaches the
        status filter rather than bailing out on a missing source directory."""
        actions, extras, problems = ds.plan(
            {'skills': [self.entry(name, status)]}, self.roots, only_skill=name)
        self.assertEqual(problems, [], f'unexpected problems: {problems}')
        return actions


class TestExposureDoesNotGateDelivery(PlanTestCase):
    def test_active_is_delivered(self):
        self.assertTrue(self.planned('active'), 'active must deploy')

    def test_on_demand_is_delivered(self):
        """The change. An on-demand skill absent from disk cannot be loaded."""
        self.assertTrue(
            self.planned('on-demand'),
            'on-demand means installed but not auto-loaded, so it must deploy')

    def test_hold_is_not_delivered(self):
        """`hold` is about unsettled content, not exposure, and stays excluded."""
        self.assertEqual(self.planned('hold'), [],
                         'a held skill must not be deployed')

    def test_non_deployable_mode_is_still_excluded(self):
        """Mode remains the delivery gate; relaxing status must not widen it."""
        e = self.entry('ads-audit', 'active')
        e['mode'] = 'VENDORED'
        actions, _extras, problems = ds.plan(
            {'skills': [e]}, self.roots, only_skill='ads-audit')
        self.assertEqual(actions, [])
        self.assertEqual(problems, [])


if __name__ == '__main__':
    unittest.main()

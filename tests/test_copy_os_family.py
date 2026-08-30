"""The Copy OS family's safety and structure invariants.

Risk class: AI guardrail (risk-based-tdd) -> the interesting property here is
not "does the skill exist" but "can a skill in this family fabricate a business
fact". That property is enforced by prose, and prose silently rots. These tests
pin the parts of the prose that are load-bearing.

Three failure modes this targets, all of which ship silently:

1. **A skill loses its provenance rule.** Every skill in this family is
   permitted to write company-specific copy. The only thing stopping it from
   inventing a customer quote is the "never invent" block in its own body. A
   skill that loses that block still loads, still works, and still reads well -
   it just fabricates.

2. **A fabricated example leaks into the methodology.** A realistic-looking
   testimonial written as an illustration is indistinguishable from a real one
   once it is copy-pasted out of the skill. The family's own rule is "write the
   slot, not a value"; these tests hold the family to it.

3. **A handoff points at a skill that does not exist.** The routing is prose,
   so a renamed or removed skill leaves a dangling reference that reads as
   authoritative and silently routes nowhere.

Not tested here: whether the advice is *good*. That is a human question. These
tests cover only the properties whose violation is invisible to a reader.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(_HERE)
MANIFEST = os.path.join(ROOT, 'manifests', 'skills.json')

FAMILY = [
    'copy-os',
    'copy-strategist',
    'direct-response-copy',
    'persuasion-engine',
    'copychief',
    'humanizer',
    'compliance-review',
    'landing-page-copy',
    'ad-copy',
    'email-copy',
    'social-copy',
]

# Skills that generate or edit company-specific copy must carry the rule. Every
# member of the family does, including the router.
MUST_CARRY_PROVENANCE = set(FAMILY)

# The eight contract elements the family's design requires of every skill.
REQUIRED_SECTIONS = (
    ('trigger', re.compile(r'(?mi)^## When to Activate\b')),
    ('non-trigger', re.compile(r'(?mi)^## When NOT to Activate\b')),
    ('output contract', re.compile(r'(?mi)^## Output contract\b')),
    ('quality gates', re.compile(r'(?mi)^## Quality gates\b')),
    ('failure conditions', re.compile(r'(?mi)^## Failure conditions\b')),
    ('handoffs', re.compile(r'(?mi)^## Handoffs\b')),
)

FRONTMATTER_NAME = re.compile(r'''(?m)^name:\s*(?:"([^"]+)"|'([^']+)'|(\S+))\s*$''')


def read(name):
    with open(os.path.join(ROOT, name, 'SKILL.md'), encoding='utf-8') as fh:
        return fh.read()


def manifest_entries():
    with open(MANIFEST, encoding='utf-8') as fh:
        return {e['skill']: e for e in json.load(fh)['skills']}


class TestFamilyIsPresent(unittest.TestCase):
    def test_every_skill_exists_with_a_skill_md(self):
        missing = [n for n in FAMILY
                   if not os.path.isfile(os.path.join(ROOT, n, 'SKILL.md'))]
        self.assertEqual([], missing, f'family members missing a SKILL.md: {missing}')

    def test_frontmatter_name_matches_folder(self):
        for name in FAMILY:
            with self.subTest(skill=name):
                m = FRONTMATTER_NAME.search(read(name))
                self.assertIsNotNone(m, f'{name}: no name in frontmatter')
                declared = next(g for g in m.groups() if g)
                self.assertEqual(name, declared)

    def test_first_line_is_the_frontmatter_delimiter(self):
        # A SKILL.md whose first line is not `---` is silently never registered.
        for name in FAMILY:
            with self.subTest(skill=name):
                with open(os.path.join(ROOT, name, 'SKILL.md'), encoding='utf-8') as fh:
                    self.assertEqual('---', fh.readline().rstrip('\n'))


class TestSafetyRules(unittest.TestCase):
    """The properties whose loss is invisible to a reader."""

    def test_every_skill_carries_the_provenance_rule(self):
        for name in sorted(MUST_CARRY_PROVENANCE):
            with self.subTest(skill=name):
                body = read(name)
                self.assertRegex(
                    body, r'(?i)never (invent|add)',
                    f'{name}: lost its "never invent" rule - it may now fabricate')
                self.assertIn(
                    'fact-provenance.md', body,
                    f'{name}: no longer points at the provenance contract')

    def test_every_skill_defines_the_three_labels(self):
        for name in sorted(MUST_CARRY_PROVENANCE):
            with self.subTest(skill=name):
                body = read(name)
                self.assertIn('[NEEDS-INPUT]', body,
                              f'{name}: lost the gap label, so a gap has nowhere to go')

    def test_no_fabricated_testimonial_appears_in_the_methodology(self):
        # A quoted sentence attributed to a Firstname Lastname is a fabricated
        # testimonial the moment someone copies it out of the skill.
        attributed = re.compile(r'"[^"\n]{15,}"\s*[-—]\s*[A-Z][a-z]+\s+[A-Z][a-z]+')
        for name in FAMILY:
            with self.subTest(skill=name):
                hits = attributed.findall(read(name))
                self.assertEqual([], hits, f'{name}: attributed quote(s) {hits}')

    def test_no_invented_customer_counts(self):
        # "4,827 teams switched" reads as a real result once it leaves the file.
        counts = re.compile(
            r'\b\d{1,3},\d{3}\+?\s+(teams|customers|users|companies|businesses|clients)\b',
            re.I)
        for name in FAMILY:
            with self.subTest(skill=name):
                hits = counts.findall(read(name))
                self.assertEqual([], hits, f'{name}: invented customer count {hits}')

    def test_persuasion_engine_names_every_hard_stop(self):
        # These are the anti-patterns the family exists to refuse. Losing one
        # silently re-permits it.
        body = read('persuasion-engine')
        for term in ('Fabricated scarcity', 'Fabricated authority',
                     'Fabricated statistics', 'Invented testimonials',
                     'False guarantees', 'Sensitive-attribute targeting'):
            with self.subTest(hard_stop=term):
                self.assertIn(term, body)

    def test_compliance_review_does_not_assert_platform_policy_as_settled(self):
        # A stale rule stated confidently is worse than no rule: the review
        # reads CLEAR against a policy that no longer exists.
        ref = os.path.join(ROOT, 'compliance-review', 'references',
                           'platform-policy-checkpoints.md')
        self.assertTrue(os.path.isfile(ref))
        with open(ref, encoding='utf-8') as fh:
            body = fh.read()
        self.assertRegex(body, r'(?i)not a policy snapshot')
        self.assertRegex(body, r'(?i)verify')
        self.assertRegex(read('compliance-review'),
                         r'(?i)verify .{0,40}(current )?polic')

    def test_humanizer_protects_meaning(self):
        # The stated failure mode of a humanizer is weakening true, strong copy.
        body = read('humanizer')
        self.assertRegex(body, r'(?i)do not make strong copy casual')
        self.assertRegex(body, r'(?i)## Never add')


class TestStructuralContract(unittest.TestCase):
    def test_every_skill_has_all_contract_sections(self):
        for name in FAMILY:
            body = read(name)
            for label, pattern in REQUIRED_SECTIONS:
                with self.subTest(skill=name, section=label):
                    self.assertRegex(body, pattern,
                                     f'{name}: missing "{label}" section')

    def test_handoffs_reference_skills_that_exist(self):
        # A dangling handoff routes nowhere while reading as authoritative.
        on_disk = {d for d in os.listdir(ROOT)
                   if os.path.isdir(os.path.join(ROOT, d)) and not d.startswith('.')}
        referenced = re.compile(r'`([a-z][a-z0-9-]{2,})`')
        # Words in backticks that are prose or file references, not skill names.
        ignore = {'fact-provenance.md', 'copy-brief.md'}
        for name in FAMILY:
            with self.subTest(skill=name):
                section = read(name).split('## Handoffs', 1)
                self.assertEqual(2, len(section), f'{name}: no Handoffs section')
                tail = section[1]
                for token in referenced.findall(tail):
                    if token in ignore or '.' in token:
                        continue
                    self.assertIn(token, on_disk,
                                  f'{name}: handoff names "{token}", which is not a skill')

    def test_copy_os_carries_both_shared_contracts(self):
        for ref in ('copy-brief.md', 'fact-provenance.md'):
            with self.subTest(reference=ref):
                self.assertTrue(
                    os.path.isfile(os.path.join(ROOT, 'copy-os', 'references', ref)))

    def test_copy_os_documents_precedence_local_over_global(self):
        body = read('copy-os')
        self.assertIn('TASK / CAMPAIGN INSTRUCTIONS', body)
        self.assertIn('GLOBAL METHODOLOGY', body)
        # Local must be listed above global, or the ordering claim is inverted.
        self.assertLess(body.index('TASK / CAMPAIGN INSTRUCTIONS'),
                        body.index('GLOBAL METHODOLOGY'))

    def test_boundaries_against_adjacent_skills_are_stated(self):
        # Each of these pairs collides on trigger words; the non-trigger section
        # is the only thing separating them.
        for skill, neighbour in (('ad-copy', 'ads-creative'),
                                 ('landing-page-copy', 'ads-landing'),
                                 ('email-copy', 'email-ops'),
                                 ('social-copy', 'content-engine'),
                                 ('humanizer', 'brand-voice'),
                                 ('direct-response-copy', 'article-writing')):
            with self.subTest(skill=skill, neighbour=neighbour):
                body = read(skill)
                head = body.split('## Inputs required')[0]
                self.assertIn(neighbour, head,
                              f'{skill}: does not disambiguate itself from {neighbour}')


class TestManifestGovernance(unittest.TestCase):
    def test_every_family_member_is_declared(self):
        entries = manifest_entries()
        missing = [n for n in FAMILY if n not in entries]
        self.assertEqual([], missing, f'undeclared, so ungoverned: {missing}')

    def test_declared_hash_matches_the_source_bytes(self):
        entries = manifest_entries()
        for name in FAMILY:
            with self.subTest(skill=name):
                path = os.path.join(ROOT, name, 'SKILL.md')
                with open(path, 'rb') as fh:
                    actual = hashlib.sha256(fh.read()).hexdigest()
                self.assertEqual(entries[name]['expected_sha256'], actual)

    def test_family_deploys_somewhere(self):
        # A skill declared with no target is exposed nowhere and silently absent.
        entries = manifest_entries()
        for name in FAMILY:
            with self.subTest(skill=name):
                self.assertTrue(entries[name]['targets'],
                                f'{name}: declared with no runtime target')
                self.assertIn(entries[name]['status'], ('active', 'on-demand'))

    def test_family_is_grouped(self):
        entries = manifest_entries()
        for name in FAMILY:
            with self.subTest(skill=name):
                self.assertEqual('copy-os', entries[name]['family'])


if __name__ == '__main__':
    unittest.main()
